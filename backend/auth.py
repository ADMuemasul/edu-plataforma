from flask import Blueprint, request, redirect, url_for, session
from database import get_user_by_email, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email(email)
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
            
        return "Credenciais inválidas", 401
    
    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return f"Erro no servidor: {str(e)}", 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        school = request.form['school']
        
        if get_user_by_email(email):
            return "Email já cadastrado", 400
            
        create_user(name, email, password, school)
        return redirect(url_for('login_page'))
    
    except Exception as e:
        print(f"Erro no registro: {str(e)}")
        return f"Erro no servidor: {str(e)}", 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))