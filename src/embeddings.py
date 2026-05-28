from abc import ABC, abstractmethod
from typing import List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings


class BaseEmbeddingsClient(ABC):
    """Clase base abstracta para clientes de embeddings."""

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Genera el embedding de un solo texto."""
        ...

    @abstractmethod
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos (batch)."""
        ...


class JinaEmbeddingsClient(BaseEmbeddingsClient):
    """Cliente para generar embeddings usando la API de Jina AI.

    Jina AI ofrece una API gratuita (hasta 1M tokens/día) compatible con OpenAI.
    Docs: https://jina.ai/embeddings
    """

    def __init__(self):
        self.api_key = settings.embedding_api_key
        self.base_url = settings.embedding_base_url.rstrip("/")
        self.model = settings.embedding_model
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embedding(self, text: str) -> List[float]:
        return self.get_embeddings_batch([text])[0]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        url = f"{self.base_url}/embeddings"
        payload = {
            "model": self.model,
            "input": texts,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=self.headers, json=payload)
            if response.status_code == 401:
                raise ValueError(
                    "Error 401 de Jina AI: API key no válida o no proporcionada. "
                    "Obtén una key gratuita en https://jina.ai/embeddings "
                    "o usa EMBEDDING_PROVIDER=local para modo offline."
                )
            response.raise_for_status()
            data = response.json()

        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in embeddings]


class LocalEmbeddingsClient(BaseEmbeddingsClient):
    """Cliente local usando sentence-transformers.

    No requiere API key ni conexión a Internet después de la primera descarga.
    Ideal para desarrollo local y POCs.
    """

    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers no está instalado. "
                "Ejecuta: pip install sentence-transformers"
            ) from exc

        self.model = SentenceTransformer(settings.embedding_model)
        # Validar dimensión configurada vs dimensión real del modelo
        actual_dim = self.model.get_embedding_dimension()
        if actual_dim != settings.embedding_dimension:
            raise ValueError(
                f"EMBEDDING_DIMENSION ({settings.embedding_dimension}) no coincide "
                f"con la dimensión del modelo '{settings.embedding_model}' ({actual_dim}). "
                f"Actualiza EMBEDDING_DIMENSION={actual_dim} en tu .env"
            )

    def get_embedding(self, text: str) -> List[float]:
        return self.get_embeddings_batch([text])[0]

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        return embeddings.tolist()


def get_embeddings_client() -> BaseEmbeddingsClient:
    """Factory que devuelve el cliente de embeddings según la configuración."""
    provider = settings.embedding_provider.lower().strip()

    if provider == "jina":
        return JinaEmbeddingsClient()
    elif provider == "local":
        return LocalEmbeddingsClient()
    else:
        raise ValueError(
            f"Proveedor de embeddings desconocido: '{provider}'. "
            f"Usa 'jina' o 'local'."
        )
