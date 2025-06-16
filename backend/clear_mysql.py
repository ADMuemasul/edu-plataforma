import os
from database import db
from app import app
from sqlalchemy import text

def try_mysql_connection(host, user, password, database):
    """Tenta conectar com diferentes configurações"""
    try:
        # Configurar credenciais
        os.environ['MYSQL_HOST'] = host
        os.environ['MYSQL_USER'] = user
        os.environ['MYSQL_PASSWORD'] = password
        os.environ['MYSQL_DB'] = database
        
        # Recriar app context com novas configurações
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            return True
    except:
        return False

def clear_mysql_database():
    # Configurações comuns do MySQL
    configs = [
        ('localhost', 'root', '', 'eduplataforma'),
        ('localhost', 'root', 'root', 'eduplataforma'),
        ('localhost', 'root', 'password', 'eduplataforma'),
        ('localhost', 'root', '123456', 'eduplataforma'),
        ('127.0.0.1', 'root', '', 'eduplataforma'),
        ('localhost', 'eduplataforma', '', 'eduplataforma'),
        ('localhost', 'eduplataforma', 'eduplataforma', 'eduplataforma'),
    ]
    
    print("=== TENTANDO CONECTAR AO MYSQL ===")
    
    connection_found = False
    for host, user, password, database in configs:
        print(f"Tentando: {user}@{host} (senha: {'sim' if password else 'não'})")
        if try_mysql_connection(host, user, password, database):
            print(f"✅ Conexão estabelecida com: {user}@{host}")
            connection_found = True
            break
        else:
            print(f"❌ Falhou")
    
    if not connection_found:
        print("\n❌ Não foi possível conectar ao MySQL com nenhuma configuração.")
        print("\n💡 Configurações testadas:")
        for host, user, password, database in configs:
            print(f"  - {user}@{host} (senha: {'sim' if password else 'não'})")
        
        print("\n🔧 Para resolver:")
        print("1. Verifique se o MySQL/XAMPP está rodando")
        print("2. Verifique qual é o usuário e senha corretos")
        print("3. Edite o script e adicione suas credenciais")
        return
    
    try:
        with app.app_context():
            print("\n=== LIMPANDO BANCO MYSQL ===")
            print(f"URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Desabilitar verificação de chaves estrangeiras temporariamente
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # Obter todas as tabelas
            result = db.session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            
            print(f"\n📋 Tabelas encontradas: {len(tables)}")
            for table in tables:
                print(f"  - {table}")
            
            if not tables:
                print("ℹ️ Nenhuma tabela encontrada no banco.")
                return
            
            # Apagar dados de todas as tabelas
            print("\n🗑️ Apagando dados de todas as tabelas...")
            for table in tables:
                try:
                    db.session.execute(text(f"DELETE FROM `{table}`"))
                    print(f"  ✅ Tabela '{table}' limpa")
                except Exception as e:
                    print(f"  ❌ Erro ao limpar '{table}': {e}")
            
            # Reabilitar verificação de chaves estrangeiras
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # Confirmar mudanças
            db.session.commit()
            
            print("\n✅ BANCO MYSQL COMPLETAMENTE LIMPO!")
            print("Todas as tabelas foram esvaziadas mas mantidas na estrutura.")
            
            # Verificar se está vazio
            print("\n📊 Verificando se está vazio...")
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                    count = result.scalar()
                    print(f"  - {table}: {count} registros")
                except Exception as e:
                    print(f"  - {table}: Erro ao contar - {e}")
                    
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")

if __name__ == "__main__":
    # ATENÇÃO: Este script vai APAGAR TODOS OS DADOS do banco MySQL!
    resposta = input("⚠️  ATENÇÃO: Isso vai APAGAR TODOS OS DADOS do banco MySQL 'eduplataforma'!\nTem certeza? Digite 'SIM' para confirmar: ")
    
    if resposta.upper() == 'SIM':
        clear_mysql_database()
    else:
        print("❌ Operação cancelada.") 