"""Modelo de Notificação"""
from datetime import datetime
from extensions import db


class Notificacao(db.Model):
    """Modelo de notificação do sistema"""
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item_checklist.id'))
    tipo = db.Column(db.String(50), nullable=False)  # 'nova_nc', 'nc_atualizada', 'prazo_proximo'
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte notificação para dicionário"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'lida': self.lida,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'item_id': self.item_id
        }
    
    def __repr__(self):
        return f'<Notificacao {self.id} - {self.titulo}>'
