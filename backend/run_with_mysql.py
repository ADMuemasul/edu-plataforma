import os
import sys

def setup_mysql_env():
    """Configura as variáveis de ambiente para MySQL"""
    os.environ['MYSQL_HOST'] = 'localhost'
    os.environ['MYSQL_USER'] = 'root'
    os.environ['MYSQL_PASSWORD'] = '20220015779Ma@'
    os.environ['MYSQL_DB'] = 'eduplataforma'
    
    print("=== CONFIGURAÇÃO MYSQL ===")
    print(f"Host: {os.environ['MYSQL_HOST']}")
    print(f"User: {os.environ['MYSQL_USER']}")
    print(f"Database: {os.environ['MYSQL_DB']}")
    print(f"Password: {'*' * len(os.environ['MYSQL_PASSWORD'])}")
    print()

if __name__ == "__main__":
    # Configurar variáveis de ambiente
    setup_mysql_env()
    
    # Importar e executar o app
    print("🚀 Iniciando Flask com MySQL...")
    from app import app
    
    # Executar o Flask
    app.run(debug=True, host='0.0.0.0', port=5000) 