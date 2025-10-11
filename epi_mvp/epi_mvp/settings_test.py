# epi_mvp/settings_test.py
from epi_mvp.settings import *  # herda tudo do settings padrão

# Força SQLite em memória para a suíte de testes
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Suíte mais rápida/estável
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Evita ruído de logs em teste (opcional)
LOGGING = {"version": 1, "disable_existing_loggers": True}

# Se o seu settings usa variáveis de ambiente para DB, garantimos que nada força MySQL
import os
os.environ["DB_ENGINE"] = "sqlite"
