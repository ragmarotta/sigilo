from flask import current_app

from app.services.message_service import MessageService
from app.services.link_service import LinkService
from app.repositories.redis_message_repository import RedisMessageRepository
from app.repositories.redis_link_repository import RedisLinkRepository
# No futuro, você poderia importar outros repositórios aqui
# from app.repositories.sql_message_repository import SqlMessageRepository


def get_message_service() -> MessageService:
    """Fábrica para o MessageService."""
    # A lógica para decidir qual repositório usar viria aqui.
    # Por enquanto, está fixo para Redis.
    repo = RedisMessageRepository()
    return MessageService(message_repo=repo)

def get_link_service() -> LinkService:
    """Fábrica para o LinkService."""
    repo = RedisLinkRepository()
    return LinkService(link_repo=repo)
