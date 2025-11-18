"""Rotas de aprovação e gestão de prazos de NC"""
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import ItemChecklist, Comentario
from utils import criar_notificacao

aprovacao_bp = Blueprint('aprovacao', __name__, url_prefix='/item')


@aprovacao_bp.route('/<int:item_id>/aceitar-escalamento', methods=['POST'])
@login_required
def aceitar_escalamento(item_id):
    """Superior aceita ou rejeita o escalamento da NC"""
    item = ItemChecklist.query.get_or_404(item_id)
    
    # Verificar se é o superior escalado
    if item.escalado_para_id != current_user.id:
        flash('Você não tem permissão para aceitar esta NC.', 'danger')
        return redirect(url_for('nc.minhas_ncs'))
    
    # Verificar se já foi aceito
    if item.escalado_aceito:
        flash('Esta NC já foi aceita.', 'info')
        return redirect(url_for('nc.minhas_ncs'))
    
    acao = request.form.get('acao')  # 'aceitar' ou 'rejeitar'
    justificativa = request.form.get('justificativa', '')
    
    if acao == 'aceitar':
        item.escalado_aceito = True
        db.session.commit()
        
        # Criar comentário de aceite
        comentario = Comentario(
            item_id=item.id,
            usuario_id=current_user.id,
            comentario=f'✅ Superior imediato ciente da NC. {justificativa}' if justificativa else '✅ Escalamento aceito.'
        )
        db.session.add(comentario)
        db.session.commit()
        
        # Notificar auditor
        criar_notificacao(
            usuario_id=item.checklist.criador_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Escalamento Aceito',
            mensagem=f'{current_user.nome} aceitou o escalamento da NC: {item.item_template.item_verificacao}'
        )
        
        # Notificar responsável original
        criar_notificacao(
            usuario_id=item.responsavel_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Escalamento Aceito',
            mensagem=f'{current_user.nome} aceitou o escalamento da NC: {item.item_template.item_verificacao}'
        )
        
        flash(f'✅ Escalamento aceito! A NC "{item.item_template.item_verificacao[:50]}..." agora está sob sua responsabilidade.', 'success')
    
    elif acao == 'rejeitar':
        # Desfazer escalamento
        item.escalado = False
        item.escalado_para_id = None
        item.escalado_aceito = False
        db.session.commit()
        
        # Criar comentário de rejeição
        comentario = Comentario(
            item_id=item.id,
            usuario_id=current_user.id,
            comentario=f'❌ Escalamento rejeitado. {justificativa}' if justificativa else '❌ Escalamento rejeitado.'
        )
        db.session.add(comentario)
        db.session.commit()
        
        # Notificar auditor
        criar_notificacao(
            usuario_id=item.checklist.criador_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Escalamento Rejeitado',
            mensagem=f'{current_user.nome} rejeitou o escalamento da NC: {item.item_template.item_verificacao}'
        )
        
        flash(f'❌ Escalamento rejeitado. A NC retornou para {item.responsavel.nome}.', 'info')
    
    return redirect(url_for('nc.minhas_ncs'))


@aprovacao_bp.route('/<int:item_id>/fechar', methods=['POST'])
@login_required
def fechar_nc(item_id):
    """Auditor pode fechar diretamente. Superior precisa de aprovação do auditor."""
    item = ItemChecklist.query.get_or_404(item_id)
    
    # Verificar permissão
    eh_auditor = item.checklist.criador_id == current_user.id
    eh_superior = item.responsavel and item.responsavel.superior_id == current_user.id
    
    if not (eh_auditor or eh_superior):
        flash('Apenas o auditor criador ou o superior do responsável podem fechar esta NC.', 'danger')
        return redirect(request.referrer or url_for('nc.minhas_ncs'))
    
    motivo = request.form.get('motivo_fechamento')
    
    if not motivo:
        flash('É necessário informar o motivo do fechamento.', 'danger')
        return redirect(request.referrer or url_for('nc.minhas_ncs'))
    
    # Se for o AUDITOR, fecha diretamente
    if eh_auditor:
        _fechar_nc_direto(item, motivo)
        flash(f'✅ NC fechada com sucesso! "{item.item_template.item_verificacao[:50]}..." foi encerrada.', 'success')
    
    # Se for o SUPERIOR, cria solicitação de aprovação
    elif eh_superior:
        _solicitar_fechamento_nc(item, motivo)
        flash(f'📨 Solicitação enviada! Aguardando aprovação do auditor {item.checklist.criador.nome} para fechar esta NC.', 'info')
    
    return redirect(request.referrer or url_for('nc.minhas_ncs'))


@aprovacao_bp.route('/<int:item_id>/propor-prazo', methods=['POST'])
@login_required
def propor_prazo(item_id):
    """Auditor pode alterar diretamente. Superior precisa de aprovação do auditor."""
    item = ItemChecklist.query.get_or_404(item_id)
    
    # Verificar permissão
    eh_auditor = item.checklist.criador_id == current_user.id
    eh_superior = item.responsavel and item.responsavel.superior_id == current_user.id
    
    if not (eh_auditor or eh_superior):
        flash('Apenas o auditor criador ou o superior do responsável podem propor novo prazo.', 'danger')
        return redirect(request.referrer or url_for('nc.minhas_ncs'))
    
    nova_data_str = request.form.get('nova_data_resolucao')
    motivo = request.form.get('motivo_prazo')
    
    if not nova_data_str:
        flash('É necessário informar a nova data de resolução.', 'danger')
        return redirect(request.referrer or url_for('nc.minhas_ncs'))
    
    try:
        nova_data = datetime.strptime(nova_data_str, '%Y-%m-%d')
        
        # Se for o AUDITOR, altera diretamente
        if eh_auditor:
            _alterar_prazo_direto(item, nova_data, motivo)
            flash(f'📅 Novo prazo definido: {nova_data.strftime("%d/%m/%Y")} para "{item.item_template.item_verificacao[:50]}..."', 'success')
        
        # Se for o SUPERIOR, cria solicitação de aprovação
        elif eh_superior:
            _solicitar_alteracao_prazo(item, nova_data, motivo)
            flash(f'📨 Solicitação de alteração de prazo enviada para {item.checklist.criador.nome}. Novo prazo proposto: {nova_data.strftime("%d/%m/%Y")}', 'info')
        
    except ValueError:
        flash('Data inválida.', 'danger')
    
    return redirect(request.referrer or url_for('nc.minhas_ncs'))


@aprovacao_bp.route('/comentario/<int:comentario_id>/aprovar', methods=['POST'])
@login_required
def aprovar_solicitacao(comentario_id):
    """Auditor aprova ou rejeita solicitação do superior ou responsável"""
    comentario = Comentario.query.get_or_404(comentario_id)
    item = comentario.item
    
    # Apenas o auditor criador pode aprovar
    if item.checklist.criador_id != current_user.id:
        flash('Apenas o auditor criador pode aprovar solicitações.', 'danger')
        return redirect(request.referrer or url_for('nc.minhas_ncs'))
    
    # Verificar se é uma solicitação pendente
    if not comentario.tipo_solicitacao or comentario.status_aprovacao != 'pendente':
        flash('Esta solicitação já foi processada ou não é uma solicitação válida.', 'danger')
        return redirect(request.referrer or url_for('nc.minhas_ncs'))
    
    acao = request.form.get('acao')
    justificativa = request.form.get('justificativa', '')
    
    if acao == 'aprovar':
        _processar_aprovacao(comentario, item, justificativa)
        tipo_msg = 'fechamento' if comentario.tipo_solicitacao == 'fechar_nc' else 'alteração de prazo'
        flash(f'✅ Solicitação de {tipo_msg} aprovada! NC: "{item.item_template.item_verificacao[:50]}..."', 'success')
    
    elif acao == 'rejeitar':
        _processar_rejeicao(comentario, item, justificativa)
        tipo_msg = 'fechamento' if comentario.tipo_solicitacao == 'fechar_nc' else 'alteração de prazo'
        flash(f'❌ Solicitação de {tipo_msg} rejeitada.', 'info')
    
    else:
        flash('Ação inválida.', 'danger')
    
    return redirect(request.referrer or url_for('nc.minhas_ncs'))


# Funções auxiliares privadas

def _fechar_nc_direto(item, motivo):
    """Fecha NC diretamente (auditor)"""
    # Cancelar qualquer aprovação pendente antes de fechar
    _cancelar_aprovacoes_pendentes(item)
    
    item.status_nc = 'Resolvida'
    item.data_resolucao = datetime.utcnow()
    item.motivo_fechamento = motivo
    
    comentario = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=f"🔒 NC fechada por {current_user.nome} ({current_user.funcao}). Motivo: {motivo}",
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario)
    db.session.commit()
    
    # Notificar responsável e superior
    if item.responsavel_id:
        criar_notificacao(
            usuario_id=item.responsavel_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='NC Fechada',
            mensagem=f'A NC "{item.item_template.item_verificacao}" foi fechada pelo auditor'
        )
    
    if item.escalado_para_id:
        criar_notificacao(
            usuario_id=item.escalado_para_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='NC Fechada',
            mensagem=f'A NC "{item.item_template.item_verificacao}" foi fechada pelo auditor'
        )


def _solicitar_fechamento_nc(item, motivo):
    """Cria solicitação de fechamento de NC (superior)"""
    comentario = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=f"🔔 {current_user.nome} ({current_user.funcao}) solicita o fechamento da NC.\nMotivo: {motivo}",
        tipo_solicitacao='fechar_nc',
        motivo_fechamento_proposto=motivo,
        status_aprovacao='pendente',
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario)
    db.session.commit()
    
    criar_notificacao(
        usuario_id=item.checklist.criador_id,
        item_id=item.id,
        tipo='nc_atualizada',
        titulo='Solicitação de Fechamento de NC',
        mensagem=f'{current_user.nome} solicita o fechamento da NC "{item.item_template.item_verificacao}". Motivo: {motivo}'
    )


def _alterar_prazo_direto(item, nova_data, motivo):
    """Altera prazo diretamente (auditor)"""
    # Cancelar qualquer aprovação pendente antes de alterar prazo
    _cancelar_aprovacoes_pendentes(item)
    
    item.nova_data_resolucao = nova_data
    
    # Se a NC estava resolvida, reabre ao alterar o prazo
    if item.status_nc == 'Resolvida':
        item.status_nc = 'Em Andamento'
        item.data_resolucao = None
    
    comentario_texto = f"📅 Novo prazo definido por {current_user.nome} ({current_user.funcao}): {nova_data.strftime('%d/%m/%Y')}"
    if motivo:
        comentario_texto += f"\nMotivo: {motivo}"
    
    comentario = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=comentario_texto,
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario)
    db.session.commit()
    
    if item.responsavel_id:
        criar_notificacao(
            usuario_id=item.responsavel_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Novo Prazo Definido',
            mensagem=f'O auditor definiu um novo prazo para a NC "{item.item_template.item_verificacao}": {nova_data.strftime("%d/%m/%Y")}'
        )


def _solicitar_alteracao_prazo(item, nova_data, motivo):
    """Cria solicitação de alteração de prazo (superior)"""
    comentario_texto = f"🔔 {current_user.nome} ({current_user.funcao}) solicita alteração do prazo para: {nova_data.strftime('%d/%m/%Y')}"
    if motivo:
        comentario_texto += f"\nMotivo: {motivo}"
    
    comentario = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=comentario_texto,
        tipo_solicitacao='novo_prazo',
        nova_data_proposta=nova_data,
        status_aprovacao='pendente',
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario)
    db.session.commit()
    
    criar_notificacao(
        usuario_id=item.checklist.criador_id,
        item_id=item.id,
        tipo='nc_atualizada',
        titulo='Solicitação de Alteração de Prazo',
        mensagem=f'{current_user.nome} solicita alteração do prazo da NC "{item.item_template.item_verificacao}" para {nova_data.strftime("%d/%m/%Y")}'
    )


def _processar_aprovacao(comentario, item, justificativa):
    """Processa aprovação de uma solicitação"""
    comentario.status_aprovacao = 'aprovado'
    comentario.aprovado_por_id = current_user.id
    comentario.data_aprovacao = datetime.utcnow()
    
    if comentario.tipo_solicitacao == 'novo_prazo':
        item.nova_data_resolucao = comentario.nova_data_proposta
        
        # Se a NC estava resolvida, reabre ao aprovar novo prazo
        if item.status_nc == 'Resolvida':
            item.status_nc = 'Em Andamento'
            item.data_resolucao = None
        
        mensagem = f"✅ Solicitação APROVADA por {current_user.nome}. Novo prazo: {comentario.nova_data_proposta.strftime('%d/%m/%Y')}"
        
        _notificar_aprovacao_prazo(comentario, item)
    
    elif comentario.tipo_solicitacao in ['resolver_nc', 'fechar_nc']:
        item.status_nc = 'Resolvida'
        item.data_resolucao = datetime.utcnow()
        item.motivo_fechamento = comentario.motivo_fechamento_proposto
        mensagem = f"✅ Solicitação APROVADA por {current_user.nome}. NC marcada como RESOLVIDA."
        
        _notificar_aprovacao_fechamento(comentario, item)
    
    if justificativa:
        mensagem += f"\nJustificativa: {justificativa}"
    
    comentario_decisao = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=mensagem,
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario_decisao)
    db.session.commit()


def _processar_rejeicao(comentario, item, justificativa):
    """Processa rejeição de uma solicitação"""
    comentario.status_aprovacao = 'rejeitado'
    comentario.aprovado_por_id = current_user.id
    comentario.data_aprovacao = datetime.utcnow()
    
    # Se for rejeição de resolução/fechamento, limpar data_resolucao e reabrir NC
    if comentario.tipo_solicitacao in ['resolver_nc', 'fechar_nc']:
        item.data_resolucao = None
        item.status_nc = 'Em Andamento'  # Reabre a NC
    
    tipo_texto = 'alteração de prazo' if comentario.tipo_solicitacao == 'novo_prazo' else 'fechamento'
    mensagem = f"❌ Solicitação REJEITADA por {current_user.nome}."
    if justificativa:
        mensagem += f"\nJustificativa: {justificativa}"
    
    criar_notificacao(
        usuario_id=comentario.usuario_id,
        item_id=item.id,
        tipo='nc_atualizada',
        titulo=f'Solicitação de {tipo_texto.title()} Rejeitada',
        mensagem=f'Sua solicitação de {tipo_texto} foi REJEITADA pelo auditor' + (f'. Justificativa: {justificativa}' if justificativa else '')
    )
    
    comentario_decisao = Comentario(
        item_id=item.id,
        usuario_id=current_user.id,
        comentario=mensagem,
        data_criacao=datetime.utcnow()
    )
    db.session.add(comentario_decisao)
    db.session.commit()


def _notificar_aprovacao_prazo(comentario, item):
    """Notifica sobre aprovação de alteração de prazo"""
    criar_notificacao(
        usuario_id=comentario.usuario_id,
        item_id=item.id,
        tipo='nc_atualizada',
        titulo='Solicitação de Prazo Aprovada',
        mensagem='Sua solicitação de alteração de prazo foi APROVADA pelo auditor'
    )
    
    if item.responsavel_id and item.responsavel_id != comentario.usuario_id:
        criar_notificacao(
            usuario_id=item.responsavel_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Prazo da NC Alterado',
            mensagem=f'O prazo da NC "{item.item_template.item_verificacao}" foi alterado para {comentario.nova_data_proposta.strftime("%d/%m/%Y")}'
        )


def _notificar_aprovacao_fechamento(comentario, item):
    """Notifica sobre aprovação de fechamento"""
    criar_notificacao(
        usuario_id=comentario.usuario_id,
        item_id=item.id,
        tipo='nc_atualizada',
        titulo='Solicitação Aprovada - NC Resolvida',
        mensagem='Sua solicitação foi APROVADA pelo auditor. NC marcada como RESOLVIDA!'
    )
    
    if item.escalado_para_id and item.escalado_para_id != comentario.usuario_id:
        criar_notificacao(
            usuario_id=item.escalado_para_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='NC Resolvida',
            mensagem=f'A NC "{item.item_template.item_verificacao}" foi marcada como RESOLVIDA'
        )


def _cancelar_aprovacoes_pendentes(item):
    """Cancela todas as solicitações de aprovação pendentes quando auditor age diretamente"""
    comentarios_pendentes = Comentario.query.filter_by(
        item_id=item.id,
        status_aprovacao='pendente'
    ).filter(
        Comentario.tipo_solicitacao.isnot(None)
    ).all()
    
    if comentarios_pendentes:
        for comentario in comentarios_pendentes:
            # Marcar como cancelado
            comentario.status_aprovacao = 'cancelado'
            comentario.aprovado_por_id = current_user.id
            comentario.data_aprovacao = datetime.utcnow()
            
            # Criar comentário informando o cancelamento
            tipo_texto = {
                'novo_prazo': 'alteração de prazo',
                'resolver_nc': 'marcar como resolvida',
                'fechar_nc': 'fechamento'
            }.get(comentario.tipo_solicitacao, 'solicitação')
            
            comentario_cancelamento = Comentario(
                item_id=item.id,
                usuario_id=current_user.id,
                comentario=f"⚠️ Solicitação de {tipo_texto} CANCELADA automaticamente. O auditor {current_user.nome} executou uma ação direta que anula esta solicitação.",
                data_criacao=datetime.utcnow()
            )
            db.session.add(comentario_cancelamento)
            
            # Notificar o solicitante
            criar_notificacao(
                usuario_id=comentario.usuario_id,
                item_id=item.id,
                tipo='nc_atualizada',
                titulo=f'Solicitação de {tipo_texto.title()} Cancelada',
                mensagem=f'Sua solicitação foi CANCELADA porque o auditor {current_user.nome} executou uma ação direta na NC.'
            )
        
        db.session.commit()
