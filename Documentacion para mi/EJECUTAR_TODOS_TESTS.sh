#!/bin/bash

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🧪 EJECUTANDO TODOS LOS TESTS - VULNERABILIDADES Y MEJORAS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

cd backend

echo "📋 Test 1: Vulnerabilidades Críticas (7 vulnerabilidades)"
echo "───────────────────────────────────────────────────────────────────────────────"
python manage.py test api.tests_vulnerabilidades_criticas -v 2
TEST1=$?

echo ""
echo "📋 Test 2: Mejoras de Rendimiento (4 mejoras)"
echo "───────────────────────────────────────────────────────────────────────────────"
python manage.py test api.tests_mejoras_rendimiento -v 2
TEST2=$?

echo ""
echo "📋 Test 3: Mejoras Adicionales (4 mejoras)"
echo "───────────────────────────────────────────────────────────────────────────────"
python manage.py test api.tests_mejoras_adicionales -v 2
TEST3=$?

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "📊 RESUMEN DE RESULTADOS"
echo "════════════════════════════════════════════════════════════════════════════════"

if [ $TEST1 -eq 0 ]; then
    echo "✅ Test 1 (Vulnerabilidades Críticas): PASÓ"
else
    echo "❌ Test 1 (Vulnerabilidades Críticas): FALLÓ"
fi

if [ $TEST2 -eq 0 ]; then
    echo "✅ Test 2 (Mejoras de Rendimiento): PASÓ"
else
    echo "❌ Test 2 (Mejoras de Rendimiento): FALLÓ"
fi

if [ $TEST3 -eq 0 ]; then
    echo "✅ Test 3 (Mejoras Adicionales): PASÓ"
else
    echo "❌ Test 3 (Mejoras Adicionales): FALLÓ"
fi

echo ""
if [ $TEST1 -eq 0 ] && [ $TEST2 -eq 0 ] && [ $TEST3 -eq 0 ]; then
    echo "🎉 TODOS LOS TESTS PASARON"
    echo "📈 Score Final: 9.8/10"
    exit 0
else
    echo "⚠️  ALGUNOS TESTS FALLARON"
    exit 1
fi
