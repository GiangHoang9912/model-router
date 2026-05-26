# Hermes Model Router

Auto-route Hermes Agent tasks to the best model based on task type.

```
Task code/debug  → Claude Sonnet    (delegate_task — full tools)
Task research    → DeepSeek Pro     (delegate_task — deep analysis)
Task creative    → Gemini Flash     (model_dispatch — 1-shot)
Task plan/review → Claude Opus      (delegate_task — reasoning)
Chat thường      → reply thẳng      (tiết kiệm)
```

## Install

```bash
pip install hermes-model-router

# Hoặc dev mode:
pip install -e .
```

## Setup

```bash
# 1. Cài skill vào Hermes
model-router init

# 2. Set provider URL của bạn (ai cũng dùng được, không chỉ 9router)
model-router url https://openrouter.ai/api/v1 -n custom:openrouter

# 3. Xem config
model-router show

# 4. Xem model khả dụng
model-router list-models
```

## Commands

| Command | Mô tả |
|---------|-------|
| `model-router init` | Cài skill vào Hermes |
| `model-router show` | Xem config hiện tại |
| `model-router url <url>` | Set provider API URL |
| `model-router set <cat> <model>` | Set model cho category |
| `model-router list-models` | Liệt kê model từ provider |
| `model-router route <text>` | Test phân loại task |
| `model-router reset` | Reset về mặc định |

## Config file

`~/.hermes/model-router/config.yaml`

```yaml
provider:
  name: custom:openrouter
  api_url: https://openrouter.ai/api/v1

routing:
  code: openai/gpt-4o
  research: anthropic/claude-sonnet-4
  creative: google/gemini-2.5-flash
  plan: anthropic/claude-opus-4
  review: anthropic/claude-sonnet-4
  default: openai/gpt-4o

keywords:
  code: [fix, bug, implement, refactor, ...]
  ...
```

## Requirements

- Python >= 3.10
- Hermes Agent
- Provider API (9router, OpenRouter, or any OpenAI-compatible endpoint)
# model-router
# model-router
# model-router
# model-router
# model-router
# model-router
