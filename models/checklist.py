"""Modelo de Checklist"""
from datetime import datetime
from extensions import db


class Checklist(db.Model):
    """Checklist de auditoria baseado em um template"""
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template_checklist.id'), nullable=False)
    projeto = db.Column(db.String(200), nullable=False)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Em Andamento')
    
    # Relacionamentos
    itens = db.relationship('ItemChecklist', backref='checklist', lazy=True, 
                           cascade='all, delete-orphan')

    def calcular_aderencia(self):
        """Calcula a porcentagem de aderência (itens conformes + NCs resolvidas)
        Ignora itens marcados como N/A no cálculo"""
        if not self.itens:
            return 0
        
        # Filtrar apenas itens aplicáveis (não N/A)
        itens_aplicaveis = [item for item in self.itens if item.resultado != 'N/A']
        
        if not itens_aplicaveis:
            return 0
        
        total_itens_aplicaveis = len(itens_aplicaveis)
        # Contar itens conformes + NCs que foram resolvidas
        itens_conformes = sum(1 for item in itens_aplicaveis 
                            if item.resultado == 'Conforme' 
                            or (item.resultado == 'Não Conforme' and item.status_nc == 'Resolvida'))
        
        return round((itens_conformes / total_itens_aplicaveis) * 100, 2)
    
    def contar_ncs_por_classificacao(self):
        """Conta não conformidades por classificação"""
        ncs = [item for item in self.itens if item.resultado == 'Não Conforme']
        
        return {
            'leve': sum(1 for nc in ncs if nc.classificacao_nc == 'L'),
            'moderada': sum(1 for nc in ncs if nc.classificacao_nc == 'M'),
            'grave': sum(1 for nc in ncs if nc.classificacao_nc == 'G'),
            'total': len(ncs)
        }
    
    def __repr__(self):
        return f'<Checklist {self.id} - {self.projeto}>'
