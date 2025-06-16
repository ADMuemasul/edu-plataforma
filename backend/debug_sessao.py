#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, Usuario, ResultadoAluno, Aluno, Caderno
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def debug_sessao():
    app = Flask(__name__)
    
    # Configurar conexão MySQL
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DB', 'eduplataforma')
    
    import urllib.parse
    password_encoded = urllib.parse.quote_plus(password) if password else ''
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password_encoded}@{host}/{database}?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            print("=== VERIFICANDO DADOS DE SESSÃO ===")
            
            # Verificar usuários
            usuarios = Usuario.query.all()
            print(f"Usuários cadastrados: {len(usuarios)}")
            for user in usuarios:
                print(f"  ID: {user.id}, Nome: {user.nome}, Email: {user.email}")
            
            # Verificar resultados salvos
            resultados = ResultadoAluno.query.all()
            print(f"\nResultados salvos: {len(resultados)}")
            for resultado in resultados:
                aluno = Aluno.query.get(resultado.aluno_id)
                caderno = Caderno.query.get(resultado.caderno_id)
                user = Usuario.query.get(resultado.user_id)
                
                print(f"  Resultado ID: {resultado.id}")
                print(f"    Aluno: {aluno.nome if aluno else 'N/A'} (ID: {resultado.aluno_id})")
                print(f"    Caderno: {caderno.titulo if caderno else 'N/A'} (ID: {resultado.caderno_id})")
                print(f"    User: {user.nome if user else 'N/A'} (ID: {resultado.user_id})")
                print(f"    Fez Prova: {resultado.fez_prova}")
                print()
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_sessao() 