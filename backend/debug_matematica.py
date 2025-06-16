#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, Caderno, BlocoCaderno, BlocoQuestao, Questao, Alternativa
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def debug_matematica():
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
            print("📐 ESTRUTURA COMPLETA - BLOCO MATEMÁTICA")
            print("=" * 60)
            
            # Buscar caderno
            caderno = Caderno.query.first()
            print(f"📚 Caderno: {caderno.titulo}")
            
            # Buscar bloco de Matemática especificamente
            bloco_mat = BlocoCaderno.query.filter_by(
                caderno_id=caderno.id,
                componente='Matemática'
            ).first()
            
            if bloco_mat:
                print(f"\n🔷 BLOCO MATEMÁTICA")
                print(f"   ID: {bloco_mat.id}")
                print(f"   Ordem: {bloco_mat.ordem}")
                print(f"   Total Questões: {bloco_mat.total_questoes}")
                print("-" * 50)
                
                # Buscar TODAS as questões do bloco
                questoes_bloco = BlocoQuestao.query.filter_by(
                    bloco_id=bloco_mat.id
                ).order_by(BlocoQuestao.ordem).all()
                
                print(f"📋 QUESTÕES ENCONTRADAS: {len(questoes_bloco)}")
                print("=" * 50)
                
                # Mostrar detalhes de cada questão
                for questao_bloco in questoes_bloco:
                    print(f"\n📝 QUESTÃO {questao_bloco.ordem:02d}")
                    print(f"   Bloco ID: {questao_bloco.bloco_id}")
                    print(f"   Questão ID: {questao_bloco.questao_id}")
                    
                    if questao_bloco.questao_id:
                        # Buscar dados da questão
                        questao = Questao.query.get(questao_bloco.questao_id)
                        if questao:
                            print(f"   Enunciado: {questao.enunciado[:60]}...")
                            
                            # Buscar alternativas
                            alternativas = Alternativa.query.filter_by(
                                questao_id=questao.id
                            ).order_by(Alternativa.id).all()
                            
                            print(f"   Alternativas: {len(alternativas)}")
                            
                            resposta_correta = None
                            for i, alt in enumerate(alternativas):
                                letra = chr(65 + i)  # A, B, C, D
                                status = "✅" if alt.correta else "❌"
                                print(f"      {letra}) {alt.texto[:40]}... {status}")
                                
                                if alt.correta:
                                    resposta_correta = letra
                            
                            print(f"   🎯 RESPOSTA CORRETA: {resposta_correta}")
                        else:
                            print("   ❌ Questão não encontrada no banco!")
                    else:
                        print("   ❌ questao_id é None!")
                    
                    print("-" * 30)
                
                # Resumo do gabarito
                print(f"\n🎯 GABARITO MATEMÁTICA:")
                gabarito = []
                for questao_bloco in questoes_bloco:
                    if questao_bloco.questao_id:
                        alternativas = Alternativa.query.filter_by(
                            questao_id=questao_bloco.questao_id
                        ).order_by(Alternativa.id).all()
                        
                        for i, alt in enumerate(alternativas):
                            if alt.correta:
                                gabarito.append(chr(65 + i))
                                break
                        else:
                            gabarito.append('?')
                    else:
                        gabarito.append('?')
                
                # Mostrar gabarito em formato limpo
                print("📋 " + " ".join(f"Q{i+1:02d}:{resp}" for i, resp in enumerate(gabarito)))
                print("📋 " + " ".join(gabarito))
                
                print(f"\n📊 ESTATÍSTICAS:")
                print(f"   Total questões: {len(gabarito)}")
                print(f"   A: {gabarito.count('A')}")
                print(f"   B: {gabarito.count('B')}")
                print(f"   C: {gabarito.count('C')}")
                print(f"   D: {gabarito.count('D')}")
                print(f"   Sem resposta: {gabarito.count('?')}")
                
            else:
                print("❌ Bloco de Matemática não encontrado!")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_matematica() 