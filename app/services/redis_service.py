from flask import current_app
import uuid
import time
import datetime
from zoneinfo import ZoneInfo
from app.services.crypto_service import CryptoService

# Define o fuso horário alvo
TARGET_TZ = ZoneInfo("America/Sao_Paulo")

class RedisService:
    """Service para interagir com o banco de dados Redis."""
    def __init__(self):
        """
        Inicializa o serviço Redis e o serviço de criptografia.
        """
        self.redis = current_app.redis
        self.crypto_service = CryptoService()

    def create_message(self, content, expires_in, max_visits, owner):
        """
        Cria uma mensagem criptografada no Redis.
        """
        token = str(uuid.uuid4())
        encrypted_content = self.crypto_service.encrypt(content)
        
        pipe = self.redis.pipeline()
        message_key = f"message:{token}"
        
        message_data = {
            b'content': encrypted_content,
            b'max_visits': int(max_visits),
            b'visits': 0,
            b'owner': owner,
            b'created_at': int(time.time())
        }
        
        pipe.hset(message_key, mapping=message_data)
        
        if int(expires_in) > 0:
            pipe.expire(message_key, int(expires_in))
            
        pipe.execute()
        return token

    def get_message(self, token):
        """
        Recupera e descriptografa uma mensagem, tratando da expiração e limites de visita.
        """
        message_key = f"message:{token}"

        if not self.redis.exists(message_key):
            return None, "Mensagem não encontrada ou expirada."

        max_visits = int(self.redis.hget(message_key, b'max_visits') or 0)
        current_visits = self.redis.hincrby(message_key, 'visits', 1)

        if max_visits > 0 and current_visits > max_visits:
            self.redis.delete(message_key)
            return None, "Mensagem expirada (limite de visualizações atingido)."

        content_bytes = self.redis.hget(message_key, b'content')
        if not content_bytes:
            return None, "Conteúdo da mensagem não encontrado."

        decrypted_content = self.crypto_service.decrypt(content_bytes)

        if max_visits > 0 and current_visits == max_visits:
            self.redis.delete(message_key)

        return decrypted_content, None

    def create_short_link(self, long_url, expires_in, owner):
        """
        Cria um link curto no Redis.
        """
        short_code = str(uuid.uuid4())[:6]
        link_key = f"link:{short_code}"
        self.redis.set(link_key, long_url)
        
        if int(expires_in) > 0:
            self.redis.expire(link_key, int(expires_in))
            
        self.redis.hset(f"link_meta:{short_code}", "owner", owner)
        return short_code

    def get_long_url(self, short_code):
        """
        Recupera uma URL longa a partir de um código curto.
        """
        link_key = f"link:{short_code}"
        return self.redis.get(link_key)

    def get_all_messages(self):
        """
        Busca metadados de todas as mensagens ativas.
        """
        messages = []
        for key in self.redis.scan_iter("message:*"):
            message_data = self.redis.hgetall(key)
            ttl = self.redis.ttl(key)

            created_at_ts = int(message_data.get(b'created_at', 0))
            created_at_utc = datetime.datetime.fromtimestamp(created_at_ts, tz=datetime.timezone.utc)
            created_at_str = created_at_utc.astimezone(TARGET_TZ).strftime('%d/%m/%Y %H:%M:%S')

            expiration_date_str = "Nunca"
            if ttl > 0:
                expiration_ts = time.time() + ttl
                expiration_utc = datetime.datetime.fromtimestamp(expiration_ts, tz=datetime.timezone.utc)
                expiration_date_str = expiration_utc.astimezone(TARGET_TZ).strftime('%d/%m/%Y %H:%M:%S')

            messages.append({
                'token': key.decode('utf-8').split(':')[1],
                'owner': message_data.get(b'owner', b'').decode('utf-8'),
                'created_at': created_at_str,
                'visits': message_data.get(b'visits', b'0').decode('utf-8'),
                'max_visits': message_data.get(b'max_visits', b'0').decode('utf-8'),
                'ttl': f'{ttl} segundos' if ttl > 0 else 'Não expira',
                'expiration_date': expiration_date_str
            })
        return messages

    def get_all_links(self):
        """
        Busca todas as URLs encurtadas ativas.
        """
        links = []
        for key in self.redis.scan_iter("link:*"):
            short_code = key.decode('utf-8').split(':')[1]
            long_url = self.redis.get(key).decode('utf-8')
            owner_data = self.redis.hgetall(f"link_meta:{short_code}")
            ttl = self.redis.ttl(key)

            expiration_date_str = "Nunca"
            if ttl > 0:
                expiration_ts = time.time() + ttl
                expiration_utc = datetime.datetime.fromtimestamp(expiration_ts, tz=datetime.timezone.utc)
                expiration_date_str = expiration_utc.astimezone(TARGET_TZ).strftime('%d/%m/%Y %H:%M:%S')

            links.append({
                'short_code': short_code,
                'long_url': long_url,
                'owner': owner_data.get(b'owner', b'').decode('utf-8'),
                'ttl': f'{ttl} segundos' if ttl > 0 else 'Não expira',
                'expiration_date': expiration_date_str
            })
        return links

    def revoke_item(self, item_type, item_id):
        """
        Revoga (apaga) um item do Redis.
        """
        if item_type == 'message':
            self.redis.delete(f"message:{item_id}")
        elif item_type == 'link':
            self.redis.delete(f"link:{item_id}", f"link_meta:{item_id}")
        else:
            raise ValueError("Tipo de item inválido para revogação")