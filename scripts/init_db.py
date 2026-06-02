#!/usr/bin/env python3
"""Inicializa la base de datos: crea extensión pgvector, tablas e índices."""

import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from src.database import DatabaseManager

console = Console()


def main():
    console.print("[bold blue]🔧 Inicializando base de datos...[/bold blue]")

    db = DatabaseManager()

    console.print("[dim]1/3 Creando extensión pgvector...[/dim]")
    db.init_extensions()

    console.print("[dim]2/3 Creando tablas...[/dim]")
    db.create_tables()

    console.print("[dim]3/3 Creando índices...[/dim]")
    db.create_index()

    console.print("[bold green]✅ Base de datos lista para usar[/bold green]")


if __name__ == "__main__":
    main()
