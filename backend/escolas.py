from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from database import db, Escola, Habilidade
from math import ceil

escolas_bp = Blueprint('escolas_bp', __name__)

@escolas_bp.route('/')
def view_escolas():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    escolas = Escola.query.filter_by(user_id=session['user_id']).all()
    return render_template('escola.html', escolas=escolas)

@escolas_bp.route('/escola', methods=['POST'])
def criar_escola():
    print('[LOG] Endpoint criar_escola chamado')
    if 'user_id' not in session:
        print('[LOG] Usuário não autenticado')
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    print('[LOG] Dados recebidos:', data)
    nome = data.get('nome', '').strip()
    rede = data.get('rede', '').strip()
    zona = data.get('zona', '').strip()
    user_id = session['user_id']
    if not all([nome, rede, zona]):
        print('[LOG] Campos obrigatórios faltando')
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400

    # Validação de duplicidade para o mesmo usuário
    if Escola.query.filter_by(user_id=user_id, nome=nome).first():
        return jsonify({"error": "Escola já cadastrada"}), 400

    nova_escola = Escola(nome=nome, rede=rede, zona=zona, user_id=user_id)
    db.session.add(nova_escola)
    db.session.commit()
    print('[LOG] Escola salva no banco:', nova_escola.id)
    return jsonify({
        "success": True,
        "message": "Escola cadastrada com sucesso",
        "escola": {
            "id": nova_escola.id,
            "nome": nova_escola.nome,
            "rede": nova_escola.rede,
            "zona": nova_escola.zona
        }
    })

@escolas_bp.route('/lista.json')
def lista_escolas_json():
    user_id = session.get('user_id')
    escolas = Escola.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": e.id, "nome": e.nome} for e in escolas])

@escolas_bp.route('/api/escolas', methods=['GET', 'POST'])
def escolas_api():
    if request.method == 'GET':
        if 'user_id' not in session:
            return jsonify({'escolas': [], 'total': 0, 'pages': 1, 'page': 1})
        user_id = session['user_id']
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = Escola.query.filter_by(user_id=user_id)
        total = query.count()
        escolas = query.order_by(Escola.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
        return jsonify({
            'escolas': [
                {'id': e.id, 'nome': e.nome, 'rede': e.rede, 'zona': e.zona}
                for e in escolas
            ],
            'total': total,
            'pages': ceil(total / per_page) if total else 1,
            'page': page
        })
    elif request.method == 'POST':
        print('[LOG] Endpoint criar_escola chamado')
        if 'user_id' not in session:
            print('[LOG] Usuário não autenticado')
            return jsonify({'error': 'Não autenticado'}), 401
        data = request.get_json()
        print('[LOG] Dados recebidos:', data)
        nome = data.get('nome', '').strip()
        rede = data.get('rede', '').strip()
        zona = data.get('zona', '').strip()
        user_id = session['user_id']
        if not all([nome, rede, zona]):
            print('[LOG] Campos obrigatórios faltando')
            return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400
        nova_escola = Escola(nome=nome, rede=rede, zona=zona, user_id=user_id)
        db.session.add(nova_escola)
        db.session.commit()
        print('[LOG] Escola salva no banco:', nova_escola.id)
        return jsonify({'success': True, 'message': 'Escola cadastrada com sucesso!', 'escola': {'id': nova_escola.id, 'nome': nova_escola.nome, 'rede': nova_escola.rede, 'zona': nova_escola.zona}})

@escolas_bp.route('/api/escolas/<int:escola_id>', methods=['PUT'])
def editar_escola(escola_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    escola = Escola.query.get_or_404(escola_id)
    nome = data.get('nome', '').strip()
    rede = data.get('rede', '').strip()
    zona = data.get('zona', '').strip()
    user_id = session['user_id']
    if not all([nome, rede, zona]):
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400
    # Validação de duplicidade para o mesmo usuário (exceto para o próprio registro)
    if Escola.query.filter(Escola.nome == nome, Escola.user_id == user_id, Escola.id != escola_id).first():
        return jsonify({'error': 'Já existe uma escola com este nome.'}), 400
    escola.nome = nome
    escola.rede = rede
    escola.zona = zona
    db.session.commit()
    return jsonify({'success': True, 'message': 'Escola atualizada com sucesso!'})

@escolas_bp.route('/api/escolas/<int:escola_id>', methods=['DELETE'])
def excluir_escola(escola_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    escola = Escola.query.get_or_404(escola_id)
    db.session.delete(escola)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Escola excluída com sucesso!'})