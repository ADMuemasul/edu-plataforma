import os
import logging
from flask import Blueprint, request, jsonify, current_app, session
from openai import OpenAI
import traceback

ai_bp = Blueprint('ai', __name__)

# Configurar a chave da API OpenAI usando variável de ambiente
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logging.warning("OPENAI_API_KEY não configurada. Funcionalidade de IA em modo fallback.")
    client = None
else:
    try:
        client = OpenAI(api_key=api_key)
        logging.info("✅ OpenAI client inicializado com sucesso! Planos personalizados habilitados.")
        print("🤖 OpenAI configurada! Planos de aula serão gerados por IA.")
    except Exception as e:
        logging.error(f"Erro ao inicializar cliente OpenAI: {e}")
        client = None

def gerar_plano_modelo(componente, ano, tema, habilidades, objetivos):
    """Gera um plano de aula modelo quando a IA não está disponível"""
    return f"""
# 📚 PLANO DE AULA: {tema}

## 🎯 INFORMAÇÕES GERAIS
- **Componente Curricular:** {componente}
- **Ano/Série:** {ano}º ano do Ensino Fundamental
- **Tema:** {tema}
- **Duração:** 50 minutos
- **Modalidade:** Presencial

## 📝 HABILIDADES BNCC
{habilidades}

## 🎯 OBJETIVOS DE APRENDIZAGEM
{objetivos}

## 📋 OBJETIVOS ESPECÍFICOS
- Compreender os conceitos fundamentais relacionados ao tema
- Desenvolver habilidades práticas através de atividades direcionadas
- Aplicar o conhecimento adquirido em situações do cotidiano
- Participar ativamente das discussões e atividades propostas

## 🛠️ MATERIAIS NECESSÁRIOS
- Quadro e giz/marcador
- Material didático (livros, apostilas)
- Recursos audiovisuais (quando disponível)
- Material para atividades práticas
- Caderno e material de escrita dos alunos

## 📚 DESENVOLVIMENTO DA AULA

### 🚀 Introdução (10 minutos)
- **Acolhida:** Recepção dos alunos e chamada
- **Motivação:** Apresentação do tema através de pergunta instigante ou situação-problema
- **Objetivos:** Explicação clara do que será aprendido na aula
- **Conhecimentos prévios:** Levantamento do que os alunos já sabem sobre o tema

### 🎓 Desenvolvimento (30 minutos)
- **Apresentação do conteúdo:** Explicação teórica do tema de forma didática e interativa
- **Exemplos práticos:** Demonstração de situações reais relacionadas ao conteúdo
- **Atividade dirigida:** Exercício prático orientado pelo professor
- **Discussão:** Momento para esclarecimento de dúvidas e participação ativa dos alunos

### 🎯 Conclusão (10 minutos)
- **Síntese:** Resumo dos pontos principais abordados
- **Aplicação:** Discussão sobre como aplicar o conhecimento no dia a dia
- **Avaliação formativa:** Verificação da compreensão através de perguntas
- **Próximos passos:** Apresentação do que será visto na próxima aula

## 📊 AVALIAÇÃO
- **Formativa:** Observação da participação e compreensão durante a aula
- **Diagnóstica:** Verificação através de perguntas e respostas
- **Atividade prática:** Exercício para fixação do conteúdo
- **Autoavaliação:** Reflexão dos alunos sobre seu próprio aprendizado

## 🏠 ATIVIDADES COMPLEMENTARES
- **Para casa:** Exercícios de fixação relacionados ao tema
- **Pesquisa:** Investigação sobre aspectos específicos do conteúdo
- **Leitura complementar:** Textos adicionais para aprofundamento
- **Projeto:** Trabalho prático para aplicação dos conhecimentos

## 🔍 ESTRATÉGIAS DIFERENCIADAS
- **Alunos com dificuldades:** Atenção individualizada e exercícios adaptados
- **Alunos avançados:** Atividades de aprofundamento e desafios extras
- **Recursos visuais:** Uso de imagens, gráficos e esquemas para facilitar a compreensão
- **Metodologias ativas:** Incentivo à participação e protagonismo dos alunos

## 📚 REFERÊNCIAS
- Base Nacional Comum Curricular (BNCC)
- Livro didático adotado pela escola
- Recursos pedagógicos complementares
- Materiais de apoio do professor

---
*Plano gerado pelo Sistema EDU-PLATAFORMA - Versão modelo educacional*
*Este plano deve ser adaptado conforme as necessidades específicas da turma*
"""

@ai_bp.route('/gerar-plano', methods=['POST'])
def gerar_plano():
    try:
        current_app.logger.info("Iniciando geração de plano de aula")
        
        # Verificar se o usuário está logado
        if 'user_id' not in session:
            current_app.logger.warning("Tentativa de acesso sem autenticação")
            return jsonify({"success": False, "error": "Usuário não autenticado"}), 401

        # Obter dados do formulário
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Dados não fornecidos"}), 400
            
        componente = data.get('componente', '').strip()
        ano = data.get('ano', '').strip()
        tema = data.get('tema', '').strip()
        habilidades = data.get('habilidades', '').strip()
        objetivos = data.get('objetivos', '').strip()
        
        current_app.logger.info(f"Dados recebidos: componente={componente}, ano={ano}, tema={tema}")
        
        # Validar dados
        if not all([componente, ano, tema, habilidades, objetivos]):
            return jsonify({
                "success": False, 
                "error": "Todos os campos são obrigatórios. Verifique se selecionou uma habilidade BNCC."
            }), 400

        # Tentar usar IA da OpenAI primeiro
        if client:
            try:
                current_app.logger.info("Tentando gerar plano com IA da OpenAI")
                
                # Criar prompt para a IA
                prompt = f"""
                Crie um plano de aula completo e detalhado para o componente curricular de {componente} 
                para o {ano}º ano do Ensino Fundamental, seguindo rigorosamente a BNCC.
                
                Tema da aula: {tema}
                Habilidades BNCC envolvidas: {habilidades}
                Objetivos de aprendizagem: {objetivos}
                
                Estruture o plano de aula com os seguintes elementos:
                1. Título criativo e atraente
                2. Informações gerais (duração, modalidade, etc.)
                3. Objetivos específicos e mensuráveis
                4. Habilidades da BNCC trabalhadas (com códigos)
                5. Materiais necessários
                6. Desenvolvimento detalhado (introdução, desenvolvimento, conclusão)
                7. Estratégias de avaliação
                8. Atividades complementares
                9. Referências bibliográficas
                
                Seja detalhado e prático, fornecendo exemplos concretos quando apropriado.
                Formate o texto usando markdown para melhor visualização.
                """
                
                # Chamar API da OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é um especialista em educação brasileira com 20 anos de experiência em criação de planos de aula alinhados à BNCC. Sempre responda em português brasileiro."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2500,
                    timeout=30  # Timeout de 30 segundos
                )
                
                # Extrair e formatar resposta
                plano_gerado = response.choices[0].message.content.strip()
                current_app.logger.info("Plano gerado com sucesso usando IA")
                
                return jsonify({
                    "success": True,
                    "plano": plano_gerado,
                    "tipo": "ia"
                })
                
            except Exception as e:
                current_app.logger.error(f"Erro na API OpenAI: {str(e)}")
                # Continuar para gerar plano modelo
                pass
        
        # Gerar plano modelo se IA não estiver disponível
        current_app.logger.info("Gerando plano modelo (fallback)")
        plano_modelo = gerar_plano_modelo(componente, ano, tema, habilidades, objetivos)
        
        return jsonify({
            "success": True,
            "plano": plano_modelo,
            "tipo": "modelo",
            "aviso": "Plano gerado usando modelo educacional. Para planos personalizados, configure a API OpenAI."
        })
    
    except Exception as e:
        current_app.logger.error(f"Erro geral ao gerar plano: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor. Tente novamente em alguns instantes."
        }), 500