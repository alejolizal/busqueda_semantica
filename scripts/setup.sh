#!/usr/bin/env bash
set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  🔍 Setup Búsqueda Semántica POC${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    exit 1
fi

# Crear .env si no existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env no encontrado. Copiando desde .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}   Por favor edita .env y configura tu EMBEDDING_API_KEY si usas Jina${NC}"
    echo ""
fi

# Crear venv si no existe
if [ ! -d "venv" ]; then
    echo -e "${CYAN}📦 Creando entorno virtual...${NC}"
    python3 -m venv venv
fi

# Activar venv
source venv/bin/activate

# Instalar dependencias
echo -e "${CYAN}📦 Instalando dependencias...${NC}"
pip install -r requirements.txt --quiet

# Levantar PostgreSQL
echo -e "${CYAN}🐘 Levantando PostgreSQL + pgvector...${NC}"
docker compose up -d

# Esperar a que PostgreSQL esté listo
echo -e "${CYAN}⏳ Esperando a que PostgreSQL esté listo...${NC}"
for i in {1..30}; do
    if docker compose ps postgres | grep -q "healthy"; then
        echo -e "${GREEN}✅ PostgreSQL listo${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Timeout esperando PostgreSQL${NC}"
        exit 1
    fi
done

# Inicializar base de datos
echo -e "${CYAN}🔧 Inicializando base de datos...${NC}"
python scripts/init_db.py

# Indexar datos de ejemplo
echo -e "${CYAN}📄 Indexando documentos de ejemplo...${NC}"
python scripts/index_data.py --file data/sample_documents.csv

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ Setup completo!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Para buscar:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}python scripts/search.py${NC}"
echo ""
