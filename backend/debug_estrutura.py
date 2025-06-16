#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, Caderno, BlocoCaderno, BlocoQuestao, Questao, Alternativa
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def debug_estrutura():
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
            print("=== VERIFICANDO ESTRUTURA DE QUESTÕES ===")
            
            # Buscar primeiro caderno
            caderno = Caderno.query.first()
            print(f"📚 Caderno: {caderno.titulo}")
            
            # Buscar blocos
            blocos = BlocoCaderno.query.filter_by(caderno_id=caderno.id).order_by(BlocoCaderno.ordem).all()
            print(f"📋 Blocos encontrados: {len(blocos)}")
            
            for bloco in blocos:
                print(f"\n🔷 Bloco {bloco.ordem} - {bloco.componente} (ID: {bloco.id})")
                
                # Buscar questões do bloco
                questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco.id).order_by(BlocoQuestao.ordem).all()
                print(f"   Questões no bloco: {len(questoes_bloco)}")
                
                for i, questao_bloco in enumerate(questoes_bloco[:3]):  # Primeiras 3
                    print(f"   Q{questao_bloco.ordem}: questao_id={questao_bloco.questao_id}")
                    
                    if questao_bloco.questao_id:
                        # Verificar se a questão existe
                        questao = Questao.query.get(questao_bloco.questao_id)
                        if questao:
                            print(f"      ✅ Questão existe: '{questao.enunciado[:50]}...'")
                            
                            # Verificar alternativas
                            alternativas = Alternativa.query.filter_by(
                                questao_id=questao.id
                            ).order_by(Alternativa.id).all()
                            
                            print(f"      Alternativas: {len(alternativas)}")
                            for j, alt in enumerate(alternativas):
                                letra = chr(65 + j)
                                status = "✅" if alt.correta else "❌"
                                print(f"         {letra}) {alt.texto[:30]}... {status}")
                        else:
                            print(f"      ❌ Questão não existe!")
                    else:
                        print(f"      ❌ questao_id é None!")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_estrutura() 