"""Rotas principais e documentos"""
from flask import Blueprint, render_template
from flask_login import login_required
from models import Checklist, TemplateChecklist

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Página inicial com lista de checklists"""
    checklists = Checklist.query.order_by(Checklist.data_criacao.desc()).all()
    templates = TemplateChecklist.query.filter_by(ativo=True).all()
    return render_template('index.html', checklists=checklists, templates=templates)


@main_bp.route('/documentos/gri')
@login_required
def ver_documento_gri():
    """Exibe o modelo de Plano de Gestão de Riscos em HTML estático"""
    return render_template('ver_documento_gri.html')
