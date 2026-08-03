import pandas as pd
from rich.console import Console

from src.database import DatabaseManager
from src.embeddings import BaseEmbeddingsClient

console = Console()

BATCH_SIZE = 100

# Nombre de la subcarpeta donde se mueven los CSV ya indexados
PROCESSED_DIR_NAME = "procesados"


def move_to_processed(csv_path: str) -> Path:
    """Mueve un CSV ya indexado a la subcarpeta 'procesados' junto al archivo original.

    Si ya existe un archivo con el mismo nombre, se agrega un timestamp
    para no sobrescribir ni perder archivos.
    """
    src = Path(csv_path)

    # Si el archivo ya está dentro de 'procesados', no se mueve de nuevo
    if PROCESSED_DIR_NAME in src.parent.parts:
        console.print(f"[dim]El archivo ya está en '{PROCESSED_DIR_NAME}', no se mueve.[/dim]")
        return src

    processed_dir = src.parent / PROCESSED_DIR_NAME
    processed_dir.mkdir(parents=True, exist_ok=True)

    dest = processed_dir / src.name
    if dest.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = processed_dir / f"{src.stem}_{timestamp}{src.suffix}"

    shutil.move(str(src), str(dest))
    console.print(f"[blue]📦 Archivo movido a {dest}[/blue]")
    return dest


def index_csv_file(csv_path: str, db: DatabaseManager, client: BaseEmbeddingsClient):
    """Carga un CSV, genera embeddings y los guarda en PostgreSQL."""
    df = pd.read_csv(csv_path)

    required_cols = {"content"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"El CSV debe contener la columna 'content'. Columnas encontradas: {list(df.columns)}"
        )

    total = len(df)
    console.print(f"[blue]📄 Cargando {total} documentos desde {csv_path}...[/blue]")

    # Procesar en batches
    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch_df = df.iloc[start:end]

        texts = batch_df["content"].astype(str).tolist()

        console.print(
            f"[dim]Generando embeddings para batch {start + 1}-{end}...[/dim]"
        )
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

            docs_to_insert.append(
                {
                    "content": row["content"],
                    "embedding": embeddings[idx - start],
                    "metadata": meta if meta else None,
                }
            )

        db.add_documents_bulk(docs_to_insert)
        console.print(f"[green]✅ Indexados {end}/{total} documentos[/green]")

    console.print(
        f"[bold green]🎉 Indexación completa: {total} documentos en total[/bold green]"
    )
