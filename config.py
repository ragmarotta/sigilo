import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Keycloak Config
    KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL')
    KEYCLOAK_REALM_NAME = os.environ.get('KEYCLOAK_REALM_NAME')
    KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID')
    KEYCLOAK_CLIENT_SECRET_KEY = os.environ.get('KEYCLOAK_CLIENT_SECRET_KEY')

    # Fernet Encryption
    FERNET_KEY = os.environ.get('FERNET_KEY')

    # Mock Keycloak
    KEYCLOAK_ENABLED = os.environ.get('KEYCLOAK_ENABLED', 'True').lower() in ('true', '1', 't')

    # Email Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
