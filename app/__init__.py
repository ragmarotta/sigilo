from flask import Flask
from flask_mail import Mail
from config import Config
import redis
from app.logging_config import setup_logging

# Configura o logging antes de criar a app
setup_logging()

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa o cliente Redis
    app.redis = redis.from_url(app.config['REDIS_URL'])

    # Inicializa o Flask-Mail
    mail.init_app(app)

    # Registrar Blueprints (rotas)
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app
