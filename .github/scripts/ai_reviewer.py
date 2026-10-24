#!/usr/bin/env python3
"""AI Pull Request Reviewer using Gemini API and custom guidelines.

Zero external dependencies - uses Python standard library only.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


def get_env_var(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "").strip()
    if required and not val:
        print(f"Error: Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return val


def get_git_diff(base_ref: str) -> str:
    """Extract git diff against the target base branch."""
    try:
        # Fetch base branch if not present
        subprocess.run(
            ["git", "fetch", "origin", base_ref, "--depth=50"],
            check=False,
            capture_output=True,
            text=True,
        )
        cmd = ["git", "diff", f"origin/{base_ref}...HEAD"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        diff = res.stdout.strip()
        if not diff:
            # Fallback to diff against origin/main or HEAD~1
            fallback = subprocess.run(
                ["git", "diff", "HEAD~1"],
                capture_output=True,
                text=True,
                check=False,
            )
            diff = fallback.stdout.strip()
        return diff
    except Exception as e:
        print(f"Warning: Failed to get git diff via origin/{base_ref}: {e}")
        return ""


def load_guidelines(guidelines_path: str) -> str:
    """Load custom guidelines markdown file."""
    if os.path.exists(guidelines_path):
        with open(guidelines_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Tuân thủ Clean Code, Security, và các quy chuẩn dự án."


def call_gemini(api_key: str, prompt: str, model_name: str = "gemini-3.6-flash") -> tuple[str, str]:
    """Call Google Gemini API (defaults to Gemini 3.6 Flash, with fallback)."""
    models_to_try = [model_name]
    for fallback in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            print(f"Calling Gemini API with model: {model}...")
            with urllib.request.urlopen(req, timeout=90) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", ""), model
                return "Không nhận được phản hồi hợp lệ từ Gemini.", model
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"Model {model} failed with HTTP {e.code}: {err_body}", file=sys.stderr)
            last_error = e
            # Handle rate-limit, overload, model not found, or server error by trying fallback model
            if e.code in (400, 404, 429, 500, 502, 503, 504):
                print(f"Model {model} returned HTTP {e.code} (overloaded or unavailable). Retrying with next fallback model...", file=sys.stderr)
                continue
            raise
        except Exception as e:
            print(f"Model {model} error: {e}", file=sys.stderr)
            last_error = e
            continue

    if last_error:
        raise last_error
    return "Không nhận được phản hồi từ các mô hình Gemini.", model_name


def post_github_comment(github_token: str, repo: str, pr_number: str, comment: str) -> None:
    """Post comment to GitHub Pull Request via REST API."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = {"body": comment}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status in (200, 201):
            print(f"Comment successfully posted to PR #{pr_number}.")
        else:
            print(f"Unexpected response status: {resp.status}", file=sys.stderr)


def main():
    gemini_api_key = get_env_var("GEMINI_API_KEY")
    github_token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    if not pr_number:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path, "r", encoding="utf-8") as f:
                    event = json.load(f)
                if "pull_request" in event:
                    pr_number = str(event["pull_request"].get("number", ""))
                elif "issue" in event:
                    pr_number = str(event["issue"].get("number", ""))
            except Exception:
                pass
    if not pr_number:
        print("Error: Missing required environment variable: PR_NUMBER", file=sys.stderr)
        sys.exit(1)

    base_ref = os.environ.get("BASE_REF", "main")
    pr_title = os.environ.get("PR_TITLE", "N/A")
    pr_body = os.environ.get("PR_BODY", "N/A")
    guidelines_file = os.environ.get("GUIDELINES_FILE", ".github/review_guidelines.md")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

    guidelines = load_guidelines(guidelines_file)
    diff = get_git_diff(base_ref)

    if not diff:
        print("Diff is empty. Nothing to review.")
        sys.exit(0)

    # Truncate diff if excessively long to avoid token limits
    max_diff_chars = 45000
    if len(diff) > max_diff_chars:
        diff_snippet = diff[:max_diff_chars] + "\n\n... [Diff quá dài, đã được cắt bớt] ..."
    else:
        diff_snippet = diff

    prompt = f"""Bạn là Senior Tech Lead kiêm AI Code Reviewer cho dự án 'Sentiment-Driven Ticket Triage System'.
Nhiệm vụ của bạn là review Pull Request dưới đây theo đúng các tiêu chí và định dạng được quy định trong tài liệu hướng dẫn.

### BỘ QUY TẮC & TIÊU CHÍ REVIEW (TỰ CẤU HÌNH):
{guidelines}

---

### THÔNG TIN PULL REQUEST #{pr_number}:
- **Tiêu đề PR**: {pr_title}
- **Nhánh mục tiêu (Base Branch)**: {base_ref}
- **Mô tả PR**:
{pr_body}

---

### NỘI DUNG THAY ĐỔI (GIT DIFF):
```diff
{diff_snippet}
```

Hãy phân tích kỹ diff, đối chiếu với từng tiêu chí trong hướng dẫn và xuất báo cáo review bằng tiếng Việt theo đúng cấu trúc mẫu ở mục 4 của hướng dẫn.
"""

    print(f"Analyzing PR #{pr_number} with {model_name}...")
    review_content, used_model = call_gemini(gemini_api_key, prompt, model_name=model_name)

    full_comment = review_content.strip()

    print("Posting review comment to PR...")
    post_github_comment(github_token, repo, pr_number, full_comment)
    print("Done!")


if __name__ == "__main__":
    main()
