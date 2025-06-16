import os
import urllib.parse

def get_database_uri():
    """Constrói a URI do banco dinamicamente baseada nas variáveis de ambiente"""
    
    # 1. Prioridade: DATABASE_URL (Railway PostgreSQL)
    if os.environ.get('DATABASE_URL'):
        database_url = os.environ.get('DATABASE_URL')
        print(f"[DEBUG] Usando DATABASE_URL: {database_url[:50]}...")
        return database_url
    
    # 2. MYSQL_URL (Railway MySQL)
    elif os.environ.get('MYSQL_URL'):
        mysql_url = os.environ.get('MYSQL_URL')
        print(f"[DEBUG] Usando MYSQL_URL: {mysql_url[:50]}...")
        return mysql_url
    
    # 3. PostgreSQL via variáveis individuais
    elif os.environ.get('PGHOST'):
        host = os.environ.get('PGHOST')
        user = os.environ.get('PGUSER')
        password = os.environ.get('PGPASSWORD')
        database = os.environ.get('PGDATABASE')
        port = os.environ.get('PGPORT', '5432')
        
        password_encoded = urllib.parse.quote_plus(password) if password else ''
        uri = f'postgresql://{user}:{password_encoded}@{host}:{port}/{database}'
        print(f"[DEBUG] Usando PostgreSQL: postgresql://{user}:***@{host}:{port}/{database}")
        return uri
    
    # 4. SQLite apenas se explicitamente solicitado
    elif os.environ.get('USE_SQLITE') == 'true':
        db_path = os.path.join(os.path.dirname(__file__), 'eduplataforma.db')
        uri = f'sqlite:///{db_path}'
        print(f"[DEBUG] Usando SQLite: {db_path}")
        return uri
    
    # 5. MySQL local (desenvolvimento)
    else:
        host = os.environ.get('MYSQL_HOST', 'localhost')
        user = os.environ.get('MYSQL_USER', 'root')
        password = os.environ.get('MYSQL_PASSWORD', '')
        database = os.environ.get('MYSQL_DB', 'eduplataforma')
        
        password_encoded = urllib.parse.quote_plus(password) if password else ''
        uri = f'mysql+pymysql://{user}:{password_encoded}@{host}/{database}?charset=utf8mb4'
        print(f"[DEBUG] Usando MySQL local: mysql+pymysql://{user}:***@{host}/{database}")
        return uri

def is_production():
    """Detecta se está rodando em produção"""
    return (
        os.environ.get('RAILWAY_ENVIRONMENT') == 'production' or
        os.environ.get('RENDER') == 'true' or
        os.environ.get('VERCEL') == '1' or
        os.environ.get('FLASK_ENV') == 'production'
    )

class Config:
    # String de conexão será definida dinamicamente
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurações de ambiente
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production' if is_production() else 'development')
    DEBUG = not is_production()
    
    # Configurações de produção
    if is_production():
        SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32).hex())
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'max_overflow': 0
        }

# Configurações da API da BNCC
BNCC_API_URL = os.getenv('BNCC_API_URL', 'https://api.bncc.gov.br/api/habilidades')
BNCC_API_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {os.getenv('BNCC_API_KEY', '')}"
}

# Mapeamento de componentes para códigos da BNCC
BNCC_COMPONENTE_MAP = {
    'Matemática': 'MAT',
    'Língua Portuguesa': 'LP',
    'Ciências': 'CIE',
    'História': 'HIS',
    'Geografia': 'GEO',
    'Arte': 'ART',
    'Educação Física': 'EF',
    'Inglês': 'ING'
}

# Configurações de timeout para requisições
REQUEST_TIMEOUT = 30
VERIFY_SSL = is_production() 