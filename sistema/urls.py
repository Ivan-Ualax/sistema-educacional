from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    # LOGIN

    path(

        'login/',

        auth_views.LoginView.as_view(
            template_name='login.html'
        ),

        name='login'

    ),

    # LOGOUT

    path(

        'logout/',

        auth_views.LogoutView.as_view(
            next_page='/login/'
        ),

        name='logout'

    ),

    # SISTEMA

    path(
        '',
        include('funcionarios.urls')
    ),

]