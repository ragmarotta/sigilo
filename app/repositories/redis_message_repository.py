from flask import current_app
import time
from app.repositories.interfaces.message_repository_interface import MessageRepositoryInterface

class RedisMessageRepository(MessageRepositoryInterface):
    """Implementação do repositório de mensagens para Redis."""

    def __init__(self):
        self.redis = current_app.redis

    def save(self, token: str, message_data: dict, expires_in: int):
        """Salva os dados de uma mensagem no Redis."""
        key = f"message:{token}"
        pipe = self.redis.pipeline()
        pipe.hset(key, mapping=message_data)
        if expires_in > 0:
            pipe.expire(key, expires_in)
        pipe.execute()

    def find_by_id(self, token: str) -> dict:
        """Busca uma mensagem pelo seu token."""
        key = f"message:{token}"
        return self.redis.hgetall(key)

    def delete(self, token: str):
        """Apaga uma mensagem do Redis."""
        key = f"message:{token}"
        self.redis.delete(key)

    def get_all(self) -> list:
        """Retorna um gerador para todas as chaves de mensagem."""
        return self.redis.scan_iter("message:*")

    def get_ttl(self, key: bytes) -> int:
        """Retorna o TTL de uma chave."""
        return self.redis.ttl(key)

    def increment_visits(self, token: str) -> int:
        """Incrementa o contador de visitas de uma mensagem."""
        key = f"message:{token}"
        return self.redis.hincrby(key, 'visits', 1)
