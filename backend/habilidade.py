from flask import Blueprint, request, jsonify, session
from database import db, Habilidade
from math import ceil
import requests
import json
import os
from config import (
    BNCC_API_URL, 
    BNCC_API_HEADERS, 
    BNCC_COMPONENTE_MAP, 
    VERIFY_SSL,
    REQUEST_TIMEOUT
)

habilidades_bp = Blueprint('habilidades_bp', __name__)

def carregar_habilidades_locais():
    """Carrega as habilidades da BNCC do arquivo JSON local"""
    try:
        habilidades = []
        base_path = os.path.join(os.path.dirname(__file__), 'data')
        
        # Lista de arquivos a serem carregados
        arquivos = [
            'bncc_habilidades.json',      # Anos 1-2 Matemática
            'bncc_habilidades_3a9.json',  # Anos 3-9 Matemática
            'bncc_habilidades_4.json',    # Ano 4 Matemática
            'bncc_habilidades_5.json',    # Ano 5 Matemática
            'bncc_habilidades_6.json',    # Ano 6 Matemática
            'bncc_habilidades_7.json',    # Ano 7 Matemática
            'bncc_habilidades_8.json',    # Ano 8 Matemática
            'bncc_habilidades_9.json',    # Ano 9 Matemática
            'bncc_habilidades_portugues_1_2.json',  # Anos 1-2 Português
            'bncc_habilidades_portugues_3.json',    # Ano 3 Português
            'bncc_habilidades_portugues_4.json',    # Ano 4 Português
            'bncc_habilidades_portugues_5.json',    # Ano 5 Português
            'bncc_habilidades_portugues_6.json',    # Ano 6 Português
            'bncc_habilidades_portugues_7.json',    # Ano 7 Português
            'bncc_habilidades_portugues_8.json',    # Ano 8 Português
            'bncc_habilidades_portugues_9.json'     # Ano 9 Português
        ]
        
        for arquivo in arquivos:
            try:
                caminho_arquivo = os.path.join(base_path, arquivo)
                print(f'[LOG] Carregando arquivo: {arquivo}')
                
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    if 'habilidades' in dados:
                        habilidades.extend(dados['habilidades'])
                        print(f'[LOG] Carregadas {len(dados["habilidades"])} habilidades de {arquivo}')
                    else:
                        print(f'[LOG] Arquivo {arquivo} não contém a chave "habilidades"')
                        
            except FileNotFoundError:
                print(f'[LOG] Arquivo não encontrado: {arquivo}')
            except json.JSONDecodeError:
                print(f'[LOG] Erro ao decodificar JSON do arquivo: {arquivo}')
            except Exception as e:
                print(f'[LOG] Erro ao carregar arquivo {arquivo}: {str(e)}')
        
        print(f'[LOG] Total de habilidades carregadas: {len(habilidades)}')
        return habilidades
        
    except Exception as e:
        print(f'[LOG] Erro ao carregar habilidades locais: {str(e)}')
        return []

def buscar_habilidades_api(componente, ano):
    """Busca habilidades da BNCC na API"""
    try:
        params = {
            'componente': BNCC_COMPONENTE_MAP.get(componente, ''),
            'etapa': 'EF',
            'ano': ano
        }
        
        response = requests.get(
            BNCC_API_URL, 
            headers=BNCC_API_HEADERS, 
            params=params, 
            verify=VERIFY_SSL,
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f'[LOG] Erro ao buscar na API: {str(e)}')
        return None

@habilidades_bp.route('/api/habilidades', methods=['POST'])
def criar_habilidade():
    print('[LOG] Recebendo requisição POST /api/habilidades')
    if 'user_id' not in session:
        print('[LOG] Usuário não autenticado')
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    print('[LOG] Dados recebidos:', data)
    codigo = data.get('codigo')
    componente = data.get('componente')
    ano = data.get('ano')
    descricao = data.get('descricao')
    if not all([codigo, componente, ano, descricao]):
        print('[LOG] Dados incompletos')
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400
    # Validação de unicidade do código BNCC
    if Habilidade.query.filter_by(codigo=codigo).first():
        print('[LOG] Código BNCC já cadastrado:', codigo)
        return jsonify({'error': 'Já existe uma habilidade com este código BNCC.'}), 400
    nova_habilidade = Habilidade(
        codigo=codigo,
        componente=componente,
        ano=ano,
        descricao=descricao
    )
    db.session.add(nova_habilidade)
    db.session.commit()
    print('[LOG] Habilidade cadastrada com sucesso:', nova_habilidade.id)
    return jsonify({'success': True, 'message': 'Habilidade cadastrada com sucesso!'})

@habilidades_bp.route('/api/habilidades', methods=['GET'])
def listar_habilidades():
    # Habilidades são globais (BNCC), não específicas por usuário
    # Não precisa verificar autenticação para listagem
    
    # Se não especificar paginação, retorna todas as habilidades
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    
    query = Habilidade.query
    total = query.count()
    
    if page and per_page:
        # Com paginação
        page = int(page)
        per_page = int(per_page)
        habilidades = query.order_by(Habilidade.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
        return jsonify({
            'habilidades': [
                {'id': h.id, 'codigo': h.codigo, 'componente': h.componente, 'ano': h.ano, 'descricao': h.descricao, 'etapa': h.etapa or 'Ensino Fundamental'}
                for h in habilidades
            ],
            'total': total,
            'pages': ceil(total / per_page),
            'page': page
        })
    else:
        # Sem paginação - retorna todas as habilidades
        habilidades = query.order_by(Habilidade.componente, Habilidade.ano, Habilidade.codigo).all()
        return jsonify({
            'habilidades': [
                {'id': h.id, 'codigo': h.codigo, 'componente': h.componente, 'ano': h.ano, 'descricao': h.descricao, 'etapa': h.etapa or 'Ensino Fundamental'}
                for h in habilidades
            ],
            'total': total
        })

@habilidades_bp.route('/api/habilidades/<int:habilidade_id>', methods=['PUT'])
def editar_habilidade(habilidade_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    data = request.get_json()
    habilidade = Habilidade.query.get_or_404(habilidade_id)
    codigo = data.get('codigo')
    componente = data.get('componente')
    ano = data.get('ano')
    descricao = data.get('descricao')
    if not all([codigo, componente, ano, descricao]):
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400
    # Validação de unicidade do código BNCC (exceto para o próprio registro)
    if Habilidade.query.filter(Habilidade.codigo == codigo, Habilidade.id != habilidade_id).first():
        return jsonify({'error': 'Já existe uma habilidade com este código BNCC.'}), 400
    habilidade.codigo = codigo
    habilidade.componente = componente
    habilidade.ano = ano
    habilidade.descricao = descricao
    db.session.commit()
    return jsonify({'success': True, 'message': 'Habilidade atualizada com sucesso!'})

@habilidades_bp.route('/api/habilidades/<int:habilidade_id>', methods=['DELETE'])
def excluir_habilidade(habilidade_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    habilidade = Habilidade.query.get_or_404(habilidade_id)
    db.session.delete(habilidade)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Habilidade excluída com sucesso!'})

@habilidades_bp.route('/api/habilidades/bncc', methods=['GET'])
def buscar_habilidades_bncc():
    print('[LOG] Recebendo requisição GET /api/habilidades/bncc')
    if 'user_id' not in session:
        print('[LOG] Usuário não autenticado')
        return jsonify({'error': 'Não autenticado'}), 401
    
    componente = request.args.get('componente')
    ano = request.args.get('ano')
    
    if not componente or not ano:
        print('[LOG] Parâmetros inválidos: componente ou ano não fornecidos')
        return jsonify({
            'success': False,
            'error': 'Componente e ano são obrigatórios'
        }), 400
    
    try:
        print(f'[LOG] Buscando habilidades para componente={componente}, ano={ano}')
        
        # Carrega dados locais primeiro
        habilidades_locais = carregar_habilidades_locais()
        
        if not habilidades_locais:
            print('[LOG] Nenhuma habilidade encontrada nos dados locais')
            return jsonify({
                'success': False,
                'error': 'Não foi possível carregar as habilidades'
            }), 500
            
        # Filtra as habilidades pelo componente e ano
        componente_codigo = BNCC_COMPONENTE_MAP.get(componente, '')
        print(f'[LOG] Filtrando por componente: {componente} -> {componente_codigo}, ano: {ano}')
        
        habilidades_filtradas = [
            h for h in habilidades_locais
            if h['componente'] == componente_codigo and
            str(h['ano']) == str(ano)
        ]
        
        print(f'[LOG] Habilidades encontradas: {len(habilidades_filtradas)}')
        
        # Debug: mostrar algumas habilidades para verificar a estrutura
        if habilidades_filtradas:
            print(f'[LOG] Primeira habilidade encontrada: {habilidades_filtradas[0]}')
        else:
            # Mostrar algumas habilidades disponíveis para debug
            print(f'[LOG] Componentes disponíveis: {set(h.get("componente", "") for h in habilidades_locais[:10])}')
            print(f'[LOG] Anos disponíveis: {set(str(h.get("ano", "")) for h in habilidades_locais[:10])}')
        
        # Se não encontrou habilidades, tenta buscar na API como fallback
        if not habilidades_filtradas:
            print('[LOG] Nenhuma habilidade encontrada localmente, tentando API como fallback')
            habilidades_api = buscar_habilidades_api(componente, ano)
            
            if habilidades_api:
                habilidades_filtradas = [
                    h for h in habilidades_api
                    if h['componente'] == BNCC_COMPONENTE_MAP.get(componente, '') and
                    str(h['ano']) == str(ano)
                ]
                print(f'[LOG] Habilidades encontradas na API: {len(habilidades_filtradas)}')
        
        return jsonify({
            'success': True,
            'habilidades': habilidades_filtradas,
            'total': len(habilidades_filtradas),
            'fonte': 'local' if habilidades_filtradas else 'api'
        })
        
    except Exception as e:
        print(f'[LOG] Erro ao buscar habilidades: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar habilidades'
        }), 500

@habilidades_bp.route('/api/habilidades/salvar-multiplas', methods=['POST'])
def salvar_multiplas_habilidades():
    print('[LOG] Recebendo requisição POST /api/habilidades/salvar-multiplas')
    if 'user_id' not in session:
        print('[LOG] Usuário não autenticado')
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        habilidades = data.get('habilidades', [])
        
        if not habilidades:
            return jsonify({'success': False, 'error': 'Nenhuma habilidade fornecida'}), 400
        
        salvadas = 0
        duplicadas = 0
        erros = []
        
        for hab in habilidades:
            try:
                codigo = hab.get('codigo')
                componente = hab.get('componente')
                ano = hab.get('ano')
                descricao = hab.get('descricao')
                
                if not all([codigo, componente, ano, descricao]):
                    erros.append(f'Dados incompletos para habilidade {codigo or "sem código"}')
                    continue
                
                # Verifica se já existe
                if Habilidade.query.filter_by(codigo=codigo).first():
                    duplicadas += 1
                    print(f'[LOG] Habilidade {codigo} já existe, pulando...')
                    continue
                
                # Mapeia o componente de volta para o nome completo
                componente_nome = None
                for nome, sigla in BNCC_COMPONENTE_MAP.items():
                    if sigla == componente:
                        componente_nome = nome
                        break
                
                if not componente_nome:
                    componente_nome = componente  # Usa o valor original se não encontrar mapeamento
                
                nova_habilidade = Habilidade(
                    codigo=codigo,
                    componente=componente_nome,
                    ano=int(ano),
                    descricao=descricao
                )
                
                db.session.add(nova_habilidade)
                salvadas += 1
                print(f'[LOG] Habilidade {codigo} adicionada para salvamento')
                
            except Exception as e:
                erros.append(f'Erro ao processar habilidade {hab.get("codigo", "sem código")}: {str(e)}')
                print(f'[LOG] Erro ao processar habilidade: {str(e)}')
        
        # Salva todas as habilidades de uma vez
        if salvadas > 0:
            db.session.commit()
            print(f'[LOG] {salvadas} habilidades salvas com sucesso')
        
        return jsonify({
            'success': True,
            'salvadas': salvadas,
            'duplicadas': duplicadas,
            'erros': erros,
            'message': f'{salvadas} habilidade(s) salva(s) com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'[LOG] Erro ao salvar habilidades: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Erro ao salvar habilidades'
        }), 500 