"""Configurações do aplicativo Flask"""
import os


class Config:
    """Classe de configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui-mude-em-producao'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///checklist.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
