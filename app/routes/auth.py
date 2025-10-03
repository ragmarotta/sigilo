from flask import Blueprint, url_for, redirect, session, request, current_app, render_template
from app.services.keycloak_service import KeycloakService
from app.services.audit_service import log_event

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login')
def login():
    """Redireciona o usuário para a página de login do Keycloak ou do mock."""
    keycloak = KeycloakService()
    redirect_uri = url_for('auth.callback', _external=True)
    auth_url = keycloak.get_auth_url(redirect_uri=redirect_uri)
    return redirect(auth_url)


@bp.route('/callback')
def callback():
    """
    Rota de callback após a autenticação no Keycloak.
    Troca o código de autorização por um token de acesso e armazena as informações do usuário na sessão.
    """
    keycloak = KeycloakService()
    code = request.args.get('code')
    redirect_uri = url_for('auth.callback', _external=True)
    
    try:
        tokens = keycloak.get_token(code=code, redirect_uri=redirect_uri)
        user_info = keycloak.get_user_info(tokens['access_token'])
        
        session['user'] = {
            'name': user_info.get('name'),
            'email': user_info.get('email'),
            'username': user_info.get('preferred_username'),
            'roles': user_info.get('realm_access', {}).get('roles', [])
        }
        session['access_token'] = tokens['access_token']
        session['refresh_token'] = tokens['refresh_token']
        
        log_event('login_success', details={'username': user_info.get('preferred_username')})
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f"Authentication failed: {e}")
        log_event('login_failure', details={'error': str(e)})
        return "Authentication failed.", 400


@bp.route('/logout')
def logout():
    """Realiza o logout do usuário no Keycloak e limpa a sessão local."""
    keycloak = KeycloakService()
    refresh_token = session.get('refresh_token')
    if refresh_token:
        try:
            keycloak.logout(refresh_token)
            log_event('logout_success')
        except Exception as e:
            current_app.logger.error(f"Keycloak logout failed: {e}")
            log_event('logout_failure', details={'error': str(e)})
    
    # Clear the local session regardless
    session.clear()
    
    # Redirect to a local "logged out" page or home page
    return redirect(url_for('main.index'))


@bp.route('/mock_login')
def mock_login():
    """Renderiza a página de login falso se o modo mock estiver ativado."""
    if current_app.config.get('KEYCLOAK_ENABLED', True):
        return "Acesso negado. O mock de login está desabilitado.", 403
    return render_template('auth/mock_login.html')


@bp.route('/mock_login/<role>')
def mock_login_as(role):
    """
    Simula o login de um usuário com uma role específica (user ou admin).
    
    Args:
        role (str): A role a ser simulada ('user' ou 'admin').
    """
    if current_app.config.get('KEYCLOAK_ENABLED', True):
        return "Acesso negado. O mock de login está desabilitado.", 403

    session.clear()
    user_info = {
        'name': f'Mock {role.capitalize()}',
        'email': f'{role}@mock.local',
        'username': f'mock{role}',
        'roles': ['offline_access', 'uma_role']
    }
    if role == 'admin':
        user_info['roles'].append('admin')
    
    session['user'] = user_info
    session['access_token'] = 'mock_access_token'
    session['refresh_token'] = 'mock_refresh_token'
    
    log_event('login_success', details={'username': user_info['username'], 'mock': True})
    return redirect(url_for('main.index'))