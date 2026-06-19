# AGENTS.md — Guía para agentes de código

> Este archivo documenta la estructura, convenciones y comandos del proyecto **Búsqueda Semántica POC**. Está escrito en español porque todo el código, comentarios y documentación del proyecto usan español como idioma principal.

---

## 1. Visión general del proyecto

Este es un **Proof of Concept (POC)** de búsqueda semántica escrito en Python. Permite:

- Convertir textos en vectores numéricos (embeddings) usando **Jina AI** vía API o un modelo **local** con `sentence-transformers`.
- Almacenar documentos y sus embeddings en **PostgreSQL + pgvector**.
- Buscar documentos por similitud semántica a través de una **CLI interactiva** construida con `Rich`.
- Cargar datasets desde archivos **CSV** y indexarlos por batches.

El flujo principal es:

```
CSV → indexer → embeddings → PostgreSQL/pgvector ← search CLI ← consulta del usuario
```

No es una aplicación web ni un servicio: es una herramienta de terminal con scripts independientes.

---

## 2. Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Lenguaje | Python 3.10+ |
| Base de datos | PostgreSQL 15 con extensión `pgvector` |
| ORM / acceso a datos | SQLAlchemy 2.x + `pgvector` (Python) + `psycopg2-binary` |
| Embeddings (API) | Jina AI (`jina-embeddings-v3`, 1024 dims) vía `httpx` |
| Embeddings (local) | `sentence-transformers` (modelos MiniLM, 384 dims) |
| Configuración | `pydantic-settings` cargando variables desde `.env` |
| CLI / UI terminal | `Rich` (tablas, paneles, spinners, progreso) |
| Procesamiento de CSV | `pandas` |
| Reintentos HTTP | `tenacity` |
| Contenedores | Docker Compose (`pgvector/pgvector:pg15`) |

No se usa `pyproject.toml`, `setup.py`, `Makefile`, `pytest.ini` ni frameworks de testing. Las dependencias están en `requirements.txt`.

---

## 3. Estructura del proyecto

```
busqueda_semantica/
├── .env                          # Variables de entorno (no versionado)
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore
├── README.md                     # Documentación de usuario detallada
├── requirements.txt              # Dependencias Python
├── docker-compose.yml            # Servicio PostgreSQL + pgvector
│
├── data/
│   └── sample_documents.csv      # Dataset de ejemplo (52 documentos, 4 categorías)
│
├── src/                          # Módulos reutilizables del proyecto
│   ├── __init__.py               # Vacío
│   ├── config.py                 # Settings con pydantic-settings
│   ├── database.py               # SQLAlchemy ORM, modelo Document, DatabaseManager
│   ├── embeddings.py             # Clientes Jina / Local + factory
│   └── indexer.py                # Lógica de indexación de CSV por batches
│
└── scripts/                      # Scripts ejecutables de alto nivel
    ├── setup.sh                  # Setup automatizado: venv, deps, Docker, init, index
    ├── init_db.py                # Crea extensión pgvector, tablas e índices
    ├── index_data.py             # Carga CSV y genera embeddings
    ├── search.py                 # CLI interactiva de búsqueda
    └── db_schema.sql             # Schema SQL puro (alternativa a init_db.py)
```

### Convención de imports

Todos los scripts en `scripts/` añaden la raíz del proyecto a `sys.path` para poder importar `src.*`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

Esto permite ejecutar los scripts directamente sin instalar el paquete.

---

## 4. Configuración y variables de entorno

La configuración se carga desde `.env` mediante `src.config.Settings` (pydantic-settings).

| Variable | Descripción | Default |
|----------|-------------|---------|
| `EMBEDDING_PROVIDER` | Proveedor: `jina` o `local` | `jina` |
| `EMBEDDING_API_KEY` | API key de Jina AI | (vacío) |
| `EMBEDDING_BASE_URL` | URL base de la API de embeddings | `https://api.jina.ai/v1` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `jina-embeddings-v3` |
| `EMBEDDING_DIMENSION` | Dimensión del vector generado | `1024` |
| `SEARCH_THRESHOLD` | Score mínimo de similitud (0.0 = sin filtro) | `0.35` |
| `SEARCH_TOP_K` | Máximo de resultados por consulta | `5` |
| `DATABASE_URL` | URL de conexión SQLAlchemy a PostgreSQL | `postgresql+psycopg2://semantic_user:semantic_pass@localhost:5432/semantic_search` |

### Reglas críticas de configuración

1. **La dimensión del embedding debe coincidir con el modelo.**
   - Jina `jina-embeddings-v3` → `1024`.
   - Sentence-transformers MiniLM → `384`.
   - El proveedor local valida la dimensión al inicializarse y lanza `ValueError` si no coincide.

2. **El schema de PostgreSQL (`VECTOR(<dim>)`) también debe coincidir.**
   - Si cambias de proveedor/modelo, debes recrear la base de datos:
     ```bash
     docker compose down -v
     docker compose up -d
     python scripts/init_db.py
     ```

3. **No versionar `.env`.** El repositorio ignora `.env` y provee `.env.example` como plantilla.

---

## 5. Comandos de build, setup y ejecución

### Setup completo (recomendado)

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Este script:
1. Verifica Docker, Docker Compose y Python 3.
2. Crea `.env` desde `.env.example` si no existe.
3. Crea y activa un entorno virtual en `venv/`.
4. Instala dependencias desde `requirements.txt`.
5. Levanta PostgreSQL con Docker Compose.
6. Ejecuta `scripts/init_db.py`.
7. Indexa `data/sample_documents.csv`.

### Setup manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env con el proveedor/modelo/dimensión deseados

docker compose up -d
python scripts/init_db.py
python scripts/index_data.py --file data/sample_documents.csv
python scripts/search.py
```

### Comandos principales

| Acción | Comando |
|--------|---------|
| Levantar base de datos | `docker compose up -d` |
| Inicializar schema | `python scripts/init_db.py` |
| Indexar CSV | `python scripts/index_data.py --file data/sample_documents.csv` |
| Buscar interactivamente | `python scripts/search.py` |
| Detener base de datos | `docker compose down` |
| Detener y borrar datos | `docker compose down -v` |

> Nota: si no se activa el entorno virtual, usar `./venv/bin/python scripts/<script>.py`.

---

## 6. Arquitectura del código

### `src/config.py`

Define `Settings` con pydantic-settings. Todas las variables usan `alias` en mayúsculas para mapear las variables de entorno. La instancia global `settings` se importa donde se necesite.

### `src/database.py`

- Modelo `Document` con columnas: `id`, `content`, `metadata` (JSONB) y `embedding` (`Vector(dimension)`).
- `DatabaseManager` encapsula:
  - `init_extensions()`: crea extensión `pgvector`.
  - `create_tables()`: crea tablas vía SQLAlchemy.
  - `create_index()`: crea índice `ivfflat` con `vector_cosine_ops`.
  - `add_document()` / `add_documents_bulk()`: inserciones.
  - `search_similar()`: búsqueda por similitud coseno con umbral opcional.
  - `count_documents()`: conteo de documentos.

La similitud se calcula como `1 - (embedding <=> :embedding)`, donde `<=>` es la distancia coseno de pgvector. El resultado es un score entre 0 y 1.

### `src/embeddings.py`

- `BaseEmbeddingsClient`: clase abstracta con `get_embedding()` y `get_embeddings_batch()`.
- `JinaEmbeddingsClient`: llama a `POST {base_url}/embeddings` con `httpx`. Usa `tenacity` para reintentos (3 intentos, backoff exponencial).
- `LocalEmbeddingsClient`: carga el modelo con `sentence-transformers` y genera embeddings localmente.
- `get_embeddings_client()`: factory que devuelve el cliente según `EMBEDDING_PROVIDER`.

### `src/indexer.py`

Lee el CSV con `pandas`, valida que exista la columna `content`, genera embeddings por batches de 100, construye metadatos a partir de las demás columnas (por ejemplo `category`) e inserta en bloque con `add_documents_bulk()`.

### `scripts/search.py`

CLI interactiva con `Rich`. Lee consultas del usuario, genera embedding de la consulta, ejecuta `search_similar()` y muestra resultados en tabla. Comandos de salida: `exit`, `quit`, `salir`.

---

## 7. Estilo de código y convenciones

- **Idioma**: español para docstrings, comentarios, mensajes de usuario y nombres de columnas mostradas (ej. `Categoría`, `Contenido`). El código técnico (nombres de variables, clases, funciones) usa inglés.
- **Comillas**: preferir comillas dobles para strings.
- **Imports**: agrupar estándar, terceros y locales. Los scripts añaden `sys.path` explícito.
- **Mensajes de consola**: usar `rich.console.Console` con emojis y colores consistentes.
- **Errores**: lanzar excepciones descriptivas; capturar en la CLI para mostrar mensajes amigables en rojo.
- **No modificar lógica de negocio existente** salvo que sea estrictamente necesario para el requerimiento actual.
- **Configuración centralizada**: cualquier nueva variable de entorno debe agregarse a `src/config.py`, `.env.example` y `README.md`.

---

## 8. Testing

**Actualmente el proyecto no tiene tests automatizados.** No existe directorio `tests/`, ni configuración de `pytest`, ni CI/CD.

Si se agregan tests en el futuro, se recomienda:

- Crear un directorio `tests/` en la raíz.
- Usar `pytest` como runner.
- Mockear las llamadas a Jina AI y a `sentence-transformers`.
- Usar una base de datos PostgreSQL de prueba o mockear `DatabaseManager`.

Para validar cambios manuales:

```bash
# 1. Verificar sintaxis de todos los archivos Python
python -m py_compile scripts/*.py src/*.py

# 2. Ejecutar el setup completo y probar una consulta
./scripts/setup.sh
python scripts/search.py
```

---

## 9. Proceso de despliegue

El despliegue es local y basado en Docker Compose:

1. Construir/levantar la base de datos:
   ```bash
   docker compose up -d
   ```
2. Inicializar el schema:
   ```bash
   python scripts/init_db.py
   ```
3. Indexar datos:
   ```bash
   python scripts/index_data.py --file data/sample_documents.csv
   ```
4. Ejecutar la CLI:
   ```bash
   python scripts/search.py
   ```

No hay despliegue en producción, pipelines CI/CD, ni orquestación Kubernetes. El puerto expuesto de PostgreSQL es `5434` en el host, mapeado al `5432` del contenedor.

### Recrear la base de datos sin Python

Existe `scripts/db_schema.sql` como alternativa pura SQL:

```bash
psql -h localhost -U semantic_user -d semantic_search -f scripts/db_schema.sql
```

Recuerda ajustar `VECTOR(1024)` a `VECTOR(384)` si usas modelos locales.

---

## 10. Consideraciones de seguridad

- **API keys**: `EMBEDDING_API_KEY` se lee desde `.env` y no debe versionarse.
- **SSL deshabilitado en Jina**: `JinaEmbeddingsClient` usa `httpx.Client(..., verify=False)` como workaround temporal para entornos corporativos con inspección SSL (Forcepoint). En producción esto debe cambiarse a `verify=True` y documentarse adecuadamente.
- **Contraseñas en texto plano**: `DATABASE_URL` y las credenciales de PostgreSQL en `docker-compose.yml` son valores de desarrollo/POC. No son secretos gestionados.
- **No hay autenticación ni autorización**: cualquiera con acceso al contenedor PostgreSQL y al entorno virtual puede consultar o modificar datos.
- **No hay validación de entrada más allá de la existencia de la columna `content` en el CSV**.

---

## 11. Notas operativas importantes

- **Cambiar de proveedor requiere recrear datos**: cada modelo genera vectores de dimensión distinta, por lo que no es posible mezclar embeddings de Jina y locales en la misma tabla sin recrearla.
- **Modelos locales descargan pesos**: la primera ejecución de `LocalEmbeddingsClient` descarga el modelo (~400 MB) y puede tardar varios minutos.
- **Índice IVFFlat**: se crea con `lists = 100`, adecuado para datasets pequeños. Para datasets grandes, revisar el tuning de pgvector.
- **Puerto de PostgreSQL**: el contenedor expone `5434` en el host. Si ese puerto está ocupado, modificar `docker-compose.yml` y `DATABASE_URL`.

---

## 12. Checklist para nuevos agentes

Antes de realizar cambios:

1. Verificar que existe `.env` o copiar desde `.env.example`.
2. Asegurar que Docker y el entorno virtual están configurados.
3. Confirmar que `EMBEDDING_DIMENSION` coincide con el modelo configurado.
4. Recordar que los scripts deben ejecutarse desde la raíz o usando `sys.path` ya configurado.
5. No ejecutar `git commit`, `git push`, `git reset`, `git rebase` ni mutaciones de git sin confirmación explícita del usuario.
