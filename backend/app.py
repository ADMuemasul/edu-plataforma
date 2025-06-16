from flask import Flask, render_template, send_from_directory, session, redirect, url_for, send_file, jsonify, request
import os
import time
from auth import auth_bp
# from ai_integration import ai_bp  # Comentado temporariamente
from database import db, init_db, User, Escola, Turma, Aluno, PlanoAula, Habilidade, Questao, Alternativa, Caderno, BlocoCaderno, BlocoQuestao, ResultadoAluno, RespostaAluno
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from dotenv import load_dotenv
from escolas import escolas_bp
from turma import turmas_bp
from aluno import alunos_bp
from config import Config, get_database_uri
from plano_aula import plano_aula_bp
from habilidade import habilidades_bp
from flask_migrate import Migrate


# Carregar variáveis de ambiente
load_dotenv()

# Configurar caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

# Verificar se os caminhos existem
print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] FRONTEND_DIR: {FRONTEND_DIR}")
print(f"[DEBUG] STATIC_DIR: {STATIC_DIR}")
print(f"[DEBUG] Frontend exists: {os.path.exists(FRONTEND_DIR)}")
print(f"[DEBUG] Static exists: {os.path.exists(STATIC_DIR)}")

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=STATIC_DIR)
app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_ultra_segura')
app.config.from_object(Config)

# Configurar URI do banco dinamicamente
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()

# Inicializa o banco de dados com o app
db.init_app(app)

# Inicializa o Flask-Migrate para gerenciar migrações do banco de dados
migrate = Migrate(app, db)

# Registrar blueprints
app.register_blueprint(auth_bp)
# app.register_blueprint(ai_bp)  # Comentado temporariamente
app.register_blueprint(escolas_bp)
app.register_blueprint(turmas_bp)
app.register_blueprint(alunos_bp)
app.register_blueprint(plano_aula_bp)
app.register_blueprint(habilidades_bp)


# Rotas para páginas HTML
@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Application is running'}, 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    count_escolas = Escola.query.filter_by(user_id=user_id).count()
    count_turmas = Turma.query.filter_by(user_id=user_id).count()
    count_alunos = Aluno.query.filter_by(user_id=user_id).count()
    count_planos = PlanoAula.query.filter_by(user_id=user_id).count()
    count_questoes = Questao.query.filter_by(user_id=user_id).count()
    count_habilidades = Habilidade.query.count()
    return render_template('dashboard.html', user=session, count_escolas=count_escolas, count_turmas=count_turmas, count_alunos=count_alunos, count_planos=count_planos, count_questoes=count_questoes, count_habilidades=count_habilidades)

@app.route('/habilidades')
def habilidades():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('habilidades.html')

@app.route('/plano-aula')
def plano_aula():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('plano-aula.html', user=session)

@app.route('/questoes')
def questoes():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    turmas = Turma.query.filter_by(user_id=user_id).order_by(Turma.ano).all()
    return render_template('questoes.html', user=session, turmas=turmas)

@app.route('/questoes/cadastrar/<int:turma_id>')
def cadastrar_questao(turma_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    turma = Turma.query.get_or_404(turma_id)
    if turma.user_id != session['user_id']:
        return redirect(url_for('questoes'))
    habilidades = Habilidade.query.filter_by(ano=turma.ano).all()
    return render_template('cadastrar-questao.html', user=session, turma=turma, habilidades=habilidades)

@app.route('/api/questoes', methods=['POST'])
def criar_questao():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    data = request.json
    questao = Questao(
        enunciado=data['enunciado'],
        imagem=data.get('imagem'),
        habilidade_id=data['habilidade_id'],
        turma_id=data['turma_id'],
        componente=data['componente'],
        user_id=session['user_id']
    )
    
    db.session.add(questao)
    db.session.flush()  # Para obter o ID da questão
    
    for alt in data['alternativas']:
        alternativa = Alternativa(
            texto=alt['texto'],
            correta=alt['correta'],
            questao_id=questao.id
        )
        db.session.add(alternativa)
    
    db.session.commit()
    return jsonify({'message': 'Questão criada com sucesso!', 'id': questao.id}), 201

@app.route('/api/questoes', methods=['GET'])
def listar_questoes():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    turma_id = request.args.get('turma_id')
    if not turma_id:
        return jsonify({'error': 'turma_id é obrigatório'}), 400
    questoes = Questao.query.filter_by(turma_id=turma_id, user_id=session['user_id']).all()
    result = []
    for q in questoes:
        alternativas = [
            {'id': alt.id, 'texto': alt.texto, 'correta': alt.correta}
            for alt in q.alternativas
        ]
        result.append({
            'id': q.id,
            'enunciado': q.enunciado,
            'imagem': q.imagem,
            'habilidade_id': q.habilidade_id,
            'componente': q.componente,
            'alternativas': alternativas
        })
    return jsonify({'questoes': result})

@app.route('/api/questoes/<int:questao_id>', methods=['DELETE'])
def excluir_questao(questao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    questao = Questao.query.get_or_404(questao_id)
    if questao.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    db.session.delete(questao)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Questão excluída com sucesso!'})

@app.route('/api/questoes/<int:questao_id>', methods=['PUT'])
def editar_questao(questao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    questao = Questao.query.get_or_404(questao_id)
    if questao.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    data = request.json
    questao.enunciado = data['enunciado']
    questao.imagem = data.get('imagem')
    questao.habilidade_id = data['habilidade_id']
    questao.componente = data['componente']
    # Remove alternativas antigas
    for alt in questao.alternativas:
        db.session.delete(alt)
    db.session.flush()
    # Adiciona novas alternativas
    for alt in data['alternativas']:
        alternativa = Alternativa(
            texto=alt['texto'],
            correta=alt['correta'],
            questao_id=questao.id
        )
        db.session.add(alternativa)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Questão atualizada com sucesso!'})

@app.route('/api/questoes/<int:questao_id>', methods=['GET'])
def detalhar_questao(questao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    questao = Questao.query.get_or_404(questao_id)
    if questao.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    
    alternativas = [
        {'id': alt.id, 'texto': alt.texto, 'correta': alt.correta}
        for alt in questao.alternativas
    ]
    
    return jsonify({
        'id': questao.id,
        'enunciado': questao.enunciado,
        'imagem': questao.imagem,
        'habilidade_id': questao.habilidade_id,
        'componente': questao.componente,
        'alternativas': alternativas
    })

@app.route('/escolas')
def escolas():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('escola.html')

@app.route('/turmas')
def turmas():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('turma.html')

@app.route('/alunos')
def alunos():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('aluno.html')

@app.route('/cadernos')
def cadernos():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('cadernos.html')

@app.route('/lanca-resultado')
def lanca_resultado():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('lanca-resultado.html')

# Rota para gerar PDF
@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        conteudo = request.json.get('conteudo')
        if not conteudo:
            return jsonify({"error": "Conteúdo não fornecido"}), 400
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Adicionar título
        titulo = Paragraph("Plano de Aula - EduPlataforma", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 12))
        
        # Adicionar conteúdo formatado
        for linha in conteudo.split('\n'):
            if linha.strip():  # Ignorar linhas vazias
                p = Paragraph(linha, styles['BodyText'])
                story.append(p)
                story.append(Spacer(1, 5))
        
        # Construir PDF
        doc.build(story)
        
        # Retornar PDF para download
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name='plano_aula.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para servir arquivos JS da pasta frontend/js como estáticos
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

# Rota para servir arquivos CSS da pasta frontend/css como estáticos
@app.route('/static/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

@app.route('/api/cadernos', methods=['GET'])
def listar_cadernos():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    cadernos = Caderno.query.filter_by(user_id=session['user_id']).all()
    return jsonify({'cadernos': [
        {
            'id': c.id,
            'titulo': c.titulo,
            'serie': c.serie,
            'qtd_blocos': c.qtd_blocos,
            'qtd_questoes_por_bloco': c.qtd_questoes_por_bloco
        } for c in cadernos
    ]})

@app.route('/api/cadernos/estatisticas', methods=['GET'])
def estatisticas_cadernos():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        
        # Contar cadernos do usuário
        total_cadernos = Caderno.query.filter_by(user_id=user_id).count()
        
        # Contar blocos dos cadernos do usuário
        total_blocos = db.session.query(BlocoCaderno).join(Caderno).filter(Caderno.user_id == user_id).count()
        
        # Calcular total de questões estimadas (baseado na configuração dos cadernos)
        cadernos = Caderno.query.filter_by(user_id=user_id).all()
        total_questoes_estimadas = sum(c.qtd_blocos * c.qtd_questoes_por_bloco for c in cadernos)
        
        return jsonify({
            "success": True,
            "total_cadernos": total_cadernos,
            "total_blocos": total_blocos,
            "total_questoes": total_questoes_estimadas
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cadernos', methods=['POST'])
def criar_caderno():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    data = request.json
    titulo = data.get('titulo')
    serie = data.get('serie')
    qtd_blocos = int(data.get('qtd_blocos'))
    qtd_questoes_por_bloco = int(data.get('qtd_questoes_por_bloco'))
    if not all([titulo, serie, qtd_blocos, qtd_questoes_por_bloco]):
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400
    caderno = Caderno(
        titulo=titulo,
        serie=serie,
        qtd_blocos=qtd_blocos,
        qtd_questoes_por_bloco=qtd_questoes_por_bloco,
        user_id=session['user_id']
    )
    db.session.add(caderno)
    db.session.flush()
    # Criar blocos: alternando entre Português e Matemática
    componentes = ['Português', 'Matemática']
    for i in range(qtd_blocos):
        bloco = BlocoCaderno(
            caderno_id=caderno.id,
            ordem=i+1,
            componente=componentes[i % 2],
            total_questoes=qtd_questoes_por_bloco
        )
        db.session.add(bloco)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Caderno cadastrado com sucesso!'})

@app.route('/api/cadernos/<int:caderno_id>', methods=['DELETE'])
def excluir_caderno(caderno_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    caderno = Caderno.query.get_or_404(caderno_id)
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Primeiro, excluir manualmente os registros relacionados para evitar problemas de integridade
        
        # 1. Buscar todos os resultados relacionados ao caderno
        resultados = ResultadoAluno.query.filter_by(caderno_id=caderno_id).all()
        
        # 2. Para cada resultado, excluir suas respostas individuais
        for resultado in resultados:
            RespostaAluno.query.filter_by(resultado_id=resultado.id).delete()
        
        # 3. Excluir todos os resultados do caderno
        ResultadoAluno.query.filter_by(caderno_id=caderno_id).delete()
        
        # 4. Excluir questões dos blocos
        for bloco in caderno.blocos:
            BlocoQuestao.query.filter_by(bloco_id=bloco.id).delete()
        
        # 5. Agora podemos excluir o caderno seguramente (os blocos serão excluídos pelo cascade)
        db.session.delete(caderno)
        db.session.commit()
        
        print(f"✅ Caderno {caderno_id} excluído com sucesso")
        return jsonify({'success': True, 'message': 'Caderno excluído com sucesso!'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao excluir caderno {caderno_id}: {str(e)}")
        return jsonify({'error': f'Erro ao excluir caderno: {str(e)}'}), 500

@app.route('/api/cadernos/<int:caderno_id>', methods=['GET'])
def detalhar_caderno(caderno_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    caderno = Caderno.query.get_or_404(caderno_id)
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    blocos = [
        {
            'id': b.id,
            'ordem': b.ordem,
            'componente': b.componente,
            'total_questoes': b.total_questoes
        } for b in caderno.blocos
    ]
    return jsonify({
        'id': caderno.id,
        'titulo': caderno.titulo,
        'serie': caderno.serie,
        'qtd_blocos': caderno.qtd_blocos,
        'qtd_questoes_por_bloco': caderno.qtd_questoes_por_bloco,
        'blocos': blocos
    })

@app.route('/cadernos/bloco/<int:bloco_id>')
def cadastrar_questoes_bloco(bloco_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    bloco = BlocoCaderno.query.get_or_404(bloco_id)
    caderno = Caderno.query.get(bloco.caderno_id)
    if caderno.user_id != session['user_id']:
        return redirect(url_for('cadernos'))
    
    # Buscar questões do usuário para o componente curricular do bloco
    user_id = session['user_id']
    componente = bloco.componente
    serie = caderno.serie
    
    # Buscar questões do usuário que correspondam ao componente do bloco E ao ano/série
    # Primeiro buscar habilidades do componente e ano desejado
    
    # Mapear "Português" para "Língua Portuguesa" se necessário
    componente_filtro = componente
    if componente == "Português":
        componente_filtro = "Língua Portuguesa"
    
    habilidades = Habilidade.query.filter(
        Habilidade.componente == componente_filtro,
        Habilidade.ano == serie
    ).all()
    
    habilidades_ids = [h.id for h in habilidades]
    
    # Se não há habilidades, retorna lista vazia
    if not habilidades_ids:
        questoes = []
    else:
        # Buscar questões que usam essas habilidades e são do usuário
        questoes = Questao.query.filter(
            Questao.user_id == user_id,
            Questao.habilidade_id.in_(habilidades_ids)
        ).all()
    
    # Buscar questões já atribuídas ao bloco
    questoes_atribuidas = BlocoQuestao.query.filter_by(bloco_id=bloco_id).order_by(BlocoQuestao.ordem).all()
    questoes_atribuidas_ids = [bq.questao_id for bq in questoes_atribuidas]
    
    # Filtrar questões disponíveis (não atribuídas)
    questoes_disponiveis = [q.id for q in questoes if q.id not in questoes_atribuidas_ids]
    
    return render_template(
        'cadastrar-questoes-bloco.html', 
        bloco=bloco, 
        caderno=caderno, 
        questoes_ids=questoes_disponiveis,
        questoes_atribuidas_ids=questoes_atribuidas_ids,
        componente=componente,
        serie=serie
    )

@app.route('/api/cadernos/bloco/<int:bloco_id>/questoes', methods=['POST'])
def atribuir_questoes_bloco(bloco_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    bloco = BlocoCaderno.query.get_or_404(bloco_id)
    caderno = Caderno.query.get(bloco.caderno_id)
    
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    questoes_ids = data.get('questoes_ids', [])
    
    if len(questoes_ids) != bloco.total_questoes:
        return jsonify({'error': f'É necessário selecionar exatamente {bloco.total_questoes} questões'}), 400
    
    # Verificar se as questões pertencem ao usuário E são do ano correto
    # Primeiro buscar habilidades do ano do caderno
    habilidades_ids = [h.id for h in Habilidade.query.filter(Habilidade.ano == caderno.serie).all()]
    
    questoes = Questao.query.filter(
        Questao.id.in_(questoes_ids),
        Questao.user_id == session['user_id'],
        Questao.habilidade_id.in_(habilidades_ids)
    ).all()
    
    if len(questoes) != len(questoes_ids):
        return jsonify({'error': 'Uma ou mais questões inválidas'}), 400
    
    try:
        # Remover questões antigas do bloco
        BlocoQuestao.query.filter_by(bloco_id=bloco_id).delete()
        
        # Adicionar novas questões ao bloco
        for ordem, questao_id in enumerate(questoes_ids, 1):
            bloco_questao = BlocoQuestao(
                bloco_id=bloco_id,
                questao_id=questao_id,
                ordem=ordem
            )
            db.session.add(bloco_questao)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Questões atribuídas com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao salvar questões: {str(e)}'}), 500

@app.route('/api/cadernos/bloco/<int:bloco_id>/questoes', methods=['GET'])
def listar_questoes_bloco(bloco_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    bloco = BlocoCaderno.query.get_or_404(bloco_id)
    caderno = Caderno.query.get(bloco.caderno_id)
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco_id).order_by(BlocoQuestao.ordem).all()
    result = []
    for bq in questoes_bloco:
        questao = bq.questao
        habilidade = Habilidade.query.get(questao.habilidade_id)
        result.append({
            'id': questao.id,
            'enunciado': questao.enunciado,
            'ano': habilidade.ano if habilidade else None,
            'habilidade_codigo': habilidade.codigo if habilidade else None,
            'habilidade_descricao': habilidade.descricao if habilidade else None,
            'ordem': bq.ordem
        })
    return jsonify({'questoes': result})

@app.route('/api/cadernos/bloco/<int:bloco_id>/questao/<int:questao_id>', methods=['DELETE'])
def remover_questao_bloco(bloco_id, questao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    bloco = BlocoCaderno.query.get_or_404(bloco_id)
    caderno = Caderno.query.get(bloco.caderno_id)
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    bloco_questao = BlocoQuestao.query.filter_by(bloco_id=bloco_id, questao_id=questao_id).first()
    if not bloco_questao:
        return jsonify({'error': 'Questão não encontrada no bloco'}), 404
    db.session.delete(bloco_questao)
    # Ajustar ordem das demais questões
    questoes_restantes = BlocoQuestao.query.filter_by(bloco_id=bloco_id).order_by(BlocoQuestao.ordem).all()
    for idx, bq in enumerate(questoes_restantes, 1):
        bq.ordem = idx
    db.session.commit()
    return jsonify({'success': True, 'message': 'Questão removida do bloco com sucesso!'})

@app.route('/api/cadernos/bloco/<int:bloco_id>/questoes/ordenar', methods=['PATCH'])
def reordenar_questoes_bloco(bloco_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    bloco = BlocoCaderno.query.get_or_404(bloco_id)
    caderno = Caderno.query.get(bloco.caderno_id)
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    data = request.json
    nova_ordem = data.get('nova_ordem', [])  # lista de questao_id na nova ordem
    if not nova_ordem:
        return jsonify({'error': 'Lista de nova ordem não fornecida'}), 400
    questoes_bloco = BlocoQuestao.query.filter_by(bloco_id=bloco_id).all()
    questao_id_para_bq = {bq.questao_id: bq for bq in questoes_bloco}
    for idx, questao_id in enumerate(nova_ordem, 1):
        bq = questao_id_para_bq.get(questao_id)
        if bq:
            bq.ordem = idx
    db.session.commit()
    return jsonify({'success': True, 'message': 'Ordem das questões atualizada com sucesso!'})

@app.route('/api/cadernos/<int:caderno_id>/cartoes-gabarito', methods=['POST'])
def gerar_cartoes_gabarito(caderno_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Buscar o caderno e verificar se pertence ao usuário
    caderno = Caderno.query.get_or_404(caderno_id)
    if caderno.user_id != session['user_id']:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Buscar usuário logado (professor)
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Buscar turmas do ano/série do caderno para o usuário
    turmas = Turma.query.filter_by(ano=caderno.serie, user_id=session['user_id']).all()
    
    if not turmas:
        return jsonify({'error': f'Nenhuma turma encontrada para o {caderno.serie}º ano'}), 404
    
    # Buscar todos os alunos das turmas encontradas
    alunos = []
    for turma in turmas:
        alunos_turma = Aluno.query.filter_by(turma_id=turma.id, user_id=session['user_id']).all()
        for aluno in alunos_turma:
            # Buscar dados da escola
            escola = Escola.query.get(aluno.escola_id)
            alunos.append({
                'nome': aluno.nome,
                'turma': turma,
                'escola': escola
            })
    
    if not alunos:
        return jsonify({'error': 'Nenhum aluno encontrado nas turmas correspondentes'}), 404
    
    # Buscar blocos do caderno
    blocos = BlocoCaderno.query.filter_by(caderno_id=caderno_id).order_by(BlocoCaderno.ordem).all()
    
    # Gerar PDF
    try:
        pdf_buffer = gerar_pdf_cartoes_gabarito(caderno, blocos, alunos, user.name)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'cartoes_gabarito_{caderno.titulo.replace(" ", "_")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

def gerar_pdf_cartoes_gabarito(caderno, blocos, alunos, nome_professor):
    """Gera PDF com cartões gabarito para todos os alunos"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=1*cm, leftMargin=1*cm,
                          topMargin=1*cm, bottomMargin=1*cm)
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_LEFT,
        textColor=colors.black
    )
    
    story = []
    
    for i, aluno_data in enumerate(alunos):
        aluno = aluno_data
        turma = aluno['turma']
        escola = aluno['escola']
        
        # Cabeçalho do cartão
        story.append(Paragraph("CARTÃO GABARITO", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Informações do aluno e escola
        info_data = [
            ['Professor(a):', nome_professor],
            ['Escola:', escola.nome if escola else 'N/A'],
            ['Aluno(a):', aluno['nome']],
            ['Série/Ano:', f"{caderno.serie}º ano"],
            ['Turno:', turma.turno],
            ['Avaliação:', caderno.titulo]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 1*cm))
        
        # Gerar cartão gabarito para cada bloco
        for bloco in blocos:
            story.append(Paragraph(f"BLOCO {bloco.ordem} - {bloco.componente}", header_style))
            story.append(Spacer(1, 0.3*cm))
            
            # Criar grade de gabarito
            questoes_por_linha = 5
            linhas = []
            
            for linha_idx in range(0, bloco.total_questoes, questoes_por_linha):
                linha_questoes = []
                linha_alternativas = []
                
                for q_idx in range(questoes_por_linha):
                    num_questao = linha_idx + q_idx + 1
                    if num_questao <= bloco.total_questoes:
                        linha_questoes.append(f"Q{num_questao:02d}")
                        linha_alternativas.append("(A) (B) (C) (D)")
                    else:
                        linha_questoes.append("")
                        linha_alternativas.append("")
                
                linhas.append(linha_questoes)
                linhas.append(linha_alternativas)
            
            # Criar tabela do gabarito
            gabarito_table = Table(linhas, colWidths=[3.2*cm]*questoes_por_linha)
            gabarito_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.white]),
            ]))
            
            story.append(gabarito_table)
            story.append(Spacer(1, 0.8*cm))
        
        # Adicionar quebra de página entre alunos (exceto no último)
        if i < len(alunos) - 1:
            story.append(PageBreak())
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# =================== API PARA HABILIDADES FILTRADAS ===================

@app.route('/api/habilidades', methods=['GET'])
def listar_habilidades_filtradas():
    """API para listar habilidades filtradas por componente e ano - usada no frontend"""
    componente = request.args.get('componente')
    ano = request.args.get('ano')
    
    query = Habilidade.query
    
    if componente:
        # Mapear "Português" para "Língua Portuguesa" se necessário
        if componente == "Português":
            componente = "Língua Portuguesa"
        query = query.filter(Habilidade.componente == componente)
    
    if ano:
        query = query.filter(Habilidade.ano == int(ano))
    
    habilidades = query.order_by(Habilidade.codigo).all()
    
    return jsonify({
        'habilidades': [{
            'id': h.id,
            'codigo': h.codigo,
            'componente': h.componente,
            'ano': h.ano,
            'descricao': h.descricao
        } for h in habilidades]
    })

# =================== APIS PARA LANÇA RESULTADO ===================

@app.route('/api/resultados/alunos', methods=['GET'])
def listar_alunos_para_resultado():
    """Lista alunos de uma turma para lançamento de resultados"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    turma_id = request.args.get('turma_id')
    caderno_id = request.args.get('caderno_id') 
    componente = request.args.get('componente')
    
    if not all([turma_id, caderno_id]):
        return jsonify({'error': 'turma_id e caderno_id são obrigatórios'}), 400
    
    # Verificar se a turma pertence ao usuário
    turma = Turma.query.filter_by(id=turma_id, user_id=session['user_id']).first()
    if not turma:
        return jsonify({'error': 'Turma não encontrada'}), 404
    
    # Verificar se o caderno pertence ao usuário  
    caderno = Caderno.query.filter_by(id=caderno_id, user_id=session['user_id']).first()
    if not caderno:
        return jsonify({'error': 'Caderno não encontrado'}), 404
    
    # Buscar alunos da turma
    alunos = Aluno.query.filter_by(turma_id=turma_id, user_id=session['user_id']).all()
    
    alunos_dados = []
    for aluno in alunos:
        # Verificar se já existe resultado para este aluno neste caderno
        resultado = ResultadoAluno.query.filter_by(
            aluno_id=aluno.id, 
            caderno_id=caderno_id
        ).first()
        
        if resultado:
            status = 'concluido' if resultado.fez_prova else 'pendente'
            acertos = resultado.total_acertos
            total = resultado.total_questoes
            percentual = resultado.percentual_acertos
        else:
            status = 'pendente'
            acertos = 0
            total = 0
            percentual = 0.0
        
        # Buscar informações da escola
        escola = Escola.query.get(aluno.escola_id)
        
        alunos_dados.append({
            'id': aluno.id,
            'nome': aluno.nome,
            'sexo': aluno.sexo,
            'escola': escola.nome if escola else 'N/A',
            'turma': turma.nome,
            'status': status,
            'acertos': acertos,
            'total': total,
            'percentual': round(percentual, 1)
        })
    
    return jsonify({'alunos': alunos_dados})

@app.route('/api/resultados', methods=['GET'])
def listar_resultados():
    """API para listar resultados dos alunos com base nos filtros aplicados"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        print(f"[DEBUG] Iniciando listar_resultados para user_id: {session['user_id']}")
        # Obter parâmetros dos filtros
        serie = request.args.get('serie')
        escola_id = request.args.get('escola')
        turma_id = request.args.get('turma')
        caderno_id = request.args.get('caderno')
        componente = request.args.get('componente')
        
        print(f"[DEBUG] Filtros recebidos: serie={serie}, escola={escola_id}, turma={turma_id}, caderno={caderno_id}, componente={componente}")
        
        if not all([serie, escola_id, turma_id, caderno_id, componente]):
            return jsonify({'error': 'Todos os filtros são obrigatórios'}), 400
        
        # Buscar o caderno e seus blocos
        caderno = Caderno.query.get_or_404(caderno_id)
        if caderno.user_id != session['user_id']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar blocos do caderno
        blocos = BlocoCaderno.query.filter_by(caderno_id=caderno_id).order_by(BlocoCaderno.ordem).all()
        
        # Filtrar blocos por componente se não for "Ambos"
        if componente != 'Ambos':
            blocos = [b for b in blocos if b.componente == componente]
        
        # Calcular total de questões com base nos blocos filtrados
        total_questoes = sum(bloco.total_questoes for bloco in blocos)
        
        # Buscar alunos da turma
        alunos = Aluno.query.filter_by(turma_id=turma_id, user_id=session['user_id']).all()
        
        # Buscar resultados existentes para cada aluno
        resultados_alunos = []
        for aluno in alunos:
            # Buscar resultado existente
            resultado = ResultadoAluno.query.filter_by(
                aluno_id=aluno.id,
                caderno_id=caderno_id,
                user_id=session['user_id']
            ).first()
            
            # Buscar dados da turma
            turma = Turma.query.get(aluno.turma_id)
            
            if resultado and resultado.fez_prova:
                print(f"[DEBUG] Aluno {aluno.nome} - Resultado encontrado: fez_prova={resultado.fez_prova}")
                print(f"[DEBUG] Total acertos no banco: {resultado.total_acertos}, Total questões: {resultado.total_questoes}")
                
                # Recalcular acertos baseado no componente filtrado
                if componente != 'Ambos':
                    # Buscar respostas do resultado específico filtradas por componente
                    respostas = db.session.query(RespostaAluno).join(
                        BlocoCaderno, RespostaAluno.bloco_id == BlocoCaderno.id
                    ).filter(
                        RespostaAluno.resultado_id == resultado.id,
                        BlocoCaderno.componente == componente
                    ).all()
                    acertos_filtrado = sum(1 for r in respostas if r.acertou)
                    print(f"[DEBUG] Componente filtrado: {componente}, Acertos: {acertos_filtrado}/{len(respostas)}")
                else:
                    acertos_filtrado = resultado.total_acertos
                    print(f"[DEBUG] Usando total_acertos do resultado: {acertos_filtrado}")
                
                resultados_alunos.append({
                    'id': aluno.id,
                    'nome': aluno.nome,
                    'turma_nome': turma.nome if turma else 'N/A',
                    'status': 'concluido',
                    'acertos': acertos_filtrado,
                    'total_questoes': total_questoes,
                    'percentual': round((acertos_filtrado / total_questoes) * 100, 1) if total_questoes > 0 else 0
                })
            else:
                print(f"[DEBUG] Aluno {aluno.nome} - Nenhum resultado ou não fez prova")
                resultados_alunos.append({
                    'id': aluno.id,
                    'nome': aluno.nome,
                    'turma_nome': turma.nome if turma else 'N/A',
                    'status': 'pendente',
                    'acertos': 0,
                    'total_questoes': total_questoes,
                    'percentual': 0
                })
        
        # Preparar dados do caderno para o frontend
        caderno_data = {
            'id': caderno.id,
            'titulo': caderno.titulo,
            'serie': caderno.serie,
            'blocos': [{
                'id': bloco.id,
                'ordem': bloco.ordem,
                'componente': bloco.componente,
                'total_questoes': bloco.total_questoes
            } for bloco in blocos]
        }
        
        print(f"[DEBUG] Retornando {len(resultados_alunos)} alunos")
        
        return jsonify({
            'success': True,
            'caderno': caderno_data,
            'alunos': resultados_alunos
        })
                
    except Exception as e:
        print(f"[ERROR] Erro em listar_resultados: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/resultados', methods=['POST'])
def salvar_resultado():
    """API para salvar resultado de um aluno"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.json
        aluno_id = data.get('aluno_id')
        caderno_id = data.get('caderno_id')
        status = data.get('status', 'pendente')
        fez_prova = (status == 'concluido')
        respostas = data.get('respostas', {})
        
        if not aluno_id or not caderno_id:
            return jsonify({'error': 'aluno_id e caderno_id são obrigatórios'}), 400
        
        # Verificar se o aluno pertence ao usuário
        aluno = Aluno.query.get_or_404(aluno_id)
        if aluno.user_id != session['user_id']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Verificar se o caderno pertence ao usuário
        caderno = Caderno.query.get_or_404(caderno_id)
        if caderno.user_id != session['user_id']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar ou criar resultado do aluno
        resultado = ResultadoAluno.query.filter_by(
            aluno_id=aluno_id,
            caderno_id=caderno_id,
            user_id=session['user_id']
        ).first()
        
        if not resultado:
            resultado = ResultadoAluno(
                aluno_id=aluno_id,
                caderno_id=caderno_id,
                user_id=session['user_id']
            )
            db.session.add(resultado)
            db.session.flush()  # Gerar ID antes de usar
        
        # Atualizar status da prova
        resultado.fez_prova = fez_prova
        
        if fez_prova and respostas:
            # Limpar respostas anteriores
            if resultado.id:
                RespostaAluno.query.filter_by(resultado_id=resultado.id).delete()
            
            # Buscar blocos do caderno
            blocos = BlocoCaderno.query.filter_by(caderno_id=caderno_id).order_by(BlocoCaderno.ordem).all()
            
            total_questoes = 0
            total_acertos = 0
            
            # Processar respostas por bloco
            for bloco_index, bloco in enumerate(blocos):
                for questao_num in range(1, bloco.total_questoes + 1):
                    questao_key = f"{bloco_index}-{questao_num}"
                    
                    if questao_key in respostas:
                        resposta_marcada = respostas[questao_key]
                        
                        # Buscar questão real do bloco para verificar resposta correta
                        questao_bloco = BlocoQuestao.query.filter_by(
                            bloco_id=bloco.id,
                            ordem=questao_num
                        ).first()
                        
                        resposta_correta = None
                        acertou = False
                        
                        print(f"[DEBUG] Processando questão {questao_key}: resposta={resposta_marcada}")
                        
                        if questao_bloco and questao_bloco.questao_id:
                            print(f"[DEBUG] Questão encontrada ID: {questao_bloco.questao_id}")
                            
                            # Buscar todas as alternativas da questão ordenadas por ID
                            alternativas = Alternativa.query.filter_by(
                                questao_id=questao_bloco.questao_id
                            ).order_by(Alternativa.id).all()
                            
                            print(f"[DEBUG] Encontradas {len(alternativas)} alternativas para questão {questao_bloco.questao_id}")
                            
                            if alternativas:
                                # Debug: mostrar todas as alternativas
                                for i, alt in enumerate(alternativas):
                                    letra = chr(65 + i)
                                    print(f"[DEBUG] Alt {i}: {letra} - correta={alt.correta} - texto='{alt.texto[:30]}...'")
                                
                                # Encontrar qual alternativa é a correta e mapear para letra
                                resposta_correta = None
                                for i, alt in enumerate(alternativas):
                                    if alt.correta:
                                        resposta_correta = chr(65 + i)  # A, B, C, D
                                        print(f"[DEBUG] ✅ Resposta correta encontrada: {resposta_correta}")
                                        break
                                
                                if resposta_correta:
                                    acertou = (resposta_marcada == resposta_correta)
                                    print(f"[DEBUG] Comparação: '{resposta_marcada}' == '{resposta_correta}' = {acertou}")
                                else:
                                    resposta_correta = 'N/A'
                                    acertou = False
                                    print(f"[DEBUG] ❌ PROBLEMA: Nenhuma alternativa correta encontrada!")
                            else:
                                resposta_correta = 'N/A'
                                acertou = False
                                print(f"[DEBUG] ❌ PROBLEMA: Nenhuma alternativa encontrada para questão {questao_bloco.questao_id}")
                        else:
                            resposta_correta = 'N/A'
                            acertou = False
                            print(f"[DEBUG] ❌ PROBLEMA: Questão do bloco não encontrada - bloco_id={bloco.id}, ordem={questao_num}")
                        
                        # Salvar resposta
                        resposta_aluno = RespostaAluno(
                            resultado_id=resultado.id,
                            bloco_id=bloco.id,
                            questao_ordem=questao_num,
                            resposta_marcada=resposta_marcada,
                            questao_id=questao_bloco.questao_id if questao_bloco else None,
                            resposta_correta=resposta_correta,
                            acertou=acertou
                        )
                        db.session.add(resposta_aluno)
                        
                        total_questoes += 1
                        if acertou:
                            total_acertos += 1
            
            # Atualizar totais no resultado
            resultado.total_questoes = total_questoes
            resultado.total_acertos = total_acertos
            resultado.percentual_acertos = (total_acertos / total_questoes * 100) if total_questoes > 0 else 0
            
            print(f"[DEBUG] Salvando resultado: {total_acertos}/{total_questoes} acertos ({resultado.percentual_acertos:.1f}%)")
        
        else:
            # Se não fez prova, zerar contadores
            resultado.total_questoes = 0
            resultado.total_acertos = 0
            resultado.percentual_acertos = 0
            
            print(f"[DEBUG] Zerando contadores - não fez prova ou sem respostas")
            
            # Limpar respostas
            if resultado.id:
                RespostaAluno.query.filter_by(resultado_id=resultado.id).delete()
        
        db.session.commit()
        print(f"[DEBUG] Resultado salvo no banco - ID: {resultado.id}")
        
        return jsonify({
            'success': True,
            'message': 'Resultado salvo com sucesso!',
            'resultado': {
                'fez_prova': resultado.fez_prova,
                'total_acertos': resultado.total_acertos,
                'total_questoes': resultado.total_questoes,
                'percentual_acertos': resultado.percentual_acertos
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao salvar resultado: {str(e)}'}), 500

@app.route('/api/resultados/<int:aluno_id>/<int:caderno_id>', methods=['GET'])
def buscar_respostas_aluno(aluno_id, caderno_id):
    """API para buscar respostas salvas de um aluno específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o aluno e caderno pertencem ao usuário
        aluno = Aluno.query.get_or_404(aluno_id)
        caderno = Caderno.query.get_or_404(caderno_id)
        
        if aluno.user_id != session['user_id'] or caderno.user_id != session['user_id']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar resultado do aluno
        resultado = ResultadoAluno.query.filter_by(
            aluno_id=aluno_id,
            caderno_id=caderno_id,
            user_id=session['user_id']
        ).first()
        
        respostas_salvas = {}
        fez_prova = False
        
        if resultado:
            fez_prova = resultado.fez_prova
            
            if fez_prova:
                # Buscar respostas do aluno
                respostas = RespostaAluno.query.filter_by(resultado_id=resultado.id).all()
                
                # Buscar blocos do caderno para mapear ordem
                blocos = BlocoCaderno.query.filter_by(caderno_id=caderno_id).order_by(BlocoCaderno.ordem).all()
                
                # Mapear respostas para o formato esperado pelo frontend
                for resposta in respostas:
                    # Encontrar índice do bloco
                    bloco_index = None
                    for i, bloco in enumerate(blocos):
                        if bloco.id == resposta.bloco_id:
                            bloco_index = i
                            break
                    
                    if bloco_index is not None:
                        questao_key = f"{bloco_index}-{resposta.questao_ordem}"
                        respostas_salvas[questao_key] = resposta.resposta_marcada
        
        return jsonify({
            'success': True,
            'fez_prova': fez_prova,
            'respostas': respostas_salvas
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar respostas: {str(e)}'}), 500

# Inicialização do banco de dados e execução do servidor
if __name__ == '__main__':
    print("Caminho absoluto do template_folder:", os.path.abspath(app.template_folder))
    print("Caminho absoluto do static_folder:", os.path.abspath(app.static_folder))
    try:
        with app.app_context():
            init_db()
        print("[SUCCESS] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    print(f"[INFO] Starting server on port {port}, debug={debug_mode}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)