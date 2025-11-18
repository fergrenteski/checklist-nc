"""Modelo de Usuário"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class Usuario(UserMixin, db.Model):
    """Modelo de usuário do sistema"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    funcao = db.Column(db.String(100), nullable=False)
    superior_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    checklists_criados = db.relationship('Checklist', foreign_keys='Checklist.criador_id', 
                                        backref='criador', lazy=True)
    notificacoes = db.relationship('Notificacao', backref='usuario', lazy=True, 
                                   cascade='all, delete-orphan')
    superior = db.relationship('Usuario', remote_side=[id], backref='subordinados')
    
    def set_senha(self, senha):
        """Define a senha do usuário com hash"""
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def get_notificacoes_nao_lidas(self):
        """Retorna o número de notificações não lidas"""
        from models.notificacao import Notificacao
        return Notificacao.query.filter_by(usuario_id=self.id, lida=False).count()
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
