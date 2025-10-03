import logging
import json
from flask import request, session

class JSONFormatter(logging.Formatter):
    """Formata registros de log como uma string JSON."""
    def format(self, record):
        log_object = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            # Informações do contexto da requisição
            'ip': request.remote_addr if request else None,
            'url': request.url if request else None,
            'method': request.method if request else None,
            # Informações de auditoria customizadas
            'event_type': getattr(record, 'event_type', 'generic'),
            'username': getattr(record, 'username', session.get('user', {}).get('username') if session else None),
            'details': getattr(record, 'details', {})
        }
        return json.dumps(log_object)

def setup_logging():
    """Configura o logger de auditoria para usar o formatador JSON."""
    # Desativa o logger padrão do Flask para não duplicar logs de requisição
    logging.getLogger('werkzeug').disabled = True

    # Configura o logger de auditoria
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    # Limpa handlers existentes para evitar duplicação
    if audit_logger.hasHandlers():
        audit_logger.handlers.clear()
        
    audit_logger.addHandler(handler)
    audit_logger.propagate = False # Evita que o log suba para o logger root
