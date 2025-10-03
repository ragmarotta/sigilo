from abc import ABC, abstractmethod

class MessageRepositoryInterface(ABC):
    """Interface que define o contrato para repositórios de mensagens."""

    @abstractmethod
    def save(self, token: str, message_data: dict, expires_in: int):
        pass

    @abstractmethod
    def find_by_id(self, token: str) -> dict:
        pass

    @abstractmethod
    def delete(self, token: str):
        pass

    @abstractmethod
    def get_all(self) -> list:
        pass

    @abstractmethod
    def get_ttl(self, key: bytes) -> int:
        pass
