#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, Caderno, BlocoCaderno, BlocoQuestao, Questao, Alternativa
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def debug_mapeamento():
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
            print("=== DEBUG MAPEAMENTO FRONTEND ↔ BACKEND ===\n")
            
            # Simular dados como vem do frontend (componente Português)
            caderno_id = 3  # AVALIAÇÃO 1
            componente = 'Português'
            
            print(f"📚 Testando caderno_id: {caderno_id}, componente: {componente}")
            
            # Buscar blocos filtrados por componente (como na API GET)
            blocos = BlocoCaderno.query.filter_by(
                caderno_id=caderno_id,
                componente=componente
            ).order_by(BlocoCaderno.ordem).all()
            
            print(f"🔍 Blocos encontrados: {len(blocos)}")
            
            for bloco_index, bloco in enumerate(blocos):
                print(f"\n🔷 Frontend bloco_index: {bloco_index} → Backend bloco_id: {bloco.id}")
                print(f"   Componente: {bloco.componente}, Ordem: {bloco.ordem}")
                
                # Simular questões como vem do frontend: "0-1", "0-2", "0-3"...
                questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco.id).order_by(BlocoQuestao.ordem).all()
                
                for questao_num in range(1, min(4, len(questoes_bloco)+1)):  # Testar primeiras 3
                    questao_key = f"{bloco_index}-{questao_num}"
                    print(f"   Frontend key: '{questao_key}' → Backend: bloco_id={bloco.id}, ordem={questao_num}")
                    
                    # Buscar questão real
                    questao_bloco = BlocoQuestao.query.filter_by(
                        bloco_id=bloco.id,
                        ordem=questao_num
                    ).first()
                    
                    if questao_bloco and questao_bloco.questao_id:
                        alternativas = Alternativa.query.filter_by(
                            questao_id=questao_bloco.questao_id
                        ).order_by(Alternativa.id).all()
                        
                        resposta_correta = None
                        for i, alt in enumerate(alternativas):
                            if alt.correta:
                                resposta_correta = chr(65 + i)
                                break
                        
                        print(f"      ✅ Questão encontrada: resposta_correta = {resposta_correta}")
                    else:
                        print(f"      ❌ Questão NÃO encontrada!")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_mapeamento() 