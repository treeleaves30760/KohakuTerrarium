"""
Built-in LLM presets and model aliases.

Model-specific metadata that can't be obtained from APIs.
Keys are model names (or aliases). Users reference these by name.
"""

from typing import Any

# ── Built-in Presets ──────────────────────────────────────────
# Model-specific metadata that can't be obtained from APIs.
# Keys are model names (or aliases). Users reference these by name.

PRESETS: dict[str, dict[str, Any]] = {
    # ═══════════════════════════════════════════════════════
    #  OpenAI via Codex OAuth (ChatGPT subscription auth)
    # ═══════════════════════════════════════════════════════
    "gpt-5.4": {
        "provider": "codex-oauth",
        "model": "gpt-5.4",
        "max_context": 272000,
    },
    "gpt-5.3-codex": {
        "provider": "codex-oauth",
        "model": "gpt-5.3-codex",
        "max_context": 272000,
    },
    "gpt-5.1": {
        "provider": "codex-oauth",
        "model": "gpt-5.1",
        "max_context": 272000,
    },
    "gpt-4o": {
        "provider": "codex-oauth",
        "model": "gpt-4o",
        "max_context": 128000,
    },
    "gpt-4o-mini": {
        "provider": "codex-oauth",
        "model": "gpt-4o-mini",
        "max_context": 128000,
    },
    # ═══════════════════════════════════════════════════════
    #  OpenAI Direct API (api key auth)
    #  reasoning_effort: none | low | medium | high | xhigh
    # ═══════════════════════════════════════════════════════
    "gpt-5.4-direct": {
        "provider": "openai",
        "model": "gpt-5.4",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 272000,
    },
    "gpt-5.4-mini-direct": {
        "provider": "openai",
        "model": "gpt-5.4-mini",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 272000,
    },
    "gpt-5.4-nano-direct": {
        "provider": "openai",
        "model": "gpt-5.4-nano",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 272000,
    },
    "gpt-5.3-codex-direct": {
        "provider": "openai",
        "model": "gpt-5.3-codex",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 272000,
    },
    "gpt-5.1-direct": {
        "provider": "openai",
        "model": "gpt-5.1",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 272000,
    },
    "gpt-4o-direct": {
        "provider": "openai",
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 128000,
    },
    "gpt-4o-mini-direct": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "max_context": 128000,
    },
    # ═══════════════════════════════════════════════════════
    #  OpenAI via OpenRouter (uses OR context windows, not Codex)
    # ═══════════════════════════════════════════════════════
    "or-gpt-5.4": {
        "provider": "openai",
        "model": "openai/gpt-5.4",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1050000,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "or-gpt-5.4-mini": {
        "provider": "openai",
        "model": "openai/gpt-5.4-mini",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 400000,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "or-gpt-5.4-nano": {
        "provider": "openai",
        "model": "openai/gpt-5.4-nano",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 400000,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "or-gpt-5.3-codex": {
        "provider": "openai",
        "model": "openai/gpt-5.3-codex",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 400000,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "or-gpt-5.1": {
        "provider": "openai",
        "model": "openai/gpt-5.1",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 400000,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "or-gpt-4o": {
        "provider": "openai",
        "model": "openai/gpt-4o",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 128000,
    },
    "or-gpt-4o-mini": {
        "provider": "openai",
        "model": "openai/gpt-4o-mini",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 128000,
    },
    # ═══════════════════════════════════════════════════════
    #  Anthropic Claude via OpenRouter (OpenAI-compat API)
    # ═══════════════════════════════════════════════════════
    "claude-opus-4.6": {
        "provider": "openai",
        "model": "anthropic/claude-opus-4.6",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1000000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "claude-sonnet-4.6": {
        "provider": "openai",
        "model": "anthropic/claude-sonnet-4.6",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1000000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "claude-sonnet-4.5": {
        "provider": "openai",
        "model": "anthropic/claude-sonnet-4.5",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1000000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "claude-haiku-4.5": {
        "provider": "openai",
        "model": "anthropic/claude-haiku-4.5",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 200000,
    },
    # Legacy aliases kept for backward compat
    "claude-sonnet-4": {
        "provider": "openai",
        "model": "anthropic/claude-sonnet-4",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 200000,
    },
    "claude-opus-4": {
        "provider": "openai",
        "model": "anthropic/claude-opus-4",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 200000,
    },
    # ═══════════════════════════════════════════════════════
    #  Anthropic Claude Direct API (non-OpenAI format)
    #  NOTE: provider="anthropic" requires dedicated client,
    #  not the OpenAI-compat provider. Adaptive thinking is
    #  the recommended mode for 4.6 models:
    #    thinking: {type: "adaptive"}, effort: low|medium|high|max
    #  Fast mode (Opus 4.6 only):
    #    speed="fast", betas=["fast-mode-2026-02-01"]
    # ═══════════════════════════════════════════════════════
    "claude-opus-4.6-direct": {
        "provider": "anthropic",
        "model": "claude-opus-4-6",
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env": "ANTHROPIC_API_KEY",
        "max_context": 1000000,
    },
    "claude-sonnet-4.6-direct": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env": "ANTHROPIC_API_KEY",
        "max_context": 1000000,
    },
    "claude-haiku-4.5-direct": {
        "provider": "anthropic",
        "model": "claude-haiku-4-5",
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env": "ANTHROPIC_API_KEY",
        "max_context": 200000,
    },
    # ═══════════════════════════════════════════════════════
    #  Google Gemini via OpenRouter
    # ═══════════════════════════════════════════════════════
    "gemini-3.1-pro": {
        "provider": "openai",
        "model": "google/gemini-3.1-pro-preview",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1048576,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "gemini-3-flash": {
        "provider": "openai",
        "model": "google/gemini-3-flash-preview",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1048576,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "gemini-3.1-flash-lite": {
        "provider": "openai",
        "model": "google/gemini-3.1-flash-lite-preview",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1048576,
    },
    "nano-banana": {
        "provider": "openai",
        "model": "google/gemini-3.1-flash-image-preview",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 65536,
    },
    # ═══════════════════════════════════════════════════════
    #  Google Gemini Direct API (OpenAI-compat endpoint)
    # ═══════════════════════════════════════════════════════
    "gemini-3.1-pro-direct": {
        "provider": "openai",
        "model": "gemini-3.1-pro-preview",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "max_context": 1048576,
    },
    "gemini-3-flash-direct": {
        "provider": "openai",
        "model": "gemini-3-flash-preview",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "max_context": 1048576,
    },
    "gemini-3.1-flash-lite-direct": {
        "provider": "openai",
        "model": "gemini-3.1-flash-lite-preview",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "max_context": 1048576,
    },
    # ═══════════════════════════════════════════════════════
    #  Gemma 4 (open models, via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "gemma-4-31b": {
        "provider": "openai",
        "model": "google/gemma-4-31b-it",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
    },
    "gemma-4-26b": {
        "provider": "openai",
        "model": "google/gemma-4-26b-a4b-it",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
    },
    # ═══════════════════════════════════════════════════════
    #  Qwen 3.5 / 3.6 series (via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "qwen3.5-plus": {
        "provider": "openai",
        "model": "qwen/qwen3.5-plus-02-15",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1000000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "qwen3.5-flash": {
        "provider": "openai",
        "model": "qwen/qwen3.5-flash-02-23",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1000000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "qwen3.5-397b": {
        "provider": "openai",
        "model": "qwen/qwen3.5-397b-a17b",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "qwen3.5-27b": {
        "provider": "openai",
        "model": "qwen/qwen3.5-27b",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "qwen3-coder": {
        "provider": "openai",
        "model": "qwen/qwen3-coder",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
    },
    "qwen3-coder-plus": {
        "provider": "openai",
        "model": "qwen/qwen3-coder-plus",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1000000,
    },
    # ═══════════════════════════════════════════════════════
    #  Moonshot Kimi K2.5 / K2 (via OpenRouter)
    #  K2.5 has built-in thinking (enabled by default).
    #  Disable via reasoning param if needed.
    # ═══════════════════════════════════════════════════════
    "kimi-k2.5": {
        "provider": "openai",
        "model": "moonshotai/kimi-k2.5",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
    },
    "kimi-k2-thinking": {
        "provider": "openai",
        "model": "moonshotai/kimi-k2-thinking",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 131072,
    },
    # ═══════════════════════════════════════════════════════
    #  MiniMax (via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "minimax-m2.7": {
        "provider": "openai",
        "model": "minimax/minimax-m2.7",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 204800,
    },
    "minimax-m2.5": {
        "provider": "openai",
        "model": "minimax/minimax-m2.5",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 197000,
    },
    # ═══════════════════════════════════════════════════════
    #  Xiaomi MiMo (via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "mimo-v2-pro": {
        "provider": "openai",
        "model": "xiaomi/mimo-v2-pro",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 1048576,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "mimo-v2-flash": {
        "provider": "openai",
        "model": "xiaomi/mimo-v2-flash",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    # ═══════════════════════════════════════════════════════
    #  Xiaomi MiMo Direct API (kt login mimo)
    # ═══════════════════════════════════════════════════════
    "mimo-v2-pro-direct": {
        "provider": "openai",
        "model": "MiMo-V2-Pro",
        "base_url": "https://api.xiaomimimo.com/v1",
        "api_key_env": "MIMO_API_KEY",
        "max_context": 1048576,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "mimo-v2-flash-direct": {
        "provider": "openai",
        "model": "MiMo-V2-Flash",
        "base_url": "https://api.xiaomimimo.com/v1",
        "api_key_env": "MIMO_API_KEY",
        "max_context": 262144,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    # ═══════════════════════════════════════════════════════
    #  GLM (Z.ai, via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "glm-5": {
        "provider": "openai",
        "model": "z-ai/glm-5",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 80000,
    },
    "glm-5-turbo": {
        "provider": "openai",
        "model": "z-ai/glm-5-turbo",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 202752,
    },
    # ═══════════════════════════════════════════════════════
    #  xAI Grok series (via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "grok-4": {
        "provider": "openai",
        "model": "x-ai/grok-4",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 256000,
        # Reasoning is mandatory and not configurable
    },
    "grok-4.20": {
        "provider": "openai",
        "model": "x-ai/grok-4.20",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 272000,  # 2M model, use 272K budget
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "grok-4.20-multi": {
        "provider": "openai",
        "model": "x-ai/grok-4.20-multi-agent",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 272000,
        "extra_body": {"reasoning": {"effort": "medium"}},
    },
    "grok-4-fast": {
        "provider": "openai",
        "model": "x-ai/grok-4-fast",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 272000,  # 2M model, use 272K budget
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "grok-4.1-fast": {
        "provider": "openai",
        "model": "x-ai/grok-4.1-fast",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 272000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "grok-code-fast": {
        "provider": "openai",
        "model": "x-ai/grok-code-fast-1",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 256000,
        "extra_body": {"reasoning": {"enabled": True}},
    },
    "grok-3": {
        "provider": "openai",
        "model": "x-ai/grok-3",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 131072,
    },
    "grok-3-mini": {
        "provider": "openai",
        "model": "x-ai/grok-3-mini",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 131072,
        "extra_body": {"reasoning": {"effort": "high"}},
    },
    # ═══════════════════════════════════════════════════════
    #  Mistral series (via OpenRouter)
    # ═══════════════════════════════════════════════════════
    "mistral-large": {
        "provider": "openai",
        "model": "mistralai/mistral-large-2512",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
    },
    "mistral-medium": {
        "provider": "openai",
        "model": "mistralai/mistral-medium-3.1",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 131072,
    },
    "mistral-small": {
        "provider": "openai",
        "model": "mistralai/mistral-small-2603",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
        "extra_body": {"reasoning": {"effort": "high"}},
    },
    "codestral": {
        "provider": "openai",
        "model": "mistralai/codestral-2508",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 256000,
    },
    "devstral": {
        "provider": "openai",
        "model": "mistralai/devstral-2512",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 262144,
    },
    "pixtral-large": {
        "provider": "openai",
        "model": "mistralai/pixtral-large-2411",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "max_context": 131072,
    },
}

# Aliases: short names -> canonical preset names
ALIASES: dict[str, str] = {
    # OpenAI
    "gpt5": "gpt-5.4",
    "gpt54": "gpt-5.4",
    "gpt53": "gpt-5.3-codex",
    "gpt4o": "gpt-4o",
    # Gemini
    "gemini": "gemini-3.1-pro",
    "gemini-pro": "gemini-3.1-pro",
    "gemini-flash": "gemini-3-flash",
    "gemini-lite": "gemini-3.1-flash-lite",
    # Claude (via OpenRouter)
    "claude": "claude-sonnet-4.6",
    "claude-sonnet": "claude-sonnet-4.6",
    "claude-opus": "claude-opus-4.6",
    "claude-haiku": "claude-haiku-4.5",
    "sonnet": "claude-sonnet-4.6",
    "opus": "claude-opus-4.6",
    "haiku": "claude-haiku-4.5",
    # Gemma
    "gemma": "gemma-4-31b",
    "gemma-4": "gemma-4-31b",
    # Qwen
    "qwen": "qwen3.5-plus",
    "qwen-coder": "qwen3-coder",
    # Kimi
    "kimi": "kimi-k2.5",
    # MiniMax
    "minimax": "minimax-m2.7",
    # MiMo
    "mimo": "mimo-v2-pro",
    # GLM
    "glm": "glm-5-turbo",
    # Grok
    "grok": "grok-4",
    "grok-fast": "grok-4-fast",
    "grok-code": "grok-code-fast",
    # Mistral
    "mistral": "mistral-large",
}
