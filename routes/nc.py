"""Rotas de gerenciamento de Não Conformidades"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import ItemChecklist, Comentario
from utils import criar_notificacao

nc_bp = Blueprint('nc', __name__)


@nc_bp.route('/minhas-ncs')
@login_required
def minhas_ncs():
    """Lista NCs atribuídas ao usuário atual ou escaladas para ele"""
    # NCs como responsável
    ncs_responsavel = ItemChecklist.query.filter_by(
        responsavel_id=current_user.id,
        resultado='Não Conforme'
    ).order_by(ItemChecklist.data_criacao.desc()).all()
    
    # NCs escaladas para mim (como superior)
    ncs_escaladas = ItemChecklist.query.filter_by(
        escalado_para_id=current_user.id,
        escalado=True
    ).order_by(ItemChecklist.data_criacao.desc()).all()
    
    # Aprovações pendentes para mim
    # 1. Como superior: escalamentos aguardando meu aceite
    escalamentos_pendentes = ItemChecklist.query.filter_by(
        escalado_para_id=current_user.id,
        escalado=True,
        escalado_aceito=False
    ).all()
    
    # 2. Como auditor: solicitações de aprovação (novo prazo, resolver NC, fechar NC)
    from models import Checklist
    aprovacoes_pendentes = []
    
    # Buscar checklists criados por mim (como auditor)
    meus_checklists = Checklist.query.filter_by(criador_id=current_user.id).all()
    checklist_ids = [c.id for c in meus_checklists]
    
    if checklist_ids:
        # Buscar comentários com solicitações pendentes nos meus checklists
        comentarios_pendentes = Comentario.query.join(
            ItemChecklist, Comentario.item_id == ItemChecklist.id
        ).filter(
            ItemChecklist.checklist_id.in_(checklist_ids),
            Comentario.status_aprovacao == 'pendente',
            Comentario.tipo_solicitacao.isnot(None)
        ).order_by(Comentario.data_criacao.desc()).all()
        
        aprovacoes_pendentes = comentarios_pendentes
    
    return render_template('minhas_ncs.html', 
                         ncs_responsavel=ncs_responsavel, 
                         ncs_escaladas=ncs_escaladas,
                         escalamentos_pendentes=escalamentos_pendentes,
                         aprovacoes_pendentes=aprovacoes_pendentes)


@nc_bp.route('/item/<int:item_id>/comentar', methods=['POST'])
@login_required
def comentar_item(item_id):
    """Adiciona comentário ao item"""
    item = ItemChecklist.query.get_or_404(item_id)
    comentario_texto = request.form.get('comentario')
    
    if not comentario_texto:
        flash('Comentário não pode estar vazio.', 'danger')
        return redirect(url_for('nc.minhas_ncs'))
    
    # Verificar permissão
    pode_comentar = (
        current_user.id == item.responsavel_id or
        current_user.id == item.escalado_para_id or
        current_user.id == item.checklist.criador_id
    )
    
    if not pode_comentar:
        flash('Você não tem permissão para comentar neste item.', 'danger')
        return redirect(url_for('main.index'))
    
    # Atualizar status para "Em Andamento" se ainda estiver "Pendente"
    if item.status_nc == 'Pendente':
        item.status_nc = 'Em Andamento'
    
    comentario = Comentario(
        item_id=item_id,
        usuario_id=current_user.id,
        comentario=comentario_texto
    )
    db.session.add(comentario)
    db.session.commit()
    
    # Notificar auditor se quem comentou foi responsável ou superior
    if current_user.id != item.checklist.criador_id:
        criar_notificacao(
            usuario_id=item.checklist.criador_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Novo Comentário na NC',
            mensagem=f'{current_user.nome} comentou na NC: {item.item_template.item_verificacao}'
        )
    
    # Notificar responsável se quem comentou foi auditor ou superior
    if current_user.id != item.responsavel_id and item.responsavel_id:
        criar_notificacao(
            usuario_id=item.responsavel_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Novo Comentário na Sua NC',
            mensagem=f'{current_user.nome} comentou na NC: {item.item_template.item_verificacao}'
        )
    
    flash('💬 Comentário adicionado! Sua mensagem foi registrada.', 'success')
    return redirect(request.referrer or url_for('nc.minhas_ncs'))


@nc_bp.route('/item/<int:item_id>/atualizar-status', methods=['POST'])
@login_required
def atualizar_status(item_id):
    """Atualiza o status de uma NC"""
    item = ItemChecklist.query.get_or_404(item_id)
    
    if item.responsavel_id != current_user.id:
        flash('Você não tem permissão para atualizar esta NC.', 'danger')
        return redirect(url_for('nc.minhas_ncs'))
    
    novo_status = request.form.get('status')
    
    # Se está marcando como Resolvida, cria solicitação de aprovação
    if novo_status == 'Resolvida':
        justificativa = request.form.get('justificativa_resolucao', '')
        
        if not justificativa:
            flash('É necessário informar como a NC foi resolvida.', 'danger')
            return redirect(url_for('nc.minhas_ncs'))
        
        # Criar solicitação de resolução
        comentario = Comentario(
            item_id=item.id,
            usuario_id=current_user.id,
            comentario=f"🔔 {current_user.nome} ({current_user.funcao}) solicita marcar a NC como RESOLVIDA.\nJustificativa: {justificativa}",
            tipo_solicitacao='resolver_nc',
            motivo_fechamento_proposto=justificativa,
            status_aprovacao='pendente',
            data_criacao=datetime.utcnow()
        )
        db.session.add(comentario)
        db.session.commit()
        
        # Notificar auditor
        criar_notificacao(
            usuario_id=item.checklist.criador_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Solicitação de Resolução de NC',
            mensagem=f'{current_user.nome} solicita marcar a NC "{item.item_template.item_verificacao}" como RESOLVIDA. Justificativa: {justificativa}'
        )
        
        flash('Solicitação de resolução enviada para aprovação do auditor.', 'info')
    
    # Para outros status, atualiza diretamente
    elif novo_status in ['Pendente', 'Em Andamento']:
        item.status_nc = novo_status
        db.session.commit()
        
        # Notificar criador do checklist
        criar_notificacao(
            usuario_id=item.checklist.criador_id,
            item_id=item.id,
            tipo='nc_atualizada',
            titulo='Status da NC Atualizado',
            mensagem=f'{current_user.nome} atualizou o status da NC "{item.item_template.item_verificacao}" para {novo_status}.'
        )
        
        flash(f'Status atualizado para {novo_status}!', 'success')
    else:
        flash('Status inválido.', 'danger')
    
    return redirect(url_for('nc.minhas_ncs'))


@nc_bp.route('/item/<int:item_id>/escalar', methods=['POST'])
@login_required
def escalar(item_id):
    """Escalona NC para o superior imediato do responsável"""
    item = ItemChecklist.query.get_or_404(item_id)
    
    # Apenas o auditor pode escalar
    if item.checklist.criador_id != current_user.id:
        flash('Apenas o auditor pode escalar esta NC.', 'danger')
        return redirect(url_for('checklist.ver', checklist_id=item.checklist_id))
    
    if not item.responsavel or not item.responsavel.superior_id:
        flash('O responsável não possui superior imediato cadastrado.', 'danger')
        return redirect(url_for('checklist.ver', checklist_id=item.checklist_id))
    
    item.escalado = True
    item.escalado_para_id = item.responsavel.superior_id
    db.session.commit()
    
    # Notificar o superior
    criar_notificacao(
        usuario_id=item.responsavel.superior_id,
        item_id=item.id,
        tipo='nova_nc',
        titulo='NC Escalada Para Você',
        mensagem=f'A NC "{item.item_template.item_verificacao}" foi escalada para você. Responsável: {item.responsavel.nome}'
    )
    
    flash(f'🚀 NC escalada! {item.escalado_para.nome} foi notificado e deve aceitar a responsabilidade.', 'success')
    return redirect(url_for('checklist.ver', checklist_id=item.checklist_id))
