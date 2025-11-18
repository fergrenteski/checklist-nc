"""Inicialização do banco de dados e dados padrão"""
from extensions import db
from models import Usuario, TemplateChecklist, ItemTemplate


def init_db(app):
    """Inicializa o banco de dados e cria dados padrão"""
    with app.app_context():
        db.create_all()
        
        # Criar usuários padrão se não existirem
        if Usuario.query.count() == 0:
            _criar_usuarios_padrao()
        
        # Criar template GRI se não existir
        if not TemplateChecklist.query.filter_by(nome="Gestão de Riscos – GRI / MPS.BR").first():
            _criar_template_gri()
        
        print("Banco de dados criado com sucesso!")


def _criar_usuarios_padrao():
    """Cria usuários padrão do sistema"""
    print("Criando usuários padrão...")
    
    # 1. Luiz - Auditor (sem superior)
    luiz = Usuario(
        nome="Luiz",
        email="luiz@empresa.com",
        funcao="Auditor",
        superior_id=None,
        ativo=True
    )
    luiz.set_senha("123456")
    db.session.add(luiz)
    db.session.flush()
    
    # 2. Ana - Gerente (sem superior, é chefe)
    ana = Usuario(
        nome="Ana",
        email="ana@empresa.com",
        funcao="Gerente",
        superior_id=None,
        ativo=True
    )
    ana.set_senha("123456")
    db.session.add(ana)
    db.session.flush()
    
    # 3. João - Gestor de Risco (superior é Ana)
    joao = Usuario(
        nome="João",
        email="joao@empresa.com",
        funcao="Gestor de Risco",
        superior_id=ana.id,
        ativo=True
    )
    joao.set_senha("123456")
    db.session.add(joao)
    
    db.session.commit()
    print(f"✅ Usuários criados:")
    print(f"   - Luiz (Auditor) - Email: luiz@empresa.com - Senha: 123456")
    print(f"   - Ana (Gerente) - Email: ana@empresa.com - Senha: 123456")
    print(f"   - João (Gestor de Risco, Superior: Ana) - Email: joao@empresa.com - Senha: 123456")


def _criar_template_gri():
    """Cria template de Gestão de Riscos (GRI / MPS.BR)"""
    print("Criando template de checklist de Gestão de Riscos (GRI / MPS.BR)...")
    
    template_gri = TemplateChecklist(
        nome="Gestão de Riscos – GRI / MPS.BR",
        descricao="Checklist para verificação do documento de Plano de Gestão de Riscos baseado em GRI / MPS.BR"
    )
    db.session.add(template_gri)
    db.session.flush()
    
    itens_gri = [
        # Seção 1 – Identificação do Projeto
        {"ordem": 1, "secao": "Identificação do Projeto", "item": "Dados do projeto preenchidos", "criterio": "Nome do projeto, responsável, gestor de riscos, data de elaboração e versão do documento estão informados"},
        
        # Seção 2 – Contexto e Escopo de Riscos
        {"ordem": 2, "secao": "Contexto e Escopo", "item": "Objetivos do projeto registrados", "criterio": "Objetivos principais do projeto estão descritos de forma clara"},
        {"ordem": 3, "secao": "Contexto e Escopo", "item": "Escopo da gestão de riscos definido", "criterio": "Áreas, processos e entregas cobertos pelo plano de riscos estão descritos"},
        {"ordem": 4, "secao": "Contexto e Escopo", "item": "Stakeholders relevantes identificados", "criterio": "Partes interessadas críticas para gestão de riscos estão listadas"},
        {"ordem": 5, "secao": "Contexto e Escopo", "item": "Critérios de aceitabilidade definidos", "criterio": "Critérios de aceitação de riscos (ex.: matriz P x I, limites) estão documentados"},
        
        # Seção 3 – Registro de Riscos
        {"ordem": 6, "secao": "Registro de Riscos", "item": "Risk Register estruturado", "criterio": "Existe tabela de riscos com ID, descrição, causa, evento, consequência, probabilidade, impacto e nível"},
        {"ordem": 7, "secao": "Registro de Riscos", "item": "Categorias de risco definidas", "criterio": "Cada risco está classificado em categorias (técnico, prazo, custo, qualidade, etc.)"},
        {"ordem": 8, "secao": "Registro de Riscos", "item": "Responsáveis pelos riscos definidos", "criterio": "Cada risco relevante possui um responsável designado"},
        
        # Seção 4 – Análise e Priorização
        {"ordem": 9, "secao": "Análise e Priorização", "item": "Escalas de probabilidade e impacto documentadas", "criterio": "Escalas numéricas ou qualitativas de probabilidade e impacto estão definidas"},
        {"ordem": 10, "secao": "Análise e Priorização", "item": "Critérios de priorização estabelecidos", "criterio": "Faixas de prioridade (baixa, média, alta, crítica) foram estabelecidas com base em P x I"},
        {"ordem": 11, "secao": "Análise e Priorização", "item": "Riscos críticos identificados", "criterio": "Existe lista dos riscos mais críticos (Top N) para foco de gestão"},
        
        # Seção 5 – Planejamento das Respostas
        {"ordem": 12, "secao": "Planejamento de Respostas", "item": "Estratégias de resposta definidas", "criterio": "Para os riscos relevantes, a estratégia (evitar, mitigar, transferir, aceitar etc.) está definida"},
        {"ordem": 13, "secao": "Planejamento de Respostas", "item": "Ações de resposta descritas", "criterio": "Ações específicas para tratar os riscos estão descritas"},
        {"ordem": 14, "secao": "Planejamento de Respostas", "item": "Responsáveis e prazos das ações definidos", "criterio": "Cada ação possui responsável, prazo e, quando aplicável, recursos necessários"},
        
        # Seção 6 – Monitoramento e Controle
        {"ordem": 15, "secao": "Monitoramento e Controle", "item": "Mecanismos de monitoramento definidos", "criterio": "Reuniões, frequência e responsáveis pela atualização dos riscos estão documentados"},
        {"ordem": 16, "secao": "Monitoramento e Controle", "item": "Indicadores de riscos definidos", "criterio": "Existem indicadores para acompanhar o desempenho da gestão de riscos"},
        {"ordem": 17, "secao": "Monitoramento e Controle", "item": "Tratamento de riscos materializados descrito", "criterio": "Existe processo definido para registrar e tratar riscos que se materializam (issues)"},
        {"ordem": 18, "secao": "Monitoramento e Controle", "item": "Processo de escalonamento definido", "criterio": "Critérios e fluxo de escalonamento de riscos estão descritos"},
        
        # Seção 7 – Comunicação
        {"ordem": 19, "secao": "Comunicação", "item": "Plano de comunicação de riscos estabelecido", "criterio": "Quem recebe quais informações, em qual formato e frequência está definido"},
        {"ordem": 20, "secao": "Comunicação", "item": "Repositório de riscos definido", "criterio": "Local de armazenamento e acesso ao registro de riscos está documentado"},
        {"ordem": 21, "secao": "Comunicação", "item": "Rastreabilidade e histórico definidos", "criterio": "Há registro de histórico de decisões, revisões e ações de riscos"},
        
        # Seção 8 – Revisão e Melhoria Contínua
        {"ordem": 22, "secao": "Revisão e Melhoria", "item": "Periodicidade de revisão do plano definida", "criterio": "Frequência e gatilhos para revisão do plano de riscos estão documentados"},
        {"ordem": 23, "secao": "Revisão e Melhoria", "item": "Lições aprendidas sobre riscos registradas", "criterio": "Existe seção ou mecanismo para registrar lições aprendidas de riscos"},
        {"ordem": 24, "secao": "Revisão e Melhoria", "item": "Atualização de políticas e procedimentos prevista", "criterio": "Há indicação de como as lições aprendidas serão incorporadas em políticas, procedimentos e checklists"},
        
        # Seção 9 – Aprovações
        {"ordem": 25, "secao": "Aprovações", "item": "Aprovação do gestor de riscos registrada", "criterio": "Campo para assinatura/nome/data do responsável pela gestão de riscos está preenchido"},
        {"ordem": 26, "secao": "Aprovações", "item": "Aprovação da gerência/patrocinador registrada", "criterio": "Campo para assinatura/nome/data do gerente/patrocinador está preenchido"},
    ]
    
    for item_data in itens_gri:
        item = ItemTemplate(
            template_id=template_gri.id,
            ordem=item_data["ordem"],
            secao=item_data["secao"],
            item_verificacao=item_data["item"],
            criterio_conformidade=item_data["criterio"]
        )
        db.session.add(item)
    
    db.session.commit()
    print("Template Gestão de Riscos (GRI / MPS.BR) criado com sucesso!")
