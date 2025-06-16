document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('plano-form');
    const resultadoDiv = document.getElementById('resultado-plano');
    const listaPlanosDiv = document.getElementById('lista-planos');
    const habilidadeSelect = document.getElementById('habilidade');
    const habilidadeInfo = document.getElementById('habilidade-info');
    const componenteSelect = document.getElementById('componente');
    const anoInput = document.getElementById('ano');
    const temaInput = document.getElementById('tema');
    const habilidadesTextarea = document.getElementById('habilidades');
    const objetivosTextarea = document.getElementById('objetivos');
    const submitButton = form.querySelector('button[type="submit"]');
    
    let planoGerado = null;  // Armazenar o plano gerado
    let habilidadesDisponiveis = []; // Armazenar todas as habilidades

    // Carregar habilidades e histórico ao abrir a página
    carregarHabilidades();
    carregarHistoricoPlanos();

    // Event listener para mudança na seleção de habilidade
    habilidadeSelect.addEventListener('change', function() {
        const habilidadeId = this.value;
        if (habilidadeId) {
            preencherCamposAutomaticamente(habilidadeId);
        } else {
            limparCampos();
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validar formulário
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }
        
        // Mostrar loader
        resultadoDiv.style.display = 'block';
        resultadoDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div class="loader" style="display: inline-block; margin-bottom: 1rem;"></div>
                <p><strong>Gerando plano de aula...</strong></p>
                <small>Isso pode levar alguns segundos. Por favor, aguarde.</small>
            </div>
        `;
        
        try {
            const formData = {
                componente: componenteSelect.value,
                ano: anoInput.value,
                tema: temaInput.value,
                habilidades: habilidadesTextarea.value,
                objetivos: objetivosTextarea.value
            };
            
            const response = await fetch('/gerar-plano', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                planoGerado = data.plano;  // Salvar o plano gerado
                
                // Verificar se há aviso (modo fallback)
                let avisoHtml = '';
                if (data.aviso) {
                    avisoHtml = `
                        <div class="alert alert-info" style="background: #e7f3ff; border: 1px solid #b3d9ff; border-radius: 8px; padding: 0.8rem; margin-bottom: 1rem; color: #0056b3;">
                            <i class="fas fa-info-circle"></i> 
                            <strong>Informação:</strong> ${data.aviso}
                        </div>
                    `;
                }
                
                resultadoDiv.innerHTML = `
                    <div class="plano-gerado">
                        <h2><i class="fas fa-file-alt"></i> Plano de Aula Gerado${data.tipo === 'modelo' ? ' (Modelo Educacional)' : ''}</h2>
                        ${avisoHtml}
                        <div class="plano-content">${formatarPlano(data.plano)}</div>
                        <div class="acoes-plano">
                            <button class="btn-download" onclick="downloadPDF()">
                                <i class="fas fa-download"></i> Baixar PDF
                            </button>
                            <button class="btn-salvar" onclick="salvarPlano()">
                                <i class="fas fa-save"></i> Salvar Plano
                            </button>
                        </div>
                    </div>
                `;
            } else {
                resultadoDiv.innerHTML = `
                    <div class="error">
                        <i class="fas fa-exclamation-circle"></i> 
                        <strong>Erro:</strong> ${data.error || 'Falha ao gerar plano de aula'}
                        <br><br>
                        <strong>Dicas para resolver:</strong>
                        <ul style="text-align: left; margin-top: 0.5rem;">
                            <li>Verifique se selecionou uma habilidade BNCC</li>
                            <li>Certifique-se de que todos os campos estão preenchidos</li>
                            <li>Recarregue a página e tente novamente</li>
                            <li>Verifique sua conexão com a internet</li>
                        </ul>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Erro:', error);
            resultadoDiv.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-circle"></i> 
                    <strong>Erro de conexão:</strong> Não foi possível conectar com o servidor. 
                    Verifique sua conexão e tente novamente.
                </div>
            `;
        }
    });

    async function carregarHabilidades() {
        try {
            habilidadeSelect.innerHTML = '<option value="">Carregando habilidades...</option>';
            
            const response = await fetch('/api/habilidades');
            if (!response.ok) {
                if (response.status === 401) {
                    habilidadeSelect.innerHTML = '<option value="">Sessão expirada. Faça login novamente.</option>';
                    return;
                }
                throw new Error('Erro ao carregar habilidades');
            }
            
            const data = await response.json();
            habilidadesDisponiveis = data.habilidades || [];
            
            if (habilidadesDisponiveis.length === 0) {
                habilidadeSelect.innerHTML = '<option value="">Nenhuma habilidade cadastrada</option>';
                return;
            }
            
            // Preencher o select com as habilidades
            habilidadeSelect.innerHTML = '<option value="">Selecione uma habilidade BNCC</option>';
            
            // Agrupar por componente e ano para melhor organização
            const habilidadesPorComponente = {};
            habilidadesDisponiveis.forEach(hab => {
                const key = `${hab.componente} - ${hab.ano}º ano`;
                if (!habilidadesPorComponente[key]) {
                    habilidadesPorComponente[key] = [];
                }
                habilidadesPorComponente[key].push(hab);
            });
            
            // Criar optgroups organizados
            Object.keys(habilidadesPorComponente).sort().forEach(grupo => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = grupo;
                
                habilidadesPorComponente[grupo].forEach(hab => {
                    const option = document.createElement('option');
                    option.value = hab.id;
                    option.textContent = `${hab.codigo} - ${hab.descricao.substring(0, 80)}${hab.descricao.length > 80 ? '...' : ''}`;
                    optgroup.appendChild(option);
                });
                
                habilidadeSelect.appendChild(optgroup);
            });
            
        } catch (error) {
            console.error('Erro ao carregar habilidades:', error);
            habilidadeSelect.innerHTML = '<option value="">Erro ao carregar habilidades</option>';
        }
    }

    function preencherCamposAutomaticamente(habilidadeId) {
        const habilidade = habilidadesDisponiveis.find(h => h.id == habilidadeId);
        if (!habilidade) return;
        
        // Preencher informações da habilidade
        habilidadeInfo.style.display = 'block';
        habilidadeInfo.innerHTML = `
            <strong>Código:</strong> ${habilidade.codigo}<br>
            <strong>Componente:</strong> ${habilidade.componente}<br>
            <strong>Ano:</strong> ${habilidade.ano}º ano<br>
            <strong>Etapa:</strong> ${habilidade.etapa}
        `;
        
        // Preencher campos automaticamente
        componenteSelect.innerHTML = `<option value="${habilidade.componente}" selected>${habilidade.componente}</option>`;
        componenteSelect.value = habilidade.componente;
        
        anoInput.value = habilidade.ano;
        
        // Gerar tema baseado na descrição da habilidade
        const tema = gerarTemaAula(habilidade.descricao);
        temaInput.value = tema;
        
        // Preencher habilidade completa
        habilidadesTextarea.value = `${habilidade.codigo} - ${habilidade.descricao}`;
        
        // Usar a descrição da habilidade como base para os objetivos
        objetivosTextarea.value = `Ao final da aula, o aluno deverá ser capaz de: ${habilidade.descricao.toLowerCase()}`;
        
        // Habilitar campos e botão
        componenteSelect.disabled = false;
        anoInput.disabled = false;
        temaInput.disabled = false;
        habilidadesTextarea.disabled = false;
        objetivosTextarea.disabled = false;
        submitButton.disabled = false;
        
        // Permitir edição do tema e objetivos
        temaInput.disabled = false;
        objetivosTextarea.disabled = false;
    }

    function limparCampos() {
        habilidadeInfo.style.display = 'none';
        
        componenteSelect.innerHTML = '<option value="">Será preenchido automaticamente</option>';
        componenteSelect.disabled = true;
        
        anoInput.value = '';
        anoInput.disabled = true;
        
        temaInput.value = '';
        temaInput.disabled = true;
        
        habilidadesTextarea.value = '';
        habilidadesTextarea.disabled = true;
        
        objetivosTextarea.value = '';
        objetivosTextarea.disabled = true;
        
        submitButton.disabled = true;
    }

    function gerarTemaAula(descricaoHabilidade) {
        // Extrair palavras-chave da descrição para gerar um tema
        const palavrasChave = descricaoHabilidade
            .toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(' ')
            .filter(palavra => palavra.length > 3)
            .slice(0, 3);
        
        // Criar um tema baseado nas palavras-chave
        if (palavrasChave.length > 0) {
            return palavrasChave
                .map(palavra => palavra.charAt(0).toUpperCase() + palavra.slice(1))
                .join(' e ');
        }
        
        return 'Tema baseado na habilidade selecionada';
    }

    async function carregarHistoricoPlanos() {
        try {
            const resp = await fetch('/api/planos-aula');
            if (!resp.ok) {
                if (resp.status === 401) {
                    listaPlanosDiv.innerHTML = '<p class="error">Sessão expirada. Faça login novamente.</p>';
                    return;
                }
                throw new Error('Erro ao buscar planos');
            }
            const planos = await resp.json();
            if (planos.length === 0) {
                listaPlanosDiv.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">Nenhum plano de aula salvo ainda. Gere seu primeiro plano!</p>';
                return;
            }
            listaPlanosDiv.innerHTML = '';
            planos.forEach(p => {
                const card = document.createElement('div');
                card.className = 'plano-card';
                card.innerHTML = `
                    <div class="plano-cabecalho">
                        <span class="plano-data"><i class="far fa-calendar-alt"></i> ${p.criado_em}</span>
                        <span class="plano-componente"><i class="fas fa-book"></i> ${p.titulo}</span>
                    </div>
                    <div class="plano-detalhes">${formatarPlano(p.conteudo)}</div>
                    <button class="btn-download"><i class="fas fa-download"></i> Baixar PDF</button>
                `;
                card.onclick = function(e) {
                    if (e.target.classList.contains('btn-download')) return;
                    card.classList.toggle('expanded');
                };
                card.querySelector('.btn-download').onclick = function(e) {
                    e.stopPropagation();
                    baixarPlanoComoPDF(p.titulo, p.conteudo);
                };
                listaPlanosDiv.appendChild(card);
            });
        } catch (err) {
            console.error('Erro ao carregar histórico:', err);
            listaPlanosDiv.innerHTML = '<p class="error">Erro ao carregar histórico de planos. Tente recarregar a página.</p>';
        }
    }

    window.salvarPlano = async function() {
        if (!planoGerado) {
            alert('Gere um plano antes de salvar');
            return;
        }
        const titulo = prompt('Digite um título para o plano de aula:', 'Plano de Aula - ' + temaInput.value);
        if (!titulo) return;
        
        try {
            const resp = await fetch('/api/planos-aula', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ titulo, conteudo: planoGerado })
            });
            
            const result = await resp.json();
            
            if (resp.ok) {
            alert('Plano salvo com sucesso!');
            carregarHistoricoPlanos();
            } else {
                alert('Erro ao salvar plano: ' + (result.error || 'Erro desconhecido'));
            }
        } catch (err) {
            console.error('Erro ao salvar:', err);
            alert('Erro ao salvar plano. Verifique sua conexão e tente novamente.');
        }
    }
});

function formatarPlano(texto) {
    if (!texto) return '';
    
    // Formata o texto retornado pela IA com quebras de linha e estrutura
    let formatted = texto
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/(\d+\.\s+[^:]+):/g, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return `<p>${formatted}</p>`;
}

async function downloadPDF() {
    if (!planoGerado) {
        alert('Gere um plano antes de baixar');
        return;
    }
    
    // Gerar PDF organizado usando a mesma estrutura do PDF.HTML
    gerarPDFOrganizado(planoGerado);
}

function gerarPDFOrganizado(conteudoPlano) {
    // Criar uma janela temporária com o conteúdo do PDF organizado
    const pdfWindow = window.open('', '_blank');
    
    // Obter dados do formulário
    const componente = document.getElementById('componente').value || 'Matemática';
    const ano = document.getElementById('ano').value || '9';
    const tema = document.getElementById('tema').value || 'Plano de Aula';
    const habilidades = document.getElementById('habilidades').value || '';
    const objetivos = document.getElementById('objetivos').value || '';
    
    // Obter nome do usuário de diferentes fontes possíveis
    let userName = 'Professor(a)';
    if (window.userName) {
        userName = window.userName;
    } else if (localStorage.getItem('userName')) {
        userName = localStorage.getItem('userName');
    } else if (sessionStorage.getItem('userName')) {
        userName = sessionStorage.getItem('userName');
    } else {
        // Tentar obter do elemento na página
        const userElement = document.querySelector('.user-name, .username, [data-user]');
        if (userElement) {
            userName = userElement.textContent || userElement.innerText || userName;
        }
    }
    
    // Processar o plano gerado para extrair seções
    const secoesParsadas = parsePlanoParaSecoes(conteudoPlano || '');
    
    const htmlContent = `
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plano de Aula - ${tema}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Aplicar os mesmos estilos do PDF.HTML */
        :root {
            --primary-color: #1e3a8a;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --light-background: #f8fafc;
            --white: #ffffff;
            --text-color: #1f2937;
            --light-text-color: #6b7280;
            --border-color: #e5e7eb;
            --success-color: #10b981;
            --warning-color: #f59e0b;
        }

        body {
            background: white;
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        .pdf-container {
            width: 210mm;
            background: var(--white);
            margin: 0 auto;
            padding: 20mm;
            font-size: 10.5pt;
            box-sizing: border-box;
        }

        .pdf-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 20mm;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            position: relative;
            margin: -20mm -20mm 0 -20mm;
        }

        //.logo-left, .logo-right {
            flex: 0 0 70px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .logo-placeholder {
            width: 55px;
            height: 55px; 
            background: white;
            border-radius: 6px;
            padding: 6px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8pt;
            font-weight: 600;
            color: var(--primary-color);
            text-align: center;
            line-height: 1.2;
        }

        .header-center {
            flex: 1;
            text-align: center;
            padding: 0 10px;
        }

        .pdf-title {
            font-size: 16pt; // tamanho da fonte PLANO DE AULA 
            font-weight: 700;
            margin: 0 0 4px 0;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }

        .pdf-subtitle {
            font-size: 11pt;
            font-weight: 400;
            margin: 0 0 6px 0;
            opacity: 0.9;
        }

        .pdf-prof {
            font-size: 10pt;
            font-weight: 500;
            margin: 0;
            opacity: 0.8;
        }

        .pdf-separator {
            border: none;
            border-top: 10px solid var(--border-color);
            margin: 0 -20mm;
        }

        .pdf-info-section {
            background: var(--light-background);
            padding: 12px 20mm;
            border-bottom: 1px solid var(--border-color);
            margin: 0 -20mm 6px -20mm;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }

        .info-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .info-label {
            font-weight: 600;
            color: var(--primary-color);
            font-size: 9.5pt;
        }

        .info-value {
            font-weight: 500;
            color: var(--text-color);
            font-size: 9.5pt;
        }

        .pdf-card {
            margin: 8px 0;
            padding: 16px 20px;
            background: var(--white);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            box-shadow: 0 1px 5px rgba(0, 0, 0, 0.04);
            line-height: 1.5;
            width: calc(100% - 40px);
        }

        .titulo-card {
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            color: white;
            text-align: center;
            border: none;
            padding: 16px 25px;
            margin: 6px 0;
        }

        .plano-titulo-principal {
            margin: 0;
            font-size: 16pt;
            font-weight: 700;
            line-height: 1.4;
        }

        .section-title {
            margin: 0 0 12px 0;
            font-size: 13pt;
            font-weight: 700;
            color: var(--primary-color);
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .bncc-card {
            background: linear-gradient(135deg, #fefce8 0%, #fffbeb 100%);
            border-left: 4px solid var(--warning-color);
        }

        .bncc-content {
            margin-top: 8px;
        }

        .competencia-item {
            background: white;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid var(--warning-color);
        }

        .bncc-codigo {
            display: inline-block;
            background: var(--warning-color);
            color: white;
            padding: 3px 7px;
            border-radius: 3px;
            font-weight: 700;
            font-size: 8.5pt;
            margin-bottom: 6px;
        }

        .bncc-descricao {
            margin: 0;
            font-style: italic;
            line-height: 1.5;
        }

        .objetivos-card {
            background: linear-gradient(135deg, #f0fdf4 0%, #f0fdf4 100%);
            border-left: 4px solid var(--success-color);
        }

        .objetivos-list {
            list-style: none;
            padding: 0;
            margin: 8px 0 0 0;
        }

        .objetivos-list li {
            padding: 6px 0 6px 22px;
            position: relative;
            line-height: 1.5;
        }

        .objetivos-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--success-color);
            font-weight: bold;
            font-size: 11pt;
        }

        .materiais-card {
            background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%);
            border-left: 4px solid var(--accent-color);
        }

        .materiais-list {
            list-style: none;
            padding: 0;
            margin: 8px 0 0 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 6px;
        }

        .materiais-list li {
            padding: 5px 0;
            line-height: 1.4;
            font-size: 9.5pt;
        }

        .desenvolvimento-card {
            background: linear-gradient(135deg, #f6faff 0%, #f0f5ff 100%);
            border-left: 4px solid var(--primary-color);
        }

        .momento-aula {
            margin: 15px 0;
            padding: 12px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid var(--primary-color);
        }

        .momento-titulo {
            margin: 0 0 8px 0;
            font-size: 11.5pt;
            font-weight: 700;
            color: var(--primary-color);
        }

        .momento-content {
            line-height: 21.5;
        }

        .momento-content p {
            margin: 6px 0;
            line-height: 1.5;
        }

        .atividade {
            margin: 12px 0;
            padding: 8px;
            background: var(--light-background);
            border-radius: 3px;
        }

        .atividade-titulo {
            margin: 0 0 6px 0;
            font-size: 10.5pt;
            font-weight: 600;
            color: var(--secondary-color);
        }

        .introducao-card {
            background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
            border-left: 4px solid #8b5cf6;
        }

        .objetivos-especificos-card {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-left: 4px solid var(--success-color);
        }

        .atividades-card {
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border-left: 4px solid #f59e0b;
        }

        .avaliacao-card {
            background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%);
            border-left: 4px solid #a855f7;
        }

        .conclusao-card {
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            border-left: 4px solid #10b981;
        }

        .referencias-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-left: 4px solid #64748b;
            margin-top: 15px;
        }

        .referencias-content p {
            margin: 8px 0;
            font-size: 9.5pt;
            line-height: 1.4;
        }

        .referencias-content strong {
            color: var(--primary-color);
            font-weight: 600;
        }

        .avaliacao-content {
            margin-top: 8px;
        }

        .avaliacao-item {
            margin: 12px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #a855f7;
        }

        .avaliacao-item h4 {
            margin: 0 0 6px 0;
            font-size: 10.5pt;
            font-weight: 600;
            color: #a855f7;
        }

        .avaliacao-item p {
            margin: 0;
            line-height: 1.5;
        }

        .avaliacao-item ul {
            list-style: none;
            padding: 0;
            margin: 6px 0 0 0;
        }

        .avaliacao-item li {
            padding: 3px 0 3px 18px;
            position: relative;
            line-height: 1.5;
        }

        .avaliacao-item li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #a855f7;
            font-weight: bold;
        }

        .pdf-footer {
            text-align: center;
            padding: 15px 20mm;
            background: var(--light-background);
            color: var(--light-text-color);
            font-size: 8.5pt;
            font-style: italic;
            border-top: 1px solid var(--border-color);
            margin: 20px -20mm 0 -20mm;
        }

        ul, ol {
            line-height: 1.5;
            margin-bottom: 8px;
        }

        li {
            line-height: 1.5;
            margin-bottom: 2px;
        }

        p {
            line-height: 1.5;
            margin: 6px 0;
        }

        strong {
            font-weight: 600;
            color: var(--primary-color);
        }

        @page {
            size: A4;
            margin: 20mm;
        }
        
        /* Evitar quebras de página desnecessárias */
        .pdf-header {
            page-break-after: avoid;
        }
        
        .pdf-separator {
            page-break-before: avoid;
            page-break-after: avoid;
        }
        
        .pdf-info-section {
            page-break-before: avoid;
            page-break-after: avoid;
        }
        
        .pdf-card:first-of-type {
            page-break-before: avoid;
        }

        @media print {
            body {
                background: white !important;
                padding: 0 !important;
                margin: 0 !important;
                height: auto !important;
                min-height: auto !important;
            }
            
            .pdf-container {
                width: 100% !important;
                height: auto !important;
                min-height: auto !important;
                box-shadow: none !important;
                border-radius: 0 !important;
                border: none !important;
                padding: 15mm !important;
                margin: 0 !important;
                overflow: visible !important;
                page-break-after: avoid !important;
            }

            .pdf-card {
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                margin: 6px 0 !important;
                padding: 14px 18px !important;
                width: calc(100% - 36px) !important;
            }

            .pdf-header {
                margin: 0 !important;
                padding: 15px 15mm !important;
                page-break-after: avoid !important;
            }
            
            .pdf-info-section {
                margin: 0 !important;
                padding: 10px 15mm !important;
                page-break-after: avoid !important;
            }
            
            .pdf-separator {
                margin: 0 !important;
                page-break-after: avoid !important;
            }
            
            .pdf-footer {
                margin: 20px 0 0 0 !important;
                padding: 15px 15mm !important;
                page-break-before: avoid !important;
            }

            .pdf-card {
                page-break-inside: avoid;
                margin: 10mm 0;
                box-shadow: none !important;
                border: 1px solid var(--border-color) !important;
            }
            
            .momento-aula {
                page-break-inside: avoid;
                margin: 8mm 0;
            }

            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
                page-break-before: avoid;
            }
            
            ul, ol {
                page-break-inside: avoid;
            }

            p {
                orphans: 3;
                widows: 3;
            }
        }
    </style>
</head>
<body>
    <div class="pdf-container">
        <div class="pdf-header">
            <div class="logo-left">
                <div class="logo-placeholder">ADM</div>
            </div>
            <div class="header-center">
                <div class="pdf-title">PLANO DE AULA</div>
                <div class="pdf-subtitle">Educação Básica - BNCC</div>
                <div class="pdf-prof">Professor - ${userName}</div>
            </div>
            <div class="logo-right">
                <div class="logo-placeholder">UEMASUL</div>
            </div>
        </div>
        <hr class="pdf-separator">
        
        <div class="pdf-info-section">
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">📚 Componente:</span>
                    <span class="info-value">${componente}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">🎯 Ano/Série:</span>
                    <span class="info-value">${ano}º ano do Ensino Fundamental</span>
                </div>
                <div class="info-item">
                    <span class="info-label">⏱️ Duração:</span>
                    <span class="info-value">50 minutos</span>
                </div>
                <div class="info-item">
                    <span class="info-label">👥 Modalidade:</span>
                    <span class="info-value">Presencial</span>
                </div>
            </div>
        </div>

        <div class="pdf-card titulo-card">
            <h1 class="plano-titulo-principal">📊 ${tema}</h1>
        </div>

        <div class="pdf-card bncc-card">
            <h2 class="section-title">📋 COMPETÊNCIAS E HABILIDADES DA BNCC</h2>
            <div class="bncc-content">
                <div class="competencia-item">
                    <div class="bncc-descricao">${habilidades || 'Competências e habilidades específicas da BNCC para ' + componente + ' - ' + ano + 'º ano do Ensino Fundamental, conforme selecionado no formulário de geração do plano.'}</div>
                </div>
            </div>
        </div>

        <div class="pdf-card objetivos-card">
            <h2 class="section-title">🎯 OBJETIVOS DE APRENDIZAGEM</h2>
            <div class="objetivos-content">
                <div class="bncc-descricao">${objetivos || 'Objetivos de aprendizagem específicos para a aula de ' + componente + ', alinhados com as competências da BNCC e adequados ao ' + ano + 'º ano do Ensino Fundamental.'}</div>
            </div>
        </div>

        ${secoesParsadas.introducao ? `
        <div class="pdf-card introducao-card">
            <h2 class="section-title">📖 INTRODUÇÃO</h2>
            <div class="bncc-descricao">${secoesParsadas.introducao}</div>
        </div>
        ` : ''}

        ${secoesParsadas.objetivos ? `
        <div class="pdf-card objetivos-especificos-card">
            <h2 class="section-title">🎯 OBJETIVOS ESPECÍFICOS</h2>
            <div class="bncc-descricao">${secoesParsadas.objetivos}</div>
        </div>
        ` : ''}

        ${secoesParsadas.materiais ? `
        <div class="pdf-card materiais-card">
            <h2 class="section-title">🛠️ RECURSOS E MATERIAIS</h2>
            <div class="materiais-content">
                <div class="bncc-descricao">${secoesParsadas.materiais}</div>
            </div>
        </div>
        ` : ''}

        ${secoesParsadas.desenvolvimento ? `
        <div class="pdf-card desenvolvimento-card">
            <h2 class="section-title">📚 DESENVOLVIMENTO DA AULA</h2>
            <div class="bncc-descricao">${secoesParsadas.desenvolvimento}</div>
        </div>
        ` : ''}

        ${secoesParsadas.atividades ? `
        <div class="pdf-card atividades-card">
            <h2 class="section-title">🎲 ATIVIDADES PRÁTICAS</h2>
            <div class="bncc-descricao">${secoesParsadas.atividades}</div>
        </div>
        ` : ''}

        ${secoesParsadas.avaliacao ? `
        <div class="pdf-card avaliacao-card">
            <h2 class="section-title">📊 AVALIAÇÃO</h2>
            <div class="avaliacao-content">
                <div class="bncc-descricao">${secoesParsadas.avaliacao}</div>
            </div>
        </div>
        ` : ''}

        ${secoesParsadas.conclusao ? `
        <div class="pdf-card conclusao-card">
            <h2 class="section-title">✅ CONCLUSÃO</h2>
            <div class="bncc-descricao">${secoesParsadas.conclusao}</div>
        </div>
        ` : ''}

        ${secoesParsadas.conteudoCompleto ? `
        <div class="pdf-card desenvolvimento-card">
            <h2 class="section-title">📚 CONTEÚDO DO PLANO</h2>
            <div class="bncc-descricao">${secoesParsadas.conteudoCompleto}</div>
        </div>
        ` : ''}

        <div class="pdf-card referencias-card">
            <h2 class="section-title">📖 REFERÊNCIAS</h2>
            <div class="referencias-content">
                <p><strong>Base Nacional Comum Curricular (BNCC)</strong> - Ministério da Educação, 2018.</p>
                <p><strong>Componente Curricular:</strong> ${componente} - ${ano}º ano do Ensino Fundamental</p>
                <p><strong>Elaborado por:</strong> ${userName}</p>
                <p><strong>Data de Elaboração:</strong> ${new Date().toLocaleDateString('pt-BR')}</p>
                <p><strong>Sistema:</strong> EDU-PLATAFORMA - Plataforma de Gestão Educacional</p>
            </div>
        </div>

        <div class="pdf-footer">
            Plano de Aula gerado pela EDU-PLATAFORMA - Sistema de Gestão Educacional | ${userName} | ${new Date().toLocaleDateString('pt-BR')}
        </div>
    </div>

    <script>
        // Aguardar carregamento e imprimir automaticamente
        window.onload = function() {
            setTimeout(function() {
                try {
                    window.print();
                    window.onafterprint = function() {
                        window.close();
                    };
                } catch (error) {
                    console.error('Erro ao imprimir:', error);
                    alert('PDF gerado! Use Ctrl+P para imprimir ou salvar como PDF.');
                }
            }, 500);
        };
    </script>
</body>
</html>
    `;

    pdfWindow.document.write(htmlContent);
    pdfWindow.document.close();
}

function parsePlanoParaSecoes(conteudo) {
    const secoes = {
        introducao: '',
        objetivos: '',
        materiais: '',
        desenvolvimento: '',
        atividades: '',
        avaliacao: '',
        conclusao: '',
        conteudoCompleto: ''
    };
    
    if (!conteudo) {
        secoes.conteudoCompleto = 'Conteúdo do plano não disponível.';
    return secoes;
}

    // Limpar e normalizar o texto
    let textoLimpo = conteudo
        .replace(/\*\*/g, '') // Remove **
        .replace(/\*/g, '') // Remove *
        .replace(/#{1,6}\s*/g, '') // Remove # ## ### etc
        .replace(/^\s*[-•]\s*/gm, '• ') // Normaliza bullets
        .trim();
    
    // Dividir em linhas para análise
    const linhas = textoLimpo.split('\n').map(linha => linha.trim()).filter(linha => linha.length > 0);
    
    // Palavras-chave para identificar seções (mais abrangente)
    const palavrasChave = {
        introducao: ['introdução', 'introducao', 'apresentação', 'apresentacao', 'contextualização', 'contextualizacao', 'tema', 'assunto'],
        objetivos: ['objetivos', 'objetivo', 'metas', 'finalidades', 'propósitos', 'propositos', 'competências', 'competencias', 'habilidades'],
        materiais: ['materiais', 'recursos', 'equipamentos', 'ferramentas', 'instrumentos', 'suprimentos', 'itens necessários', 'itens necessarios'],
        desenvolvimento: ['desenvolvimento', 'metodologia', 'procedimentos', 'estratégias', 'estrategias', 'execução', 'execucao', 'implementação', 'implementacao'],
        atividades: ['atividades', 'exercícios', 'exercicios', 'tarefas', 'práticas', 'praticas', 'dinâmicas', 'dinamicas', 'jogos', 'brincadeiras'],
        avaliacao: ['avaliação', 'avaliacao', 'verificação', 'verificacao', 'acompanhamento', 'feedback', 'correção', 'correcao', 'análise', 'analise'],
        conclusao: ['conclusão', 'conclusao', 'encerramento', 'finalização', 'finalizacao', 'síntese', 'sintese', 'resumo', 'considerações', 'consideracoes']
    };
    
    // Função para identificar o tipo de seção
    function identificarSecao(linha) {
        const linhaLower = linha.toLowerCase();
        
        for (const [secao, palavras] of Object.entries(palavrasChave)) {
            for (const palavra of palavras) {
                if (linhaLower.includes(palavra)) {
                    return secao;
                }
            }
        }
        return null;
    }
    
    // Processar linha por linha
    let secaoAtual = null;
    let conteudoSecao = [];
    
    for (let i = 0; i < linhas.length; i++) {
        const linha = linhas[i];
        const tipoSecao = identificarSecao(linha);
        
        if (tipoSecao) {
            // Salvar seção anterior se existir
            if (secaoAtual && conteudoSecao.length > 0) {
                secoes[secaoAtual] = conteudoSecao.join('\n').trim();
            }
            
            // Iniciar nova seção
            secaoAtual = tipoSecao;
            conteudoSecao = [linha];
        } else if (secaoAtual) {
            // Adicionar conteúdo à seção atual
            conteudoSecao.push(linha);
        } else {
            // Se não há seção definida, adicionar à introdução
            if (!secoes.introducao) {
                secoes.introducao = linha;
            } else {
                secoes.introducao += '\n' + linha;
            }
        }
    }
    
    // Salvar última seção
    if (secaoAtual && conteudoSecao.length > 0) {
        secoes[secaoAtual] = conteudoSecao.join('\n').trim();
    }
    
    // Se não conseguiu dividir em seções, usar estratégia de backup
    if (!secoes.introducao && !secoes.objetivos && !secoes.materiais && 
        !secoes.desenvolvimento && !secoes.atividades && !secoes.avaliacao && !secoes.conclusao) {
        
        // Dividir por parágrafos e tentar identificar padrões
        const paragrafos = textoLimpo.split('\n\n').filter(p => p.trim().length > 0);
        
        if (paragrafos.length >= 3) {
            secoes.introducao = paragrafos[0];
            secoes.desenvolvimento = paragrafos.slice(1, -1).join('\n\n');
            secoes.avaliacao = paragrafos[paragrafos.length - 1];
        } else {
            secoes.conteudoCompleto = textoLimpo;
        }
    }
    
    // Limpar seções vazias e formatar
    Object.keys(secoes).forEach(key => {
        if (secoes[key]) {
            secoes[key] = formatarTextoSecao(secoes[key]);
        }
    });
    
    return secoes;
}

function formatarTextoSecao(texto) {
    if (!texto) return '';
    
    return texto
        .replace(/\n{3,}/g, '\n\n') // Máximo 2 quebras de linha seguidas
        .replace(/^\s*[-•]\s*/gm, '• ') // Normalizar bullets
        .replace(/(\d+)\.\s*/g, '$1. ') // Normalizar numeração
        .replace(/([.!?])\s*\n\s*([A-ZÁÊÇÕ])/g, '$1\n\n$2') // Quebras entre frases
        .trim();
}

function baixarPlanoComoPDF(titulo, conteudo) {
    // Usar a nova função organizada
    gerarPDFOrganizado(conteudo);
}



// Função removida - causava problemas de carregamento