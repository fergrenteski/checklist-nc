"""Rotas de gerenciamento de notificações"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Notificacao

notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')


@notificacoes_bp.route('/')
@login_required
def listar():
    """Lista todas as notificações do usuário"""
    todas_notificacoes = Notificacao.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Notificacao.data_criacao.desc()).all()
    
    return render_template('notificacoes.html', notificacoes=todas_notificacoes)


@notificacoes_bp.route('/<int:notif_id>/marcar-lida', methods=['POST'])
@login_required
def marcar_lida(notif_id):
    """Marca uma notificação como lida"""
    notificacao = Notificacao.query.get_or_404(notif_id)
    
    if notificacao.usuario_id == current_user.id:
        notificacao.lida = True
        db.session.commit()
    
    return jsonify({'success': True})


@notificacoes_bp.route('/marcar-todas-lidas', methods=['POST'])
@login_required
def marcar_todas_lidas():
    """Marca todas as notificações como lidas"""
    Notificacao.query.filter_by(
        usuario_id=current_user.id,
        lida=False
    ).update({'lida': True})
    
    db.session.commit()
    
    return jsonify({'success': True})


@notificacoes_bp.route('/count')
@login_required
def contar():
    """API: Retorna o número de notificações não lidas"""
    count = Notificacao.query.filter_by(
        usuario_id=current_user.id,
        lida=False
    ).count()
    
    return jsonify({'count': count})
