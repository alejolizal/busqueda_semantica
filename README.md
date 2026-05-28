# 🔍 Búsqueda Semántica POC

> Proof of Concept de búsqueda semántica con **embeddings de Kimi (Moonshot AI)**, **PostgreSQL + pgvector** y una **CLI interactiva en Python**.

Este proyecto demuestra cómo construir un sistema de búsqueda por similitud semántica desde cero: convierte textos en vectores numéricos usando la API de Kimi, los almacena en PostgreSQL con la extensión `pgvector`, y permite consultarlos desde una interfaz de terminal elegante gracias a [Rich](https://github.com/Textualize/rich).

---

## ✨ Características

- 🤖 **Embeddings con Kimi API** — Usa el modelo `model-embedding-001` de Moonshot AI para generar representaciones vectoriales de texto.
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
│   (ejemplo)     │     │  - Kimi API      │     │ pgvector        │
└─────────────────┘     │  - Embeddings    │     │ (Docker)        │
                        └──────────────────┘     └─────────────────┘
                                                          ▲
                                                          │ consulta SQL
┌─────────────────┐     ┌──────────────────┐              │
│   Usuario CLI   │────▶│  Search App      │──────────────┘
│   (Rich)        │     │  - Kimi API      │
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
| API Key Kimi | — | [Obtener](https://platform.moonshot.cn/) |

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

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y agrega tu API key de Kimi:

```env
KIMI_API_KEY=sk-tu-api-key-aqui
```

> 🔑 Obtén tu API key en [https://platform.moonshot.cn/](https://platform.moonshot.cn/)

### 4. Levantar PostgreSQL con pgvector

```bash
docker compose up -d
```

### 5. Inicializar la base de datos

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
╭───────────────────────────────────────╮
│ 🔍 Búsqueda Semántica POC             │
│ Modelo: model-embedding-001           │
│ Base de datos: PostgreSQL + pgvector  │
│                                       │
│ Escribe tu consulta y presiona Enter. │
│ Escribe exit o quit para salir.       │
╰───────────────────────────────────────╯

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
│   ├── embeddings.py           # Cliente HTTP para API de Kimi
│   └── indexer.py              # Lógica de indexación CSV por batches
│
└── scripts/
    ├── init_db.py              # Inicializa extensión pgvector, tablas e índices
    ├── index_data.py           # Carga CSV y genera embeddings vía Kimi API
    ├── search.py               # CLI interactiva con Rich
    └── db_schema.sql           # Schema SQL puro para recrear la BD sin Python
```

---

## ⚙️ Configuración

Todas las variables se cargan desde el archivo `.env`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `KIMI_API_KEY` | API key de Moonshot AI (requerida) | — |
| `KIMI_BASE_URL` | URL base de la API de Kimi | `https://api.moonshot.cn/v1` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `model-embedding-001` |
| `EMBEDDING_DIMENSION` | Dimensión del vector de embeddings | `1536` |
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+psycopg2://semantic_user:semantic_pass@localhost:5432/semantic_search` |

---

## 🗄️ Scripts de base de datos

Para recrear la base de datos en otro equipo **sin usar Python**, ejecuta el schema SQL directamente:

### Opción A: Con psql

```bash
# Asegúrate de que el contenedor esté corriendo
docker compose up -d

# Ejecutar el schema
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
    embedding VECTOR(1536)
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

## 🧪 Testing local

Si quieres probar el flujo completo sin consumir la API de Kimi, puedes crear un script que inserte vectores aleatorios directamente en la base de datos:

```python
import random
from src.database import DatabaseManager

db = DatabaseManager()

fake_docs = [
    {"content": "Documento de prueba 1", "embedding": [random.random() for _ in range(1536)], "metadata": {"category": "Test"}},
    {"content": "Documento de prueba 2", "embedding": [random.random() for _ in range(1536)], "metadata": {"category": "Test"}},
]

db.add_documents_bulk(fake_docs)
print(f"Documentos en BD: {db.count_documents()}")
```

---

## 🐛 Troubleshooting

### Error: `KIMI_API_KEY no está configurada`

Asegúrate de crear el archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
# Edita .env y agrega tu API key
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

---

## 📄 Licencia

MIT © Alejandro Lizal
