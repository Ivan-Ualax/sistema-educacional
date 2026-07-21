"""
Django settings for sistema project.
"""

import os
from pathlib import Path

import dj_database_url  # type: ignore


BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SEGURANÇA
# =========================================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-local'
)

DEBUG = os.environ.get(
    'DEBUG',
    'True'
).lower() == 'true'


ALLOWED_HOSTS = [
    'sistema-educacional-xsfm.onrender.com',
    'localhost',
    '127.0.0.1',
]


CSRF_TRUSTED_ORIGINS = [
    'https://sistema-educacional-xsfm.onrender.com',
]


# Necessário para reconhecer o HTTPS usado pelo Render
SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)


# Cookies seguros quando o DEBUG estiver desativado
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# =========================================================
# APLICATIVOS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'funcionarios',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'sistema.urls'


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        'BACKEND': (
            'django.template.backends.django.'
            'DjangoTemplates'
        ),

        'DIRS': [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                (
                    'django.template.context_processors.'
                    'request'
                ),

                (
                    'django.contrib.auth.'
                    'context_processors.auth'
                ),

                (
                    'django.contrib.messages.'
                    'context_processors.messages'
                ),
            ],
        },
    },
]


WSGI_APPLICATION = 'sistema.wsgi.application'


# =========================================================
# BANCO DE DADOS
# =========================================================

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# =========================================================
# VALIDAÇÃO DE SENHAS
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },

    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },

    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },

    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# =========================================================
# IDIOMA E FUSO HORÁRIO
# =========================================================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# =========================================================
# ARQUIVOS ESTÁTICOS
# =========================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# A pasta static dentro do app funcionarios já é encontrada
# automaticamente pelo Django.
STATICFILES_DIRS = []

pasta_static_global = BASE_DIR / 'static'

if pasta_static_global.exists():
    STATICFILES_DIRS.append(pasta_static_global)


STATICFILES_STORAGE = (
    'whitenoise.storage.'
    'CompressedManifestStaticFilesStorage'
)


# =========================================================
# ARQUIVOS DE MÍDIA
# =========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# LOGIN E LOGOUT
# =========================================================

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/login/'


# =========================================================
# CONFIGURAÇÕES PADRÃO
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'