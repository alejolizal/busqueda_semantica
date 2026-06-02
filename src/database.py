import json
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, Text, JSON, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

from src.config import settings

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    embedding = Column(Vector(settings.embedding_dimension))


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(settings.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_extensions(self):
        """Crea la extensión pgvector si no existe."""
        with self.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()

    def create_tables(self):
        """Crea todas las tablas definidas en los modelos."""
        Base.metadata.create_all(self.engine)

    def create_index(self):
        """Crea un índice IVFFlat para búsqueda por similitud coseno."""
        with self.engine.connect() as conn:
            conn.execute(
                text(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_documents_embedding
                    ON documents USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                    """
                )
            )
            conn.commit()

    def add_document(self, content: str, embedding: List[float], metadata: Optional[dict] = None):
        """Inserta un documento con su embedding."""
        session = self.SessionLocal()
        try:
            doc = Document(content=content, embedding=embedding, metadata_=metadata)
            session.add(doc)
            session.commit()
            return doc.id
        finally:
            session.close()

    def add_documents_bulk(self, documents: List[dict]):
        """Inserta múltiples documentos en una sola transacción."""
        session = self.SessionLocal()
        try:
            docs = [
                Document(
                    content=d["content"],
                    embedding=d["embedding"],
                    metadata_=d.get("metadata"),
                )
                for d in documents
            ]
            session.add_all(docs)
            session.commit()
        finally:
            session.close()

    def search_similar(
        self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.0
    ) -> List[dict]:
        """Busca los documentos más similares usando similitud coseno.

        Retorna lista de dicts con: id, content, metadata, similarity_score.
        Si threshold > 0, filtra resultados con score menor al umbral.
        """
        session = self.SessionLocal()
        try:
            # 1 - cosine_similarity para que el score sea 0-1 (más alto = más similar)
            sql = text(
                """
                SELECT
                    id,
                    content,
                    metadata,
                    1 - (embedding <=> :embedding) AS similarity_score
                FROM documents
                ORDER BY embedding <=> :embedding
                LIMIT :top_k
                """
            )
            result = session.execute(
                sql,
                {
                    "embedding": str(query_embedding),
                    "top_k": top_k,
                },
            )
            rows = []
            for row in result.mappings():
                score = float(row["similarity_score"])
                if threshold > 0 and score < threshold:
                    continue
                rows.append({
                    "id": row["id"],
                    "content": row["content"],
                    "metadata": row["metadata"],
                    "similarity_score": score,
                })
            return rows
        finally:
            session.close()

    def count_documents(self) -> int:
        session = self.SessionLocal()
        try:
            return session.query(Document).count()
        finally:
            session.close()
