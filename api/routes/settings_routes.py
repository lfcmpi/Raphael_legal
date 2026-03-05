"""Settings routes — env vars and system prompts (admin only)."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.auth import get_current_user
from api.db_models import User

router = APIRouter(prefix="/api/settings", tags=["settings"])

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_PROMPT_FILE = _PROJECT_ROOT / "insumos" / "prompt-legal-case-processor.md"
_ENV_FILE = _PROJECT_ROOT / ".env"

# Env keys that can be viewed/edited from the UI
EDITABLE_ENVS = [
    "ANTHROPIC_API_KEY",
    "MODEL_NAME",
    "OUTPUT_DIR",
    "TEMPLATES_DIR",
    "JWT_SECRET",
    "CORS_ORIGINS",
]


def _require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores")


# --- Env vars ---


class EnvVarsResponse(BaseModel):
    vars: dict[str, str]


class EnvVarsUpdateRequest(BaseModel):
    vars: dict[str, str]


def _read_env_file() -> dict[str, str]:
    result: dict[str, str] = {}
    if not _ENV_FILE.exists():
        return result
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def _write_env_file(data: dict[str, str]) -> None:
    lines = [f"{k}={v}" for k, v in data.items()]
    _ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


@router.get("/env", response_model=EnvVarsResponse)
def get_env_vars(user: User = Depends(get_current_user)) -> EnvVarsResponse:
    """Get editable env vars. Admin only. API keys are masked."""
    _require_admin(user)
    env_data = _read_env_file()
    filtered: dict[str, str] = {}
    for key in EDITABLE_ENVS:
        val = env_data.get(key, os.getenv(key, ""))
        # Mask secrets
        if "KEY" in key or "SECRET" in key:
            if len(val) > 8:
                filtered[key] = val[:8] + "..." + val[-4:]
            else:
                filtered[key] = "***"
        else:
            filtered[key] = val
    return EnvVarsResponse(vars=filtered)


@router.put("/env", response_model=EnvVarsResponse)
def update_env_vars(body: EnvVarsUpdateRequest, user: User = Depends(get_current_user)) -> EnvVarsResponse:
    """Update env vars. Admin only. Only editable keys accepted."""
    _require_admin(user)
    env_data = _read_env_file()

    for key, value in body.vars.items():
        if key not in EDITABLE_ENVS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Variavel '{key}' nao e editavel")
        # Skip masked values (user didn't change them)
        if value.endswith("...") and "..." in value:
            continue
        env_data[key] = value
        os.environ[key] = value

    _write_env_file(env_data)

    # Return masked version
    return get_env_vars(user)


# --- System prompt ---


class PromptResponse(BaseModel):
    content: str


class PromptUpdateRequest(BaseModel):
    content: str


@router.get("/prompt", response_model=PromptResponse)
def get_prompt(user: User = Depends(get_current_user)) -> PromptResponse:
    """Get system prompt. Admin only."""
    _require_admin(user)
    if _PROMPT_FILE.exists():
        content = _PROMPT_FILE.read_text(encoding="utf-8")
    else:
        content = ""
    return PromptResponse(content=content)


@router.put("/prompt", response_model=PromptResponse)
def update_prompt(body: PromptUpdateRequest, user: User = Depends(get_current_user)) -> PromptResponse:
    """Update system prompt. Admin only."""
    _require_admin(user)
    _PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PROMPT_FILE.write_text(body.content, encoding="utf-8")

    # Reload the cached prompt in the prompts module
    import raphael_legal.prompts as prompts_mod
    prompts_mod.SYSTEM_PROMPT = prompts_mod._load_system_prompt()

    return PromptResponse(content=body.content)
