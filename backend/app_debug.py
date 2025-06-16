print("🔥 EDU PLATAFORMA - SISTEMA COMPLETO - DEBUG INICIANDO")

try:
    from flask import Flask, render_template, send_from_directory, session, redirect, url_for, send_file, jsonify, request
    print("✅ Flask importado com sucesso")
except Exception as e:
    print(f"❌ Erro importando Flask: {e}")

try:
    import os
    import time
    print("✅ Módulos básicos importados")
except Exception as e:
    print(f"❌ Erro módulos básicos: {e}")

try:
    from auth import auth_bp
    print("✅ Auth blueprint importado")
except Exception as e:
    print(f"❌ Erro importando auth: {e}")

try:
    from database import db, init_db, User, Escola, Turma, Aluno, PlanoAula, Habilidade, Questao, Alternativa, Caderno, BlocoCaderno, BlocoQuestao, ResultadoAluno, RespostaAluno
    print("✅ Database e modelos importados")
except Exception as e:
    print(f"❌ Erro importando database: {e}")

try:
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    print("✅ ReportLab importado")
except Exception as e:
    print(f"❌ Erro importando ReportLab: {e}")

try:
    from dotenv import load_dotenv
    print("✅ Dotenv importado")
except Exception as e:
    print(f"❌ Erro importando dotenv: {e}")

try:
    from escolas import escolas_bp
    from turma import turmas_bp
    from aluno import alunos_bp
    from plano_aula import plano_aula_bp
    from habilidade import habilidades_bp
    print("✅ Todos os blueprints importados")
except Exception as e:
    print(f"❌ Erro importando blueprints: {e}")

try:
    from config import Config, get_database_uri
    print("✅ Config importado")
except Exception as e:
    print(f"❌ Erro importando config: {e}")

try:
    from flask_migrate import Migrate
    print("✅ Flask-Migrate importado")
except Exception as e:
    print(f"❌ Erro importando migrate: {e}")

print("🔥 EDU PLATAFORMA - INICIANDO CONFIGURAÇÃO")

# Carregar variáveis de ambiente
try:
    load_dotenv()
    print("✅ Variáveis de ambiente carregadas")
except Exception as e:
    print(f"❌ Erro carregando .env: {e}")

# Configurar caminhos absolutos
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
    STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')
    print(f"✅ BASE_DIR: {BASE_DIR}")
    print(f"✅ FRONTEND_DIR: {FRONTEND_DIR}")
    print(f"✅ STATIC_DIR: {STATIC_DIR}")
    print(f"✅ Frontend exists: {os.path.exists(FRONTEND_DIR)}")
    print(f"✅ Static exists: {os.path.exists(STATIC_DIR)}")
except Exception as e:
    print(f"❌ Erro configurando paths: {e}")

# Criar app Flask
try:
    app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=STATIC_DIR)
    print("✅ Flask app criado")
except Exception as e:
    print(f"❌ Erro criando Flask app: {e}")

# Configurar app
try:
    app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_ultra_segura')
    app.config.from_object(Config)
    print("✅ Configurações básicas aplicadas")
except Exception as e:
    print(f"❌ Erro configurações básicas: {e}")

# Configurar banco
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    print(f"✅ Database URI configurado")
except Exception as e:
    print(f"❌ Erro configurando database URI: {e}")

# Inicializar database
try:
    db.init_app(app)
    print("✅ Database inicializado")
except Exception as e:
    print(f"❌ Erro inicializando database: {e}")

# Inicializar migrate
try:
    migrate = Migrate(app, db)
    print("✅ Flask-Migrate configurado")
except Exception as e:
    print(f"❌ Erro configurando migrate: {e}")

# Registrar blueprints
try:
    app.register_blueprint(auth_bp)
    print("✅ Auth blueprint registrado")
except Exception as e:
    print(f"❌ Erro registrando auth blueprint: {e}")

try:
    app.register_blueprint(escolas_bp)
    app.register_blueprint(turmas_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(plano_aula_bp)
    app.register_blueprint(habilidades_bp)
    print("✅ Todos os blueprints registrados")
except Exception as e:
    print(f"❌ Erro registrando blueprints: {e}")

# Rota básica de teste
@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'EDU PLATAFORMA - SISTEMA COMPLETO FUNCIONANDO!', 'version': 'debug-complete'}, 200

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f'''
        <html>
        <body>
            <h1>🎓 EDU PLATAFORMA - SISTEMA COMPLETO</h1>
            <p>✅ Sistema funcionando, mas erro no template: {str(e)}</p>
            <p><a href="/health">Health Check</a></p>
            <p><a href="/dashboard">Dashboard</a></p>
        </body>
        </html>
        '''

@app.route('/dashboard')
def dashboard():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        user_id = session['user_id']
        count_escolas = Escola.query.filter_by(user_id=user_id).count()
        count_turmas = Turma.query.filter_by(user_id=user_id).count()
        count_alunos = Aluno.query.filter_by(user_id=user_id).count()
        count_planos = PlanoAula.query.filter_by(user_id=user_id).count()
        count_questoes = Questao.query.filter_by(user_id=user_id).count()
        count_habilidades = Habilidade.query.count()
        return render_template('dashboard.html', user=session, 
                               count_escolas=count_escolas, count_turmas=count_turmas, 
                               count_alunos=count_alunos, count_planos=count_planos, 
                               count_questoes=count_questoes, count_habilidades=count_habilidades)
    except Exception as e:
        return f'''
        <html>
        <body>
            <h1>🎓 Dashboard - EDU PLATAFORMA</h1>
            <p>❌ Erro: {str(e)}</p>
            <p><a href="/">Voltar</a></p>
        </body>
        </html>
        '''

@app.route('/login')
def login_page():
    try:
        return render_template('login.html')
    except Exception as e:
        return f'''
        <html>
        <body>
            <h1>🔐 Login - EDU PLATAFORMA</h1>
            <p>❌ Erro carregando template: {str(e)}</p>
            <p><a href="/">Voltar</a></p>
        </body>
        </html>
        '''

if __name__ == '__main__':
    print("🔥 EDU PLATAFORMA - INICIANDO SERVIDOR DEBUG")
    try:
        with app.app_context():
            init_db()
        print("✅ Database inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro inicializando database: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 EDU PLATAFORMA - SERVIDOR INICIANDO NA PORTA {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

print("🔥 EDU PLATAFORMA - CONFIGURAÇÃO DEBUG COMPLETA") 