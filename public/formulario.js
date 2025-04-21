// Configuração da URL da API Google Apps Script
const API_URL = 'https://script.google.com/macros/s/AKfycbzOGs-MY6Jm9ZcqGs1U5y0xf8RJ6hjtMFLodd_qFvZppMjyMWztBHWjfUaRR10XWYyMQg/exec';

// Variáveis globais para elementos do DOM
let registroForm;
let participacaoSim;
let participacaoNao;
let camposParticipacaoSim;
let camposParticipacaoNao;
let motivoNao;
let outroMotivoDiv;
let limparFormularioBtn;
let searchButton;
let refreshButton;
let searchInput;
let registrosTableBody;
let loadingSpinner;
let noRecordsMessage;
let alertMessages;
let serventiasList = [];

// Inicializar ao carregar o documento
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando aplicação COGEX...');
    
    // Inicializar elementos do DOM
    inicializarElementos();
    
    // Carregar lista de serventias do JSON
    carregarServentias();
    
    // Configurar event listeners
    configurarEventListeners();
    
    // Verificar se estamos na aba de listagem para carregar registros
    if (window.location.hash === '#list-tab-pane') {
        document.getElementById('list-tab').click();
    }
});

// Função para inicializar todos os elementos do DOM
function inicializarElementos() {
    registroForm = document.getElementById('registroForm');
    participacaoSim = document.getElementById('participacaoSim');
    participacaoNao = document.getElementById('participacaoNao');
    camposParticipacaoSim = document.getElementById('camposParticipacaoSim');
    camposParticipacaoNao = document.getElementById('camposParticipacaoNao');
    motivoNao = document.getElementById('motivoNao');
    outroMotivoDiv = document.getElementById('outroMotivoDiv');
    limparFormularioBtn = document.getElementById('limparFormulario');
    searchButton = document.getElementById('searchButton');
    refreshButton = document.getElementById('refreshButton');
    searchInput = document.getElementById('searchInput');
    registrosTableBody = document.getElementById('registrosTableBody');
    loadingSpinner = document.getElementById('loadingSpinner');
    noRecordsMessage = document.getElementById('noRecordsMessage');
    alertMessages = document.getElementById('alertMessages');
}

// Configurar todos os event listeners necessários
function configurarEventListeners() {
    // Event listeners para campos de participação
    if (participacaoSim) {
        participacaoSim.addEventListener('change', toggleParticipacaoFields);
    }
    
    if (participacaoNao) {
        participacaoNao.addEventListener('change', toggleParticipacaoFields);
    }
    
    // Event listener para mostrar/ocultar campo de "outro motivo"
    if (motivoNao) {
        motivoNao.addEventListener('change', function() {
            outroMotivoDiv.style.display = this.value === 'Outros' ? 'block' : 'none';
        });
    }
    
    // Event listener para botão de limpar formulário
    if (limparFormularioBtn) {
        limparFormularioBtn.addEventListener('click', resetForm);
    }
    
    // Event listener para envio de formulário
    if (registroForm) {
        registroForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Event listeners para pesquisa
    if (searchButton) {
        searchButton.addEventListener('click', searchRegistros);
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchRegistros();
            }
        });
    }
    
    // Event listener para botão de atualizar lista
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Adicionar classe para efeito de rotação
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.add('rotating');
                setTimeout(() => {
                    icon.classList.remove('rotating');
                }, 1000);
            }
            loadRegistros();
        });
    }
    
    // Event listener para aba de listagem
    const listTab = document.getElementById('list-tab');
    if (listTab) {
        listTab.addEventListener('click', function() {
            loadRegistros();
        });
    }
    
    // Configurar modais para visualização e exclusão
    setupModalEvents();
    
    // Adicionar evento para voltar ao topo (opcional)
    adicionarBotaoVoltarAoTopo();
}

// Função para carregar lista de serventias do JSON
async function carregarServentias() {
    try {
        console.log('Carregando lista de serventias...');
        const response = await fetch("serventias_registre_se.json");
        
        if (!response.ok) {
            throw new Error(`Erro ao carregar arquivo JSON: ${response.status}`);
        }
        
        const data = await response.json();
        serventiasList = data.serventias;
        
        const select = document.getElementById("serventia");
        if (!select) {
            console.warn('Elemento select "serventia" não encontrado');
            return;
        }
        
        // Limpar opções existentes
        select.innerHTML = '<option value="">Selecione uma serventia...</option>';
        
        // Adicionar novas opções
        serventiasList.forEach(s => {
            const option = document.createElement("option");
            option.value = s.nome;
            option.textContent = s.nome;
            select.appendChild(option);
        });
        
        console.log(`${serventiasList.length} serventias carregadas com sucesso`);
    } catch (erro) {
        console.error("Erro ao carregar serventias:", erro);
        showAlert("Erro ao carregar lista de serventias. Por favor, recarregue a página.", "danger");
    }
}

// Função para alternar campos baseado na participação
function toggleParticipacaoFields() {
    if (!camposParticipacaoSim || !camposParticipacaoNao) {
        console.warn('Elementos de participação não encontrados');
        return;
    }
    
    if (participacaoSim.checked) {
        camposParticipacaoSim.classList.remove('d-none');
        camposParticipacaoNao.classList.add('d-none');
        
        // Limpar campos da opção "Não"
        if (motivoNao) motivoNao.value = '';
        if (document.getElementById('outroMotivo')) {
            document.getElementById('outroMotivo').value = '';
        }
        if (outroMotivoDiv) outroMotivoDiv.style.display = 'none';
    } else {
        camposParticipacaoSim.classList.add('d-none');
        camposParticipacaoNao.classList.remove('d-none');
        
        // Limpar campos quantitativos
        const camposNumericos = ['viasEmitidas', 'registrosNascimento', 'averacoesPaternidade', 
                              'retificacoes', 'registrosTardios', 'restauracoes'];
        
        camposNumericos.forEach(campo => {
            const elemento = document.getElementById(campo);
            if (elemento) elemento.value = '0';
        });
    }
}

// Função para resetar o formulário
function resetForm() {
    if (!registroForm) {
        console.warn('Formulário não encontrado');
        return;
    }
    
    registroForm.reset();
    toggleParticipacaoFields();
    if (outroMotivoDiv) outroMotivoDiv.style.display = 'none';
    showAlert('Formulário limpo com sucesso.', 'info');
}

// Função para validar o formulário
function validateForm() {
    // Validar campos obrigatórios
    const serventia = document.getElementById('serventia').value.trim();
    const responsavel = document.getElementById('responsavel').value.trim();
    
    if (!serventia) {
        showAlert('Por favor, informe o nome da serventia.', 'danger');
        document.getElementById('serventia').focus();
        document.getElementById('serventia').classList.add('is-invalid');
        return false;
    } else {
        document.getElementById('serventia').classList.remove('is-invalid');
    }
    
    if (!responsavel) {
        showAlert('Por favor, informe o nome do responsável.', 'danger');
        document.getElementById('responsavel').focus();
        document.getElementById('responsavel').classList.add('is-invalid');
        return false;
    } else {
        document.getElementById('responsavel').classList.remove('is-invalid');
    }
    
    // Validar motivo se não participou
    if (participacaoNao.checked && motivoNao && !motivoNao.value) {
        showAlert('Por favor, informe o motivo da não participação.', 'danger');
        motivoNao.focus();
        motivoNao.classList.add('is-invalid');
        return false;
    } else if (motivoNao) {
        motivoNao.classList.remove('is-invalid');
    }
    
    // Se selecionar "Outros" como motivo, verificar se especificou
    if (participacaoNao.checked && 
        motivoNao && motivoNao.value === 'Outros' && 
        document.getElementById('outroMotivo') && 
        !document.getElementById('outroMotivo').value.trim()) {
        
        showAlert('Por favor, especifique o motivo da não participação.', 'danger');
        document.getElementById('outroMotivo').focus();
        document.getElementById('outroMotivo').classList.add('is-invalid');
        return false;
    } else if (document.getElementById('outroMotivo')) {
        document.getElementById('outroMotivo').classList.remove('is-invalid');
    }
    
    return true;
}

// Função para lidar com o envio do formulário
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Validar campos obrigatórios
    if (!validateForm()) {
        return;
    }
    
    // Adicionar classe para desabilitar o formulário durante o envio
    registroForm.classList.add('form-submitting');
    
    // Coletar dados do formulário
    const formData = new FormData(registroForm);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        // Converter campos numéricos para números
        if (['viasEmitidas', 'registrosNascimento', 'averacoesPaternidade', 
             'retificacoes', 'registrosTardios', 'restauracoes'].includes(key)) {
            value = parseInt(value) || 0;
        }
        data[key] = value;
    }
    
    // Adicionar timestamp
    data.timestamp = new Date().toISOString();
    
    // Se não participou, zerar campos de participação
    if (data.participacao === 'Não') {
        data.dataInicio = '';
        data.classificacao = '';
        data.acoesRealizadas = '';
        data.publicosAtendidos = '';
        data.viasEmitidas = 0;
        data.registrosNascimento = 0;
        data.averacoesPaternidade = 0;
        data.retificacoes = 0;
        data.registrosTardios = 0;
        data.restauracoes = 0;
        data.tags = '';
        
        // Adicionar motivo especificado se for "Outros"
        if (data.motivoNao === 'Outros' && document.getElementById('outroMotivo')) {
            data.motivoNao = 'Outros: ' + document.getElementById('outroMotivo').value;
        }
    } else {
        data.motivoNao = '';
    }
    
    // Enviar dados para a API
    saveRegistro(data);
}

// Função aprimorada para salvar registros com tratamento de erros
async function saveRegistro(data) {
    try {
        // Mostrar mensagem de salvando...
        showAlert('Enviando dados...', 'info');
        
        // Desabilitar botão de salvar para evitar duplo envio
        const salvarBtn = document.getElementById('salvarRegistro');
        if (salvarBtn) {
            salvarBtn.disabled = true;
            salvarBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';
        }
        
        // Preparar dados para envio
        const jsonData = JSON.stringify(data);
        
        // Enviar para a API do Google Apps Script com controle de timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000); // 20 segundos de timeout
        
        console.log('Enviando dados para a API:', API_URL);
        
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        // Verificar se a resposta é válida
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('<i class="fas fa-check-circle me-2"></i>Registro salvo com sucesso!', 'success');
            resetForm();
            
            // Se tiver um ID de registro, oferecer link para visualização
            if (result.data && result.data.id) {
                showAlert(`<i class="fas fa-info-circle me-2"></i>Registro #${result.data.id} criado com sucesso!`, 'success');
                
                // Opcional: Perguntar se deseja ver os detalhes
                if (confirm(`Registro #${result.data.id} criado com sucesso! Deseja visualizar os detalhes?`)) {
                    // Mudar para a aba de listagem
                    document.getElementById('list-tab').click();
                    // Aguardar carregamento e destacar o registro
                    setTimeout(() => {
                        loadRegistros().then(() => {
                            const rows = document.querySelectorAll('#registrosTableBody tr');
                            for (const row of rows) {
                                const idCell = row.querySelector('td:first-child');
                                if (idCell && idCell.textContent === result.data.id.toString()) {
                                    row.classList.add('highlight-row');
                                    row.scrollIntoView({behavior: 'smooth', block: 'center'});
                                    break;
                                }
                            }
                        });
                    }, 500);
                }
            }
        } else {
            throw new Error(result.message || 'Erro ao salvar registro');
        }
    } catch (error) {
        console.error('Erro ao salvar registro:', error);
        
        // Mensagem de erro mais informativa
        let errorMsg = `<i class="fas fa-exclamation-circle me-2"></i>Erro ao salvar registro: ${error.message}`;
        
        if (error.name === 'AbortError') {
            errorMsg = '<i class="fas fa-clock me-2"></i>A conexão expirou ao tentar salvar. Verifique sua internet e tente novamente.';
        }
        
        showAlert(errorMsg, 'danger');
    } finally {
        // Restaurar botão de salvar
        const salvarBtn = document.getElementById('salvarRegistro');
        if (salvarBtn) {
            salvarBtn.disabled = false;
            salvarBtn.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Registro';
        }
        
        // Remover classe para habilitar o formulário novamente
        if (registroForm) {
            registroForm.classList.remove('form-submitting');
        }
    }
}

// Função para carregar todos os registros
async function loadRegistros() {
    try {
        // Mostrar spinner de carregamento
        loadingSpinner.classList.remove('d-none');
        registrosTableBody.innerHTML = '';
        noRecordsMessage.classList.add('d-none');
        
        // Fazer requisição para a API com controle de timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 segundos de timeout
        
        console.log('Carregando registros da API:', `${API_URL}?action=getAll`);
        
        const response = await fetch(`${API_URL}?action=getAll`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Esconder spinner
        loadingSpinner.classList.add('d-none');
        
        if (result.success) {
            if (result.data && result.data.length > 0) {
                // Renderizar registros na tabela
                renderRegistros(result.data);
                
                // Log para depuração
                console.log(`Carregados ${result.data.length} registros com sucesso`);
            } else {
                // Mostrar mensagem de nenhum registro
                noRecordsMessage.classList.remove('d-none');
                console.log('Nenhum registro encontrado na planilha');
            }
        } else {
            throw new Error(result.message || 'Erro ao carregar registros');
        }
    } catch (error) {
        console.error('Erro ao carregar registros:', error);
        loadingSpinner.classList.add('d-none');
        
        // Mensagem de erro mais informativa
        let errorMsg = `<i class="fas fa-exclamation-circle me-2"></i>Erro ao carregar registros: ${error.message}`;
        
        if (error.name === 'AbortError') {
            errorMsg = '<i class="fas fa-clock me-2"></i>A conexão expirou. Verifique sua internet e tente novamente.';
        }
        
        showAlert(errorMsg, 'danger');
    }
}

// Função para renderizar os registros na tabela
function renderRegistros(registros) {
    registrosTableBody.innerHTML = '';
    
    // Ordenar por ID decrescente (mais recentes primeiro)
    registros.sort((a, b) => b['ID'] - a['ID']);
    
    registros.forEach(registro => {
        // Calcular total de registros
        const totalRegistros = (
            parseInt(registro['Registros Nascimento'] || 0) +
            parseInt(registro['Vias Emitidas'] || 0) +
            parseInt(registro['Averbações Paternidade'] || 0) +
            parseInt(registro['Retificações'] || 0) +
            parseInt(registro['Registros Tardios'] || 0) +
            parseInt(registro['Restaurações'] || 0)
        );
        
        // Formatar data
        let dataFormatada = 'N/A';
        if (registro['Timestamp']) {
            try {
                const data = new Date(registro['Timestamp']);
                dataFormatada = data.toLocaleDateString('pt-BR');
            } catch (e) {
                console.error('Erro ao formatar data:', e);
                dataFormatada = 'Formato inválido';
            }
        }
        
        // Determinar a classe de status para cor
        const statusClass = registro['Participação'] === 'Sim' ? 'text-success' : 'text-danger';
        
        // Criar linha da tabela com melhorias visuais
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${registro['ID']}</td>
            <td>${registro['Serventia'] || '—'}</td>
            <td>${registro['Responsável'] || '—'}</td>
            <td><span class="${statusClass}">${registro['Participação'] || 'Sim'}</span></td>
            <td>${totalRegistros}</td>
            <td>${dataFormatada}</td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-primary view-btn" data-id="${registro['ID']}" title="Visualizar">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-warning edit-btn" data-id="${registro['ID']}" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-btn" data-id="${registro['ID']}" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        registrosTableBody.appendChild(tr);
    });
    
    // Adicionar event listeners para os botões de ação
    addActionButtonListeners();
}

// Função para pesquisar registros
function searchRegistros() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    // Se não houver termo de busca, recarregar todos os registros
    if (!searchTerm) {
        loadRegistros();
        return;
    }
    
    // Obter todas as linhas da tabela
    const rows = registrosTableBody.querySelectorAll('tr');
    
    // Se não houver linhas, carregar registros primeiro
    if (rows.length === 0) {
        loadRegistros().then(() => {
            filterRows(searchTerm);
        });
    } else {
        filterRows(searchTerm);
    }
}

// Função para filtrar linhas na busca
function filterRows(searchTerm) {
    let found = false;
    const rows = registrosTableBody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
            // Realçar o termo de busca
            highlightSearchTerm(row, searchTerm);
            found = true;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Mostrar ou esconder mensagem de nenhum registro
    if (found) {
        noRecordsMessage.classList.add('d-none');
    } else {
        noRecordsMessage.classList.remove('d-none');
        noRecordsMessage.textContent = `Nenhum registro encontrado contendo "${searchTerm}".`;
    }
}

// Função para realçar o termo de busca
function highlightSearchTerm(row, term) {
    const cells = row.querySelectorAll('td');
    cells.forEach(cell => {
        if (!cell.querySelector('.action-buttons')) { // Pular células com botões
            const text = cell.innerText;
            const regex = new RegExp(`(${term})`, 'gi');
            cell.innerHTML = text.replace(regex, '<span class="highlight">$1</span>');
        }
    });
}

// Função para adicionar event listeners aos botões de ação
function addActionButtonListeners() {
    // Botões de visualização
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            viewRegistro(id);
        });
    });
    
    // Botões de edição
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            editRegistro(id);
        });
    });
    
    // Botões de exclusão
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            showDeleteConfirmation(id);
        });
    });
}

// Função para configurar eventos dos modais
function setupModalEvents() {
    // Configurar botão de salvar edição
    const salvarEdicaoBtn = document.getElementById('salvarEdicaoBtn');
    if (salvarEdicaoBtn) {
        salvarEdicaoBtn.addEventListener('click', () => {
            const id = salvarEdicaoBtn.getAttribute('data-id');
            saveRegistroEdit(id);
        });
    }
    
    // Configurar botão de confirmar exclusão
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', () => {
            const id = confirmDeleteBtn.getAttribute('data-id');
            deleteRegistro(id);
        });
    }
}

// Função para visualizar um registro
async function viewRegistro(id) {
    try {
        // Mostrar overlay de carregamento
        showLoadingOverlay();
        
        // Fazer requisição para a API para obter os detalhes do registro
        const response = await fetch(`${API_URL}?action=getRegistro&id=${id}`);
        
        // Esconder overlay de carregamento
        hideLoadingOverlay();
        
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.data) {
            // Preencher o modal com os dados do registro (somente leitura)
            fillModalWithData(result.data, true);
            
            // Atualizar título do modal
            document.getElementById('registroModalLabel').textContent = `Visualizar Registro #${id}`;
            
            // Esconder botão de salvar
            document.getElementById('salvarEdicaoBtn').style.display = 'none';
            
            // Mostrar o modal
            const registroModal = new bootstrap.Modal(document.getElementById('registroModal'));
            registroModal.show();
        } else {
            throw new Error(result.message || 'Erro ao carregar registro');
        }
    } catch (error) {
        console.error('Erro ao visualizar registro:', error);
        hideLoadingOverlay();
        showAlert(`<i class="fas fa-exclamation-circle me-2"></i>Erro ao visualizar registro: ${error.message}`, 'danger');
    }
}

// Função para editar um registro
async function editRegistro(id) {
    try {
        // Mostrar overlay de carregamento
        showLoadingOverlay();
        
        // Fazer requisição para a API para obter os detalhes do registro
        const response = await fetch(`${API_URL}?action=getRegistro&id=${id}`);
        
        // Esconder overlay de carregamento
        hideLoadingOverlay();
        
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.data) {
            // Preencher o modal com os dados do registro (editável)
            fillModalWithData(result.data, false);
            
            // Atualizar título do modal
            document.getElementById('registroModalLabel').textContent = `Editar Registro #${id}`;
            
            // Mostrar botão de salvar e adicionar ID para uso posterior
            const salvarBtn = document.getElementById('salvarEdicaoBtn');
            salvarBtn.style.display = 'block';
            salvarBtn.setAttribute('data-id', id);
            
            // Mostrar o modal
            const registroModal = new bootstrap.Modal(document.getElementById('registroModal'));
            registroModal.show();
        } else {
            throw new Error(result.message || 'Erro ao carregar registro');
        }
    } catch (error) {
        console.error('Erro ao editar registro:', error);
        hideLoadingOverlay();
        showAlert(`<i class="fas fa-exclamation-circle me-2"></i>Erro ao editar registro: ${error.message}`, 'danger');
    }
}

// Função para preencher o modal com os dados do registro
function fillModalWithData(data, readonly) {
    // Gerar HTML para o modal
    const modalBody = document.querySelector('#registroModal .modal-body');
    
    // Calcular total de registros
    const totalRegistros = (
        parseInt(data['Registros Nascimento'] || 0) +
        parseInt(data['Vias Emitidas'] || 0) +
        parseInt(data['Averbações Paternidade'] || 0) +
        parseInt(data['Retificações'] || 0) +
        parseInt(data['Registros Tardios'] || 0) +
        parseInt(data['Restaurações'] || 0)
    );
    
    // Formatar data
    let dataFormatada = 'N/A';
    if (data['Timestamp']) {
        const timestamp = new Date(data['Timestamp']);
        dataFormatada = timestamp.toLocaleDateString('pt-BR') + ' ' + 
                       timestamp.toLocaleTimeString('pt-BR');
    }
    
    let html = `
        <form id="editForm">
            <div class="row mb-3">
                <div class="col-md-4">
                    <label class="form-label">ID:</label>
                    <input type="text" class="form-control" value="${data['ID']}" readonly>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Protocolo:</label>
                    <input type="text" class="form-control" value="${data['Protocolo'] || ''}" readonly>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Data/Hora:</label>
                    <input type="text" class="form-control" value="${dataFormatada}" readonly>
                </div>
            </div>
            
            <h5 class="mt-4 mb-3 border-bottom pb-2">Dados da Serventia</h5>
            <div class="row mb-3">
                <div class="col-md-8">
                    <label class="form-label">Serventia:</label>
                    <input type="text" class="form-control" name="serventia" value="${data['Serventia']}" ${readonly ? 'readonly' : ''}>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Telefone:</label>
                    <input type="text" class="form-control" name="telefone" value="${data['Telefone'] || ''}" ${readonly ? 'readonly' : ''}>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-8">
                    <label class="form-label">Responsável:</label>
                    <input type="text" class="form-control" name="responsavel" value="${data['Responsável']}" ${readonly ? 'readonly' : ''}>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Email:</label>
                    <input type="email" class="form-control" name="email" value="${data['Email'] || ''}" ${readonly ? 'readonly' : ''}>
                </div>
            </div>
            
            <h5 class="mt-4 mb-3 border-bottom pb-2">Dados da Participação</h5>
            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label">Participou:</label>
                    <select class="form-select" name="participacao" ${readonly ? 'disabled' : ''} id="modal-participacao">
                        <option value="Sim" ${data['Participação'] === 'Sim' || !data['Participação'] ? 'selected' : ''}>Sim</option>
                        <option value="Não" ${data['Participação'] === 'Não' ? 'selected' : ''}>Não</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Data de Início:</label>
                    <input type="date" class="form-control" name="dataInicio" value="${data['Data de Início'] || ''}" ${readonly ? 'readonly' : ''}>
                </div>
            </div>
    `;
    
    // Adicionar campos específicos para participação
    if (data['Participação'] !== 'Não') {
        html += `
            <div id="modal-camposParticipacaoSim">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Classificação:</label>
                        <select class="form-select" name="classificacao" ${readonly ? 'disabled' : ''}>
                            <option value="" ${!data['Classificação'] ? 'selected' : ''}>Selecione...</option>
                            <option value="Integral" ${data['Classificação'] === 'Integral' ? 'selected' : ''}>Integral - Todos os dias</option>
                            <option value="Parcial" ${data['Classificação'] === 'Parcial' ? 'selected' : ''}>Parcial - Alguns dias</option>
                            <option value="Pontual" ${data['Classificação'] === 'Pontual' ? 'selected' : ''}>Pontual - Ação específica</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Total de Registros:</label>
                        <input type="text" class="form-control" value="${totalRegistros}" readonly>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Ações Realizadas:</label>
                    <textarea class="form-control" name="acoesRealizadas" rows="3" ${readonly ? 'readonly' : ''}>${data['Ações Realizadas'] || ''}</textarea>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Públicos Atendidos:</label>
                    <textarea class="form-control" name="publicosAtendidos" rows="2" ${readonly ? 'readonly' : ''}>${data['Públicos Atendidos'] || ''}</textarea>
                </div>
                
                <h5 class="mt-4 mb-3 border-bottom pb-2">Dados Quantitativos</h5>
                <div class="row mb-3">
                    <div class="col-md-4">
                        <label class="form-label">2ª Vias Emitidas:</label>
                        <input type="number" class="form-control" name="viasEmitidas" value="${data['Vias Emitidas'] || 0}" min="0" ${readonly ? 'readonly' : ''}>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Registros de Nascimento:</label>
                        <input type="number" class="form-control" name="registrosNascimento" value="${data['Registros Nascimento'] || 0}" min="0" ${readonly ? 'readonly' : ''}>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Averbações de Paternidade:</label>
                        <input type="number" class="form-control" name="averacoesPaternidade" value="${data['Averbações Paternidade'] || 0}" min="0" ${readonly ? 'readonly' : ''}>
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-4">
                        <label class="form-label">Retificações:</label>
                        <input type="number" class="form-control" name="retificacoes" value="${data['Retificações'] || 0}" min="0" ${readonly ? 'readonly' : ''}>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Registros Tardios:</label>
                        <input type="number" class="form-control" name="registrosTardios" value="${data['Registros Tardios'] || 0}" min="0" ${readonly ? 'readonly' : ''}>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Restaurações:</label>
                        <input type="number" class="form-control" name="restauracoes" value="${data['Restaurações'] || 0}" min="0" ${readonly ? 'readonly' : ''}>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Tags/Palavras-chave:</label>
                    <input type="text" class="form-control" name="tags" value="${data['Tags'] || ''}" ${readonly ? 'readonly' : ''}>
                </div>
            </div>
        `;
    } else {
        html += `
            <div id="modal-camposParticipacaoNao">
                <div class="mb-3">
                    <label class="form-label">Motivo da Não Participação:</label>
                    <input type="text" class="form-control" value="${data['Motivo Não Participação'] || ''}" ${readonly ? 'readonly' : ''} name="motivoNao">
                </div>
            </div>
        `;
    }
    
    // Observações (comum a ambos os casos)
    html += `
        <div class="mb-3">
            <label class="form-label">Observações:</label>
            <textarea class="form-control" name="observacoes" rows="3" ${readonly ? 'readonly' : ''}>${data['Observações'] || ''}</textarea>
        </div>
        </form>
    `;
    
    modalBody.innerHTML = html;
    
    // Adicionar event listener para alternar campos no modal
    if (!readonly) {
        const modalParticipacao = document.getElementById('modal-participacao');
        if (modalParticipacao) {
            modalParticipacao.addEventListener('change', function() {
                const simCampos = document.getElementById('modal-camposParticipacaoSim');
                const naoCampos = document.getElementById('modal-camposParticipacaoNao');
                
                if (this.value === 'Sim') {
                    if (simCampos) simCampos.style.display = 'block';
                    if (naoCampos) naoCampos.style.display = 'none';
                } else {
                    if (simCampos) simCampos.style.display = 'none';
                    if (naoCampos) naoCampos.style.display = 'block';
                }
            });
        }
    }
}

// Função para salvar edições em um registro
async function saveRegistroEdit(id) {
    try {
        // Coletar dados do formulário de edição
        const form = document.getElementById('editForm');
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Converter campos numéricos para números
            if (['viasEmitidas', 'registrosNascimento', 'averacoesPaternidade', 
                 'retificacoes', 'registrosTardios', 'restauracoes'].includes(key)) {
                value = parseInt(value) || 0;
            }
            data[key] = value;
        }
        
        // Adicionar ID para atualização
        data.id = id;
        
        // Mostrar mensagem de atualização
        showAlert('<i class="fas fa-spinner fa-spin me-2"></i>Atualizando registro...', 'info');
        
        // Desabilitar botão de salvar
        const salvarBtn = document.getElementById('salvarEdicaoBtn');
        if (salvarBtn) {
            salvarBtn.disabled = true;
            salvarBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';
        }
        
        // Enviar para a API
        const response = await fetch(`${API_URL}?action=atualizarRegistro`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('<i class="fas fa-check-circle me-2"></i>Registro atualizado com sucesso!', 'success');
            
            // Fechar o modal
            const registroModal = bootstrap.Modal.getInstance(document.getElementById('registroModal'));
            registroModal.hide();
            
            // Recarregar lista de registros
            loadRegistros();
        } else {
            throw new Error(result.message || 'Erro ao atualizar registro');
        }
    } catch (error) {
        console.error('Erro ao atualizar registro:', error);
        showAlert(`<i class="fas fa-exclamation-circle me-2"></i>Erro ao atualizar registro: ${error.message}`, 'danger');
    } finally {
        // Restaurar botão de salvar
        const salvarBtn = document.getElementById('salvarEdicaoBtn');
        if (salvarBtn) {
            salvarBtn.disabled = false;
            salvarBtn.innerHTML = 'Salvar Alterações';
        }
    }
}

// Função para mostrar o modal de confirmação de exclusão
function showDeleteConfirmation(id) {
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    confirmDeleteBtn.setAttribute('data-id', id);
    
    // Atualizar texto da mensagem com o ID do registro
    const modalBody = document.querySelector('#confirmDeleteModal .modal-body');
    modalBody.innerHTML = `
        <p><i class="fas fa-exclamation-triangle text-danger me-2"></i>Tem certeza que deseja excluir o registro #${id}?</p>
        <p class="text-danger"><strong>Esta ação não pode ser desfeita.</strong></p>
    `;
    
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    confirmDeleteModal.show();
}

// Função para excluir um registro
async function deleteRegistro(id) {
    try {
        showAlert('<i class="fas fa-spinner fa-spin me-2"></i>Excluindo registro...', 'info');
        
        // Desabilitar botão de exclusão
        const deleteBtn = document.getElementById('confirmDeleteBtn');
        if (deleteBtn) {
            deleteBtn.disabled = true;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Excluindo...';
        }
        
        // Enviar para a API
        const response = await fetch(`${API_URL}?action=excluirRegistro&id=${id}`, {
            method: 'GET'
        });
        
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('<i class="fas fa-check-circle me-2"></i>Registro excluído com sucesso!', 'success');
            
            // Fechar o modal
            const confirmDeleteModal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            confirmDeleteModal.hide();
            
            // Recarregar lista de registros
            loadRegistros();
        } else {
            throw new Error(result.message || 'Erro ao excluir registro');
        }
    } catch (error) {
        console.error('Erro ao excluir registro:', error);
        showAlert(`<i class="fas fa-exclamation-circle me-2"></i>Erro ao excluir registro: ${error.message}`, 'danger');
    } finally {
        // Restaurar botão de exclusão
        const deleteBtn = document.getElementById('confirmDeleteBtn');
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.innerHTML = 'Excluir';
        }
    }
}

// Função melhorada para mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = message + `
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
    `;
    
    if (!alertMessages) {
        alertMessages = document.getElementById('alertMessages');
    }
    
    // Se não houver container de alertas, criar um
    if (!alertMessages) {
        alertMessages = document.createElement('div');
        alertMessages.id = 'alertMessages';
        document.querySelector('.container').prepend(alertMessages);
    }
    
    alertMessages.appendChild(alertDiv);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            alertDiv.remove();
        }, 150);
    }, 5000);
}

// Função para mostrar overlay de carregamento
function showLoadingOverlay() {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner-border text-light loading-spinner" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

// Função para esconder overlay de carregamento
function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Função para adicionar botão voltar ao topo
function adicionarBotaoVoltarAoTopo() {
    // Verificar se já existe o botão
    if (document.querySelector('.back-to-top')) {
        return;
    }
    
    // Criar botão
    const backToTopBtn = document.createElement('div');
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTopBtn);
    
    // Função para mostrar/ocultar o botão
    function toggleBackToTopButton() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    }
    
    // Event listener para scroll
    window.addEventListener('scroll', toggleBackToTopButton);
    
    // Event listener para clicar no botão
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}
