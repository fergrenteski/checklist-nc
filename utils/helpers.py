"""Funções auxiliares do sistema"""
from extensions import db, socketio
from models.notificacao import Notificacao


def criar_notificacao(usuario_id, item_id, tipo, titulo, mensagem):
    """Cria uma notificação e envia via WebSocket"""
    notificacao = Notificacao(
        usuario_id=usuario_id,
        item_id=item_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem
    )
    db.session.add(notificacao)
    db.session.commit()
    
    # Envia notificação em tempo real via WebSocket
    socketio.emit('nova_notificacao', 
                  notificacao.to_dict(), 
                  room=f'user_{usuario_id}')
    
    return notificacao
