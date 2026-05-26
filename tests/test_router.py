"""Tests for model-router."""

import yaml
from pathlib import Path
from model_router.router import classify, load_config, get_model_for_task, get_provider


def test_load_config():
    cfg = load_config()
    assert "routing" in cfg
    assert "keywords" in cfg
    assert "provider" in cfg
    assert "code" in cfg["routing"]
    assert "default" in cfg["routing"]


def test_provider_config():
    cfg = load_config()
    name, url = get_provider(cfg)
    assert "9router" in name or "openrouter" in name.lower() or len(name) > 0
    assert url.startswith("http")


def test_classify_code():
    kw = {
        "code": ["fix", "bug", "implement"],
        "research": ["analyze", "research"],
    }
    assert classify("fix login bug", kw) == "code"
    assert classify("implement api endpoint", kw) == "code"


def test_classify_research():
    kw = {
        "code": ["fix", "bug", "implement"],
        "research": ["analyze", "research"],
    }
    assert classify("analyze pros and cons", kw) == "research"
    assert classify("research microservices", kw) == "research"


def test_classify_default():
    kw = {
        "code": ["fix", "bug"],
        "research": ["analyze"],
    }
    assert classify("hello world", kw) == "default"


def test_classify_vietnamese():
    kw = {
        "code": ["sửa", "lỗi"],
        "research": ["phân tích", "nghiên cứu"],
    }
    assert classify("anh sửa con bug này", kw) == "code"
    assert classify("phân tích ưu nhược", kw) == "research"


def test_get_model_for_task():
    cfg = load_config()
    cat, model, provider, url = get_model_for_task("fix bug login", cfg)
    assert cat == "code"
    assert len(model) > 0
    assert len(provider) > 0


def test_default_model():
    cfg = load_config()
    cat, model, provider, url = get_model_for_task("hello", cfg)
    assert cat == "default"
    assert model == cfg["routing"]["default"]


def test_config_file_exists():
    assert Path(__file__).parent.parent / "model_router" / "config.yaml"
