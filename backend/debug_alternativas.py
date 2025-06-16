#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, BlocoQuestao, Questao, Alternativa, BlocoCaderno
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def debug_alternativas():
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
            print("=== VERIFICANDO ALTERNATIVAS CORRETAS ===")
            
            # Buscar um bloco específico para teste
            bloco = BlocoCaderno.query.first()
            print(f"\nTeste com Bloco ID: {bloco.id} - {bloco.componente}")
            
            # Buscar questões do bloco
            questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco.id).order_by(BlocoQuestao.ordem).all()
            
            print(f"Questões encontradas no bloco: {len(questoes_bloco)}")
            
            for questao_bloco in questoes_bloco[:5]:  # Testar primeiras 5
                print(f"\n✓ Questão Bloco - Ordem: {questao_bloco.ordem}, Questão ID: {questao_bloco.questao_id}")
                
                # Buscar alternativas da questão
                if questao_bloco.questao_id:
                    alternativas = Alternativa.query.filter_by(
                        questao_id=questao_bloco.questao_id
                    ).order_by(Alternativa.id).all()
                    
                    print(f"  Alternativas encontradas: {len(alternativas)}")
                    
                    for i, alt in enumerate(alternativas):
                        letra = chr(65 + i)  # A, B, C, D
                        print(f"    {letra}) {alt.texto[:50]}... | Correta: {alt.correta}")
                        
                    # Encontrar resposta correta
                    resposta_correta = None
                    for i, alt in enumerate(alternativas):
                        if alt.correta:
                            resposta_correta = chr(65 + i)
                            break
                    
                    print(f"  → Resposta correta: {resposta_correta}")
                else:
                    print("  ❌ Questão ID é None!")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_alternativas() 