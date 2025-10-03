from flask import Blueprint, render_template, request, url_for, flash, redirect, session, current_app
from app.services.redis_service import RedisService
from app.services.email_service import send_access_email
from app.services.audit_service import log_event

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Renderiza a página principal da aplicação."""
    return render_template('index.html')


@bp.route('/favicon.ico')
def favicon():
    """Retorna uma resposta vazia para o favicon para evitar erros no log."""
    return '', 204


@bp.route('/create/message', methods=['POST'])
def create_message():
    """
    Cria uma mensagem segura a partir dos dados do formulário.
    Requer que o usuário esteja logado.
    """
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    content = request.form.get('content')
    expires_in = request.form.get('expires_in')
    max_visits = request.form.get('max_visits')
    recipient_email = request.form.get('recipient_email')
    
    redis_service = RedisService()
    token = redis_service.create_message(
        content=content,
        expires_in=expires_in,
        max_visits=max_visits,
        owner=session['user']['username']
    )
    
    access_url = url_for('main.view_message', token=token, _external=True)
    
    if recipient_email:
        send_access_email(recipient_email, access_url)

    log_event('message_created', details={'token': token, 'expires_in': expires_in, 'max_visits': max_visits})
    return render_template('message_created.html', access_url=access_url)


@bp.route('/message/<token>')
def view_message(token):
    """
    Exibe uma mensagem segura a partir de um token de acesso.
    
    Args:
        token (str): O token único para acessar a mensagem.
    """
    redis_service = RedisService()
    content, error = redis_service.get_message(token)
    
    if error:
        log_event('message_access_failed', details={'token': token, 'error': error})
        return render_template('message_error.html', error=error)
        
    log_event('message_accessed', details={'token': token})
    return render_template('view_message.html', content=content)


@bp.route('/create/link', methods=['POST'])
def create_link():
    """
    Cria um link encurtado a partir dos dados do formulário.
    Requer que o usuário esteja logado.
    """
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    long_url = request.form.get('long_url')
    expires_in = request.form.get('expires_in_link')

    redis_service = RedisService()
    short_code = redis_service.create_short_link(
        long_url=long_url,
        expires_in=expires_in,
        owner=session['user']['username']
    )
    
    access_url = url_for('main.redirect_to_url', short_code=short_code, _external=True)
    
    log_event('link_created', details={'short_code': short_code, 'long_url': long_url})
    return render_template('message_created.html', access_url=access_url)


@bp.route('/<short_code>')
def redirect_to_url(short_code):
    """
    Redireciona um código curto para a URL original correspondente.

    Args:
        short_code (str): O código curto a ser resolvido.
    """
    redis_service = RedisService()
    long_url = redis_service.get_long_url(short_code)
    
    if long_url:
        log_event('link_redirected', details={'short_code': short_code, 'long_url': long_url.decode('utf-8')})
        return redirect(long_url.decode('utf-8'))
    else:
        log_event('link_redirect_failed', details={'short_code': short_code})
        return render_template('404.html'), 404