"""Blueprints de rotas do sistema"""
from .auth import auth_bp
from .main import main_bp
from .checklist_routes import checklist_bp
from .preencher import preencher_bp
from .nc import nc_bp
from .aprovacao import aprovacao_bp
from .notificacoes import notificacoes_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'checklist_bp',
    'preencher_bp',
    'nc_bp',
    'aprovacao_bp',
    'notificacoes_bp'
]


def register_blueprints(app):
    """Registra todos os blueprints no aplicativo Flask"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(checklist_bp)
    app.register_blueprint(preencher_bp)
    app.register_blueprint(nc_bp)
    app.register_blueprint(aprovacao_bp)
    app.register_blueprint(notificacoes_bp)
