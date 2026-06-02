#!/usr/bin/env python3
"""Interfaz CLI interactiva para búsqueda semántica usando Rich."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from src.database import DatabaseManager
from src.embeddings import BaseEmbeddingsClient, get_embeddings_client
from src.config import settings

console = Console()


def display_results(results: list, query: str, threshold: float = 0.0):
    """Muestra los resultados de búsqueda en una tabla formateada con Rich."""
    if not results:
        if threshold > 0:
            console.print(
                f"[yellow]⚠️  Ningún resultado superó el umbral de similitud "
                f"({threshold:.2f}). Prueba con otra consulta.[/yellow]"
            )
        else:
            console.print("[yellow]⚠️  No se encontraron resultados.[/yellow]")
        return

    table = Table(
        title=f'Resultados para: "{query}"',
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Score", style="cyan", width=8, justify="center")
    table.add_column("Categoría", style="green", width=15)
    table.add_column("Contenido", style="white", overflow="fold")

    for idx, row in enumerate(results, start=1):
        score = row["similarity_score"]
        meta = row["metadata"] or {}
        category = meta.get("category", "—")
        content = row["content"]

        # Truncar contenido muy largo
        if len(content) > 200:
            content = content[:197] + "..."

        score_str = f"{score:.3f}"
        table.add_row(str(idx), score_str, category, content)

    console.print(table)


def run_search(db: DatabaseManager, client: BaseEmbeddingsClient, query: str, top_k: int = 5, threshold: float = 0.0):
    """Ejecuta una búsqueda semántica y muestra resultados."""
    with console.status("[bold green]Generando embedding de la consulta...[/bold green]"):
        query_embedding = client.get_embedding(query)

    with console.status("[bold blue]Buscando en PostgreSQL...[/bold blue]"):
        results = db.search_similar(query_embedding, top_k=top_k, threshold=threshold)

    display_results(results, query, threshold=threshold)
    return results


def main():
    console.print(
        Panel.fit(
            Text.from_markup(
                f"[bold cyan]🔍 Búsqueda Semántica POC[/bold cyan]\n"
                f"Proveedor: [yellow]{settings.embedding_provider}[/yellow] | "
                f"Modelo: [yellow]{settings.embedding_model}[/yellow]\n"
                f"Base de datos: [yellow]PostgreSQL + pgvector[/yellow] | "
                f"Umbral: [yellow]{settings.search_threshold}[/yellow] | "
                f"Top-K: [yellow]{settings.search_top_k}[/yellow]\n\n"
                f"Escribe tu consulta y presiona [bold]Enter[/bold].\n"
                f"Escribe [bold red]exit[/bold red] o [bold red]quit[/bold red] para salir."
            ),
            border_style="cyan",
        )
    )

    db = DatabaseManager()
    client = get_embeddings_client()

    # Verificar conexión y contar documentos
    try:
        count = db.count_documents()
        console.print(f"[dim]📦 {count} documentos indexados en la base de datos[/dim]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Error conectando a la base de datos: {e}[/bold red]")
        sys.exit(1)

    while True:
        try:
            query = console.input("[bold green]➜ Consulta:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Saliendo...[/dim]")
            break

        if not query:
            continue

        if query.lower() in ("exit", "quit", "salir"):
            console.print("[dim]👋 Hasta luego![/dim]")
            break

        try:
            run_search(db, client, query, top_k=settings.search_top_k, threshold=settings.search_threshold)
        except Exception as e:
            console.print(f"[bold red]❌ Error durante la búsqueda: {e}[/bold red]")

        console.print()  # Línea en blanco entre consultas


if __name__ == "__main__":
    main()
