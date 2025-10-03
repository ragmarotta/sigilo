from abc import ABC, abstractmethod

class LinkRepositoryInterface(ABC):
    """Interface que define o contrato para repositórios de links."""

    @abstractmethod
    def save(self, short_code: str, long_url: str, owner: str, expires_in: int):
        pass

    @abstractmethod
    def find_by_id(self, short_code: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, short_code: str):
        pass

    @abstractmethod
    def get_all(self) -> list:
        pass

    @abstractmethod
    def get_meta(self, short_code: str) -> dict:
        pass

    @abstractmethod
    def get_ttl(self, key: bytes) -> int:
        pass
