"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parent
FIXTURES_DIR = REPO_ROOT / "fixtures"

OWNER_SIGN = os.getenv("DESK_OWNER_SIGN", "✝️🧿🪬")
ASSISTANT_SIGN = os.getenv("DESK_ASSISTANT_SIGN", "3️⃣🧿5️⃣")
OPERATOR = os.getenv("DESK_OPERATOR", "elghaly / Wyndham Heaven")

# demo = scripted Strands loop (no cloud keys); bedrock/openai = live model when configured
MODEL_MODE = os.getenv("DESK_MODEL_MODE", "demo").lower()


@dataclass(frozen=True)
class Settings:
    owner_sign: str = OWNER_SIGN
    assistant_sign: str = ASSISTANT_SIGN
    operator: str = OPERATOR
    model_mode: str = MODEL_MODE
    fixtures_dir: Path = FIXTURES_DIR


def get_settings() -> Settings:
    return Settings()
