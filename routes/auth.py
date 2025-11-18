"""Rotas de autenticação"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de novo usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        funcao = request.form.get('funcao')
        superior_id = request.form.get('superior_id', type=int)
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('auth.registro'))
        
        usuario = Usuario(
            nome=nome, 
            email=email, 
            funcao=funcao, 
            superior_id=superior_id if superior_id else None
        )
        usuario.set_senha(senha)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    usuarios = Usuario.query.filter_by(ativo=True).all()
    return render_template('registro.html', usuarios=usuarios)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de perfil do usuário"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        funcao = request.form.get('funcao')
        superior_id = request.form.get('superior_id', type=int)
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        
        # Verificar se o email já está em uso por outro usuário
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente and usuario_existente.id != current_user.id:
            flash('Este email já está em uso por outro usuário.', 'danger')
            return redirect(url_for('auth.perfil'))
        
        # Atualizar dados básicos
        current_user.nome = nome
        current_user.email = email
        current_user.funcao = funcao
        current_user.superior_id = superior_id if superior_id else None
        
        # Se está tentando mudar a senha
        if senha_atual and nova_senha:
            if current_user.verificar_senha(senha_atual):
                if len(nova_senha) >= 6:
                    current_user.set_senha(nova_senha)
                    flash('Senha alterada com sucesso!', 'success')
                else:
                    flash('A nova senha deve ter pelo menos 6 caracteres.', 'danger')
                    return redirect(url_for('auth.perfil'))
            else:
                flash('Senha atual incorreta.', 'danger')
                return redirect(url_for('auth.perfil'))
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.perfil'))
    
    usuarios = Usuario.query.filter(
        Usuario.id != current_user.id, 
        Usuario.ativo == True
    ).all()
    return render_template('perfil.html', usuarios=usuarios)
