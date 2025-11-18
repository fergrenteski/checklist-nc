"""Modelo de Item de Checklist"""
from datetime import datetime, timedelta
from extensions import db


class ItemChecklist(db.Model):
    """Item individual de um checklist (instância de um item do template)"""
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    item_template_id = db.Column(db.Integer, db.ForeignKey('item_template.id'), nullable=False)
    
    # Dados da auditoria
    resultado = db.Column(db.String(20))  # Conforme, Não Conforme, N/A
    observacao = db.Column(db.Text)
    
    # Dados da NC (se não conforme)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    classificacao_nc = db.Column(db.String(1))  # L, M, G
    acao_corretiva = db.Column(db.Text)
    prazo_resolucao = db.Column(db.DateTime)
    nova_data_resolucao = db.Column(db.DateTime)
    status_nc = db.Column(db.String(20), default='Pendente')
    escalado = db.Column(db.Boolean, default=False)
    escalado_para_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    escalado_aceito = db.Column(db.Boolean, default=False)  # Superior aceitou o escalamento
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_preenchimento = db.Column(db.DateTime)
    data_resolucao = db.Column(db.DateTime)
    motivo_fechamento = db.Column(db.Text)
    
    # Relacionamentos
    item_template = db.relationship('ItemTemplate', backref='instancias')
    responsavel = db.relationship('Usuario', foreign_keys=[responsavel_id], 
                                  backref='ncs_atribuidas')
    escalado_para = db.relationship('Usuario', foreign_keys=[escalado_para_id], 
                                    backref='ncs_escaladas')
    notificacoes = db.relationship('Notificacao', backref='item', lazy=True, 
                                   cascade='all, delete-orphan')
    comentarios = db.relationship('Comentario', backref='item', lazy=True, 
                                 cascade='all, delete-orphan', 
                                 order_by='Comentario.data_criacao')
    
    def get_prazo_limite(self):
        """Retorna a data limite para resolução"""
        if self.nova_data_resolucao:
            return self.nova_data_resolucao
        return self.prazo_resolucao
    
    def dias_restantes(self):
        """Calcula dias restantes até o prazo"""
        if self.status_nc != 'Resolvida':
            prazo_limite = self.get_prazo_limite()
            if prazo_limite:
                dias = (prazo_limite - datetime.utcnow()).days
                return dias
        return None
    
    def calcular_prazo_automatico(self):
        """Calcula prazo baseado na classificação: L=5 dias, M=3 dias, G=2 dias"""
        if not self.classificacao_nc or not self.data_preenchimento:
            return None
        
        dias = {'L': 5, 'M': 3, 'G': 2}
        prazo_dias = dias.get(self.classificacao_nc, 5)
        return self.data_preenchimento + timedelta(days=prazo_dias)
    
    def __repr__(self):
        return f'<ItemChecklist {self.id} - {self.resultado}>'
