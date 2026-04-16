"""
MarketOS — LLM Provider Abstraction
Switch providers by changing ONE line in .env:

    LLM_PROVIDER=gemini       →  Google Gemini 2.0 Flash  (default, dev)
    LLM_PROVIDER=anthropic    →  Anthropic Claude Sonnet 4
    LLM_PROVIDER=openrouter   →  OpenRouter (production)

All agents call get_llm() — no agent touches API keys directly.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0):
    """
    Return a LangChain chat model for the configured provider.

    temperature=0   → deterministic (supervisor, compliance)
    temperature=0.7 → creative      (copy agent)
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set in your .env file. "
                "Add it or switch LLM_PROVIDER=gemini."
            )
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=api_key,
            temperature=temperature,
            max_tokens=4096,
        )

    elif provider == "openrouter":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENROUTER_API_KEY is not set in your .env file. "
                "Add it or switch LLM_PROVIDER=gemini."
            )
        model = os.getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=4096,
            default_headers={
                "HTTP-Referer": "https://marketos.ai",
                "X-Title": "MarketOS",
            },
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set in your .env file. "
                "Add it or switch LLM_PROVIDER=anthropic."
            )
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=4096,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider}'. "
            "Valid values: gemini | anthropic | openrouter"
        )

