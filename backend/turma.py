from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from database import db, Turma, Escola
from math import ceil

turmas_bp = Blueprint('turmas_bp', __name__)

@turmas_bp.route('/')
def view_turmas():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    escolas = Escola.query.filter_by(user_id=user_id).all()
    turmas = Turma.query.filter_by(user_id=user_id).all()
    return render_template('turma.html', escolas=escolas, turmas=turmas)

@turmas_bp.route('/turma', methods=['POST'])
def criar_turma():
    print('[LOG] Endpoint criar_turma chamado')
    if 'user_id' not in session:
        print('[LOG] Usuário não autenticado')
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    print('[LOG] Dados recebidos:', data)
    nome = data.get('nome', '').strip()
    ano = data.get('ano')
    escola_id = data.get('escola_id')
    turno = data.get('turno')
    user_id = session['user_id']
    if not all([nome, ano, escola_id, turno]):
        print('[LOG] Campos obrigatórios faltando')
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    if Turma.query.filter_by(nome=nome, escola_id=escola_id, user_id=user_id).first():
        print('[LOG] Turma já cadastrada nesta escola')
        return jsonify({'error': 'Turma já cadastrada nesta escola'}), 400
    nova_turma = Turma(nome=nome, ano=ano, escola_id=escola_id, turno=turno, user_id=user_id)
    db.session.add(nova_turma)
    db.session.commit()
    print('[LOG] Turma salva no banco:', nova_turma.id)
    return jsonify({'success': True, 'message': 'Turma cadastrada com sucesso!', 'turma': {'id': nova_turma.id, 'nome': nova_turma.nome, 'ano': nova_turma.ano, 'turno': nova_turma.turno, 'escola_id': nova_turma.escola_id}})

@turmas_bp.route('/turma/<int:id>', methods=['DELETE'])
def excluir_turma(id):
    if 'user_id' not in session:
        return jsonify({"error": "Não autenticado"}), 401

    user_id = session['user_id']
    turma = Turma.query.filter_by(id=id, user_id=user_id).first_or_404()
    if turma.alunos:
        return jsonify({"error": "Não é possível excluir turma com alunos vinculados"}), 400

    db.session.delete(turma)
    db.session.commit()
    return jsonify({"success": True, "message": "Turma excluída."})

# Endpoint para AJAX do cadastro de aluno (dropdown dinâmico de turmas por escola)
@turmas_bp.route('/lista.json')
def listar_turmas_json():
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    escola_id = request.args.get("escola_id")
    turmas = Turma.query.filter_by(escola_id=escola_id, user_id=user_id).all() if escola_id else []
    return jsonify([{"id": t.id, "nome": t.nome} for t in turmas])

@turmas_bp.route('/api/turmas', methods=['GET'])
def listar_turmas():
    if 'user_id' not in session:
        return jsonify({'turmas': [], 'total': 0, 'pages': 1, 'page': 1})
    user_id = session['user_id']
    escola_id = request.args.get('escola_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    query = Turma.query.filter_by(user_id=user_id)
    if escola_id:
        query = query.filter_by(escola_id=escola_id)
    total = query.count()
    turmas = query.order_by(Turma.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
    return jsonify({
        'turmas': [
            {'id': t.id, 'nome': t.nome, 'ano': t.ano, 'turno': t.turno, 'escola_id': t.escola_id}
            for t in turmas
        ],
        'total': total,
        'pages': ceil(total / per_page) if total else 1,
        'page': page
    })

@turmas_bp.route('/api/turmas', methods=['POST'])
def criar_turma_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    nome = data.get('nome', '').strip()
    ano = data.get('ano')
    escola_id = data.get('escola_id')
    turno = data.get('turno')
    user_id = session['user_id']
    if not all([nome, ano, escola_id, turno]):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    if Turma.query.filter_by(nome=nome, escola_id=escola_id, user_id=user_id).first():
        return jsonify({'error': 'Turma já cadastrada nesta escola'}), 400
    nova_turma = Turma(nome=nome, ano=ano, escola_id=escola_id, turno=turno, user_id=user_id)
    db.session.add(nova_turma)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Turma cadastrada com sucesso!', 'turma': {'id': nova_turma.id, 'nome': nova_turma.nome, 'ano': nova_turma.ano, 'turno': nova_turma.turno, 'escola_id': nova_turma.escola_id}})

@turmas_bp.route('/api/turmas/<int:turma_id>', methods=['PUT'])
def editar_turma(turma_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    turma = Turma.query.get_or_404(turma_id)
    nome = data.get('nome', '').strip()
    ano = data.get('ano')
    escola_id = data.get('escola_id')
    turno = data.get('turno')
    user_id = session['user_id']
    if not all([nome, ano, escola_id, turno]):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    if Turma.query.filter(Turma.nome == nome, Turma.escola_id == escola_id, Turma.user_id == user_id, Turma.id != turma_id).first():
        return jsonify({'error': 'Já existe uma turma com este nome nesta escola'}), 400
    turma.nome = nome
    turma.ano = ano
    turma.escola_id = escola_id
    turma.turno = turno
    db.session.commit()
    return jsonify({'success': True, 'message': 'Turma atualizada com sucesso!'})

@turmas_bp.route('/api/turmas/<int:turma_id>', methods=['DELETE'])
def excluir_turma_api(turma_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    turma = Turma.query.get_or_404(turma_id)
    if hasattr(turma, 'alunos') and turma.alunos:
        return jsonify({'error': 'Não é possível excluir turma com alunos vinculados'}), 400
    db.session.delete(turma)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Turma excluída com sucesso!'})