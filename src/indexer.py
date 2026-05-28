from typing import List

import pandas as pd
from rich.console import Console
from rich.progress import track

from src.database import DatabaseManager
from src.embeddings import KimiEmbeddingsClient

console = Console()

BATCH_SIZE = 100


def index_csv_file(csv_path: str, db: DatabaseManager, client: KimiEmbeddingsClient):
    """Carga un CSV, genera embeddings y los guarda en PostgreSQL."""
    df = pd.read_csv(csv_path)

    required_cols = {"content"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"El CSV debe contener la columna 'content'. Columnas encontradas: {list(df.columns)}")

    total = len(df)
    console.print(f"[blue]📄 Cargando {total} documentos desde {csv_path}...[/blue]")

    # Procesar en batches
    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch_df = df.iloc[start:end]

        texts = batch_df["content"].astype(str).tolist()

        console.print(f"[dim]Generando embeddings para batch {start+1}-{end}...[/dim]")
        embeddings = client.get_embeddings_batch(texts)

        docs_to_insert = []
        for idx, row in batch_df.iterrows():
            meta = {}
            if "category" in row:
                meta["category"] = row["category"]
            # Agregar cualquier otra columna como metadata
            for col in df.columns:
                if col not in ("content",):
                    meta[col] = row[col]

            docs_to_insert.append({
                "content": row["content"],
                "embedding": embeddings[idx - start],
                "metadata": meta if meta else None,
            })

        db.add_documents_bulk(docs_to_insert)
        console.print(f"[green]✅ Indexados {end}/{total} documentos[/green]")

    console.print(f"[bold green]🎉 Indexación completa: {total} documentos en total[/bold green]")
