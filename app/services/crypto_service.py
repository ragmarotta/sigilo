from flask import current_app
from cryptography.fernet import Fernet

class CryptoService:
    """Encapsula a lógica de criptografia e descriptografia da aplicação."""
    def __init__(self):
        """
        Inicializa o serviço de criptografia, carregando a chave Fernet.
        Levanta um erro se a chave não estiver configurada.
        """
        fernet_key = current_app.config.get('FERNET_KEY')
        if not fernet_key:
            raise ValueError("FERNET_KEY não configurada na aplicação.")
        self.fernet = Fernet(fernet_key.encode('utf-8'))

    def encrypt(self, data_string: str) -> bytes:
        """
        Criptografa uma string.

        Args:
            data_string (str): A string de texto puro a ser criptografada.

        Returns:
            bytes: Os dados criptografados.
        """
        return self.fernet.encrypt(data_string.encode('utf-8'))

    def decrypt(self, encrypted_bytes: bytes) -> str:
        """
        Descriptografa uma sequência de bytes.

        Args:
            encrypted_bytes (bytes): Os dados criptografados.

        Returns:
            str: A string de texto puro descriptografada.
        """
        return self.fernet.decrypt(encrypted_bytes).decode('utf-8')
