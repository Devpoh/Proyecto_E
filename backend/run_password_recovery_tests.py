#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧪 SCRIPT - Ejecutar Tests de Recuperación de Contraseña
═══════════════════════════════════════════════════════════════════════════════

Script para ejecutar todos los tests del sistema de recuperación de contraseña.

Uso:
    python run_password_recovery_tests.py
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)
    
    # Ejecutar tests específicos
    failures = test_runner.run_tests([
        'api.tests.test_password_recovery.PasswordResetTokenModelTest',
        'api.tests.test_password_recovery.PasswordResetEndpointsTest',
        'api.tests.test_password_recovery.PasswordResetSecurityTest',
    ])
    
    sys.exit(bool(failures))
