import time
from typing import List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings


class KimiEmbeddingsClient:
    """Cliente para generar embeddings usando la API de Kimi (Moonshot AI)."""

    def __init__(self):
        if not settings.kimi_api_key:
            raise ValueError(
                "KIMI_API_KEY no está configurada. "
                "Copia .env.example a .env y agrega tu API key de Moonshot AI."
            )
        self.api_key = settings.kimi_api_key
        self.base_url = settings.kimi_base_url.rstrip("/")
        self.model = settings.embedding_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embedding(self, text: str) -> List[float]:
        """Genera el embedding de un solo texto."""
        return self.get_embeddings_batch([text])[0]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos (batch).

        La API de embeddings de OpenAI-compatible suele aceptar batches.
        Kimi/OpenAI embeddings endpoint recibe `input` como lista de strings.
        """
        url = f"{self.base_url}/embeddings"
        payload = {
            "model": self.model,
            "input": texts,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

        # Ordenar por índice para mantener el orden de entrada
        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in embeddings]
