---
name: model-router
description: "Auto-route Hermes tasks to the best model — code→Sonnet, research→DeepSeek, creative→Gemini, plan→Opus, review→Sonnet"
tags: [hermes, routing, model, dispatch, optimization]
---

# Model Router

Tự động đánh giá task của user và route đến model phù hợp nhất.

## Cách hoạt động

```
User message
     │
     ▼
  Hermes đọc skill này
     │
     ├── task CODE/DEBUG    → delegate_task(model=Sonnet)  [có tool access]
     ├── task RESEARCH      → delegate_task(model=DeepSeek) [phân tích sâu]
     ├── task CREATIVE      → model_dispatch(Gemini)        [1-shot đủ]
     ├── task PLAN/REVIEW   → delegate_task(model=Opus)     [cần reasoning]
     └── chat thường        → reply thẳng                   [tiết kiệm]
```

## Luật route

Đọc `~/.hermes/model-router/config.yaml` để biết provider + model cho từng loại task.

### Khi nào dùng delegate_task
- Task cần tools: terminal, file, git, search
- Task dài, nhiều bước
- Code, debug, research, plan

### Khi nào dùng model_dispatch
- Task 1-shot: creative writing, content
- Review code (chỉ cần đọc, không cần sửa)

### Khi nào reply thẳng
- Chat đơn giản, câu hỏi ngắn
- Không match keyword nào

## Config

Xem config hiện tại:
```bash
model-router show
```

Set provider URL (OpenRouter, 9router, custom, ...):
```bash
model-router url https://openrouter.ai/api/v1
model-router url http://localhost:20128/v1 -n custom:9router
```

Sửa model cho 1 category:
```bash
model-router set code ag/claude-opus-4-6-thinking
model-router set research ds/deepseek-v4-pro-max
```

Xem model khả dụng từ provider:
```bash
model-router list-models
```

## delegate_task format

Đọc `provider.name` và `provider.api_url` từ config.yaml để biết provider. Mặc định `custom:9router`.

```python
delegate_task(
    goal="...",
    context="...",
    model={
        "provider": "custom:9router",         # từ config provider.name
        "model": "ag/claude-sonnet-4-6"        # từ config routing.code
    }
)
```

## Lưu ý

- Luôn đọc config.yaml trước khi route — user có thể đã thay đổi model mapping hoặc provider
- Với task code/research: truyền đủ context (file paths, error messages, constraints)
- Nếu delegate_task fail → thử model_dispatch với model default
- KHÔNG tự ý sửa config.yaml
