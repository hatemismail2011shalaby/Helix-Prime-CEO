from abc import ABC, abstractmethod
import os

class ModelBackend(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        ...

class OllamaBackend(ModelBackend):
    def __init__(self, model: str = "qwen3:8b") -> None:
        self.model = model

    def chat(self, prompt: str) -> str:
        import ollama
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']

class CloudBackend(ModelBackend):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", 
                 base_url: str = "https://api.groq.com/openai/v1") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def chat(self, prompt: str) -> str:
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

def get_model_backend() -> ModelBackend:
    backend_type = os.environ.get("HELIX_MODEL_BACKEND", "ollama")
    
    if backend_type == "cloud":
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise KeyError("GROQ_API_KEY environment variable is required for cloud backend")
        return CloudBackend(api_key=api_key)
    else:
        return OllamaBackend()