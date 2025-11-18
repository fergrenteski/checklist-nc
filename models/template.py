"""Modelos de Template de Checklist"""
from datetime import datetime
from extensions import db


class TemplateChecklist(db.Model):
    """Template pré-definido de checklist"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    itens_template = db.relationship('ItemTemplate', backref='template', lazy=True, 
                                    cascade='all, delete-orphan')
    checklists = db.relationship('Checklist', backref='template', lazy=True)
    
    def __repr__(self):
        return f'<TemplateChecklist {self.nome}>'


class ItemTemplate(db.Model):
    """Itens pré-definidos do template"""
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template_checklist.id'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    secao = db.Column(db.String(100), nullable=False)
    item_verificacao = db.Column(db.String(300), nullable=False)
    criterio_conformidade = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<ItemTemplate {self.ordem} - {self.item_verificacao[:30]}>'
