import os
import sys
from abc import ABC, abstractmethod

class ModelBackendUnavailableError(RuntimeError):
    """Model backend unavailable."""
    pass

class ModelBackend(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        ...

class EchoBackend(ModelBackend):
    def chat(self, prompt: str) -> str:
        clean_prompt = prompt.strip() or "empty prompt"
        return f"Local Helix response: {clean_prompt}"

class OllamaBackend(ModelBackend):
    def __init__(self, model: str = "qwen3:14b") -> None:
        import os
        self.model = os.environ.get("OLLAMA_MODEL", model)

    def chat(self, prompt: str) -> str:
        try:
            import ollama
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception as exc:
            raise ModelBackendUnavailableError(
                f"Ollama backend unavailable (model='{self.model}'): {exc}"
            ) from exc

class CloudBackend(ModelBackend):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", 
                 base_url: str = "https://api.groq.com/openai/v1") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def chat(self, prompt: str) -> str:
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as exc:
            raise ModelBackendUnavailableError("Cloud backend unavailable") from exc

def get_model_backend() -> ModelBackend:
    backend_type = os.environ.get("HELIX_MODEL_BACKEND", "ollama").lower().strip()
    if backend_type == "cloud":
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise KeyError("GROQ_API_KEY environment variable is required for cloud backend")
        model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        return CloudBackend(api_key=api_key, model=model, base_url=base_url)
    elif backend_type in ("ollama", "ollama_model", "ollama_backend"):
        try:
            return OllamaBackend()
        except Exception as exc:
            print("[helix] Warning: Ollama backend unavailable. Falling back to local Echo backend. To enable a real LLM, set HELIX_MODEL_BACKEND=ollama and ensure the ollama package/service is available.", file=sys.stderr)
            return EchoBackend()
    elif backend_type in ("echo", "local", "test"):
        return EchoBackend()
    else:
        raise ValueError(f"Unsupported HELIX_MODEL_BACKEND: {backend_type}")

