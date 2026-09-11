from __future__ import annotations

import os
from dataclasses import dataclass


def _integer(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _floating(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    llm_base_url: str = "http://127.0.0.1:8000/v1"
    llm_model: str = "qwen3.5-9b"
    llm_provider: str = "vllm"
    llm_api_key: str = "EMPTY"
    llm_temperature: float = 0.0
    llm_timeout_seconds: float = 900.0
    llm_max_tokens: int = 2048
    llm_structured_method: str = "prompt_json"
    groq_api_key: str = ""
    law_candidates: int = 18
    max_law_evidence: int = 8

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        return cls(
            llm_base_url=os.getenv("LLM_BASE_URL", defaults.llm_base_url),
            llm_model=os.getenv("LLM_MODEL", defaults.llm_model),
            llm_provider=os.getenv("LLM_PROVIDER", defaults.llm_provider),
            llm_api_key=os.getenv("LLM_API_KEY", defaults.llm_api_key),
            llm_temperature=_floating("LLM_TEMPERATURE", defaults.llm_temperature),
            llm_timeout_seconds=_floating(
                "LLM_TIMEOUT_SECONDS", defaults.llm_timeout_seconds
            ),
            llm_max_tokens=_integer("LLM_MAX_TOKENS", defaults.llm_max_tokens),
            llm_structured_method=os.getenv(
                "LLM_STRUCTURED_METHOD", defaults.llm_structured_method
            ),
            groq_api_key=os.getenv("GROQ_KEY", os.getenv("GROQ_API_KEY", "")),
            law_candidates=_integer("ALQAC_LAW_CANDIDATES", defaults.law_candidates),
            max_law_evidence=_integer(
                "ALQAC_MAX_LAW_EVIDENCE", defaults.max_law_evidence
            ),
        )

    def validate_for_run(self, *, require_api_key: bool = False) -> None:
        del require_api_key
        if self.llm_structured_method not in {"json_schema", "prompt_json"}:
            raise ValueError(
                "LLM_STRUCTURED_METHOD phải là json_schema hoặc prompt_json"
            )
        if self.llm_provider not in {"vllm", "ollama", "groq"}:
            raise ValueError("LLM_PROVIDER phải là vllm, ollama hoặc groq")
        if self.law_candidates < 1:
            raise ValueError("ALQAC_LAW_CANDIDATES phải >= 1")
        if self.max_law_evidence < 1:
            raise ValueError("ALQAC_MAX_LAW_EVIDENCE phải >= 1")
