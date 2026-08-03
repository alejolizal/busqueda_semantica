#!/usr/bin/env python3
"""Carga datos desde CSVs y los indexa en PostgreSQL con embeddings.

Sin argumentos, indexa todos los CSV pendientes en la carpeta data/
(los ya indexados se mueven automáticamente a data/procesados/).
"""

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
    parser = argparse.ArgumentParser(description="Indexa documentos desde CSVs")
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Ruta a un archivo CSV específico (default: todos los CSV pendientes en data/)",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="data",
        help="Carpeta donde buscar CSVs pendientes (default: data)",
    )
    args = parser.parse_args()

    if args.file:
        csv_path = Path(args.file)
        if not csv_path.exists():
            console.print(f"[bold red]❌ Archivo no encontrado: {csv_path}[/bold red]")
            sys.exit(1)
        csv_files = [csv_path]
    else:
        data_dir = Path(args.dir)
        if not data_dir.is_dir():
            console.print(f"[bold red]❌ Carpeta no encontrada: {data_dir}[/bold red]")
            sys.exit(1)
        # glob no recursivo: excluye automáticamente data/procesados/
        csv_files = sorted(data_dir.glob("*.csv"))
        if not csv_files:
            console.print(f"[yellow]⚠️  No hay CSVs pendientes en {data_dir}/[/yellow]")
            return

    console.print(f"[blue]📂 {len(csv_files)} archivo(s) por indexar:[/blue]")
    for f in csv_files:
        console.print(f"[dim]   - {f}[/dim]")

    db = DatabaseManager()
    client = get_embeddings_client()

    for csv_path in csv_files:
        try:
            index_csv_file(str(csv_path), db, client)
        except Exception as e:
            console.print(f"[bold red]❌ Error indexando {csv_path}: {e}[/bold red]")
            console.print("[yellow]Continuando con el siguiente archivo...[/yellow]")


if __name__ == "__main__":
    main()
