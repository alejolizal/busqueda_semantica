# 🔍 Búsqueda Semántica POC

Proof of Concept de búsqueda semántica usando:
- **API de Kimi (Moonshot AI)** para generar embeddings (`model-embedding-001`)
- **PostgreSQL + pgvector** para almacenar y buscar vectores
- **Python + Rich** para una interfaz de terminal interactiva

---

## 📋 Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.10+
- API Key de [Moonshot AI](https://platform.moonshot.cn/)

---

## 🚀 Instalación y uso

### 1. Clonar y entrar al proyecto

```bash
cd busqueda_semantica
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
# Edita .env y coloca tu KIMI_API_KEY
```

### 4. Levantar PostgreSQL con pgvector

```bash
docker compose up -d
```

### 5. Inicializar la base de datos

```bash
python scripts/init_db.py
```

### 6. Indexar datos de ejemplo

```bash
python scripts/index_data.py --file data/sample_documents.csv
```

### 7. Buscar semánticamente

```bash
python scripts/search.py
```

Escribe tu consulta en lenguaje natural y presiona **Enter**. El sistema encontrará los documentos más similares usando similitud coseno sobre los embeddings.

---

## 📁 Estructura del proyecto

```
busqueda_semantica/
├── docker-compose.yml          # PostgreSQL 15 + pgvector
├── .env.example                # Variables de entorno de ejemplo
├── requirements.txt            # Dependencias Python
├── data/
│   └── sample_documents.csv    # Dataset de ejemplo (52 documentos)
├── src/
│   ├── config.py               # Configuración con pydantic-settings
│   ├── database.py             # SQLAlchemy + pgvector
│   ├── embeddings.py           # Cliente API de Kimi
│   └── indexer.py              # Lógica de indexación CSV
└── scripts/
    ├── init_db.py              # Inicializa extensión y tablas
    ├── index_data.py           # Carga CSV y genera embeddings
    └── search.py               # CLI interactiva con Rich
```

---

## 🧪 Ejemplos de búsqueda

Una vez ejecutado `python scripts/search.py`, prueba consultas como:

- `inteligencia artificial`
- `música y cultura`
- `guerras del siglo XX`
- `descubrimientos científicos`
- `arte moderno`
- `tecnología de contenedores`

Los resultados se ordenan por **score de similitud** (0 a 1, donde 1 es idéntico).

---

## ⚙️ Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `KIMI_API_KEY` | Tu API key de Moonshot AI | — |
| `KIMI_BASE_URL` | URL base de la API | `https://api.moonshot.cn/v1` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `model-embedding-001` |
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+psycopg2://semantic_user:semantic_pass@localhost:5432/semantic_search` |

---

## 🛑 Detener

```bash
docker compose down        # Detener contenedor
docker compose down -v     # Detener y eliminar datos
```

---

## 📄 Licencia

MIT
