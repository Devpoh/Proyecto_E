#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Punto de entrada para el worker de Celery
Asegura que Django esté completamente inicializado antes de ejecutar tareas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Ahora importar Celery
from config.celery import app

if __name__ == '__main__':
    # Ejecutar worker sin argumentos adicionales
    # Los argumentos se pasan desde la línea de comandos
    app.worker_main()
