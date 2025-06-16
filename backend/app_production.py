import os
from flask import Flask, render_template, send_from_directory, session, redirect, url_for, send_file, jsonify, request
from auth import auth_bp
from database import db, init_db, User, Escola, Turma, Aluno, PlanoAula, Habilidade, Questao, Alternativa, Caderno, BlocoCaderno, BlocoQuestao, ResultadoAluno, RespostaAluno
from config import Config, get_database_uri
from dotenv import load_dotenv
from escolas import escolas_bp
from turma import turmas_bp
from aluno import alunos_bp
from plano_aula import plano_aula_bp
from habilidade import habilidades_bp
from flask_migrate import Migrate

# Carregar variáveis de ambiente
load_dotenv()

# Configurar caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

# Verificar se os caminhos existem
print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] FRONTEND_DIR: {FRONTEND_DIR}")
print(f"[DEBUG] STATIC_DIR: {STATIC_DIR}")
print(f"[DEBUG] Frontend exists: {os.path.exists(FRONTEND_DIR)}")
print(f"[DEBUG] Static exists: {os.path.exists(STATIC_DIR)}")

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=STATIC_DIR)
app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_ultra_segura')
app.config.from_object(Config)

# Configurar URI do banco dinamicamente
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
print(f"[DEBUG] Database URI configured")

# Inicializa o banco de dados com o app
db.init_app(app)
print(f"[DEBUG] Database initialized")

# Inicializa o Flask-Migrate para gerenciar migrações do banco de dados
migrate = Migrate(app, db)
print(f"[DEBUG] Flask-Migrate initialized")

# Registrar blueprints com tratamento de erro
try:
    app.register_blueprint(auth_bp)
    print(f"[DEBUG] auth_bp registered")
    
    app.register_blueprint(escolas_bp)
    print(f"[DEBUG] escolas_bp registered")
    
    app.register_blueprint(turmas_bp)
    print(f"[DEBUG] turmas_bp registered")
    
    app.register_blueprint(alunos_bp)
    print(f"[DEBUG] alunos_bp registered")
    
    app.register_blueprint(plano_aula_bp)
    print(f"[DEBUG] plano_aula_bp registered")
    
    app.register_blueprint(habilidades_bp)
    print(f"[DEBUG] habilidades_bp registered")
    
    # AI blueprint is optional
    try:
        from ai_integration import ai_bp
        app.register_blueprint(ai_bp)
        print(f"[DEBUG] ai_bp registered")
    except Exception as e:
        print(f"[WARNING] AI blueprint not loaded: {e}")

except Exception as e:
    print(f"[ERROR] Blueprint registration failed: {e}")

# Rotas básicas
@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Application is running'}, 200

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"[ERROR] Template error: {e}")
        return '<h1>Edu Plataforma</h1><p>Sistema funcionando! Templates em manutenção.</p>'

@app.route('/login')
def login_page():
    try:
        return render_template('login.html')
    except Exception as e:
        print(f"[ERROR] Login template error: {e}")
        return '<h1>Login</h1><p>Página de login em manutenção.</p>'

# Inicialização
if __name__ == '__main__':
    print("Caminho absoluto do template_folder:", os.path.abspath(app.template_folder))
    print("Caminho absoluto do static_folder:", os.path.abspath(app.static_folder))
    
    try:
        with app.app_context():
            init_db()
        print("[SUCCESS] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    print(f"[INFO] Starting server on port {port}, debug={debug_mode}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 