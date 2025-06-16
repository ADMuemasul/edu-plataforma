#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import db, Caderno, BlocoCaderno, BlocoQuestao, Questao, Alternativa
from flask import Flask
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def gabarito_simples():
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
            print("🎯 GABARITO - 5º ANO - AVALIAÇÃO 1")
            print("=" * 50)
            
            # Buscar todos os cadernos disponíveis
            cadernos = Caderno.query.all()
            print(f"📚 Cadernos encontrados: {len(cadernos)}")
            for cad in cadernos:
                print(f"  - {cad.titulo} (Série: {cad.serie})")
            
            # Buscar caderno específico (primeiro caderno disponível)
            caderno = cadernos[0] if cadernos else None
            
            if caderno:
                # Buscar blocos do caderno
                blocos = BlocoCaderno.query.filter_by(caderno_id=caderno.id).order_by(BlocoCaderno.ordem).all()
                
                for bloco in blocos:
                    print(f"\n📘 {bloco.componente.upper()} (Bloco {bloco.ordem})")
                    print("-" * 30)
                    
                    # Buscar questões do bloco
                    questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco.id).order_by(BlocoQuestao.ordem).all()
                    
                    respostas = []
                    for questao_bloco in questoes_bloco:
                        if questao_bloco.questao_id:
                            # Buscar alternativas
                            alternativas = Alternativa.query.filter_by(
                                questao_id=questao_bloco.questao_id
                            ).order_by(Alternativa.id).all()
                            
                            resposta_correta = None
                            for i, alt in enumerate(alternativas):
                                if alt.correta:
                                    resposta_correta = chr(65 + i)  # A, B, C, D
                                    break
                            
                            respostas.append(f"Q{questao_bloco.ordem:02d}: {resposta_correta or '?'}")
                    
                    # Mostrar respostas em formato compacto
                    for i in range(0, len(respostas), 4):
                        linha = "  ".join(respostas[i:i+4])
                        print(f"  {linha}")
                
                print("\n" + "=" * 50)
                print("🎯 GABARITO COMPLETO:")
                
                # Criar gabarito unificado
                gabarito_completo = []
                for bloco in blocos:
                    questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco.id).order_by(BlocoQuestao.ordem).all()
                    
                    for questao_bloco in questoes_bloco:
                        if questao_bloco.questao_id:
                            alternativas = Alternativa.query.filter_by(
                                questao_id=questao_bloco.questao_id
                            ).order_by(Alternativa.id).all()
                            
                            for i, alt in enumerate(alternativas):
                                if alt.correta:
                                    gabarito_completo.append(chr(65 + i))
                                    break
                
                # Mostrar gabarito em linha
                gabarito_str = " ".join(gabarito_completo)
                print(f"📋 {gabarito_str}")
                
                print(f"\n📊 Total de questões: {len(gabarito_completo)}")
                print(f"📈 Distribuição: A={gabarito_completo.count('A')}, B={gabarito_completo.count('B')}, C={gabarito_completo.count('C')}, D={gabarito_completo.count('D')}")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    gabarito_simples() 