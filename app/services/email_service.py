from flask import current_app
from flask_mail import Message
from app import mail
from app.services.audit_service import log_event

def send_access_email(recipient_email, access_url):
    """
    Envia um e-mail com o link de acesso seguro usando Flask-Mail.

    Args:
        recipient_email (str): O e-mail do destinatário.
        access_url (str): A URL de acesso a ser enviada no corpo do e-mail.
    """
    try:
        app = current_app._get_current_object()
        msg = Message(
            subject="[SIGILO] Seu Link de Acesso Seguro",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = f"""Olá,\n\nUm link seguro foi gerado para você no sistema SIGILO do TJMG.\n\nAcesse através do link: {access_url}\n\nLembre-se que o link pode ter um prazo de validade ou um número limitado de acessos.\n\n--\nTribunal de Justiça de Minas Gerais"""
        
        mail.send(msg)
        log_event('email_sent_success', details={'recipient': recipient_email})
    except Exception as e:
        log_event('email_sent_failure', details={'recipient': recipient_email, 'error': str(e)})
        # Loga o erro mas não impede a execução do resto da aplicação
        current_app.logger.error(f"Falha ao enviar e-mail para {recipient_email}: {e}")
