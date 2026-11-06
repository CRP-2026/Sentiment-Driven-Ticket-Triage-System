import os
import sys
import os
from pathlib import Path
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    db_url: str = "sqlite:///./tickets.db"
    testing: bool = False
    model_name: str = "mock"          # mock | baseline | deberta
    model_path: str = str(BASE_DIR / "models")
    model_task: str = "absa"          # absa | document
    enable_abte: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]
    hf_hub_offline: bool = False

    configs_dir: str = str(BASE_DIR / "configs")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=(),
    )

    def is_testing(self) -> bool:
        return self.testing or os.getenv("TESTING", "").lower() in ("true", "1") or "pytest" in sys.modules

settings = Settings()
