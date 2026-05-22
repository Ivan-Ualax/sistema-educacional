from django.apps import AppConfig


class FuncionariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcionarios'

    def ready(self):
        try:
            from .scripts import create_admin
            create_admin.run()
        except Exception as e:
            print("Erro ao criar admin:", e)