"""Rota de preenchimento de checklist"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Checklist, Usuario, Comentario
from utils import criar_notificacao

preencher_bp = Blueprint('preencher', __name__, url_prefix='/checklist')


@preencher_bp.route('/<int:checklist_id>/preencher', methods=['GET', 'POST'])
@login_required
def preencher_checklist(checklist_id):
    """Preencher ou editar itens do checklist"""
    checklist = Checklist.query.get_or_404(checklist_id)
    
    # Apenas o criador pode preencher
    if checklist.criador_id != current_user.id:
        flash('Apenas o auditor pode preencher este checklist.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        _processar_preenchimento(checklist)
        db.session.commit()
        flash('Checklist preenchido com sucesso!', 'success')
        return redirect(url_for('checklist.ver', checklist_id=checklist_id))
    
    usuarios = Usuario.query.filter_by(ativo=True).all()
    return render_template('preencher_checklist.html', checklist=checklist, usuarios=usuarios)


def _processar_preenchimento(checklist):
    """Processa o preenchimento de todos os itens do checklist"""
    for item in checklist.itens:
        item_key = f'item_{item.id}'
        resultado = request.form.get(f'{item_key}_resultado')
        
        if resultado:
            valores_antigos = _guardar_valores_antigos(item)
            eh_edicao = item.resultado is not None
            
            item.resultado = resultado
            item.observacao = request.form.get(f'{item_key}_observacao')
            
            if not eh_edicao:
                item.data_preenchimento = datetime.utcnow()
            
            if resultado == 'Não Conforme':
                _processar_nao_conformidade(item, item_key, valores_antigos, eh_edicao)
            elif eh_edicao and valores_antigos['resultado'] == 'Não Conforme':
                _limpar_dados_nc(item, resultado)


def _guardar_valores_antigos(item):
    """Guarda valores antigos do item para comparação"""
    return {
        'resultado': item.resultado,
        'classificacao_nc': item.classificacao_nc,
        'responsavel_id': item.responsavel_id,
        'acao_corretiva': item.acao_corretiva,
        'observacao': item.observacao
    }


def _processar_nao_conformidade(item, item_key, valores_antigos, eh_edicao):
    """Processa item marcado como Não Conforme"""
    nova_classificacao = request.form.get(f'{item_key}_classificacao')
    novo_responsavel_id = request.form.get(f'{item_key}_responsavel', type=int)
    nova_acao = request.form.get(f'{item_key}_acao')
    
    alteracoes = []
    
    # Detectar se houve alterações reais
    houve_alteracoes = False
    if eh_edicao and valores_antigos['resultado'] == 'Não Conforme':
        alteracoes_detectadas = _detectar_alteracoes(valores_antigos, nova_classificacao, novo_responsavel_id, nova_acao)
        if alteracoes_detectadas:
            houve_alteracoes = True
            alteracoes.extend(alteracoes_detectadas)
    
    # Se estava resolvida e houve alterações reais, limpar escalamento e dados de resolução
    if eh_edicao and item.status_nc == 'Resolvida' and houve_alteracoes:
        item.escalado = False
        item.escalado_para_id = None
        item.escalado_aceito = False
        item.data_resolucao = None
        item.motivo_fechamento = None
        alteracoes.append("⚠️ NC reaberta - escalamento removido")
    
    # Atualizar valores
    item.classificacao_nc = nova_classificacao
    
    # Se responsável mudou, atualizar superior também e limpar escalamento
    if item.responsavel_id != novo_responsavel_id:
        item.responsavel_id = novo_responsavel_id
        # Atualizar superior automaticamente
        if novo_responsavel_id:
            novo_responsavel = Usuario.query.get(novo_responsavel_id)
            if novo_responsavel and novo_responsavel.superior_id:
                # Se estava escalado, limpar
                if item.escalado:
                    item.escalado = False
                    item.escalado_para_id = None
                    item.escalado_aceito = False
                    if eh_edicao:
                        alteracoes.append("⚠️ Escalamento removido (responsável alterado)")
    
    item.acao_corretiva = nova_acao
    
    # Recalcular prazo se necessário
    if not eh_edicao or valores_antigos['classificacao_nc'] != nova_classificacao:
        if not item.data_preenchimento:
            item.data_preenchimento = datetime.utcnow()
        item.prazo_resolucao = item.calcular_prazo_automatico()
        item.nova_data_resolucao = None
    
    # Registrar alterações
    if alteracoes and eh_edicao:
        _registrar_alteracoes(item, alteracoes)
    elif not eh_edicao and item.responsavel_id:
        _notificar_nova_atribuicao(item)


def _detectar_alteracoes(valores_antigos, nova_classificacao, novo_responsavel_id, nova_acao):
    """Detecta alterações feitas em uma NC existente"""
    alteracoes = []
    
    if valores_antigos['classificacao_nc'] != nova_classificacao:
        classificacao_map = {'L': '🟢 Leve', 'M': '🟡 Moderada', 'G': '🔴 Grave'}
        alt_antiga = classificacao_map.get(valores_antigos['classificacao_nc'], 'N/A')
        alt_nova = classificacao_map.get(nova_classificacao)
        alteracoes.append(f"Classificação: {alt_antiga} → {alt_nova}")
    
    if valores_antigos['responsavel_id'] != novo_responsavel_id:
        responsavel_antigo = Usuario.query.get(valores_antigos['responsavel_id']) if valores_antigos['responsavel_id'] else None
        responsavel_novo = Usuario.query.get(novo_responsavel_id) if novo_responsavel_id else None
        nome_antigo = responsavel_antigo.nome if responsavel_antigo else 'N/A'
        nome_novo = responsavel_novo.nome if responsavel_novo else 'N/A'
        alteracoes.append(f"Responsável: {nome_antigo} → {nome_novo}")
    
    if valores_antigos['acao_corretiva'] != nova_acao:
        alteracoes.append("Ação corretiva atualizada")
    
    return alteracoes


def _registrar_alteracoes(item, alteracoes):
    """Registra alterações feitas em uma NC e notifica responsável"""
    item.status_nc = 'Pendente'
    
    # Criar comentário automático
    comentario_alteracao = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=f"✏️ NC editada por {current_user.nome} ({current_user.funcao}):\n• " + "\n• ".join(alteracoes),
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario_alteracao)
    
    # Notificar responsável
    if item.responsavel_id:
        criar_notificacao(
            usuario_id=item.responsavel_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='NC Editada - Status voltou para Pendente',
            mensagem=f'A NC "{item.item_template.item_verificacao}" foi editada pelo auditor. Alterações: {", ".join(alteracoes)}'
        )


def _notificar_nova_atribuicao(item):
    """Notifica responsável de nova NC atribuída"""
    prazo = item.get_prazo_limite().strftime("%d/%m/%Y")
    criar_notificacao(
        usuario_id=item.responsavel_id,
        item_id=item.id,
        tipo='nova_nc',
        titulo='Nova Não Conformidade Atribuída',
        mensagem=f'Você foi designado responsável pela NC: {item.item_template.item_verificacao} - Classificação: {item.classificacao_nc} - Prazo: {prazo}'
    )


def _limpar_dados_nc(item, novo_resultado):
    """Limpa dados da NC quando item muda de Não Conforme para outro status"""
    comentario_alteracao = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=f"✏️ Item editado por {current_user.nome}: Não Conforme → {novo_resultado}",
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario_alteracao)
    
    # Limpar dados da NC (incluindo escalamento)
    item.classificacao_nc = None
    item.responsavel_id = None
    item.acao_corretiva = None
    item.status_nc = None
    item.prazo_resolucao = None
    item.nova_data_resolucao = None
    item.escalado = False
    item.escalado_para_id = None
    item.escalado_aceito = False
