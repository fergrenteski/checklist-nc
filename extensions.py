"""Extensões Flask centralizadas"""
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager

# Inicializar extensões
db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()

# Configurar login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'
