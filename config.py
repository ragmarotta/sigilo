import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Fail fast if critical secrets are not set
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("A variável de ambiente 'SECRET_KEY' não foi definida. A aplicação não pode iniciar de forma segura.")

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Keycloak Config
    KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL')
    KEYCLOAK_REALM_NAME = os.environ.get('KEYCLOAK_REALM_NAME')
    KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID')

    # Fernet Encryption
    FERNET_KEY = os.environ.get('FERNET_KEY')
    if not FERNET_KEY:
        raise ValueError("A variável de ambiente 'FERNET_KEY' não foi definida. A criptografia de dados está comprometida.")

    # Mock Keycloak - Avoid allowing this to be disabled in production via env var
    # For production, this should always be True. Logic for disabling should be in test-specific configs.
    KEYCLOAK_ENABLED = os.environ.get('ENVIRONMENT') != 'production' and \
                     os.environ.get('KEYCLOAK_ENABLED', 'True').lower() in ('true', '1', 't')
    
    KEYCLOAK_CLIENT_SECRET_KEY = os.environ.get('KEYCLOAK_CLIENT_SECRET_KEY')

    # App Version
    APP_VERSION = "1.0.0-SNAPSHOT"

    # Email Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
