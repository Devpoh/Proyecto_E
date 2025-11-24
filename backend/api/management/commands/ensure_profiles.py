"""
═══════════════════════════════════════════════════════════════════════════════
MANAGEMENT COMMAND - Ensure User Profiles
═══════════════════════════════════════════════════════════════════════════════

Comando para asegurar que todos los usuarios tengan perfil
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile


class Command(BaseCommand):
    help = 'Asegura que todos los usuarios tengan perfil con rol correcto'

    def handle(self, *args, **kwargs):
        users_without_profile = 0
        users_updated = 0
        
        for user in User.objects.all():
            # Crear perfil si no existe
            if not hasattr(user, 'profile'):
                rol = 'admin' if (user.is_superuser or user.is_staff) else 'cliente'
                UserProfile.objects.create(user=user, rol=rol)
                users_without_profile += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Perfil creado para {user.username} con rol: {rol}')
                )
            else:
                # Actualizar rol si es superuser/staff pero no es admin
                if (user.is_superuser or user.is_staff) and user.profile.rol != 'admin':
                    user.profile.rol = 'admin'
                    user.profile.save()
                    users_updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[OK] Rol actualizado para {user.username} a: admin')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[RESUMEN]:\n'
                f'   - Perfiles creados: {users_without_profile}\n'
                f'   - Roles actualizados: {users_updated}\n'
                f'   - Total usuarios: {User.objects.count()}'
            )
        )
