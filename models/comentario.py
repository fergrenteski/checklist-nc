"""Modelo de Comentário"""
from datetime import datetime
from extensions import db


class Comentario(db.Model):
    """Comentários na NC entre responsável, auditor e superior"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item_checklist.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para solicitações de aprovação
    tipo_solicitacao = db.Column(db.String(50))  # 'novo_prazo', 'fechar_nc', 'resolver_nc', None
    nova_data_proposta = db.Column(db.DateTime)
    motivo_fechamento_proposto = db.Column(db.Text)
    status_aprovacao = db.Column(db.String(20))  # 'pendente', 'aprovado', 'rejeitado', 'cancelado', None
    aprovado_por_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data_aprovacao = db.Column(db.DateTime)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='comentarios')
    aprovador = db.relationship('Usuario', foreign_keys=[aprovado_por_id])
    
    def __repr__(self):
        return f'<Comentario {self.id} - Item {self.item_id}>'
