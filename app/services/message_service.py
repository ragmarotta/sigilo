import uuid
import time
import datetime
from zoneinfo import ZoneInfo
from app.services.crypto_service import CryptoService
from app.repositories.interfaces.message_repository_interface import MessageRepositoryInterface

TARGET_TZ = ZoneInfo("America/Sao_Paulo")

class MessageService:
    """Camada de serviço com a lógica de negócio para mensagens."""

    def __init__(self, message_repo: MessageRepositoryInterface):
        self.crypto_service = CryptoService()
        self.message_repo = message_repo

    def create_message(self, content: str, expires_in: int, max_visits: int, owner: str) -> str:
        """Criptografa e coordena o salvamento de uma nova mensagem."""
        token = str(uuid.uuid4())
        encrypted_content = self.crypto_service.encrypt(content)
        
        message_data = {
            b'content': encrypted_content,
            b'max_visits': int(max_visits),
            b'visits': 0,
            b'owner': owner,
            b'created_at': int(time.time())
        }
        
        self.message_repo.save(token, message_data, int(expires_in))
        return token

    def find_and_process_message(self, token: str):
        """Busca uma mensagem, processa as regras de negócio e a retorna descriptografada."""
        # A lógica de incremento e verificação de visitas foi movida para o repositório
        # para manter a lógica de negócio no serviço mais limpa.
        message_data = self.message_repo.find_by_id(token)
        if not message_data:
            return None, "Mensagem não encontrada ou expirada."

        max_visits = int(message_data.get(b'max_visits', 0))
        # O repositório agora deve lidar com o incremento
        current_visits = self.message_repo.increment_visits(token)

        if max_visits > 0 and current_visits > max_visits:
            self.message_repo.delete(token)
            return None, "Mensagem expirada (limite de visualizações atingido)."

        content_bytes = message_data.get(b'content')
        if not content_bytes:
            return None, "Conteúdo da mensagem não encontrado."

        decrypted_content = self.crypto_service.decrypt(content_bytes)

        if max_visits > 0 and current_visits == max_visits:
            self.message_repo.delete(token)

        return decrypted_content, None

    def get_all_formatted_messages(self) -> list:
        """Busca todas as mensagens e as formata para exibição."""
        messages = []
        for key in self.message_repo.get_all():
            token = key.decode('utf-8').split(':')[1]
            message_data = self.message_repo.find_by_id(token)
            ttl = self.message_repo.get_ttl(key)

            created_at_ts = int(message_data.get(b'created_at', 0))
            created_at_utc = datetime.datetime.fromtimestamp(created_at_ts, tz=datetime.timezone.utc)
            created_at_str = created_at_utc.astimezone(TARGET_TZ).strftime('%d/%m/%Y %H:%M:%S')

            expiration_date_str = "Nunca"
            if ttl > 0:
                expiration_ts = time.time() + ttl
                expiration_utc = datetime.datetime.fromtimestamp(expiration_ts, tz=datetime.timezone.utc)
                expiration_date_str = expiration_utc.astimezone(TARGET_TZ).strftime('%d/%m/%Y %H:%M:%S')

            messages.append({
                'token': token,
                'owner': message_data.get(b'owner', b'').decode('utf-8'),
                'created_at': created_at_str,
                'visits': message_data.get(b'visits', b'0').decode('utf-8'),
                'max_visits': message_data.get(b'max_visits', b'0').decode('utf-8'),
                'ttl': f'{ttl} segundos' if ttl > 0 else 'Não expira',
                'expiration_date': expiration_date_str
            })
        return messages

    def revoke_message(self, token: str):
        """Coordena a revogação de uma mensagem."""
        self.message_repo.delete(token)