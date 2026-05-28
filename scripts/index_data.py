#!/usr/bin/env python3
"""Carga datos desde un CSV y los indexa en PostgreSQL con embeddings."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from src.database import DatabaseManager
from src.embeddings import get_embeddings_client
from src.indexer import index_csv_file

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Indexa documentos desde un CSV")
    parser.add_argument(
        "--file",
        type=str,
        default="data/sample_documents.csv",
        help="Ruta al archivo CSV con los documentos (default: data/sample_documents.csv)",
    )
    args = parser.parse_args()

    csv_path = Path(args.file)
    if not csv_path.exists():
        console.print(f"[bold red]❌ Archivo no encontrado: {csv_path}[/bold red]")
        sys.exit(1)

    db = DatabaseManager()
    client = get_embeddings_client()

    index_csv_file(str(csv_path), db, client)


if __name__ == "__main__":
    main()
