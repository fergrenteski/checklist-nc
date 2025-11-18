"""Aplicação principal Flask - Sistema de Checklist de Não Conformidades"""
import os
from datetime import timedelta
from flask import Flask
from config import config
from extensions import db, socketio, login_manager
from routes import register_blueprints
from database import init_db
from models import Usuario


def create_app(config_name='default'):
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Carregar configurações
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    
    # Filtro customizado para converter UTC para horário de Brasília (UTC-3)
    @app.template_filter('brasilia')
    def brasilia_timezone(dt):
        """Converte datetime UTC para horário de Brasília (UTC-3)"""
        if dt is None:
            return None
        return dt - timedelta(hours=3)
    
    # Configurar login manager
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Inicializar banco de dados
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    init_db(app)
    
    # Importar eventos WebSocket
    import events  # noqa: F401
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5001)
