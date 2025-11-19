"""
═══════════════════════════════════════════════════════════════════════════════
🔐 MODELS - User Profile
═══════════════════════════════════════════════════════════════════════════════

Modelo de perfil de usuario con roles personalizados
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Perfil extendido de usuario con roles personalizados
    """
    
    ROLES = [
        ('cliente', 'Cliente'),
        ('mensajero', 'Mensajero'),
        ('trabajador', 'Trabajador'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"
    
    @property
    def has_admin_access(self):
        """Verifica si el usuario tiene acceso al panel de admin"""
        return self.rol in ['admin', 'trabajador', 'mensajero']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear usuario"""
    if created:
        # Si es superuser o staff, asignar rol admin
        rol = 'admin' if (instance.is_superuser or instance.is_staff) else 'cliente'
        UserProfile.objects.create(user=instance, rol=rol)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar perfil al guardar usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
