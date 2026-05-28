from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración del proyecto cargada desde variables de entorno."""

    # Proveedor de embeddings: "jina" | "local"
    embedding_provider: str = Field("jina", alias="EMBEDDING_PROVIDER")

    # Configuración de API (usada por Jina y otros proveedores API)
    embedding_api_key: str = Field("", alias="EMBEDDING_API_KEY")
    embedding_base_url: str = Field("https://api.jina.ai/v1", alias="EMBEDDING_BASE_URL")

    # Modelo y dimensión (debe ser coherente con el proveedor)
    embedding_model: str = Field("jina-embeddings-v3", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(1024, alias="EMBEDDING_DIMENSION")

    database_url: str = Field(
        "postgresql+psycopg2://semantic_user:semantic_pass@localhost:5432/semantic_search",
        alias="DATABASE_URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
