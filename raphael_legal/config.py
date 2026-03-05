import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = Path(__file__).parent.parent


class Settings:
    def __init__(self) -> None:
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-sonnet-4-6")
        self.OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", str(_PROJECT_ROOT / "output")))
        self.TEMPLATES_DIR: Path = Path(os.getenv("TEMPLATES_DIR", str(_PROJECT_ROOT / "templates")))
