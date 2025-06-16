#!/usr/bin/env python3
"""
Script para iniciar o servidor Flask com configuração MySQL
Uso: python servidor.py
"""

import os
import sys

def main():
    print("=" * 50)
    print("    INICIANDO SERVIDOR EDU-PLATAFORMA")
    print("=" * 50)
    print()
    
    # Configurar variáveis de ambiente MySQL
    os.environ['MYSQL_HOST'] = 'localhost'
    os.environ['MYSQL_USER'] = 'root'
    os.environ['MYSQL_PASSWORD'] = '20220015779Ma@'
    os.environ['MYSQL_DB'] = 'eduplataforma'
    
    print("Configuração MySQL:")
    print(f"Host: {os.environ['MYSQL_HOST']}")
    print(f"User: {os.environ['MYSQL_USER']}")
    print(f"Database: {os.environ['MYSQL_DB']}")
    print(f"Password: {'*' * len(os.environ['MYSQL_PASSWORD'])}")
    print()
    
    print("🚀 Iniciando Flask...")
    print("📱 URL: http://localhost:5000")
    print("🔑 Login: mateus@admin / 123123")
    print()
    print("Para parar o servidor, pressione Ctrl+C")
    print()
    
    try:
        # Importar e executar o app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main() 