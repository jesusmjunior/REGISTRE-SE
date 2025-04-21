// Configuração da API Google Apps Script
const API_CONFIG = {
  // URL da implantação do Google Apps Script
  URL: 'https://script.google.com/macros/s/AKfycbzOGs-MY6Jm9ZcqGs1U5y0xf8RJ6hjtMFLodd_qFvZppMjyMWztBHWjfUaRR10XWYyMQg/exec',
};

// Funções para comunicação com a API
const API = {
  // Obter todos os registros
  getAllRegistros: async function() {
    try {
      const response = await fetch(`${API_CONFIG.URL}?action=getAll`, {
        method: 'GET',
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao obter registros:', error);
      throw error;
    }
  },
  
  // Obter um registro por ID
  getRegistroPorId: async function(id) {
    try {
      const response = await fetch(`${API_CONFIG.URL}?action=getRegistro&id=${id}`, {
        method: 'GET',
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao obter registro:', error);
      throw error;
    }
  },
  
  // Salvar novo registro
  saveRegistro: async function(data) {
    try {
      const response = await fetch(API_CONFIG.URL, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao salvar registro:', error);
      throw error;
    }
  },
  
  // Atualizar registro existente
  updateRegistro: async function(id, data) {
    try {
      data.id = id; // Adicionar ID aos dados
      
      const response = await fetch(`${API_CONFIG.URL}?action=atualizarRegistro`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao atualizar registro:', error);
      throw error;
    }
  },
  
  // Excluir registro
  deleteRegistro: async function(id) {
    try {
      const response = await fetch(`${API_CONFIG.URL}?action=excluirRegistro&id=${id}`, {
        method: 'GET',
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao excluir registro:', error);
      throw error;
    }
  }
};
