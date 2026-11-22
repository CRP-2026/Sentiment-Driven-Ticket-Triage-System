import os
import shutil
import sys
import types
from pathlib import Path

from starlette.testclient import TestClient

from ticket_triage.api.main import _resolve_nli_model_source
from ticket_triage.core.sentiment import baseline as baseline_mod
from ticket_triage.core.sentiment.abte import extract_aspect_terms
from ticket_triage.core.sentiment.baseline import (
    DEFAULT_HF_MODELS,
    ZeroShotNliModel,
    load_aspect_hypotheses,
)
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.settings import settings


def test_load_aspect_hypotheses_none_path_and_invalid_yaml(tmp_path, monkeypatch):
    monkeypatch.setattr(baseline_mod, "_find_config_file", lambda _filename="": None)
    assert load_aspect_hypotheses() == {}

    missing = tmp_path / "missing.yaml"
    assert load_aspect_hypotheses(missing) == {}

    non_dict = tmp_path / "list.yaml"
    non_dict.write_text("- a\n- b\n", encoding="utf-8")
    assert load_aspect_hypotheses(non_dict) == {}


def test_zero_shot_nli_model_uses_injected_hypotheses_and_templates(monkeypatch):
    captured_calls: list[dict] = []

    def fake_classifier(text: str, candidate_labels: list[str], hypothesis_template: str):
        captured_calls.append(
            {
                "text": text,
                "candidate_labels": candidate_labels,
                "hypothesis_template": hypothesis_template,
            }
        )
        return {"labels": [candidate_labels[0]], "scores": [0.91]}

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.pipeline = lambda task, model, device=-1: fake_classifier
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    custom_hypotheses = {
        "overall_sentiment_template": "Overall tone is {}.",
        "aspect_sentiment_template": "Feedback on {aspect} sounds {sentiment}.",
        "aspect_names": {"refund_payment": "billing refunds"},
        "sentiments": {"negative": "angry", "neutral": "calm", "positive": "happy"},
    }
    model = ZeroShotNliModel(
        model_name_or_path="org/custom-deberta",
        hypotheses=custom_hypotheses,
    )

    assert model.is_mock is False
    result = model.predict("Please refund my card.", candidates=["refund_payment"])
    assert result.overall.label == "negative"
    assert result.overall.confidence == 0.91
    assert result.aspects[0].aspect == "refund_payment"
    assert captured_calls[0]["hypothesis_template"] == "Overall tone is {}."
    assert captured_calls[1]["hypothesis_template"] == "Feedback on billing refunds sounds {}."

    # Empty candidates list (document fallback mode) skips per-aspect NLI calls
    captured_calls.clear()
    doc_result = model.predict("Please refund my card.", candidates=[])
    assert doc_result.overall.label == "negative"
    assert doc_result.aspects == []
    assert len(captured_calls) == 1


def test_resolve_nli_model_source_priority(tmp_path):
    empty_models = tmp_path / "empty_models"
    empty_models.mkdir()
    (empty_models / ".gitkeep").write_text("", encoding="utf-8")

    # 1. Empty models dir without config.json falls back to default HF model for baseline/deberta
    src_base, kind_base = _resolve_nli_model_source("baseline", str(empty_models), "")
    assert src_base == DEFAULT_HF_MODELS["baseline"]
    assert kind_base == "default_hf"

    src_deb, kind_deb = _resolve_nli_model_source("deberta", str(empty_models), "")
    assert src_deb == DEFAULT_HF_MODELS["deberta"]
    assert kind_deb == "default_hf"

    # 2. Explicit MODEL_ID in .env overrides defaults when local dir has no config.json
    src_id, kind_id = _resolve_nli_model_source(
        "deberta", str(empty_models), "facebook/bart-large-mnli"
    )
    assert src_id == "facebook/bart-large-mnli"
    assert kind_id == "env_model_id"

    # 3. Valid local model dir containing config.json takes highest priority
    local_dir = tmp_path / "local_model"
    local_dir.mkdir()
    (local_dir / "config.json").write_text("{}", encoding="utf-8")
    src_local, kind_local = _resolve_nli_model_source(
        "deberta", str(local_dir), "facebook/bart-large-mnli"
    )
    assert src_local == str(local_dir)
    assert kind_local == "local"


def test_lifespan_model_selection_from_settings(client: TestClient, tmp_path, monkeypatch):
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    repo_configs = Path(__file__).resolve().parents[1] / "configs"
    for filename in ("aspects.yaml", "aspect_hypotheses.yaml", "priority_rules.yaml"):
        src = repo_configs / filename
        if src.is_file():
            shutil.copy2(src, configs_dir / filename)

    empty_models = tmp_path / "models_empty"
    empty_models.mkdir()
    (empty_models / ".gitkeep").write_text("", encoding="utf-8")

    local_models = tmp_path / "models_ready"
    local_models.mkdir()
    (local_models / "config.json").write_text('{"model_type": "deberta-v2"}', encoding="utf-8")

    orig_model = getattr(client.app.state, "sentiment_model", None)
    orig_name = getattr(client.app.state, "model_name", None)
    orig_task = getattr(client.app.state, "model_task", None)
    orig_abte = getattr(client.app.state, "enable_abte", None)
    orig_keywords = getattr(client.app.state, "aspect_keywords", None)
    orig_hf_offline = os.environ.get("HF_HUB_OFFLINE")

    monkeypatch.setattr(settings, "configs_dir", str(configs_dir))

    try:
        # Case A: MODEL_NAME=deberta with empty models dir -> uses default DeBERTa HF repo
        monkeypatch.setattr(settings, "model_name", "deberta")
        monkeypatch.setattr(settings, "model_path", str(empty_models))
        monkeypatch.setattr(settings, "model_id", "")
        monkeypatch.setattr(settings, "model_task", "absa")
        monkeypatch.setattr(settings, "hf_hub_offline", False)
        with TestClient(client.app) as scoped:
            assert scoped.app.state.model_name == "deberta"
            assert scoped.app.state.model_task == "absa"
            assert isinstance(scoped.app.state.sentiment_model, ZeroShotNliModel)
            assert (
                scoped.app.state.sentiment_model.model_name_or_path
                == DEFAULT_HF_MODELS["deberta"]
            )
            assert "sentiments" in scoped.app.state.sentiment_model._config
            assert os.environ.get("HF_HUB_OFFLINE") == "0"

        # Case B: MODEL_NAME=deberta with valid local config.json -> loads local dir + offline=1
        monkeypatch.setattr(settings, "model_path", str(local_models))
        monkeypatch.setattr(settings, "hf_hub_offline", True)
        with TestClient(client.app) as scoped:
            assert isinstance(scoped.app.state.sentiment_model, ZeroShotNliModel)
            assert scoped.app.state.sentiment_model.model_name_or_path == str(local_models)
            assert os.environ.get("HF_HUB_OFFLINE") == "1"

        # Case C: Custom MODEL_NAME with MODEL_ID and empty local path -> uses MODEL_ID
        monkeypatch.setattr(settings, "model_name", "custom")
        monkeypatch.setattr(settings, "model_path", str(empty_models))
        monkeypatch.setattr(settings, "model_id", "org/my-zero-shot-model")
        with TestClient(client.app) as scoped:
            assert isinstance(scoped.app.state.sentiment_model, ZeroShotNliModel)
            assert scoped.app.state.sentiment_model.model_name_or_path == "org/my-zero-shot-model"

        # Case D: MODEL_NAME=mock always picks MockSentimentModel even if config.json exists
        monkeypatch.setattr(settings, "model_name", "mock")
        monkeypatch.setattr(settings, "model_path", str(local_models))
        monkeypatch.setattr(settings, "model_task", "document")
        monkeypatch.setattr(settings, "enable_abte", False)
        with TestClient(client.app) as scoped:
            assert isinstance(scoped.app.state.sentiment_model, MockSentimentModel)
            assert scoped.app.state.model_task == "document"
            assert scoped.app.state.enable_abte is False
            resp = scoped.post(
                "/api/v1/tickets",
                json={"content": "My package is broken and never received! Urgent refund."},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["aspects"] == []
            assert body["dominant_aspect"] is None
            assert body["priority_breakdown"]["aspect_bonus"] == 0.0

        # Case E: ENABLE_ABTE=true populates extracted aspect terms in ABSA mode
        monkeypatch.setattr(settings, "model_name", "mock")
        monkeypatch.setattr(settings, "model_task", "absa")
        monkeypatch.setattr(settings, "enable_abte", True)
        with TestClient(client.app) as scoped:
            assert scoped.app.state.enable_abte is True
            resp = scoped.post(
                "/api/v1/tickets",
                json={"content": "My package never received and I need a refund to my credit card."},
            )
            assert resp.status_code == 201
            aspects_by_id = {item["aspect"]: item for item in resp.json()["aspects"]}
            assert "shipping" in aspects_by_id
            assert "never received" in aspects_by_id["shipping"]["terms"]
            assert "refund_payment" in aspects_by_id
            assert "credit card" in aspects_by_id["refund_payment"]["terms"]
    finally:
        if orig_hf_offline is None:
            os.environ.pop("HF_HUB_OFFLINE", None)
        else:
            os.environ["HF_HUB_OFFLINE"] = orig_hf_offline
        if orig_model is not None:
            client.app.state.sentiment_model = orig_model
        if orig_name is not None:
            client.app.state.model_name = orig_name
        if orig_task is not None:
            client.app.state.model_task = orig_task
        if orig_abte is not None:
            client.app.state.enable_abte = orig_abte
        if orig_keywords is not None:
            client.app.state.aspect_keywords = orig_keywords


def test_extract_aspect_terms_longest_match_first():
    terms = extract_aspect_terms(
        "My Package was NEVER RECEIVED and I was double charged on my Credit Card.",
        "refund_payment",
    )
    assert terms == ("double charged", "Credit Card")


def test_health_reports_model_loaded_false_on_nli_fallback(client: TestClient, monkeypatch):
    orig_model = getattr(client.app.state, "sentiment_model", None)
    orig_name = getattr(client.app.state, "model_name", None)
    try:
        fallback_nli = ZeroShotNliModel(model_name_or_path="org/missing-model", hypotheses={})
        monkeypatch.setattr(fallback_nli, "_ensure_loaded", lambda: None)
        fallback_nli._classifier = None
        client.app.state.model_name = "deberta"
        client.app.state.sentiment_model = fallback_nli

        res = client.get("/api/v1/health")
        assert res.status_code == 200
        payload = res.json()
        assert payload["is_mock"] is True
        assert payload["model_loaded"] is False
    finally:
        if orig_model is not None:
            client.app.state.sentiment_model = orig_model
        if orig_name is not None:
            client.app.state.model_name = orig_name


def test_single_aspect_factual_complaint_aligns_with_negative_overall(monkeypatch):
    def fake_classifier(text: str, candidate_labels: list[str], hypothesis_template: str):
        if "Regarding" in hypothesis_template:
            # Giả lập câu trần thuật ngắn bị NLI chấm neutral sát nút (0.52 vs 0.48)
            return {
                "labels": ["neutral", "negative", "positive"],
                "scores": [0.52, 0.48, 0.0],
            }
        return {
            "labels": ["negative", "neutral", "positive"],
            "scores": [0.88, 0.10, 0.02],
        }

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.pipeline = lambda task, model, device=-1: fake_classifier
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    model = ZeroShotNliModel(
        model_name_or_path="org/custom-deberta",
        hypotheses={
            "overall_sentiment_template": "This customer ticket is {}.",
            "aspect_sentiment_template": "Regarding {aspect}, this customer ticket is {sentiment}.",
            "aspect_names": {"refund_payment": "refunds, charges, billing or payment dispute"},
            "sentiments": {"positive": "positive", "neutral": "neutral", "negative": "negative"},
        },
    )
    res = model.predict("I was charged 5 times.", candidates=["refund_payment"])
    assert res.overall.label == "negative"
    assert res.overall.confidence == 0.88
    assert len(res.aspects) == 1
    assert res.aspects[0].aspect == "refund_payment"
    assert res.aspects[0].sentiment == "negative"
    assert res.aspects[0].confidence == 0.88


def test_repo_aspect_hypotheses_uses_problem_report_verbalizer():
    repo_hypotheses = Path(__file__).resolve().parents[1] / "configs" / "aspect_hypotheses.yaml"
    cfg = load_aspect_hypotheses(repo_hypotheses)
    assert "problem" in cfg["sentiments"]["negative"].lower()
    assert "informational" not in cfg["sentiments"]["neutral"].lower()
    assert "feeling" not in cfg["aspect_sentiment_template"].lower()
