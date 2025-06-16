import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_PATH = os.path.join(os.path.dirname(__file__), 'eduplataforma.db')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    school = db.Column(db.String(100))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Habilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False)
    componente = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    etapa = db.Column(db.String(50), default='Ensino Fundamental')
    objetos_conhecimento = db.Column(db.Text)

# NOVOS MODELOS ADICIONADOS
class Escola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    rede = db.Column(db.String(20), nullable=False)
    zona = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.String(20), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escola.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escola.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class PlanoAula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.Text, nullable=False)
    imagem = db.Column(db.String(500))  # URL da imagem
    habilidade_id = db.Column(db.Integer, db.ForeignKey('habilidade.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    componente = db.Column(db.String(50), nullable=True)  # Componente Curricular
    criado_em = db.Column(db.DateTime, server_default=db.func.now())
    alternativas = db.relationship('Alternativa', backref='questao', lazy=True, cascade='all, delete-orphan')

class Alternativa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'), nullable=False)
    correta = db.Column(db.Boolean, default=False)

class Caderno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    serie = db.Column(db.Integer, nullable=False)
    qtd_blocos = db.Column(db.Integer, nullable=False)
    qtd_questoes_por_bloco = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blocos = db.relationship('BlocoCaderno', backref='caderno', lazy=True, cascade='all, delete-orphan')
    # Relacionamento com resultados configurado para cascade delete
    resultados = db.relationship('ResultadoAluno', backref='caderno_ref', lazy=True, cascade='all, delete-orphan')

class BlocoCaderno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caderno_id = db.Column(db.Integer, db.ForeignKey('caderno.id'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    componente = db.Column(db.String(50), nullable=False)  # Matemática ou Português
    total_questoes = db.Column(db.Integer, nullable=False)
    questoes = db.relationship('BlocoQuestao', backref='bloco', lazy=True, cascade='all, delete-orphan')

class BlocoQuestao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey('bloco_caderno.id'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)  # Ordem da questão no bloco
    questao = db.relationship('Questao', backref='blocos')

class ResultadoAluno(db.Model):
    """Tabela para armazenar os resultados dos alunos nas provas"""
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    caderno_id = db.Column(db.Integer, db.ForeignKey('caderno.id'), nullable=False)
    fez_prova = db.Column(db.Boolean, default=False)
    total_questoes = db.Column(db.Integer, default=0)
    total_acertos = db.Column(db.Integer, default=0)
    percentual_acertos = db.Column(db.Float, default=0.0)
    data_lancamento = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref='resultados')
    # Relacionamento com respostas individuais
    respostas = db.relationship('RespostaAluno', backref='resultado_ref', lazy=True, cascade='all, delete-orphan')

class RespostaAluno(db.Model):
    """Tabela para armazenar as respostas individuais dos alunos"""
    id = db.Column(db.Integer, primary_key=True)
    resultado_id = db.Column(db.Integer, db.ForeignKey('resultado_aluno.id'), nullable=False)
    bloco_id = db.Column(db.Integer, db.ForeignKey('bloco_caderno.id'), nullable=False)
    questao_ordem = db.Column(db.Integer, nullable=False)  # Ordem da questão no bloco (1, 2, 3...)
    resposta_marcada = db.Column(db.String(1), nullable=False)  # A, B, C, D
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'), nullable=True)  # Referência à questão real
    resposta_correta = db.Column(db.String(1), nullable=True)  # A alternativa correta
    acertou = db.Column(db.Boolean, default=False)
    
    # Relacionamentos - removidos backref para evitar conflitos
    resultado = db.relationship('ResultadoAluno')
    bloco = db.relationship('BlocoCaderno')
    questao = db.relationship('Questao')

def init_db():
    print('[LOG] Chamando init_db() - URI:', db.engine.url)
    db.create_all()
    print('[LOG] Tabelas criadas no banco')
    
    # Criar usuário admin padrão se não existir
    if not User.query.filter_by(email='admin@escola.com').first():
        admin = User(
            name='Administrador',
            email='admin@escola.com',
            school='Escola Modelo'
        )
        admin.set_password('senha123')
        db.session.add(admin)
        print("👤 Usuário admin criado")
    
    # Criar habilidades de exemplo
    if not Habilidade.query.first():
        habilidades = [
            Habilidade(
                codigo='EF05MA01',
                componente='Matemática',
                ano=5,
                descricao='Resolver problemas com números naturais',
                objetos_conhecimento='["Operações básicas", "Resolução de problemas"]'
            ),
            Habilidade(
                codigo='EF05LP03',
                componente='Língua Portuguesa',
                ano=5,
                descricao='Leitura e compreensão de textos',
                objetos_conhecimento='["Interpretação textual", "Compreensão leitora"]'
            )
        ]
        db.session.add_all(habilidades)
        print("📚 Habilidades de exemplo criadas")
    
    db.session.commit()
    print("✅ Banco de dados inicializado com sucesso!")

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def create_user(name, email, password, school):
    new_user = User(name=name, email=email, school=school)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user