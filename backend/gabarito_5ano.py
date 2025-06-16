#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, Caderno, BlocoCaderno, BlocoQuestao, Questao, Alternativa
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def mostrar_gabarito_5ano():
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
            print("=== GABARITO COMPLETO - 5º ANO ===\n")
            
            # Buscar cadernos do 5º ano
            cadernos_5ano = Caderno.query.filter_by(serie='5º ANO').all()
            
            for caderno in cadernos_5ano:
                print(f"📚 CADERNO: {caderno.titulo}")
                print(f"📖 SÉRIE: {caderno.serie}")
                print("-" * 50)
                
                # Buscar blocos do caderno
                blocos = BlocoCaderno.query.filter_by(caderno_id=caderno.id).order_by(BlocoCaderno.ordem).all()
                
                for bloco in blocos:
                    print(f"\n🔷 BLOCO {bloco.ordem} - {bloco.componente.upper()}")
                    print("=" * 40)
                    
                    # Buscar questões do bloco
                    questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco.id).order_by(BlocoQuestao.ordem).all()
                    
                    for questao_bloco in questoes_bloco:
                        if questao_bloco.questao_id:
                            questao = Questao.query.get(questao_bloco.questao_id)
                            
                            if questao:
                                print(f"\nQuestão {questao_bloco.ordem:02d}:")
                                print(f"📝 {questao.enunciado[:100]}...")
                                
                                # Buscar alternativas
                                alternativas = Alternativa.query.filter_by(
                                    questao_id=questao.id
                                ).order_by(Alternativa.id).all()
                                
                                resposta_correta = None
                                for i, alt in enumerate(alternativas):
                                    letra = chr(65 + i)  # A, B, C, D
                                    status = "✅" if alt.correta else "❌"
                                    print(f"   {letra}) {alt.texto[:60]}... {status}")
                                    
                                    if alt.correta:
                                        resposta_correta = letra
                                
                                print(f"🎯 RESPOSTA CORRETA: {resposta_correta or 'N/A'}")
                                print("-" * 30)
                
                print("\n" + "="*60 + "\n")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    mostrar_gabarito_5ano() 