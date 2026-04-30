"""Lightweight wrapper around a local Hugging Face causal language model."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "/data/LLM/qwen2_5/Qwen2.5-14B-Instruct")


@dataclass
class GenerationConfig:
    max_new_tokens: int = 2048
    temperature: float = 0.6
    top_p: float = 0.9
    do_sample: bool = True


class LocalLLMClient:
    """Lazy-loads a local chat model and exposes a simple generate method."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        generation_config: Optional[GenerationConfig] = None,
    ) -> None:
        self.model_id = model_id
        self.generation_config = generation_config or GenerationConfig()
        self._tokenizer = None
        self._model = None

    @property
    def tokenizer(self):
        self._ensure_loaded()
        return self._tokenizer

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def generate(self, prompt: str) -> str:
        self._ensure_loaded()
        messages = [{"role": "user", "content": prompt}]
        input_ids = self._tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self._model.device)

        outputs = self._model.generate(
            input_ids,
            max_new_tokens=self.generation_config.max_new_tokens,
            do_sample=self.generation_config.do_sample,
            temperature=self.generation_config.temperature,
            top_p=self.generation_config.top_p,
        )
        response = outputs[0][input_ids.shape[-1] :]
        return self._tokenizer.decode(response, skip_special_tokens=True).strip()

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Missing model dependencies. Install them with: "
                "pip install -r requirements.txt"
            ) from exc

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype="auto",
            device_map="auto",
        )
