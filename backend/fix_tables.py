"""
Script para eliminar y recrear las tablas RefreshToken y LoginAttempt
Ejecutar: python fix_tables.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def fix_tables():
    print("=" * 80)
    print("Eliminando y recreando tablas RefreshToken y LoginAttempt")
    print("=" * 80)
    print()
    
    with connection.cursor() as cursor:
        # Eliminar tablas si existen
        print("[1/4] Eliminando tabla refresh_tokens si existe...")
        cursor.execute("DROP TABLE IF EXISTS refresh_tokens CASCADE;")
        print("      OK - Tabla refresh_tokens eliminada")
        
        print("[2/4] Eliminando tabla login_attempts si existe...")
        cursor.execute("DROP TABLE IF EXISTS login_attempts CASCADE;")
        print("      OK - Tabla login_attempts eliminada")
        
        print()
        print("[3/4] Eliminando registros de migraciones...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'api' 
            AND name IN ('0008_refreshtoken', '0009_loginattempt');
        """)
        print("      OK - Registros de migraciones eliminados")
        
    print()
    print("[4/4] Ejecutando migraciones nuevamente...")
    print()
    
    # Ejecutar migraciones
    from django.core.management import call_command
    call_command('migrate', 'api')
    
    print()
    print("=" * 80)
    print("[EXITO] Tablas recreadas correctamente!")
    print("=" * 80)
    print()
    print("Ahora puedes iniciar el servidor con: python manage.py runserver")
    print()

if __name__ == '__main__':
    try:
        fix_tables()
    except Exception as e:
        print()
        print("[ERROR]", str(e))
        print()
        import traceback
        traceback.print_exc()
