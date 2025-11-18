"""
Migração: Adiciona campo escalado_aceito ao ItemChecklist

Este script adiciona a coluna 'escalado_aceito' à tabela item_checklist
para controlar se o superior aceitou o escalamento da NC.
"""

from extensions import db
from sqlalchemy import text

def upgrade():
    """Adiciona coluna escalado_aceito"""
    try:
        # Adicionar coluna com valor padrão False
        with db.engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE item_checklist ADD COLUMN escalado_aceito BOOLEAN DEFAULT 0"
            ))
            conn.commit()
        
        print("✅ Coluna 'escalado_aceito' adicionada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        raise


def downgrade():
    """Remove coluna escalado_aceito"""
    try:
        with db.engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE item_checklist DROP COLUMN escalado_aceito"
            ))
            conn.commit()
        
        print("✅ Coluna 'escalado_aceito' removida com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao remover coluna: {e}")
        raise


if __name__ == '__main__':
    from app import app
    
    with app.app_context():
        print("Executando migração: add_escalado_aceito")
        upgrade()
        print("Migração concluída!")
