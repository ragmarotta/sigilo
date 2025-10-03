from flask import current_app
import uuid
from cryptography.fernet import Fernet
import time


class RedisService:
    """Service para interagir com o banco de dados Redis."""
    def __init__(self):
        """
        Inicializa o serviço, o cliente Redis e a instância de criptografia Fernet.
        """
        self.redis = current_app.redis
        fernet_key = current_app.config.get('FERNET_KEY')
        if not fernet_key:
            raise ValueError("FERNET_KEY não configurada na aplicação.")
        self.fernet = Fernet(fernet_key.encode('utf-8'))

    def create_message(self, content, expires_in, max_visits, owner):
        """
        Cria uma mensagem criptografada no Redis.

        Args:
            content (str): O conteúdo da mensagem a ser criptografada.
            expires_in (int): O tempo de expiração em segundos. 0 para não expirar.
            max_visits (int): O número máximo de visualizações permitidas.
            owner (str): O nome de usuário do criador da mensagem.

        Returns:
            str: O token único gerado para esta mensagem.
        """
        token = str(uuid.uuid4())
        encrypted_content = self.fernet.encrypt(content.encode('utf-8'))
        
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

        Args:
            token (str): O token da mensagem a ser recuperada.

        Returns:
            tuple: Uma tupla contendo (conteúdo_descriptografado, None) em caso de sucesso,
                   ou (None, mensagem_de_erro) em caso de falha.
        """
        message_key = f"message:{token}"
        
        pipe = self.redis.pipeline()
        pipe.hgetall(message_key)
        pipe.hincrby(message_key, 'visits', 1)
        results = pipe.execute()
        
        message_data = results[0]
        
        if not message_data:
            return None, "Mensagem não encontrada ou expirada."

        visits = int(message_data.get(b'visits', 0))
        max_visits = int(message_data.get(b'max_visits', 0))

        if max_visits > 0 and visits > max_visits:
            self.redis.delete(message_key) # Clean up
            return None, "Mensagem expirada (limite de visualizações atingido)."
            
        decrypted_content = self.fernet.decrypt(message_data[b'content']).decode('utf-8')
        
        # If this was the last allowed visit, delete the message
        if max_visits > 0 and visits == max_visits:
            self.redis.delete(message_key)

        return decrypted_content, None

    def create_short_link(self, long_url, expires_in, owner):
        """
        Cria um link curto no Redis.

        Args:
            long_url (str): A URL original a ser encurtada.
            expires_in (int): O tempo de expiração em segundos. 0 para não expirar.
            owner (str): O nome de usuário do criador do link.

        Returns:
            str: O código curto gerado para a URL.
        """
        # Simple short code generation
        short_code = str(uuid.uuid4())[:6]
        
        link_key = f"link:{short_code}"
        self.redis.set(link_key, long_url)
        
        if int(expires_in) > 0:
            self.redis.expire(link_key, int(expires_in))
            
        # Log the owner (optional)
        self.redis.hset(f"link_meta:{short_code}", "owner", owner)

        return short_code

    def get_long_url(self, short_code):
        """
        Recupera uma URL longa a partir de um código curto.

        Args:
            short_code (str): O código curto a ser resolvido.

        Returns:
            bytes: A URL longa em bytes, ou None se não for encontrada.
        """
        link_key = f"link:{short_code}"
        return self.redis.get(link_key)

    def get_all_messages(self):
        """
        Busca metadados de todas as mensagens ativas usando SCAN para não bloquear o servidor.

        Returns:
            list: Uma lista de dicionários, cada um representando uma mensagem.
        """
        messages = []
        for key in self.redis.scan_iter("message:*"):
            message_data = self.redis.hgetall(key)
            ttl = self.redis.ttl(key)
            messages.append({
                'token': key.decode('utf-8').split(':')[1],
                'owner': message_data.get(b'owner', b'').decode('utf-8'),
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(message_data.get(b'created_at', 0)))),
                'visits': message_data.get(b'visits', b'0').decode('utf-8'),
                'max_visits': message_data.get(b'max_visits', b'0').decode('utf-8'),
                'ttl': f'{ttl} segundos' if ttl > 0 else 'Não expira'
            })
        return messages

    def get_all_links(self):
        """
        Busca todas as URLs encurtadas ativas usando SCAN.

        Returns:
            list: Uma lista de dicionários, cada um representando um link.
        """
        links = []
        for key in self.redis.scan_iter("link:*"):
            short_code = key.decode('utf-8').split(':')[1]
            long_url = self.redis.get(key).decode('utf-8')
            owner_data = self.redis.hgetall(f"link_meta:{short_code}")
            ttl = self.redis.ttl(key)
            links.append({
                'short_code': short_code,
                'long_url': long_url,
                'owner': owner_data.get(b'owner', b'').decode('utf-8'),
                'ttl': f'{ttl} segundos' if ttl > 0 else 'Não expira'
            })
        return links

    def revoke_item(self, item_type, item_id):
        """
        Revoga (apaga) um item do Redis.

        Args:
            item_type (str): O tipo de item ('message' ou 'link').
            item_id (str): O identificador (token ou short_code) do item.
        """
        if item_type == 'message':
            self.redis.delete(f"message:{item_id}")
        elif item_type == 'link':
            self.redis.delete(f"link:{item_id}", f"link_meta:{item_id}")
        else:
            raise ValueError("Tipo de item inválido para revogação")
