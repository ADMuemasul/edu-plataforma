from flask import Blueprint, request, jsonify, session
from database import db, PlanoAula

plano_aula_bp = Blueprint('plano_aula_bp', __name__)

@plano_aula_bp.route('/api/planos-aula', methods=['POST'])
def criar_plano_aula():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    data = request.json
    titulo = data.get('titulo')
    conteudo = data.get('conteudo')
    if not titulo or not conteudo:
        return jsonify({'error': 'Título e conteúdo são obrigatórios'}), 400
    plano = PlanoAula(titulo=titulo, conteudo=conteudo, user_id=session['user_id'])
    db.session.add(plano)
    db.session.commit()
    return jsonify({'message': 'Plano de aula salvo com sucesso!', 'id': plano.id}), 201

@plano_aula_bp.route('/api/planos-aula', methods=['GET'])
def listar_planos_aula():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    planos = PlanoAula.query.filter_by(user_id=session['user_id']).order_by(PlanoAula.criado_em.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'titulo': p.titulo,
            'conteudo': p.conteudo,
            'criado_em': p.criado_em.strftime('%Y-%m-%d %H:%M')
        } for p in planos
    ]) 