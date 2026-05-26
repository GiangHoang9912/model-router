"""Core routing logic: classify task → dispatch to best model."""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


def get_config_dir():
    """~/.hermes/model-router/ — nơi chứa config và state."""
    return Path.home() / ".hermes" / "model-router"


def get_config_path():
    return get_config_dir() / "config.yaml"


def get_default_config():
    """Config mặc định — dùng khi chưa có config user."""
    return Path(__file__).parent / "config.yaml"


def load_config():
    """Load config của user, fallback về default."""
    user = get_config_path()
    if user.exists():
        with open(user) as f:
            return yaml.safe_load(f)
    with open(get_default_config()) as f:
        return yaml.safe_load(f)


def save_config(cfg):
    """Ghi config xuống disk."""
    get_config_dir().mkdir(parents=True, exist_ok=True)
    with open(get_config_path(), "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def get_provider(cfg):
    """Trả về (provider_name, api_url) từ config."""
    p = cfg.get("provider", {})
    return p.get("name", "custom:9router"), p.get("api_url", "http://localhost:20128/v1")


def classify(text, keywords):
    """Phân loại text dựa vào keyword list."""
    t = text.lower()
    for category, words in keywords.items():
        if any(w.lower() in t for w in words):
            return category
    return "default"


def get_model_for_task(text, cfg):
    """Trả về (category, model, provider_name, api_url) cho 1 task."""
    routing = cfg["routing"]
    keywords = cfg["keywords"]
    provider_name, api_url = get_provider(cfg)
    cat = classify(text, keywords)
    model = routing.get(cat, routing["default"])
    return cat, model, provider_name, api_url


def dispatch_via_hermes_cli(prompt, model, cfg):
    """Gửi task đến model cụ thể qua Hermes CLI 1-shot."""
    result = subprocess.run(
        ["hermes", "--model", model, prompt],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result.stdout if result.returncode == 0 else result.stderr


def fetch_available_models(cfg=None):
    """Lấy danh sách model từ provider api_url trong config."""
    import urllib.request

    if cfg is None:
        cfg = load_config()

    _, api_url = get_provider(cfg)
    models_url = api_url.rstrip("/") + "/models"

    try:
        with urllib.request.urlopen(models_url, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["id"] for m in data.get("data", [])]
    except Exception:
        return []
