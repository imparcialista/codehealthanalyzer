// Dashboard JavaScript para CodeHealthAnalyzer

class Dashboard {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupCharts();
        this.loadInitialData();
        this.setupEventListeners();
    }
    
    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket conectado');
                this.updateConnectionStatus('connected');
                this.reconnectAttempts = 0;
                this.showNotification('Conectado ao servidor', 'success');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.updateDashboard(data);
                } catch (error) {
                    console.error('Erro ao processar mensagem WebSocket:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket desconectado');
                this.updateConnectionStatus('disconnected');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('Erro WebSocket:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('Erro ao criar WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateConnectionStatus('connecting');
            
            setTimeout(() => {
                console.log(`Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                this.setupWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            this.showNotification('Falha ao conectar com o servidor', 'error');
        }
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        const statusText = statusElement.nextElementSibling;
        
        statusElement.className = 'w-3 h-3 rounded-full mr-2';
        
        switch (status) {
            case 'connected':
                statusElement.classList.add('bg-green-500');
                statusText.textContent = 'Conectado';
                break;
            case 'connecting':
                statusElement.classList.add('bg-yellow-500');
                statusText.textContent = 'Conectando...';
                break;
            case 'disconnected':
            case 'error':
                statusElement.classList.add('bg-red-500');
                statusText.textContent = 'Desconectado';
                break;
        }
    }
    
    setupCharts() {
        // Gráfico de Score ao Longo do Tempo
        const scoreCtx = document.getElementById('scoreChart').getContext('2d');
        this.charts.score = new Chart(scoreCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Score de Qualidade',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // Gráfico de Violações por Tipo
        const violationsCtx = document.getElementById('violationsChart').getContext('2d');
        this.charts.violations = new Chart(violationsCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#10b981',
                        '#3b82f6',
                        '#8b5cf6',
                        '#f97316'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadInitialData() {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            this.updateDashboard(data);
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            this.showNotification('Erro ao carregar dados', 'error');
        }
    }
    
    updateDashboard(data) {
        if (data.error) {
            this.showNotification(`Erro: ${data.error}`, 'error');
            return;
        }
        
        // Atualizar métricas principais
        this.updateMetrics(data);
        
        // Atualizar gráficos
        this.updateCharts(data);
        
        // Atualizar tabela de arquivos
        this.updateFilesTable(data);
        
        // Atualizar timestamp
        this.updateTimestamp(data.timestamp);
    }
    
    updateMetrics(data) {
        const elements = {
            'quality-score': data.quality_score || 0,
            'total-files': data.total_files || 0,
            'violation-files': data.violation_files || 0,
            'high-priority': data.high_priority_issues || 0
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Animação de contagem
                this.animateNumber(element, parseInt(element.textContent) || 0, value);
                
                // Aplicar cor baseada no score
                if (id === 'quality-score') {
                    element.className = `text-2xl font-semibold ${this.getScoreColor(value)}`;
                }
            }
        });
    }
    
    animateNumber(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.round(start + (end - start) * progress);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    getScoreColor(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        return 'score-poor';
    }
    
    updateCharts(data) {
        // Atualizar gráfico de score
        if (this.charts.score) {
            const maxDataPoints = 20; // Limitar a 20 pontos
            
            // Adicionar novo ponto e manter apenas os últimos maxDataPoints
            const currentTime = new Date().toLocaleTimeString();
            const currentScore = data.quality_score || 0;
            
            this.charts.score.data.labels.push(currentTime);
            this.charts.score.data.datasets[0].data.push(currentScore);
            
            // Remover pontos antigos se exceder o limite
            if (this.charts.score.data.labels.length > maxDataPoints) {
                this.charts.score.data.labels.shift();
                this.charts.score.data.datasets[0].data.shift();
            }
            
            this.charts.score.update('none');
        }
        
        // Atualizar gráfico de violações
        if (data.violations_by_type && this.charts.violations) {
            const labels = Object.keys(data.violations_by_type);
            const values = Object.values(data.violations_by_type);
            
            this.charts.violations.data.labels = labels;
            this.charts.violations.data.datasets[0].data = values;
            this.charts.violations.update('none');
        }
    }
    
    async updateFilesTable(data) {
        try {
            const response = await fetch('/api/violations');
            const violations = await response.json();
            
            const tableBody = document.getElementById('files-table');
            tableBody.innerHTML = '';
            
            const files = violations.files || [];
            files.slice(0, 10).forEach(file => {
                const row = document.createElement('tr');
                row.className = 'interactive';
                
                const priorityClass = `priority-${file.priority || 'low'}`;
                const violationCount = file.violations ? file.violations.length : 0;
                
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        ${file.file || 'N/A'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${priorityClass}">
                            ${file.priority || 'low'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${violationCount}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${file.lines || 0}
                    </td>
                `;
                
                tableBody.appendChild(row);
            });
            
        } catch (error) {
            console.error('Erro ao atualizar tabela:', error);
        }
    }
    
    updateTimestamp(timestamp) {
        const element = document.getElementById('last-update');
        if (element && timestamp) {
            const date = new Date(timestamp);
            element.textContent = date.toLocaleString();
        }
    }
    
    setupEventListeners() {
        // Refresh manual
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                e.preventDefault();
                this.loadInitialData();
                this.showNotification('Dados atualizados', 'info');
            }
        });
        
        // Detectar visibilidade da página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Página não está visível, pausar atualizações
                if (this.ws) {
                    this.ws.close();
                }
            } else {
                // Página voltou a ficar visível, reconectar
                this.setupWebSocket();
            }
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Mostrar notificação
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Remover notificação após 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Inicializar dashboard quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});