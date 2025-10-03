import logging
from flask import request, session

# Obtém o logger configurado
audit_logger = logging.getLogger('audit')

def log_event(event_type, details=None):
    """
    Registra um evento de auditoria.

    Args:
        event_type (str): O tipo de evento (ex: 'login_success').
        details (dict, optional): Um dicionário com detalhes extras sobre o evento.
    """
    extra_info = {
        'event_type': event_type,
        'details': details or {}
    }
    audit_logger.info(f"Evento de auditoria: {event_type}", extra=extra_info)
