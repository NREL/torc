/**
 * Torc Dashboard - Core Methods
 * Settings, Navigation, Connection, and Auto-Refresh
 */

Object.assign(TorcDashboard.prototype, {
    // ==================== Settings ====================

    loadSettings() {
        const darkMode = localStorage.getItem('torc-dark-mode') === 'true';
        if (darkMode) {
            document.body.classList.add('dark-mode');
            const checkbox = document.getElementById('dark-mode');
            if (checkbox) checkbox.checked = true;
        }

        const refreshInterval = localStorage.getItem('torc-refresh-interval') || '30';
        const intervalInput = document.getElementById('refresh-interval');
        if (intervalInput) intervalInput.value = refreshInterval;

        const apiUrl = api.getBaseUrl();
        const apiInput = document.getElementById('api-url');
        if (apiInput) apiInput.value = apiUrl;
    },

    saveSettings() {
        const darkMode = document.getElementById('dark-mode')?.checked || false;
        const refreshInterval = document.getElementById('refresh-interval')?.value || '30';
        const apiUrl = document.getElementById('api-url')?.value || '/torc-service/v1';

        localStorage.setItem('torc-dark-mode', darkMode);
        localStorage.setItem('torc-refresh-interval', refreshInterval);
        api.setBaseUrl(apiUrl);

        if (darkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }

        this.showToast('Settings saved', 'success');

        // Restart auto-refresh with new interval
        this.stopAutoRefresh();
        this.startAutoRefresh();
    },

    // ==================== Navigation ====================

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const tab = item.dataset.tab;
                this.switchTab(tab);
            });
        });
    },

    switchTab(tabName, skipHistory = false) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabName}`);
        });

        // Track previous tab for back navigation (unless we're going back)
        if (!skipHistory && this.currentTab !== tabName) {
            this.previousTab = this.currentTab;
        }
        this.currentTab = tabName;

        // Update back button visibility in DAG tab
        this.updateDAGBackButton();

        // Tab-specific initialization
        if (tabName === 'dag' && dagVisualizer && this.selectedWorkflowId) {
            dagVisualizer.initialize();
            dagVisualizer.loadJobDependencies(this.selectedWorkflowId);
        }

        // Sync events workflow selector with selected workflow and clear badge
        if (tabName === 'events') {
            const badge = document.getElementById('event-badge');
            if (badge) badge.style.display = 'none';
            if (this.selectedWorkflowId) {
                const eventsSelector = document.getElementById('events-workflow-selector');
                if (eventsSelector) {
                    eventsSelector.value = this.selectedWorkflowId;
                }
            }
        }

        // Sync debug workflow selector with selected workflow
        if (tabName === 'debugging' && this.selectedWorkflowId) {
            const debugSelector = document.getElementById('debug-workflow-selector');
            if (debugSelector) {
                debugSelector.value = this.selectedWorkflowId;
            }
        }
    },

    // ==================== Connection ====================

    async testConnection() {
        const result = await api.testConnection();
        this.isConnected = result.success;
        this.updateConnectionStatus(result.success);

        const serverInfo = document.getElementById('server-info');
        if (serverInfo) {
            if (result.success) {
                serverInfo.innerHTML = `<p style="color: var(--success-color)">Connected to ${api.getBaseUrl()}</p>`;
            } else {
                serverInfo.innerHTML = `<p style="color: var(--danger-color)">Connection failed: ${result.error}</p>`;
            }
        }

        return result;
    },

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            const dot = statusEl.querySelector('.status-dot');
            const text = statusEl.querySelector('.status-text');
            if (connected) {
                dot.classList.remove('disconnected');
                dot.classList.add('connected');
                text.textContent = 'Connected';
            } else {
                dot.classList.remove('connected');
                dot.classList.add('disconnected');
                text.textContent = 'Disconnected';
            }
        }
    },

    // ==================== Auto Refresh ====================

    startAutoRefresh() {
        const interval = parseInt(localStorage.getItem('torc-refresh-interval') || '30') * 1000;
        this.autoRefreshInterval = setInterval(() => {
            if (this.currentTab === 'workflows') {
                this.loadWorkflows();
            } else if (this.currentTab === 'details' && this.selectedWorkflowId) {
                this.loadWorkflowDetails(this.selectedWorkflowId);
            } else if (this.currentTab === 'dag' && this.selectedWorkflowId) {
                dagVisualizer.refresh();
            }
        }, interval);
    },

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    },
});
