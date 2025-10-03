from flask import current_app
from app.repositories.interfaces.link_repository_interface import LinkRepositoryInterface

class RedisLinkRepository(LinkRepositoryInterface):
    """Implementação do repositório de links para Redis."""

    def __init__(self):
        self.redis = current_app.redis

    def save(self, short_code: str, long_url: str, owner: str, expires_in: int):
        """Salva um link encurtado e seus metadados."""
        link_key = f"link:{short_code}"
        self.redis.set(link_key, long_url)
        if expires_in > 0:
            self.redis.expire(link_key, expires_in)
        self.redis.hset(f"link_meta:{short_code}", "owner", owner)

    def find_by_id(self, short_code: str) -> bytes:
        """Busca uma URL longa pelo código curto."""
        return self.redis.get(f"link:{short_code}")

    def delete(self, short_code: str):
        """Apaga um link e seus metadados."""
        self.redis.delete(f"link:{short_code}", f"link_meta:{short_code}")

    def get_all(self) -> list:
        """Retorna um gerador para todas as chaves de link."""
        return self.redis.scan_iter("link:*")

    def get_meta(self, short_code: str) -> dict:
        """Busca os metadados de um link."""
        return self.redis.hgetall(f"link_meta:{short_code}")

    def get_ttl(self, key: bytes) -> int:
        """Retorna o TTL de uma chave."""
        return self.redis.ttl(key)
