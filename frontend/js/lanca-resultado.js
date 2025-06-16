document.addEventListener('DOMContentLoaded', function() {
    const formFiltros = document.getElementById('form-filtros');
    const statsSection = document.getElementById('stats-section');
    const alunosSection = document.getElementById('alunos-section');
    const alunosGrid = document.getElementById('alunos-grid');
    const emptyStateAlunos = document.getElementById('empty-state-alunos');
    
    let filtrosAtivos = {};
    let alunosData = [];
    let escolasData = [];
    let turmasData = [];
    let cadernosData = [];
    let alunoAtual = null;

    // Carrega dados iniciais
    async function carregarDadosIniciais() {
        try {
            await Promise.all([
                carregarEscolas(),
                carregarSeries(),
                carregarCadernos()
            ]);
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            mostrarNotificacao('Erro ao carregar dados iniciais', 'error');
        }
    }

    // Carrega escolas
    async function carregarEscolas() {
        try {
            const resp = await fetch('/api/escolas');
            const data = await resp.json();
            escolasData = data.escolas || data;
            
            const escolaSelect = document.getElementById('escola-filtro');
            escolaSelect.innerHTML = '<option value="">Selecione a escola</option>';
            escolasData.forEach(escola => {
                escolaSelect.innerHTML += `<option value="${escola.id}">${escola.nome}</option>`;
            });
        } catch (error) {
            console.error('Erro ao carregar escolas:', error);
        }
    }

    // Carrega séries/anos
    async function carregarSeries() {
        const serieSelect = document.getElementById('serie-filtro');
        serieSelect.innerHTML = '<option value="">Selecione a série</option>';
        
        // Adicionar séries do 1º ao 9º ano
        for (let i = 1; i <= 9; i++) {
            serieSelect.innerHTML += `<option value="${i}">${i}º ano</option>`;
        }
    }

    // Carrega cadernos
    async function carregarCadernos() {
        try {
            const resp = await fetch('/api/cadernos');
            if (resp.ok) {
                const data = await resp.json();
                cadernosData = data.cadernos || data;
                
                const cadernoSelect = document.getElementById('caderno-filtro');
                cadernoSelect.innerHTML = '<option value="">Selecione o caderno</option>';
                cadernosData.forEach(caderno => {
                    cadernoSelect.innerHTML += `<option value="${caderno.id}">${caderno.titulo}</option>`;
                });
            }
        } catch (error) {
            console.error('Erro ao carregar cadernos:', error);
            // Fallback com cadernos fictícios se a API não estiver implementada
            const cadernoSelect = document.getElementById('caderno-filtro');
            cadernoSelect.innerHTML = `
                <option value="">Selecione o caderno</option>
                <option value="1">Caderno 1 - 2024</option>
                <option value="2">Caderno 2 - 2024</option>
                <option value="3">Caderno 3 - 2024</option>
            `;
        }
    }

    // Carrega turmas por escola
    async function carregarTurmasPorEscola(escolaId) {
        if (!escolaId) {
            document.getElementById('turma-filtro').innerHTML = '<option value="">Selecione a turma</option>';
            return;
        }

        try {
            const resp = await fetch(`/api/turmas?escola_id=${escolaId}`);
            const data = await resp.json();
            turmasData = data.turmas || [];
            
            const turmaSelect = document.getElementById('turma-filtro');
            turmaSelect.innerHTML = '<option value="">Selecione a turma</option>';
            turmasData.forEach(turma => {
                turmaSelect.innerHTML += `<option value="${turma.id}">${turma.nome}</option>`;
            });
        } catch (error) {
            console.error('Erro ao carregar turmas:', error);
        }
    }

    // Event listener para mudança de escola
    document.getElementById('escola-filtro').addEventListener('change', function() {
        carregarTurmasPorEscola(this.value);
    });

    // Submissão do formulário de filtros
    formFiltros.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        filtrosAtivos = {
            serie: document.getElementById('serie-filtro').value,
            escola: document.getElementById('escola-filtro').value,
            turma: document.getElementById('turma-filtro').value,
            caderno: document.getElementById('caderno-filtro').value,
            componente: document.getElementById('componente-filtro').value
        };

        // Validar se todos os campos obrigatórios estão preenchidos
        if (!filtrosAtivos.serie || !filtrosAtivos.escola || !filtrosAtivos.turma || 
            !filtrosAtivos.caderno || !filtrosAtivos.componente) {
            mostrarNotificacao('Por favor, preencha todos os campos obrigatórios', 'warning');
            return;
        }

        mostrarLoading();
        await carregarAlunos();
        esconderLoading();
    });

    // Carrega alunos baseado nos filtros
    async function carregarAlunos() {
        try {
            const params = new URLSearchParams({
                turma_id: filtrosAtivos.turma,
                caderno_id: filtrosAtivos.caderno,
                componente: filtrosAtivos.componente
            });

            const resp = await fetch(`/api/resultados/alunos?${params}`);
            const data = await resp.json();
            
            if (resp.ok) {
                alunosData = data.alunos || [];
                renderizarAlunos();
                renderizarEstatisticas();
                mostrarSecoes();
            } else {
                throw new Error(data.message || 'Erro ao carregar alunos');
            }
        } catch (error) {
            console.error('Erro ao carregar alunos:', error);
            // Fallback com dados simulados para demonstração
            await carregarAlunosSimulados();
        }
    }

    // Fallback com dados simulados
    async function carregarAlunosSimulados() {
        try {
            const resp = await fetch(`/api/alunos?turma_id=${filtrosAtivos.turma}`);
            const data = await resp.json();
            
            if (resp.ok) {
                const alunos = data.alunos || [];
                alunosData = alunos.map(aluno => ({
                    id: aluno.id,
                    nome: aluno.nome,
                    escola: getEscolaNome(filtrosAtivos.escola),
                    turma: getTurmaNome(filtrosAtivos.turma),
                    status: Math.random() > 0.3 ? 'pendente' : 'concluido',
                    acertos: Math.floor(Math.random() * 20),
                    total: 20,
                    percentual: 0
                }));

                // Calcular percentuais
                alunosData.forEach(aluno => {
                    aluno.percentual = Math.round((aluno.acertos / aluno.total) * 100);
                });

                renderizarAlunos();
                renderizarEstatisticas();
                mostrarSecoes();
            }
        } catch (error) {
            console.error('Erro ao carregar alunos simulados:', error);
            mostrarNotificacao('Erro ao carregar dados dos alunos', 'error');
        }
    }

    // Mostra as seções de estatísticas e alunos
    function mostrarSecoes() {
        statsSection.style.display = 'block';
        alunosSection.style.display = 'block';
        
        // Animação de entrada
        setTimeout(() => {
            statsSection.style.animation = 'slideUp 0.8s ease-out';
            alunosSection.style.animation = 'slideUp 0.8s ease-out 0.2s both';
        }, 100);
    }

    // Renderiza estatísticas
    function renderizarEstatisticas() {
        const concluidos = alunosData.filter(a => a.status === 'concluido').length;
        const pendentes = alunosData.filter(a => a.status === 'pendente').length;
        const total = alunosData.length;
        const percentualConclusao = total > 0 ? Math.round((concluidos / total) * 100) : 0;

        // Atualizar números dos cards com animação
        animarContador('total-concluidos', concluidos);
        animarContador('total-pendentes', pendentes);
        document.getElementById('percentual-conclusao').textContent = `${percentualConclusao}%`;

        // Animar barras de progresso
        setTimeout(() => {
            const progressConcluidos = document.getElementById('progress-concluidos');
            const progressPendentes = document.getElementById('progress-pendentes');
            const progressPercentual = document.getElementById('progress-percentual');

            if (total > 0) {
                progressConcluidos.style.width = `${(concluidos / total) * 100}%`;
                progressPendentes.style.width = `${(pendentes / total) * 100}%`;
                progressPercentual.style.width = `${percentualConclusao}%`;
            }
        }, 500);
    }

    // Função para animar contadores
    function animarContador(elementId, valorFinal) {
        const elemento = document.getElementById(elementId);
        const valorInicial = 0;
        const duracao = 1000; // 1 segundo
        const incremento = valorFinal / (duracao / 16); // 60fps
        let valorAtual = valorInicial;

        const animacao = setInterval(() => {
            valorAtual += incremento;
            if (valorAtual >= valorFinal) {
                valorAtual = valorFinal;
                clearInterval(animacao);
            }
            elemento.textContent = Math.floor(valorAtual);
        }, 16);
    }

    // Renderiza cards dos alunos
    function renderizarAlunos() {
        if (!alunosData.length) {
            alunosGrid.style.display = 'none';
            emptyStateAlunos.style.display = 'block';
            return;
        }

        alunosGrid.style.display = 'grid';
        emptyStateAlunos.style.display = 'none';
        
        alunosGrid.innerHTML = '';

        alunosData.forEach((aluno, index) => {
            const alunoCard = document.createElement('div');
            alunoCard.className = `aluno-card ${aluno.status}`;
            alunoCard.setAttribute('data-id', aluno.id);
            
            let performanceClass = 'performance-insuficiente';
            if (aluno.percentual >= 70) performanceClass = 'performance-avancado';
            else if (aluno.percentual >= 50) performanceClass = 'performance-basico';

            const statusIcon = aluno.status === 'concluido' ? 'fas fa-check-circle' : 'fas fa-clock';
            const statusText = aluno.status === 'concluido' ? 'Concluído' : 'Pendente';

            alunoCard.innerHTML = `
                <div class="aluno-header">
                    <div class="aluno-info">
                        <div class="aluno-nome">
                            <i class="fas fa-user-graduate" style="margin-right: 0.5rem; color: var(--primary);"></i>
                            ${aluno.nome}
                        </div>
                        <div class="aluno-detalhes">
                            <i class="fas fa-graduation-cap" style="margin-right: 0.3rem; color: var(--text-secondary);"></i>
                            ${filtrosAtivos.componente} • ${aluno.turma || 'Turma não informada'}
                        </div>
                    </div>
                    <div class="aluno-status status-${aluno.status}">
                        <i class="${statusIcon}" style="margin-right: 0.3rem;"></i>
                        ${statusText}
                    </div>
                </div>
                
                ${aluno.status === 'concluido' ? `
                    <div class="aluno-progress">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.9rem; color: var(--text-secondary);">
                                <i class="fas fa-chart-bar" style="margin-right: 0.3rem;"></i>
                                Performance
                            </span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-primary);">
                                ${aluno.acertos}/${aluno.total} (${aluno.percentual}%)
                            </span>
                        </div>
                        <div class="performance-bar">
                            <div class="performance-fill ${performanceClass}" style="width: ${aluno.percentual}%;"></div>
                        </div>
                        <div style="text-align: center; margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-secondary);">
                            ${aluno.percentual >= 70 ? '🏆 Excelente' : aluno.percentual >= 50 ? '👍 Bom' : '⚠️ Precisa melhorar'}
                        </div>
                    </div>
                ` : `
                    <div class="aluno-progress">
                        <div style="text-align: center; color: var(--text-secondary); font-size: 0.9rem; padding: 1rem 0;">
                            <i class="fas fa-plus-circle" style="font-size: 1.5rem; color: var(--primary); display: block; margin-bottom: 0.5rem;"></i>
                            <span>Clique para lançar resultado</span>
                        </div>
                    </div>
                `}
            `;

            // Adicionar event listener para clique no card
            alunoCard.addEventListener('click', () => abrirModalGabarito(aluno));
            
            alunosGrid.appendChild(alunoCard);

            // Animação de entrada escalonada
            setTimeout(() => {
                alunoCard.style.animation = `slideUp 0.5s ease-out ${index * 0.1}s both`;
            }, 100);
        });
    }

    // Abrir modal do gabarito
    function abrirModalGabarito(aluno) {
        alunoAtual = aluno;
        document.getElementById('modal-aluno-nome').textContent = `Gabarito - ${aluno.nome}`;
        
        const checkboxFezProva = document.getElementById('aluno-fez-prova');
        checkboxFezProva.checked = aluno.status === 'concluido';
        
        // Toggle do gabarito baseado no status
        toggleGabarito(checkboxFezProva.checked);
        
        if (checkboxFezProva.checked) {
            carregarGabarito(aluno);
        }

        document.getElementById('modal-gabarito').classList.add('active');
    }

    // Event listener para checkbox "aluno fez prova"
    document.getElementById('aluno-fez-prova').addEventListener('change', function() {
        toggleGabarito(this.checked);
    });

    // Toggle do container do gabarito
    function toggleGabarito(mostrar) {
        const gabaritoContainer = document.getElementById('gabarito-container');
        if (mostrar) {
            gabaritoContainer.style.display = 'block';
            if (alunoAtual && alunoAtual.status === 'pendente') {
                gerarGabaritoVazio();
            }
        } else {
            gabaritoContainer.style.display = 'none';
        }
    }

    // Carrega gabarito do aluno
    async function carregarGabarito(aluno) {
        try {
            const resp = await fetch(`/api/resultados/${aluno.id}/${filtrosAtivos.caderno}`);
            if (resp.ok) {
                const data = await resp.json();
                console.log('Dados do gabarito carregados:', data);
                
                if (data.fez_prova && data.respostas && Object.keys(data.respostas).length > 0) {
                    // Converter respostas do formato backend para frontend
                    const respostasConvertidas = converterRespostasParaFrontend(data.respostas);
                    renderizarGabaritoComRespostas(respostasConvertidas);
                } else {
                    // Gerar gabarito vazio para preenchimento
                    gerarGabaritoVazio();
                }
            } else {
                console.log('Erro na resposta da API, gerando gabarito vazio');
                gerarGabaritoVazio();
            }
        } catch (error) {
            console.error('Erro ao carregar gabarito:', error);
            gerarGabaritoVazio();
        }
    }

    // Converte respostas do formato backend (0-1, 0-2) para frontend (Matemática, Português)
    function converterRespostasParaFrontend(respostasBackend) {
        const componentes = filtrosAtivos.componente === 'Ambos' ? ['Matemática', 'Português'] : [filtrosAtivos.componente];
        const respostasFrontend = {};
        
        Object.entries(respostasBackend).forEach(([chave, resposta]) => {
            const [blocoIndex, questaoNum] = chave.split('-');
            const componente = componentes[parseInt(blocoIndex)];
            
            if (componente) {
                if (!respostasFrontend[componente]) {
                    respostasFrontend[componente] = {};
                }
                respostasFrontend[componente][questaoNum] = resposta;
            }
        });
        
        return respostasFrontend;
    }

    // Renderiza gabarito com respostas salvas
    function renderizarGabaritoComRespostas(respostasData) {
        const gabaritoContainer = document.getElementById('gabarito-container');
        gabaritoContainer.innerHTML = '';

        Object.entries(respostasData).forEach(([componente, questoes]) => {
            const bloco = document.createElement('div');
            bloco.className = 'gabarito-bloco';
            bloco.innerHTML = `
                <h4><i class="fas fa-${componente === 'Matemática' ? 'calculator' : 'book'}"></i> ${componente}</h4>
                <div class="questoes-grid" data-componente="${componente}">
                    ${gerarQuestoes(componente, Math.max(...Object.keys(questoes).map(Number)), questoes)}
                </div>
            `;
            gabaritoContainer.appendChild(bloco);
        });
    }

    // Gera gabarito vazio para preenchimento
    function gerarGabaritoVazio() {
        const gabaritoContainer = document.getElementById('gabarito-container');
        const componentes = filtrosAtivos.componente === 'Ambos' ? ['Matemática', 'Português'] : [filtrosAtivos.componente];
        
        gabaritoContainer.innerHTML = '';

        componentes.forEach(comp => {
            const bloco = document.createElement('div');
            bloco.className = 'gabarito-bloco';
            bloco.innerHTML = `
                <h4><i class="fas fa-${comp === 'Matemática' ? 'calculator' : 'book'}"></i> ${comp}</h4>
                <div class="questoes-grid" data-componente="${comp}">
                    ${gerarQuestoes(comp, 10, {})}
                </div>
            `;
            gabaritoContainer.appendChild(bloco);
        });
    }

    // Gera gabarito simulado
    function gerarGabaritoSimulado(aluno) {
        const gabaritoContainer = document.getElementById('gabarito-container');
        const componentes = filtrosAtivos.componente === 'Ambos' ? ['Matemática', 'Português'] : [filtrosAtivos.componente];
        
        gabaritoContainer.innerHTML = '';

        componentes.forEach(comp => {
            // Gerar respostas aleatórias para simulação
            const respostasSimuladas = {};
            for (let i = 1; i <= 10; i++) {
                if (Math.random() > 0.2) { // 80% de chance de ter resposta
                    respostasSimuladas[i] = ['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)];
                }
            }

            const bloco = document.createElement('div');
            bloco.className = 'gabarito-bloco';
            bloco.innerHTML = `
                <h4><i class="fas fa-${comp === 'Matemática' ? 'calculator' : 'book'}"></i> ${comp}</h4>
                <div class="questoes-grid" data-componente="${comp}">
                    ${gerarQuestoes(comp, 10, respostasSimuladas)}
                </div>
            `;
            gabaritoContainer.appendChild(bloco);
        });
    }

    // Renderiza gabarito real
    function renderizarGabarito(gabaritoData) {
        const gabaritoContainer = document.getElementById('gabarito-container');
        gabaritoContainer.innerHTML = '';

        Object.entries(gabaritoData).forEach(([componente, questoes]) => {
            const bloco = document.createElement('div');
            bloco.className = 'gabarito-bloco';
            bloco.innerHTML = `
                <h4><i class="fas fa-${componente === 'Matemática' ? 'calculator' : 'book'}"></i> ${componente}</h4>
                <div class="questoes-grid" data-componente="${componente}">
                    ${gerarQuestoes(componente, Object.keys(questoes).length, questoes)}
                </div>
            `;
            gabaritoContainer.appendChild(bloco);
        });
    }

    // Gera HTML das questões
    function gerarQuestoes(componente, totalQuestoes, respostas) {
        let html = '';
        for (let i = 1; i <= totalQuestoes; i++) {
            const respostaSelecionada = respostas[i] || '';
            html += `
                <div class="questao-item">
                    <div class="questao-numero">Questão ${i}</div>
                    <div class="alternativas">
                        ${['A', 'B', 'C', 'D'].map(alt => `
                            <div class="alternativa ${respostaSelecionada === alt ? 'selecionada' : ''}" 
                                 data-questao="${i}" 
                                 data-componente="${componente}" 
                                 data-alternativa="${alt}">
                                ${alt}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        return html;
    }

    // Event delegation para alternativas
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('alternativa')) {
            const questao = e.target.dataset.questao;
            const componente = e.target.dataset.componente;
            
            // Remover seleção anterior da mesma questão
            const questaoAlternativas = document.querySelectorAll(`[data-questao="${questao}"][data-componente="${componente}"]`);
            questaoAlternativas.forEach(alt => alt.classList.remove('selecionada'));
            
            // Adicionar nova seleção
            e.target.classList.add('selecionada');
        }
    });

    // Função para salvar gabarito
    window.salvarGabarito = async function() {
        if (!alunoAtual) return;

        const fezProva = document.getElementById('aluno-fez-prova').checked;
        
        if (!fezProva) {
            // Salvar como não fez a prova
            await salvarStatusAluno('pendente', {});
            return;
        }

        // Coletar respostas no formato correto para o backend
        const respostas = {};
        const alternativasSelecionadas = document.querySelectorAll('.alternativa.selecionada');
        
        // Buscar blocos do caderno para mapear corretamente
        const componentes = filtrosAtivos.componente === 'Ambos' ? ['Matemática', 'Português'] : [filtrosAtivos.componente];
        
        alternativasSelecionadas.forEach(alt => {
            const componente = alt.dataset.componente;
            const questao = parseInt(alt.dataset.questao);
            const alternativa = alt.dataset.alternativa;
            
            // Encontrar o índice do bloco baseado no componente
            const blocoIndex = componentes.indexOf(componente);
            if (blocoIndex !== -1) {
                const questaoKey = `${blocoIndex}-${questao}`;
                respostas[questaoKey] = alternativa;
            }
        });

        console.log('Respostas coletadas:', respostas);
        await salvarStatusAluno('concluido', respostas);
    };

    // Salva status do aluno
    async function salvarStatusAluno(status, respostas) {
        try {
            mostrarLoading();
            
            const data = {
                aluno_id: alunoAtual.id,
                caderno_id: filtrosAtivos.caderno,
                componente: filtrosAtivos.componente,
                status: status,
                respostas: respostas
            };

            const resp = await fetch('/api/resultados', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (resp.ok) {
                const responseData = await resp.json();
                mostrarNotificacao('Resultado salvo com sucesso!', 'success');
                
                // Atualizar status do aluno na lista com dados reais do backend
                const alunoIndex = alunosData.findIndex(a => a.id === alunoAtual.id);
                if (alunoIndex !== -1) {
                    alunosData[alunoIndex].status = status;
                    if (status === 'concluido' && responseData.resultado) {
                        // Usar dados reais do backend
                        alunosData[alunoIndex].acertos = responseData.resultado.total_acertos;
                        alunosData[alunoIndex].total = responseData.resultado.total_questoes;
                        alunosData[alunoIndex].percentual = Math.round(responseData.resultado.percentual_acertos);
                    } else {
                        // Zerar dados se pendente
                        alunosData[alunoIndex].acertos = 0;
                        alunosData[alunoIndex].total = 0;
                        alunosData[alunoIndex].percentual = 0;
                    }
                    
                    // Atualizar o objeto alunoAtual também
                    alunoAtual.status = status;
                    if (status === 'concluido' && responseData.resultado) {
                        alunoAtual.acertos = responseData.resultado.total_acertos;
                        alunoAtual.total = responseData.resultado.total_questoes;
                        alunoAtual.percentual = Math.round(responseData.resultado.percentual_acertos);
                    } else {
                        alunoAtual.acertos = 0;
                        alunoAtual.total = 0;
                        alunoAtual.percentual = 0;
                    }
                }
                
                renderizarAlunos();
                renderizarEstatisticas();
                fecharModalGabarito();
            } else {
                const error = await resp.json();
                throw new Error(error.message || 'Erro ao salvar resultado');
            }
        } catch (error) {
            console.error('Erro ao salvar resultado:', error);
            mostrarNotificacao('Erro ao salvar resultado', 'error');
        } finally {
            esconderLoading();
        }
    }

    // Funções auxiliares
    function getEscolaNome(escolaId) {
        const escola = escolasData.find(e => e.id == escolaId);
        return escola ? escola.nome : 'Escola não encontrada';
    }

    function getTurmaNome(turmaId) {
        const turma = turmasData.find(t => t.id == turmaId);
        return turma ? turma.nome : 'Turma não encontrada';
    }

    // Funções globais
    window.fecharModalGabarito = function() {
        document.getElementById('modal-gabarito').classList.remove('active');
        alunoAtual = null;
    };

    window.mostrarLoading = function() {
        document.getElementById('modal-loading').classList.add('active');
    };

    window.esconderLoading = function() {
        document.getElementById('modal-loading').classList.remove('active');
    };

    // Inicialização
    carregarDadosIniciais();
});

// Sistema de notificações
function mostrarNotificacao(mensagem, tipo = 'info') {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${tipo}`;
    
    const cores = getCorNotificacao(tipo);
    const icone = getIconeNotificacao(tipo);

    notification.style.cssText = `
        background: linear-gradient(135deg, ${cores.bg}, ${cores.bg}dd);
        color: #FFFFFD;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 0.8rem;
        transform: translateX(400px);
        opacity: 0;
        transition: all 0.4s ease;
        pointer-events: auto;
        cursor: pointer;
        animation: slideInRight 0.4s ease-out;
    `;

    notification.innerHTML = `
        <i class="${icone}" style="font-size: 1.2rem;"></i>
        <span>${mensagem}</span>
        <i class="fas fa-times" style="margin-left: auto; opacity: 0.7; cursor: pointer;"></i>
    `;

    container.appendChild(notification);

    // Animação de entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);

    // Auto-remover após 4 segundos
    const autoRemove = setTimeout(() => {
        removeNotification(notification);
    }, 4000);

    // Remover ao clicar
    notification.addEventListener('click', () => {
        clearTimeout(autoRemove);
        removeNotification(notification);
    });
}

function removeNotification(notification) {
    notification.style.transform = 'translateX(400px)';
    notification.style.opacity = '0';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 400);
}

function getIconeNotificacao(tipo) {
    const icones = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icones[tipo] || icones.info;
}

function getCorNotificacao(tipo) {
    const cores = {
        success: { bg: '#28a745' },
        error: { bg: '#dc3545' },
        warning: { bg: '#ffc107' },
        info: { bg: '#457D97' }
    };
    return cores[tipo] || cores.info;
} 