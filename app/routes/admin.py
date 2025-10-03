from flask import Blueprint, render_template, redirect, url_for, flash
from app.decorators import admin_required
from app.dependencies import get_message_service, get_link_service
from app.services.audit_service import log_event

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@admin_required
def index():
    """Renderiza o painel de administração com a lista de mensagens e links ativos."""
    message_service = get_message_service()
    link_service = get_link_service()
    all_messages = message_service.get_all_formatted_messages()
    all_links = link_service.get_all_formatted_links()
    return render_template('admin/index.html', messages=all_messages, links=all_links)


@bp.route('/revoke/<item_type>/<item_id>', methods=['POST'])
@admin_required
def revoke(item_type, item_id):
    """
    Revoga (apaga) uma mensagem ou link.

    Args:
        item_type (str): O tipo de item a ser revogado ('message' ou 'link').
        item_id (str): O ID (token ou short_code) do item.
    """
    try:
        if item_type == 'message':
            service = get_message_service()
            service.revoke_message(item_id)
        elif item_type == 'link':
            service = get_link_service()
            service.revoke_link(item_id)
        else:
            raise ValueError("Tipo de item inválido")

        log_event('item_revoked', details={'item_type': item_type, 'item_id': item_id})
        flash(f'{item_type.capitalize()} revogado com sucesso!', 'green lighten-2')
    except ValueError as e:
        log_event('item_revoke_failed', details={'item_type': item_type, 'item_id': item_id, 'error': str(e)})
        flash(f'Erro ao revogar item: {e}', 'red lighten-2')
    
    return redirect(url_for('admin.index'))