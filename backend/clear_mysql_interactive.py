import os
from database import db
from app import app
from sqlalchemy import text

def clear_mysql_database():
    print("=== CONFIGURAÇÃO DO MYSQL ===")
    print("Por favor, forneça as credenciais do seu banco MySQL:")
    
    host = input("Host (padrão: localhost): ").strip() or 'localhost'
    user = input("Usuário (padrão: root): ").strip() or 'root'
    password = input("Senha (deixe vazio se não houver): ").strip()
    database = input("Nome do banco (padrão: eduplataforma): ").strip() or 'eduplataforma'
    
    # Configurar credenciais
    os.environ['MYSQL_HOST'] = host
    os.environ['MYSQL_USER'] = user
    os.environ['MYSQL_PASSWORD'] = password
    os.environ['MYSQL_DB'] = database
    
    try:
        with app.app_context():
            print(f"\n=== TESTANDO CONEXÃO ===")
            print(f"Conectando em: {user}@{host}/{database}")
            
            # Testar conexão
            db.session.execute(text("SELECT 1"))
            print("✅ Conexão estabelecida!")
            
            # Verificar se o banco existe
            result = db.session.execute(text("SELECT DATABASE()"))
            current_db = result.scalar()
            print(f"Banco atual: {current_db}")
            
            # Obter todas as tabelas
            result = db.session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            
            print(f"\n📋 Tabelas encontradas: {len(tables)}")
            if tables:
                for table in tables:
                    # Contar registros em cada tabela
                    try:
                        count_result = db.session.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                        count = count_result.scalar()
                        print(f"  - {table}: {count} registros")
                    except Exception as e:
                        print(f"  - {table}: Erro ao contar - {e}")
            else:
                print("ℹ️ Nenhuma tabela encontrada no banco.")
                return
            
            # Confirmar limpeza
            print(f"\n⚠️  ATENÇÃO: Isso vai APAGAR TODOS OS DADOS de {len(tables)} tabelas!")
            confirma = input("Tem certeza? Digite 'SIM' para confirmar: ")
            
            if confirma.upper() != 'SIM':
                print("❌ Operação cancelada.")
                return
            
            print("\n=== LIMPANDO BANCO MYSQL ===")
            
            # Desabilitar verificação de chaves estrangeiras temporariamente
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # Apagar dados de todas as tabelas
            print("🗑️ Apagando dados de todas as tabelas...")
            success_count = 0
            for table in tables:
                try:
                    db.session.execute(text(f"DELETE FROM `{table}`"))
                    print(f"  ✅ Tabela '{table}' limpa")
                    success_count += 1
                except Exception as e:
                    print(f"  ❌ Erro ao limpar '{table}': {e}")
            
            # Reabilitar verificação de chaves estrangeiras
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # Confirmar mudanças
            db.session.commit()
            
            print(f"\n✅ LIMPEZA CONCLUÍDA!")
            print(f"📊 {success_count}/{len(tables)} tabelas foram limpas com sucesso.")
            
            # Verificar se está vazio
            print("\n📊 Verificação final...")
            total_records = 0
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                    count = result.scalar()
                    total_records += count
                    if count > 0:
                        print(f"  ⚠️ {table}: {count} registros restantes")
                    else:
                        print(f"  ✅ {table}: vazia")
                except Exception as e:
                    print(f"  ❌ {table}: Erro ao verificar - {e}")
            
            if total_records == 0:
                print("\n🎉 BANCO COMPLETAMENTE LIMPO!")
            else:
                print(f"\n⚠️ Ainda há {total_records} registros no banco.")
                    
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Possíveis causas:")
        print("1. MySQL não está rodando")
        print("2. Credenciais incorretas")
        print("3. Banco 'eduplataforma' não existe")
        print("4. Usuário sem permissões adequadas")

if __name__ == "__main__":
    clear_mysql_database() 