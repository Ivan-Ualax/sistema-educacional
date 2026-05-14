from django.contrib import admin
from .models import Cargo, Funcionario, HoraExtra

admin.site.register(Cargo)
admin.site.register(Funcionario)
admin.site.register(HoraExtra)