from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración del proyecto cargada desde variables de entorno."""

    kimi_api_key: str = Field("", alias="KIMI_API_KEY")
    kimi_base_url: str = Field("https://api.moonshot.cn/v1", alias="KIMI_BASE_URL")

    embedding_model: str = Field("model-embedding-001", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(1536, alias="EMBEDDING_DIMENSION")

    database_url: str = Field(
        "postgresql+psycopg2://semantic_user:semantic_pass@localhost:5432/semantic_search",
        alias="DATABASE_URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
