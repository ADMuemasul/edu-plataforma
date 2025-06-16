#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, ResultadoAluno, RespostaAluno, Aluno, Caderno
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def debug_acertos():
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
            print("=== VERIFICANDO RESULTADOS E ACERTOS ===")
            resultados = ResultadoAluno.query.all()
            
            for resultado in resultados:
                aluno = Aluno.query.get(resultado.aluno_id)
                caderno = Caderno.query.get(resultado.caderno_id)
                
                print(f"\n✓ Resultado ID: {resultado.id}")
                print(f"  Aluno: {aluno.nome if aluno else 'N/A'}")
                print(f"  Caderno: {caderno.titulo if caderno else 'N/A'}")
                print(f"  Fez Prova: {resultado.fez_prova}")
                print(f"  Total Questões: {resultado.total_questoes}")
                print(f"  Total Acertos: {resultado.total_acertos}")
                print(f"  Percentual: {resultado.percentual_acertos}%")
                
                # Verificar respostas individuais
                respostas = RespostaAluno.query.filter_by(resultado_id=resultado.id).all()
                acertos_reais = sum(1 for r in respostas if r.acertou)
                
                print(f"  Respostas no banco: {len(respostas)}")
                print(f"  Acertos calculados: {acertos_reais}")
                
                if acertos_reais != resultado.total_acertos:
                    print(f"  ❌ DIVERGÊNCIA! Banco: {resultado.total_acertos}, Calculado: {acertos_reais}")
                else:
                    print(f"  ✅ Acertos corretos!")
                
                # Mostrar algumas respostas para debug
                print("  Primeiras 5 respostas:")
                for i, resposta in enumerate(respostas[:5]):
                    print(f"    {i+1}. Questão {resposta.questao_ordem}: {resposta.resposta_marcada} -> Correta: {resposta.resposta_correta} | Acertou: {resposta.acertou}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_acertos() 