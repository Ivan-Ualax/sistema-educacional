from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@email.com',
            password=make_password('12345678'),
            is_superuser=True,
            is_staff=True
        )

class Migration(migrations.Migration):

    dependencies = [
        ('funcionarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]