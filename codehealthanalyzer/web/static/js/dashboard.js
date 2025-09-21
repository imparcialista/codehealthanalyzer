// Dashboard JavaScript para CodeHealthAnalyzer

class Dashboard {
    constructor() {
        this.ws = null;
        this.charts = {}; // no charts anymore, kept for compatibility
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.autoRefreshId = null;
        this.activePriority = 'all';
        this.searchQuery = '';
        this.cachedFiles = [];
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
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
    
    setupCharts() { /* charts removed */ }
    
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
        
        // Atualizar resumo textual e prioridades
        this.renderSummary(data);
        this.renderPriorities(data);
        
        // Atualizar tabela de arquivos
        this.updateFilesTable();
        
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
    
    updateCharts(data) { /* charts removed */ }

    renderSummary(data) {
        const grid = document.getElementById('summary-kv');
        if (!grid) return;
        const score = data.quality_score ?? 0;
        this.setSummaryBadge(score);
        const tiles = [
            { label: 'Score de Qualidade', value: `${score}/100`, tone: score >= 80 ? 'green' : score >= 60 ? 'yellow' : 'red' },
            { label: 'Arquivos analisados', value: data.total_files ?? 0 },
            { label: 'Arquivos com violações', value: data.violation_files ?? 0 },
            { label: 'Templates', value: data.template_files ?? 0 },
            { label: 'Erros Ruff', value: data.error_count ?? 0 },
            { label: 'Issues de alta prioridade', value: data.high_priority_issues ?? 0 },
        ];
        grid.innerHTML = '';
        tiles.forEach(t => {
            const card = document.createElement('div');
            card.className = 'border rounded-md p-3 bg-gray-50 hover:bg-gray-100 transition';
            const label = document.createElement('div');
            label.className = 'text-xs uppercase tracking-wide text-gray-500';
            label.textContent = t.label;
            const value = document.createElement('div');
            value.className = 'mt-1 text-lg font-semibold text-gray-900';
            if (t.tone === 'green') value.classList.add('text-green-700');
            if (t.tone === 'yellow') value.classList.add('text-yellow-700');
            if (t.tone === 'red') value.classList.add('text-red-700');
            value.textContent = `${t.value}`;
            card.appendChild(label);
            card.appendChild(value);
            grid.appendChild(card);
        });
    }

    renderPriorities(data) {
        const listEl = document.getElementById('priorities-list');
        if (!listEl) return;
        listEl.innerHTML = '';
        const items = data.priorities || [];
        const countEl = document.getElementById('priorities-count');
        if (countEl) countEl.textContent = `${items.length} itens`;
        if (!items.length) {
            const li = document.createElement('li');
            li.textContent = 'Nenhuma ação urgente necessária!';
            listEl.appendChild(li);
            return;
        }
        items.forEach((p, idx) => {
            const li = document.createElement('li');
            const count = typeof p.count === 'number' ? p.count : (p.quantity || 0);
            li.textContent = `${idx + 1}. ${p.title || 'N/A'} (${count})`;
            listEl.appendChild(li);
        });
    }
    
    async updateFilesTable() {
        try {
            const response = await fetch('/api/violations');
            const violations = await response.json();
            
            const tableBody = document.getElementById('files-table');
            tableBody.innerHTML = '';
            
            const items = [
                ...(violations.violations || []),
                ...(violations.warnings || []),
            ];
            this.cachedFiles = items;

            const filtered = this.getFilteredFiles();
            if (!filtered.length) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="4" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                        Nenhum arquivo com problemas encontrado no momento.
                    </td>
                `;
                tableBody.appendChild(row);
                return;
            }

            // Ordena por prioridade e quantidade de violações
            const priorityWeight = { high: 3, medium: 2, low: 1 };
            filtered.sort((a, b) => {
                const ap = priorityWeight[a.priority || 'low'];
                const bp = priorityWeight[b.priority || 'low'];
                if (bp !== ap) return bp - ap;
                const av = (a.violations || []).length;
                const bv = (b.violations || []).length;
                return bv - av;
            });

            filtered.slice(0, 20).forEach(file => {
                const row = document.createElement('tr');
                row.className = 'interactive';
                
                const priorityClass = `priority-${file.priority || 'low'}`;
                const violationCount = file.violations ? file.violations.length : 0;
                
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        ${file.file || file.filename || 'N/A'}
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

    getFilteredFiles() {
        const q = (this.searchQuery || '').toLowerCase();
        return (this.cachedFiles || []).filter(item => {
            const p = (item.priority || 'low').toLowerCase();
            const byPriority = this.activePriority === 'all' || p === this.activePriority;
            const name = (item.file || item.filename || '').toLowerCase();
            const bySearch = !q || name.includes(q);
            return byPriority && bySearch;
        });
    }

    setSummaryBadge(score) {
        const badge = document.getElementById('summary-badge');
        if (!badge) return;
        badge.textContent = score >= 80 ? 'SAUDÁVEL' : score >= 60 ? 'ATENÇÃO' : 'PROBLEMAS';
        badge.className = 'px-3 py-1 rounded-full text-xs font-semibold';
        if (score >= 80) {
            badge.classList.add('bg-green-100', 'text-green-700');
        } else if (score >= 60) {
            badge.classList.add('bg-yellow-100', 'text-yellow-700');
        } else {
            badge.classList.add('bg-red-100', 'text-red-700');
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

        // Botão atualizar
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadInitialData());
        }

        // Auto-atualizar
        const autoRefresh = document.getElementById('auto-refresh');
        if (autoRefresh) {
            autoRefresh.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.autoRefreshId = setInterval(() => this.loadInitialData(), 5000);
                } else if (this.autoRefreshId) {
                    clearInterval(this.autoRefreshId);
                    this.autoRefreshId = null;
                }
            });
        }

        // Chips de prioridade
        document.querySelectorAll('.priority-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.priority-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                this.activePriority = chip.getAttribute('data-priority') || 'all';
                this.renderFilteredTable();
            });
        });

        // Busca com debounce
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let t = null;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(t);
                t = setTimeout(() => {
                    this.searchQuery = e.target.value || '';
                    this.renderFilteredTable();
                }, 250);
            });
        }
    }

    renderFilteredTable() {
        const tableBody = document.getElementById('files-table');
        if (!tableBody) return;
        tableBody.innerHTML = '';
        const priorityWeight = { high: 3, medium: 2, low: 1 };
        const filtered = this.getFilteredFiles().sort((a, b) => {
            const ap = priorityWeight[a.priority || 'low'];
            const bp = priorityWeight[b.priority || 'low'];
            if (bp !== ap) return bp - ap;
            const av = (a.violations || []).length;
            const bv = (b.violations || []).length;
            return bv - av;
        });
        if (!filtered.length) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="4" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                    Nenhum arquivo encontrado para os filtros atuais.
                </td>
            `;
            tableBody.appendChild(row);
            return;
        }
        filtered.slice(0, 50).forEach(file => {
            const row = document.createElement('tr');
            row.className = 'interactive';
            const priorityClass = `priority-${file.priority || 'low'}`;
            const violationCount = file.violations ? file.violations.length : 0;
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${file.file || file.filename || 'N/A'}
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