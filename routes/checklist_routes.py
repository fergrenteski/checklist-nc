"""Rotas de gerenciamento de checklists"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Checklist, ItemChecklist, TemplateChecklist, Usuario, Comentario
from utils import criar_notificacao

checklist_bp = Blueprint('checklist', __name__, url_prefix='/checklist')


@checklist_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo checklist baseado em template"""
    if request.method == 'POST':
        template_id = request.form.get('template_id', type=int)
        projeto = request.form.get('projeto')
        
        template = TemplateChecklist.query.get_or_404(template_id)
        
        # Criar checklist baseado no template
        checklist = Checklist(
            template_id=template_id,
            projeto=projeto,
            criador_id=current_user.id
        )
        db.session.add(checklist)
        db.session.flush()
        
        # Criar itens baseados no template
        for item_template in template.itens_template:
            item = ItemChecklist(
                checklist_id=checklist.id,
                item_template_id=item_template.id
            )
            db.session.add(item)
        
        db.session.commit()
        
        flash('Checklist criado com sucesso! Agora preencha os itens.', 'success')
        return redirect(url_for('preencher.preencher_checklist', checklist_id=checklist.id))
    
    templates = TemplateChecklist.query.filter_by(ativo=True).all()
    return render_template('novo_checklist.html', templates=templates)


@checklist_bp.route('/<int:checklist_id>')
@login_required
def ver(checklist_id):
    """Visualizar checklist completo"""
    checklist = Checklist.query.get_or_404(checklist_id)
    aderencia = checklist.calcular_aderencia()
    ncs = checklist.contar_ncs_por_classificacao()
    
    return render_template('ver_checklist.html', 
                         checklist=checklist, 
                         aderencia=aderencia,
                         ncs=ncs)


@checklist_bp.route('/<int:checklist_id>/deletar', methods=['POST'])
@login_required
def deletar(checklist_id):
    """Deletar um checklist"""
    checklist = Checklist.query.get_or_404(checklist_id)
    
    db.session.delete(checklist)
    db.session.commit()
    
    flash('Checklist deletado com sucesso!', 'success')
    return redirect(url_for('main.index'))


@checklist_bp.route('/<int:checklist_id>/estatisticas')
@login_required
def estatisticas(checklist_id):
    """API: Retorna estatísticas do checklist"""
    checklist = Checklist.query.get_or_404(checklist_id)
    
    return jsonify({
        'aderencia': checklist.calcular_aderencia(),
        'ncs': checklist.contar_ncs_por_classificacao(),
        'total_itens': len(checklist.itens)
    })
