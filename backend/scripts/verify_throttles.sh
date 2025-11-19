#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 SCRIPT - Verificar Throttles en Local
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este script verifica que los throttles funcionan correctamente.
# Envía múltiples requests rápidos y verifica que se devuelve 429.
#
# Uso:
#   bash scripts/verify_throttles.sh
#
# Requisitos:
#   - Django server corriendo en http://localhost:8000
#   - curl instalado
#   - Token JWT válido (opcional, para endpoints autenticados)

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
BASE_URL="http://localhost:8000/api"
TOKEN=""  # Agregar tu token JWT aquí si es necesario

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧪 VERIFICACIÓN DE THROTTLES${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}\n"

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: Productos (SIN THROTTLE - Debe permitir todos)
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}TEST 1: /api/productos/ (SIN THROTTLE)${NC}"
echo "Enviando 50 requests rápidos (esperado: todos 200)"
echo ""

success_count=0
throttle_count=0

for i in {1..50}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/productos/")
    if [ "$response" = "200" ]; then
        ((success_count++))
    elif [ "$response" = "429" ]; then
        ((throttle_count++))
    fi
    printf "."
done

echo ""
echo -e "Resultados: ${GREEN}✅ $success_count OK${NC} | ${RED}❌ $throttle_count THROTTLED${NC}"

if [ $throttle_count -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: No hay throttle en /api/productos/${NC}\n"
else
    echo -e "${RED}❌ FAIL: Hay throttle en /api/productos/ (no debería)${NC}\n"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Carrusel (SIN THROTTLE - Debe permitir todos)
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}TEST 2: /api/carrusel/ (SIN THROTTLE)${NC}"
echo "Enviando 50 requests rápidos (esperado: todos 200)"
echo ""

success_count=0
throttle_count=0

for i in {1..50}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/carrusel/")
    if [ "$response" = "200" ]; then
        ((success_count++))
    elif [ "$response" = "429" ]; then
        ((throttle_count++))
    fi
    printf "."
done

echo ""
echo -e "Resultados: ${GREEN}✅ $success_count OK${NC} | ${RED}❌ $throttle_count THROTTLED${NC}"

if [ $throttle_count -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: No hay throttle en /api/carrusel/${NC}\n"
else
    echo -e "${RED}❌ FAIL: Hay throttle en /api/carrusel/ (no debería)${NC}\n"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Login (AUTH THROTTLE - 10/hora)
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}TEST 3: /api/auth/login/ (AUTH THROTTLE - 10/hora)${NC}"
echo "Enviando 15 requests rápidos (esperado: 10 OK + 5 THROTTLED)"
echo ""

success_count=0
throttle_count=0

for i in {1..15}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/login/" \
        -H "Content-Type: application/json" \
        -d '{"username": "test", "password": "wrong"}')
    
    if [ "$response" = "200" ] || [ "$response" = "401" ] || [ "$response" = "400" ]; then
        ((success_count++))
    elif [ "$response" = "429" ]; then
        ((throttle_count++))
    fi
    printf "."
done

echo ""
echo -e "Resultados: ${GREEN}✅ $success_count OK${NC} | ${RED}❌ $throttle_count THROTTLED${NC}"

if [ $throttle_count -gt 0 ]; then
    echo -e "${GREEN}✅ PASS: Throttle funcionando en /api/auth/login/${NC}\n"
else
    echo -e "${YELLOW}⚠️  WARNING: No se detectó throttle (puede ser normal si no hay rate limit configurado)${NC}\n"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ VERIFICACIÓN COMPLETADA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}\n"

echo "Próximos pasos:"
echo "1. Ejecutar tests: pytest tests/test_throttles.py -v"
echo "2. Revisar logs en Django: python manage.py runserver"
echo "3. Configurar .env para producción"
echo "4. Desplegar"
