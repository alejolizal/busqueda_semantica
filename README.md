# 🔍 Búsqueda Semántica POC

> Proof of Concept de búsqueda semántica con **embeddings de Jina AI o Local**, **PostgreSQL + pgvector** y una **CLI interactiva en Python**.

Este proyecto demuestra cómo construir un sistema de búsqueda por similitud semántica desde cero: convierte textos en vectores numéricos usando el proveedor de embeddings que elijas (API de Jina AI o modelos locales con `sentence-transformers`), los almacena en PostgreSQL con la extensión `pgvector`, y permite consultarlos desde una interfaz de terminal elegante gracias a [Rich](https://github.com/Textualize/rich).

---

## ✨ Características

- 🤖 **Dos proveedores de embeddings** — Elige entre:
  - **Jina AI** (`jina-embeddings-v3`): API gratuita (requiere registro), multilingüe, muy buena calidad.
  - **Local** (`sentence-transformers`): 100% offline, sin API keys, sin límites de uso.
- 🐘 **PostgreSQL + pgvector** — Almacenamiento y búsqueda de vectores con similitud coseno directamente en SQL.
- 🐳 **Docker** — Levanta la base de datos en un solo comando con Docker Compose.
- 📊 **CLI interactiva con Rich** — Tablas formateadas, colores, spinners de carga y experiencia de usuario en terminal.
- 📁 **Indexación de CSV** — Carga datasets desde archivos CSV y genera embeddings automáticamente en batches.
- 🔧 **Scripts SQL incluidos** — Schema puro para recrear la base de datos sin depender de Python.

---

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Dataset CSV   │────▶│  Indexer (Python)│────▶│ PostgreSQL +    │
│   (ejemplo)     │     │  - Jina / Local  │     │ pgvector        │
└─────────────────┘     │  - Embeddings    │     │ (Docker)        │
                        └──────────────────┘     └─────────────────┘
                                                          ▲
                                                          │ consulta SQL
┌─────────────────┐     ┌──────────────────┐              │
│   Usuario CLI   │────▶│  Search App      │──────────────┘
│   (Rich)        │     │  - Jina / Local  │
└─────────────────┘     │  - Similitud     │
                        └──────────────────┘
```

---

## 📋 Requisitos

| Herramienta | Versión | Link |
|-------------|---------|------|
| Docker | 20.10+ | [Instalar](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.0+ | [Instalar](https://docs.docker.com/compose/install/) |
| Python | 3.10+ | [Instalar](https://www.python.org/downloads/) |

> **No necesitas API key** para empezar. El proveedor **Local** funciona 100% offline.

---

## 🚀 Instalación rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/alejolizal/busqueda_semantica.git
cd busqueda_semantica
git checkout feature/poc-busqueda-semantica
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ La instalación de `sentence-transformers` descarga PyTorch, lo cual puede tardar varios minutos la primera vez.

### 3. Configurar variables de entorno

Elige tu proveedor y copia el `.env` correspondiente:

#### Opción A: Jina AI (recomendada si tienes API key)
```bash
cp .env.example .env
```

Configura tu API key de Jina AI (gratuita en [jina.ai/embeddings](https://jina.ai/embeddings)):

```env
EMBEDDING_API_KEY=jina_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Opción B: Local (sentence-transformers)
Edita `.env` y cambia:

```env
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```

### 4. Levantar PostgreSQL con pgvector

```bash
docker compose up -d
```

### 5. Inicializar la base de datos

> ⚠️ Si cambiaste a `EMBEDDING_DIMENSION=384`, ajusta también `scripts/db_schema.sql` (`VECTOR(384)`) antes de ejecutar esto, o borra el volumen previo con `docker compose down -v`.

```bash
python scripts/init_db.py
```

Salida esperada:

```
🔧 Inicializando base de datos...
1/3 Creando extensión pgvector...
2/3 Creando tablas...
3/3 Creando índices...
✅ Base de datos lista para usar
```

### 6. Indexar datos de ejemplo

```bash
python scripts/index_data.py --file data/sample_documents.csv
```

Salida esperada:

```
📄 Cargando 52 documentos desde data/sample_documents.csv...
✅ Indexados 52/52 documentos
🎉 Indexación completa: 52 documentos en total
```

---

## 💻 Uso

### Iniciar la búsqueda interactiva

```bash
python scripts/search.py
```

Interfaz esperada:

```
╭───────────────────────────────────────────────────╮
│ 🔍 Búsqueda Semántica POC                         │
│ Proveedor: jina | Modelo: jina-embeddings-v3      │
│ Base de datos: PostgreSQL + pgvector              │
│                                                   │
│ Escribe tu consulta y presiona Enter.             │
│ Escribe exit o quit para salir.                   │
╰───────────────────────────────────────────────────╯

📦 52 documentos indexados en la base de datos

➜ Consulta: inteligencia artificial
```

### Ejemplos de consultas

Prueba escribir estas consultas en lenguaje natural:

| Consulta | Resultado esperado |
|----------|-------------------|
| `inteligencia artificial` | Documentos sobre IA, machine learning y redes neuronales |
| `guerras del siglo XX` | Segunda Guerra Mundial, Guerra Fría, Revolución Rusa |
| `arte moderno` | Cubismo, impresionismo, surrealismo |
| `tecnología de contenedores` | Docker, Kubernetes, nube |
| `descubrimientos científicos` | Relatividad, evolución, física cuántica |

### Salida de resultados

```
                    Resultados para: "inteligencia artificial"
┏━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  # ┃ Score  ┃ Categoría   ┃ Contenido                                            ┃
┡━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│  1 │ 0.892  │ Tecnología  │ El aprendizaje automático es una rama de la intelig… │
│  2 │ 0.845  │ Tecnología  │ Las redes neuronales artificiales están inspiradas…  │
│  3 │ 0.821  │ Tecnología  │ La inteligencia artificial generativa puede crear…   │
└────┴────────┴─────────────┴──────────────────────────────────────────────────────┘
```

> Los resultados se ordenan por **score de similitud coseno** (0 a 1). Cuanto más cercano a 1, más relevante es el documento.

---

## 📁 Estructura del proyecto

```
busqueda_semantica/
├── docker-compose.yml          # PostgreSQL 15 + pgvector
├── .env.example                # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
│
├── data/
│   └── sample_documents.csv    # Dataset de ejemplo (52 documentos categorizados)
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuración con pydantic-settings
│   ├── database.py             # SQLAlchemy ORM + operaciones pgvector
│   ├── embeddings.py           # Clientes Jina AI + Local (factory)
│   └── indexer.py              # Lógica de indexación CSV por batches
│
└── scripts/
    ├── init_db.py              # Inicializa extensión pgvector, tablas e índices
    ├── index_data.py           # Carga CSV y genera embeddings
    ├── search.py               # CLI interactiva con Rich
    └── db_schema.sql           # Schema SQL puro para recrear la BD sin Python
```

---

## ⚙️ Configuración

Todas las variables se cargan desde el archivo `.env`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `EMBEDDING_PROVIDER` | Proveedor: `jina` o `local` | `jina` |
| `EMBEDDING_API_KEY` | API key de Jina AI (requerida para Jina) | — |
| `EMBEDDING_BASE_URL` | URL base de la API | `https://api.jina.ai/v1` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `jina-embeddings-v3` |
| `EMBEDDING_DIMENSION` | Dimensión del vector | `1024` |
| `SEARCH_THRESHOLD` | Umbral mínimo de similitud (0.0 = desactivado) | `0.35` |
| `SEARCH_TOP_K` | Máximo de resultados a retornar | `5` |
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+psycopg2://semantic_user:semantic_pass@localhost:5432/semantic_search` |

### Combinaciones válidas

| Proveedor | Modelo | Dimensión | Requiere API key | Requiere internet |
|-----------|--------|-----------|------------------|-------------------|
| `jina` | `jina-embeddings-v3` | `1024` | ✅ (gratuita) | ✅ |
| `local` | `paraphrase-multilingual-MiniLM-L12-v2` | `384` | ❌ | ❌ |
| `local` | `all-MiniLM-L6-v2` | `384` | ❌ | ❌ |

> ⚠️ **Importante**: Si cambias de proveedor o modelo, asegúrate de que `EMBEDDING_DIMENSION` coincida con la dimensión real del modelo. De lo contrario, `init_db.py` fallará con un error de validación.

### Threshold de similitud

El parámetro `SEARCH_THRESHOLD` filtra resultados con score menor al umbral configurado:

- `0.35` (default): Solo muestra documentos con score ≥ 0.35. Elimina resultados poco relevantes.
- `0.0`: Desactiva el filtro. Muestra los top-k sin importar el score.

Si ningún resultado supera el umbral, verás:

```
⚠️  Ningún resultado superó el umbral de similitud (0.35). Prueba con otra consulta.
```

---

## 🗄️ Scripts de base de datos

Para recrear la base de datos en otro equipo **sin usar Python**, ejecuta el schema SQL directamente:

### Opción A: Con psql

```bash
# Asegúrate de que el contenedor esté corriendo
docker compose up -d

# Ejecutar el schema (ajusta VECTOR(1024) a VECTOR(384) si usas local)
psql -h localhost -U semantic_user -d semantic_search -f scripts/db_schema.sql
```

### Opción B: Con Python (recomendada)

```bash
python scripts/init_db.py
```

### Contenido de `db_schema.sql`

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1024)  -- <-- cambiar a 384 para modelos locales
);

CREATE INDEX IF NOT EXISTS idx_documents_embedding
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## 📊 Dataset de ejemplo

El archivo `data/sample_documents.csv` contiene **52 documentos** organizados en 4 categorías:

- 🖥️ **Tecnología** (13 documentos)
- 📜 **Historia** (13 documentos)
- 🔬 **Ciencia** (13 documentos)
- 🎨 **Arte** (13 documentos)

Cada fila tiene las columnas `content` y `category`.

Puedes reemplazar este CSV por tu propio dataset — solo asegúrate de incluir una columna llamada **`content`**.

---

## 🧪 Cambiar de proveedor sin perder datos

Si ya indexaste con un proveedor y quieres probar otro, debes **recrear la tabla** porque cada modelo genera vectores de distinta dimensión:

```bash
# 1. Borrar datos previos
docker compose down -v
docker compose up -d

# 2. Actualizar .env con el nuevo proveedor/modelo/dimensión

# 3. Re-crear tablas
python scripts/init_db.py

# 4. Re-indexar
python scripts/index_data.py --file data/sample_documents.csv
```

---

## 🐛 Troubleshooting

### Error: `EMBEDDING_DIMENSION no coincide con la dimensión del modelo`

Asegúrate de que `EMBEDDING_DIMENSION` en tu `.env` coincida con la dimensión real del modelo:

```bash
# Para Jina
EMBEDDING_DIMENSION=1024

# Para sentence-transformers (MiniLM)
EMBEDDING_DIMENSION=384
```

### Error de conexión a PostgreSQL

Verifica que el contenedor esté corriendo:

```bash
docker compose ps
docker compose logs postgres
```

Si es la primera vez, espera unos segundos a que PostgreSQL termine de inicializarse.

### Error: `pgvector` no está disponible

Asegúrate de usar la imagen correcta en `docker-compose.yml`:

```yaml
image: pgvector/pgvector:pg15
```

Si cambiaste a una imagen de PostgreSQL estándar, la extensión `pgvector` no estará disponible.

### Error: `sentence-transformers no está instalado`

Si usas el proveedor `local` y te falta la dependencia:

```bash
pip install sentence-transformers
```

La primera ejecución descargará el modelo (~400MB) y puede tardar unos minutos.

---

## 🛑 Detener el proyecto

```bash
# Detener contenedores
docker compose down

# Detener y eliminar datos persistentes
docker compose down -v
```

---

## 🛠️ Tecnologías utilizadas

- [Python](https://www.python.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [pgvector](https://github.com/pgvector/pgvector)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Rich](https://github.com/Textualize/rich)
- [Httpx](https://www.python-httpx.org/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Jina AI Embeddings](https://jina.ai/embeddings)
- [Sentence-Transformers](https://www.sbert.net/)

---

## 📄 Licencia

MIT © Alejandro Lizal
