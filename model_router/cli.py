"""model-router CLI — quản lý config và dispatch task."""

import argparse
import shutil
import sys
from pathlib import Path

from .router import (
    classify,
    fetch_available_models,
    get_config_path,
    get_default_config,
    get_model_for_task,
    get_provider,
    load_config,
    save_config,
)


SKILL_DIR = Path.home() / ".hermes" / "skills" / "model-router"
PACKAGE_SKILL = Path(__file__).parent / "skill"


def cmd_show():
    cfg = load_config()
    provider_name, api_url = get_provider(cfg)
    print("📋 Model Router Config")
    print(f"   File: {get_config_path()}")
    print()
    print(f"   Provider : {provider_name}")
    print(f"   API URL  : {api_url}")
    print()
    print("   Routing:")
    for cat, model in cfg["routing"].items():
        print(f"     {cat:12s} → {model}")
    print()
    print("   Keywords:")
    for cat, words in cfg["keywords"].items():
        print(f"     {cat:12s} : {', '.join(words[:5])}{'...' if len(words) > 5 else ''}")


def cmd_set(category, model):
    cfg = load_config()
    if category not in cfg["routing"]:
        print(f"❌ Category '{category}' không tồn tại. Các category: {list(cfg['routing'].keys())}")
        sys.exit(1)
    old = cfg["routing"][category]
    cfg["routing"][category] = model
    save_config(cfg)
    print(f"✅ {category}: {old} → {model}")


def cmd_url(url=None, name=None):
    """Set hoặc xem provider URL."""
    cfg = load_config()
    provider_name, old_url = get_provider(cfg)

    if url is None:
        print(f"   Provider : {provider_name}")
        print(f"   API URL  : {old_url}")
        return

    if "provider" not in cfg:
        cfg["provider"] = {}

    cfg["provider"]["api_url"] = url
    if name:
        cfg["provider"]["name"] = name

    save_config(cfg)
    print(f"✅ API URL: {old_url} → {url}")
    if name:
        print(f"   Provider name: {name}")
    print()
    print("   Test kết nối:")
    print(f"     model-router list-models")


def cmd_list_models():
    cfg = load_config()
    _, api_url = get_provider(cfg)
    models = fetch_available_models(cfg)

    if not models:
        print(f"❌ Không kết nối được: {api_url}")
        sys.exit(1)

    print(f"📡 Models from {api_url} ({len(models)}):")
    print()
    # Group by prefix
    groups = {}
    for m in sorted(models):
        prefix = m.split("/")[0] if "/" in m else "other"
        groups.setdefault(prefix, []).append(m)
    for prefix, ms in sorted(groups.items()):
        print(f"  [{prefix}]")
        for m in ms:
            print(f"    {m}")
        print()


def cmd_reset():
    import yaml
    with open(get_default_config()) as f:
        cfg = yaml.safe_load(f)
    save_config(cfg)
    print("✅ Config reset về mặc định")


def cmd_route(text):
    cfg = load_config()
    provider_name, api_url = get_provider(cfg)
    cat, model, _, _ = get_model_for_task(text, cfg)
    keywords = cfg["keywords"].get(cat, [])
    matched = [kw for kw in keywords if kw.lower() in text.lower()]
    print(f"📤 Route: \"{text[:60]}{'...' if len(text)>60 else ''}\"")
    print(f"   Provider : {provider_name} ({api_url})")
    print(f"   Category : {cat}")
    print(f"   Model    : {model}")
    print(f"   Matched  : {matched[:3]}")


def cmd_init():
    """Cài skill model-router vào Hermes."""
    if not PACKAGE_SKILL.exists():
        print("❌ Không tìm thấy thư mục skill/ trong package")
        sys.exit(1)

    SKILL_DIR.mkdir(parents=True, exist_ok=True)

    # Copy SKILL.md
    shutil.copy2(PACKAGE_SKILL / "SKILL.md", SKILL_DIR / "SKILL.md")

    # Copy references
    ref_dir = SKILL_DIR / "references"
    ref_dir.mkdir(exist_ok=True)
    src_ref = PACKAGE_SKILL / "references"
    if src_ref.exists():
        for f in src_ref.iterdir():
            shutil.copy2(f, ref_dir / f.name)

    # Copy default config nếu chưa có
    if not get_config_path().exists():
        cfg = load_config()
        save_config(cfg)

    print("✅ Model Router đã được cài vào Hermes!")
    print(f"   Skill : {SKILL_DIR}")
    print(f"   Config: {get_config_path()}")
    print()
    print("   Cấu hình provider của bạn:")
    print("     model-router url https://openrouter.ai/api/v1")
    print()
    print("   Dùng thử:")
    print("     model-router show")
    print("     model-router list-models")


def main():
    parser = argparse.ArgumentParser(
        prog="model-router",
        description="Auto route Hermes tasks to the best model",
    )
    subs = parser.add_subparsers(dest="cmd")

    subs.add_parser("show", help="Hiển thị config hiện tại")
    subs.add_parser("list-models", help="Liệt kê model khả dụng từ provider")
    subs.add_parser("reset", help="Reset config về mặc định")
    subs.add_parser("init", help="Cài skill vào Hermes")

    set_p = subs.add_parser("set", help="Set model cho 1 category")
    set_p.add_argument("category", help="Category: code, research, creative, plan, review, default")
    set_p.add_argument("model", help="Model ID (vd: ag/claude-sonnet-4-6)")

    url_p = subs.add_parser("url", help="Xem hoặc set provider URL")
    url_p.add_argument("url", nargs="?", help="API URL (vd: https://openrouter.ai/api/v1)")
    url_p.add_argument("--name", "-n", help="Provider name (vd: custom:openrouter)")

    route_p = subs.add_parser("route", help="Test route 1 task text")
    route_p.add_argument("text", help="Task text để test")

    args = parser.parse_args()

    if args.cmd == "show":
        cmd_show()
    elif args.cmd == "set":
        cmd_set(args.category, args.model)
    elif args.cmd == "url":
        cmd_url(url=args.url, name=args.name)
    elif args.cmd == "list-models":
        cmd_list_models()
    elif args.cmd == "reset":
        cmd_reset()
    elif args.cmd == "route":
        cmd_route(args.text)
    elif args.cmd == "init":
        cmd_init()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
