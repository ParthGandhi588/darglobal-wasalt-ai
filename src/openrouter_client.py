import os
import json
from typing import List, Dict, Any, Generator, Optional
from openai import OpenAI

DEFAULT_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        self._init_client()

    def _init_client(self):
        if self.api_key:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "https://darglobal.co.uk",
                    "X-Title": "DarGlobal & Wasalt AI Assistant",
                }
            )
        else:
            self.client = None

    def update_key(self, api_key: str):
        self.api_key = api_key
        self._init_client()

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        stream: bool = True
    ):
        """
        Generate chat response with automated fallback through free models.
        """
        if not self.client:
            yield "⚠️ **OpenRouter API Key not set.** Please enter your OpenRouter API Key in the sidebar or configure the `OPENROUTER_API_KEY` environment variable."
            return

        candidate_models = [model] if model else DEFAULT_FREE_MODELS
        # ensure all defaults are appended as fallbacks
        for m in DEFAULT_FREE_MODELS:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for current_model in candidate_models:
            try:
                if stream:
                    response = self.client.chat.completions.create(
                        model=current_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True
                    )
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                    return
                else:
                    response = self.client.chat.completions.create(
                        model=current_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False
                    )
                    yield response.choices[0].message.content
                    return
            except Exception as e:
                last_error = e
                # Fallback to next model
                continue

        # If all free models failed
        yield f"⚠️ **Error communicating with OpenRouter free models:** {str(last_error)}. Please try again in a few moments or verify your API key."
