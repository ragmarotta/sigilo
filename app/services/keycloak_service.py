import requests
from flask import current_app, url_for, redirect


class KeycloakService:
    """Service para interagir com o Keycloak para autenticação OIDC."""
    def __init__(self):
        """Inicializa o serviço, carregando as configurações do Keycloak."""
        self.enabled = current_app.config.get('KEYCLOAK_ENABLED', True)
        if not self.enabled:
            return

        self.server_url = current_app.config['KEYCLOAK_SERVER_URL']
        self.realm = current_app.config['KEYCLOAK_REALM_NAME']
        self.client_id = current_app.config['KEYCLOAK_CLIENT_ID']
        self.client_secret = current_app.config['KEYCLOAK_CLIENT_SECRET_KEY']
        self.well_known_url = f"{self.server_url}/realms/{self.realm}/.well-known/openid-configuration"
        self._config = None

    @property
    def config(self):
        """Obtém a configuração OIDC do endpoint .well-known do Keycloak."""
        if not self.enabled:
            return {}
        if not self._config:
            self._config = requests.get(self.well_known_url).json()
        return self._config

    def get_auth_url(self, redirect_uri):
        """
        Monta a URL de autorização do Keycloak para o fluxo de login.

        Args:
            redirect_uri (str): A URI de callback para onde o Keycloak deve redirecionar.

        Returns:
            str: A URL completa para redirecionar o usuário.
        """
        if not self.enabled:
            return url_for('auth.mock_login')
            
        auth_endpoint = self.config['authorization_endpoint']
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'openid profile email',
        }
        req = requests.Request('GET', auth_endpoint, params=params)
        return req.prepare().url

    def get_token(self, code, redirect_uri):
        """
        Troca um código de autorização por um token de acesso.

        Args:
            code (str): O código de autorização recebido do Keycloak.
            redirect_uri (str): A URI de callback utilizada no passo anterior.

        Returns:
            dict: Um dicionário contendo o token de acesso, refresh token, etc.
        """
        if not self.enabled:
            return None

        token_endpoint = self.config['token_endpoint']
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
        }
        response = requests.post(token_endpoint, data=payload)
        response.raise_for_status()
        return response.json()

    def get_user_info(self, access_token):
        """
        Busca as informações do usuário a partir do token de acesso.

        Args:
            access_token (str): O token de acesso do usuário.

        Returns:
            dict: Um dicionário com as informações do perfil do usuário.
        """
        if not self.enabled:
            return None

        userinfo_endpoint = self.config['userinfo_endpoint']
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def logout(self, refresh_token):
        """
        Realiza o logout do usuário no Keycloak, invalidando o token.

        Args:
            refresh_token (str): O refresh token associado à sessão do usuário.
        """
        if not self.enabled:
            return None

        logout_endpoint = self.config['end_session_endpoint']
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
        }
        response = requests.post(logout_endpoint, data=payload)
        response.raise_for_status()
        return response
