from django.contrib.auth.models import User

def run():
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@email.com",
            password="12345678"
        )
        print("admin criado")
    else:
        print("já existe")