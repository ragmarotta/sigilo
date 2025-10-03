import uuid
import time
import datetime
from zoneinfo import ZoneInfo
from app.repositories.interfaces.link_repository_interface import LinkRepositoryInterface

TARGET_TZ = ZoneInfo("America/Sao_Paulo")

class LinkService:
    """Camada de serviço com a lógica de negócio para links."""

    def __init__(self, link_repo: LinkRepositoryInterface):
        self.link_repo = link_repo

    def create_short_link(self, long_url: str, expires_in: int, owner: str) -> str:
        """Coordena a criação de um novo link encurtado."""
        short_code = str(uuid.uuid4())[:6]
        self.link_repo.save(short_code, long_url, owner, int(expires_in))
        return short_code

    def find_long_url(self, short_code: str) -> bytes:
        """Busca uma URL longa a partir de um código curto."""
        return self.link_repo.find_by_id(short_code)

    def get_all_formatted_links(self) -> list:
        """Busca todos os links e os formata para exibição."""
        links = []
        for key in self.link_repo.get_all():
            short_code = key.decode('utf-8').split(':')[1]
            long_url = self.link_repo.find_by_id(short_code).decode('utf-8')
            owner_data = self.link_repo.get_meta(short_code)
            ttl = self.link_repo.get_ttl(key)

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

    def revoke_link(self, short_code: str):
        """Coordena a revogação de um link."""
        self.link_repo.delete(short_code)