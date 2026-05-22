from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil = apps.get_model('funcionarios', 'Perfil')
        Perfil.objects.get_or_create(usuario=instance)