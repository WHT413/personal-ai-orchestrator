"""
Config loader — reads config/config.yaml and exposes typed settings.

Usage:
    from config.settings import load_config
    cfg = load_config()
    print(cfg.llm.binary_path)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config" / "config.yaml"


@dataclass
class LLMConfig:
    binary_path: str
    model_path: str
    context_size: int
    gpu_layers: int
    temperature: float
    timeout_seconds: int


@dataclass
class DataConfig:
    dir: str  # resolved to absolute path by loader


@dataclass
class TelegramConfig:
    bot_token: str


@dataclass
class AppConfig:
    llm: LLMConfig
    data: DataConfig
    telegram: TelegramConfig


def load_config(path: str | Path | None = None) -> AppConfig:
    """
    Load configuration from a YAML file.

    Resolution order:
    1. `path` argument (if provided)
    2. CONFIG_PATH environment variable
    3. config/config.yaml  (default)

    Args:
        path: Optional explicit path to a config YAML file.

    Returns:
        Populated AppConfig instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        KeyError / ValueError: If required fields are missing.
    """
    config_path = Path(
        path
        or os.environ.get("CONFIG_PATH", "")
        or _DEFAULT_CONFIG_PATH
    )

    if not config_path.is_absolute():
        config_path = _PROJECT_ROOT / config_path

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Copy config/config.example.yaml to config/config.yaml and fill in your values."
        )

    with config_path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm_raw = raw["llm"]
    model_path = llm_raw["model_path"]
    if not os.path.isabs(model_path):
        model_path = str(_PROJECT_ROOT / model_path)

    binary_path = llm_raw["binary_path"]
    if not os.path.isabs(binary_path):
        binary_path = str(_PROJECT_ROOT / binary_path)

    llm = LLMConfig(
        binary_path=binary_path,
        model_path=model_path,
        context_size=int(llm_raw.get("context_size", 4096)),
        gpu_layers=int(llm_raw.get("gpu_layers", -1)),
        temperature=float(llm_raw.get("temperature", 0.7)),
        timeout_seconds=int(llm_raw.get("timeout_seconds", 300)),
    )

    # ── Data ─────────────────────────────────────────────────────────────────
    data_raw = raw.get("data", {})
    data_dir = data_raw.get("dir", "data")
    if not os.path.isabs(data_dir):
        data_dir = str(_PROJECT_ROOT / data_dir)

    data = DataConfig(dir=data_dir)

    # ── Telegram ─────────────────────────────────────────────────────────────
    tg_raw = raw.get("telegram", {})
    telegram = TelegramConfig(
        bot_token=tg_raw.get("bot_token", ""),
    )

    return AppConfig(llm=llm, data=data, telegram=telegram)
