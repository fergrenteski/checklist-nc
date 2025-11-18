"""Eventos WebSocket do sistema"""
from flask_socketio import emit, join_room
from flask_login import current_user
from extensions import socketio
from models import Notificacao


@socketio.on('connect')
def handle_connect():
    """Evento de conexão do usuário"""
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('connected', {'message': 'Conectado ao sistema de notificações'})


@socketio.on('disconnect')
def handle_disconnect():
    """Evento de desconexão do usuário"""
    if current_user.is_authenticated:
        print(f'Usuário {current_user.nome} desconectado')


@socketio.on('marcar_lida')
def handle_marcar_lida(data):
    """Marca notificação como lida via WebSocket"""
    if current_user.is_authenticated:
        from extensions import db
        notif_id = data.get('notificacao_id')
        notificacao = Notificacao.query.get(notif_id)
        
        if notificacao and notificacao.usuario_id == current_user.id:
            notificacao.lida = True
            db.session.commit()
