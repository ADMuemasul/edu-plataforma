from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from database import db, Aluno, Escola, Turma
from math import ceil

alunos_bp = Blueprint('alunos_bp', __name__)

@alunos_bp.route('/')
def view_alunos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    alunos = Aluno.query.filter_by(user_id=user_id).all()
    escolas = Escola.query.filter_by(user_id=user_id).all()
    turmas = Turma.query.filter_by(user_id=user_id).all()
    return render_template('aluno.html', alunos=alunos, escolas=escolas, turmas=turmas)

@alunos_bp.route('/aluno', methods=['POST'])
def criar_aluno():
    print('[LOG] Endpoint criar_aluno chamado')
    if 'user_id' not in session:
        print('[LOG] Usuário não autenticado')
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    print('[LOG] Dados recebidos:', data)
    nome = data.get('nome', '').strip()
    sexo = data.get('sexo')
    escola_id = data.get('escola_id')
    turma_id = data.get('turma_id')
    user_id = session['user_id']
    if not all([nome, sexo, escola_id, turma_id]):
        print('[LOG] Campos obrigatórios faltando')
        return jsonify({'error': 'Todos os campos obrigatórios!'}), 400
    novo_aluno = Aluno(nome=nome, sexo=sexo, escola_id=escola_id, turma_id=turma_id, user_id=user_id)
    db.session.add(novo_aluno)
    db.session.commit()
    print('[LOG] Aluno salvo no banco:', novo_aluno.id)
    return jsonify({'success': True, 'message': 'Aluno cadastrado com sucesso', 'aluno': {'id': novo_aluno.id, 'nome': novo_aluno.nome, 'sexo': novo_aluno.sexo, 'escola_id': novo_aluno.escola_id, 'turma_id': novo_aluno.turma_id}})

@alunos_bp.route('/aluno/<int:id>', methods=['DELETE'])
def excluir_aluno(id):
    if 'user_id' not in session:
        return jsonify({"error": "Não autenticado"}), 401

    user_id = session['user_id']
    aluno = Aluno.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(aluno)
    db.session.commit()
    return jsonify({"success": True, "message": "Aluno excluído."})

@alunos_bp.route('/api/alunos', methods=['GET'])
def listar_alunos():
    if 'user_id' not in session:
        return jsonify({'alunos': [], 'total': 0, 'pages': 1, 'page': 1})
    user_id = session['user_id']
    turma_id = request.args.get('turma_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    query = Aluno.query.filter_by(user_id=user_id)
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    total = query.count()
    alunos = query.order_by(Aluno.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
    return jsonify({
        'alunos': [
            {'id': a.id, 'nome': a.nome, 'sexo': a.sexo, 'escola_id': a.escola_id, 'turma_id': a.turma_id}
            for a in alunos
        ],
        'total': total,
        'pages': ceil(total / per_page) if total else 1,
        'page': page
    })

@alunos_bp.route('/api/alunos', methods=['POST'])
def criar_aluno_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    nome = data.get('nome', '').strip()
    sexo = data.get('sexo')
    escola_id = data.get('escola_id')
    turma_id = data.get('turma_id')
    user_id = session['user_id']
    if not all([nome, sexo, escola_id, turma_id]):
        return jsonify({'error': 'Todos os campos obrigatórios!'}), 400
    novo_aluno = Aluno(nome=nome, sexo=sexo, escola_id=escola_id, turma_id=turma_id, user_id=user_id)
    db.session.add(novo_aluno)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Aluno cadastrado com sucesso', 'aluno': {'id': novo_aluno.id, 'nome': novo_aluno.nome, 'sexo': novo_aluno.sexo, 'escola_id': novo_aluno.escola_id, 'turma_id': novo_aluno.turma_id}})

@alunos_bp.route('/api/alunos/<int:aluno_id>', methods=['PUT'])
def editar_aluno(aluno_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    aluno = Aluno.query.get_or_404(aluno_id)
    nome = data.get('nome', '').strip()
    sexo = data.get('sexo')
    escola_id = data.get('escola_id')
    turma_id = data.get('turma_id')
    user_id = session['user_id']
    if not all([nome, sexo, escola_id, turma_id]):
        return jsonify({'error': 'Todos os campos obrigatórios!'}), 400
    aluno.nome = nome
    aluno.sexo = sexo
    aluno.escola_id = escola_id
    aluno.turma_id = turma_id
    db.session.commit()
    return jsonify({'success': True, 'message': 'Aluno atualizado com sucesso!'})

@alunos_bp.route('/api/alunos/<int:aluno_id>', methods=['DELETE'])
def excluir_aluno_api(aluno_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Aluno excluído com sucesso!'})