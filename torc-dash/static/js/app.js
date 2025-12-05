/**
 * Torc Dashboard Application
 * Main application logic and UI management
 */

class TorcDashboard {
    constructor() {
        this.currentTab = 'workflows';
        this.selectedWorkflowId = null;
        this.selectedSubTab = 'jobs';
        this.workflows = [];
        this.events = [];
        this.lastEventId = null;
        this.eventPollInterval = null;
        this.autoRefreshInterval = null;
        this.isConnected = false;
        this.uploadedSpecContent = null;
        this.currentCreateTab = 'upload';
        this.debugJobs = [];
        this.selectedDebugJob = null;
        this.currentLogTab = 'stdout';
    }

    async init() {
        // Load saved settings
        this.loadSettings();

        // Setup event listeners
        this.setupNavigation();
        this.setupWorkflowsTab();
        this.setupDetailsTab();
        this.setupDAGTab();
        this.setupEventsTab();
        this.setupDebuggingTab();
        this.setupSettingsTab();
        this.setupModal();
        this.setupExecutionPlanModal();
        this.setupInitConfirmModal();

        // Initial data load
        await this.testConnection();
        if (this.isConnected) {
            await this.loadWorkflows();
            this.startAutoRefresh();
        }
    }

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
    }

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
    }

    // ==================== Navigation ====================

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const tab = item.dataset.tab;
                this.switchTab(tab);
            });
        });
    }

    switchTab(tabName) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabName}`);
        });

        this.currentTab = tabName;

        // Tab-specific initialization
        if (tabName === 'dag' && dagVisualizer && this.selectedWorkflowId) {
            dagVisualizer.initialize();
            dagVisualizer.loadJobDependencies(this.selectedWorkflowId);
        }

        // Clear event badge when viewing events
        if (tabName === 'events') {
            const badge = document.getElementById('event-badge');
            if (badge) badge.style.display = 'none';
        }
    }

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
    }

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
    }

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
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    // ==================== Workflows Tab ====================

    setupWorkflowsTab() {
        document.getElementById('btn-refresh-workflows')?.addEventListener('click', () => {
            this.loadWorkflows();
        });

        document.getElementById('btn-create-workflow')?.addEventListener('click', () => {
            this.showModal('create-workflow-modal');
        });

        // Workflow filter
        document.getElementById('workflow-filter')?.addEventListener('input', (e) => {
            this.filterWorkflows(e.target.value);
        });
    }

    async loadWorkflows() {
        try {
            const workflows = await api.listWorkflows(0, 100);
            this.workflows = workflows || [];
            this.renderWorkflowsTable(this.workflows);
            this.updateWorkflowSelectors(this.workflows);
        } catch (error) {
            console.error('Error loading workflows:', error);
            this.showToast('Error loading workflows: ' + error.message, 'error');
        }
    }

    filterWorkflows(filterText) {
        if (!filterText) {
            this.renderWorkflowsTable(this.workflows);
            return;
        }

        const lowerFilter = filterText.toLowerCase();
        const filtered = this.workflows.filter(w =>
            (w.name || '').toLowerCase().includes(lowerFilter) ||
            (w.owner || '').toLowerCase().includes(lowerFilter) ||
            (w.id || '').toLowerCase().includes(lowerFilter) ||
            (w.description || '').toLowerCase().includes(lowerFilter)
        );
        this.renderWorkflowsTable(filtered);
    }

    renderWorkflowsTable(workflows) {
        const tbody = document.getElementById('workflows-body');
        if (!tbody) return;

        if (!workflows || workflows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="placeholder-message">No workflows found</td></tr>';
            return;
        }

        tbody.innerHTML = workflows.map(workflow => `
            <tr data-workflow-id="${workflow.id}">
                <td><code>${this.truncateId(workflow.id)}</code></td>
                <td>${this.escapeHtml(workflow.name || 'Unnamed')}</td>
                <td>${this.escapeHtml(workflow.owner || '-')}</td>
                <td>${this.getStatusBadge(workflow)}</td>
                <td>${workflow.job_count || '-'}</td>
                <td>${this.formatDate(workflow.created_at)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-success" onclick="app.runWorkflow('${workflow.id}')" title="Run Locally">Run</button>
                        <button class="btn btn-sm btn-primary" onclick="app.submitWorkflow('${workflow.id}')" title="Submit to Scheduler">Submit</button>
                        <button class="btn btn-sm btn-secondary" onclick="app.viewWorkflow('${workflow.id}')" title="View Details">View</button>
                        <button class="btn btn-sm btn-secondary" onclick="app.viewDAG('${workflow.id}')" title="View DAG">DAG</button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteWorkflow('${workflow.id}')" title="Delete">Del</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getStatusBadge(workflow) {
        // Compute workflow status from job counts if available
        let statusClass = 'status-uninitialized';
        let statusText = 'Unknown';

        if (workflow.status) {
            statusText = workflow.status;
            statusClass = `status-${workflow.status.toLowerCase()}`;
        } else if (workflow.completed_count !== undefined) {
            const total = workflow.job_count || 0;
            const completed = workflow.completed_count || 0;
            const failed = workflow.failed_count || 0;
            const running = workflow.running_count || 0;

            if (failed > 0) {
                statusClass = 'status-failed';
                statusText = `Failed (${failed})`;
            } else if (completed === total && total > 0) {
                statusClass = 'status-completed';
                statusText = 'Completed';
            } else if (running > 0) {
                statusClass = 'status-running';
                statusText = `Running (${running})`;
            } else if (completed > 0) {
                statusClass = 'status-pending';
                statusText = `${completed}/${total}`;
            } else {
                statusClass = 'status-ready';
                statusText = 'Ready';
            }
        }

        return `<span class="status-badge ${statusClass}">${statusText}</span>`;
    }

    updateWorkflowSelectors(workflows) {
        const selectors = [
            'workflow-selector',
            'dag-workflow-selector',
            'events-workflow-selector',
            'debug-workflow-selector',
        ];

        selectors.forEach(id => {
            const select = document.getElementById(id);
            if (!select) return;

            const currentValue = select.value;
            const options = workflows.map(w =>
                `<option value="${w.id}">${this.escapeHtml(w.name || w.id)}</option>`
            ).join('');

            if (id === 'events-workflow-selector') {
                select.innerHTML = `<option value="">All Workflows</option>${options}`;
            } else {
                select.innerHTML = `<option value="">Select a workflow...</option>${options}`;
            }

            // Restore selection if still valid
            if (currentValue && workflows.find(w => w.id === currentValue)) {
                select.value = currentValue;
            }
        });
    }

    async viewWorkflow(workflowId) {
        this.selectedWorkflowId = workflowId;
        document.getElementById('workflow-selector').value = workflowId;
        this.switchTab('details');
        await this.loadWorkflowDetails(workflowId);
    }

    async viewDAG(workflowId) {
        this.selectedWorkflowId = workflowId;
        document.getElementById('dag-workflow-selector').value = workflowId;
        this.switchTab('dag');
        dagVisualizer.initialize();
        await dagVisualizer.loadJobDependencies(workflowId);
    }

    async deleteWorkflow(workflowId) {
        if (!confirm('Are you sure you want to delete this workflow? This action cannot be undone.')) {
            return;
        }

        try {
            const result = await api.cliDeleteWorkflow(workflowId);
            if (result.success) {
                this.showToast('Workflow deleted', 'success');
                await this.loadWorkflows();
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout), 'error');
            }
        } catch (error) {
            this.showToast('Error deleting workflow: ' + error.message, 'error');
        }
    }

    async runWorkflow(workflowId) {
        if (!confirm('Run this workflow locally? This will execute jobs on this machine.')) {
            return;
        }

        this.showToast('Starting workflow run...', 'info');
        try {
            const result = await api.cliRunWorkflow(workflowId);
            if (result.success) {
                this.showToast('Workflow started successfully', 'success');
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout), 'error');
            }
        } catch (error) {
            this.showToast('Error running workflow: ' + error.message, 'error');
        }
    }

    async submitWorkflow(workflowId) {
        if (!confirm('Submit this workflow to the scheduler (e.g., Slurm)?')) {
            return;
        }

        this.showToast('Submitting workflow...', 'info');
        try {
            const result = await api.cliSubmitWorkflow(workflowId);
            if (result.success) {
                this.showToast('Workflow submitted successfully', 'success');
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout), 'error');
            }
        } catch (error) {
            this.showToast('Error submitting workflow: ' + error.message, 'error');
        }
    }

    async initializeWorkflow(workflowId, force = false) {
        try {
            // If not forcing, first check if there are existing output files
            if (!force) {
                const checkResult = await api.cliCheckInitialize(workflowId);

                // Parse the JSON response from stdout
                if (checkResult.success && checkResult.stdout) {
                    try {
                        const dryRunData = JSON.parse(checkResult.stdout);
                        const fileCount = dryRunData.existing_output_file_count || 0;

                        if (fileCount > 0) {
                            // Show confirmation modal
                            this.showInitializeConfirmModal(workflowId, fileCount, dryRunData.existing_output_files || []);
                            return;
                        }
                    } catch (parseError) {
                        // JSON parse failed, continue with initialization
                        console.warn('Could not parse dry-run response:', parseError);
                    }
                }
            }

            // Proceed with actual initialization
            const result = await api.cliInitializeWorkflow(workflowId, force);
            if (result.success) {
                this.showToast('Workflow initialized', 'success');
                await this.loadWorkflows();
                if (this.selectedWorkflowId === workflowId) {
                    await this.loadWorkflowDetails(workflowId);
                }
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout), 'error');
            }
        } catch (error) {
            this.showToast('Error initializing workflow: ' + error.message, 'error');
        }
    }

    showInitializeConfirmModal(workflowId, fileCount, files) {
        // Store for use by confirm button
        this.pendingInitializeWorkflowId = workflowId;

        // Update modal content
        const content = document.getElementById('init-confirm-content');
        if (content) {
            const fileList = files.slice(0, 10).map(f => `<li><code>${this.escapeHtml(f)}</code></li>`).join('');
            const moreFiles = files.length > 10 ? `<li>... and ${files.length - 10} more</li>` : '';

            content.innerHTML = `
                <p>This workflow has <strong>${fileCount}</strong> existing output file(s) that will be deleted:</p>
                <ul class="file-list">${fileList}${moreFiles}</ul>
                <p>Do you want to proceed and delete these files?</p>
            `;
        }

        this.showModal('init-confirm-modal');
    }

    // ==================== Details Tab ====================

    setupDetailsTab() {
        document.getElementById('workflow-selector')?.addEventListener('change', async (e) => {
            const workflowId = e.target.value;
            if (workflowId) {
                this.selectedWorkflowId = workflowId;
                await this.loadWorkflowDetails(workflowId);
            } else {
                this.clearWorkflowDetails();
            }
        });

        document.getElementById('btn-refresh-details')?.addEventListener('click', async () => {
            if (this.selectedWorkflowId) {
                await this.loadWorkflowDetails(this.selectedWorkflowId);
            }
        });

        // Sub-tab navigation
        document.querySelectorAll('.sub-tab[data-subtab]').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchSubTab(tab.dataset.subtab);
            });
        });

        // Workflow action buttons
        document.getElementById('btn-init-workflow')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.initializeWorkflow(this.selectedWorkflowId);
        });

        document.getElementById('btn-reinit-workflow')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.reinitializeWorkflow(this.selectedWorkflowId);
        });

        document.getElementById('btn-reset-workflow')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.resetWorkflow(this.selectedWorkflowId);
        });

        document.getElementById('btn-run-workflow-detail')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.runWorkflow(this.selectedWorkflowId);
        });

        document.getElementById('btn-submit-workflow-detail')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.submitWorkflow(this.selectedWorkflowId);
        });

        document.getElementById('btn-show-dag')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.viewDAG(this.selectedWorkflowId);
        });

        document.getElementById('btn-show-plan')?.addEventListener('click', () => {
            if (this.selectedWorkflowId) this.showExecutionPlan(this.selectedWorkflowId);
        });
    }

    async reinitializeWorkflow(workflowId) {
        if (!confirm('Re-initialize workflow? This will reset all jobs to uninitialized state.')) {
            return;
        }
        // Use the API to reinitialize (reset then initialize)
        try {
            await api.request(`/workflows/${workflowId}/reset`, { method: 'POST' });
            await this.initializeWorkflow(workflowId);
        } catch (error) {
            this.showToast('Error re-initializing: ' + error.message, 'error');
        }
    }

    async resetWorkflow(workflowId) {
        if (!confirm('Reset workflow? This will set all jobs back to uninitialized state.')) {
            return;
        }
        try {
            await api.request(`/workflows/${workflowId}/reset`, { method: 'POST' });
            this.showToast('Workflow reset', 'success');
            await this.loadWorkflowDetails(workflowId);
        } catch (error) {
            this.showToast('Error resetting: ' + error.message, 'error');
        }
    }

    async loadWorkflowDetails(workflowId) {
        try {
            const workflow = await api.getWorkflow(workflowId);

            // Show workflow summary
            const container = document.getElementById('details-container');
            container.innerHTML = `
                <div class="workflow-summary">
                    <div class="summary-card">
                        <div class="value">${workflow.id ? this.truncateId(workflow.id) : '-'}</div>
                        <div class="label">ID</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">${this.escapeHtml(workflow.name || 'Unnamed')}</div>
                        <div class="label">Name</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">${this.escapeHtml(workflow.owner || '-')}</div>
                        <div class="label">Owner</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">${this.formatDate(workflow.created_at)}</div>
                        <div class="label">Created</div>
                    </div>
                </div>
            `;

            // Show actions panel and sub-tabs
            document.getElementById('workflow-actions-panel').style.display = 'flex';
            document.getElementById('details-sub-tabs').style.display = 'flex';

            // Load current sub-tab content
            await this.loadSubTabContent(workflowId, this.selectedSubTab);
        } catch (error) {
            console.error('Error loading workflow details:', error);
            this.showToast('Error loading workflow details: ' + error.message, 'error');
        }
    }

    clearWorkflowDetails() {
        document.getElementById('details-container').innerHTML = `
            <div class="placeholder-message">Select a workflow to view details</div>
        `;
        document.getElementById('workflow-actions-panel').style.display = 'none';
        document.getElementById('details-sub-tabs').style.display = 'none';
        document.getElementById('details-content').innerHTML = '';
    }

    switchSubTab(subtab) {
        this.selectedSubTab = subtab;

        document.querySelectorAll('.sub-tab[data-subtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.subtab === subtab);
        });

        if (this.selectedWorkflowId) {
            this.loadSubTabContent(this.selectedWorkflowId, subtab);
        }
    }

    async loadSubTabContent(workflowId, subtab) {
        const content = document.getElementById('details-content');

        try {
            switch (subtab) {
                case 'jobs':
                    const jobs = await api.listJobs(workflowId);
                    content.innerHTML = this.renderJobsTable(jobs);
                    break;
                case 'files':
                    const files = await api.listFiles(workflowId);
                    content.innerHTML = this.renderFilesTable(files);
                    break;
                case 'user-data':
                    const userData = await api.listUserData(workflowId);
                    content.innerHTML = this.renderUserDataTable(userData);
                    break;
                case 'results':
                    const results = await api.listResults(workflowId);
                    content.innerHTML = this.renderResultsTable(results);
                    break;
                case 'schedulers':
                    const schedulers = await api.listSchedulers(workflowId);
                    content.innerHTML = this.renderSchedulersTable(schedulers);
                    break;
                case 'compute-nodes':
                    const nodes = await api.listComputeNodes(workflowId);
                    content.innerHTML = this.renderComputeNodesTable(nodes);
                    break;
                case 'resources':
                    const resources = await api.listResourceRequirements(workflowId);
                    content.innerHTML = this.renderResourcesTable(resources);
                    break;
            }
        } catch (error) {
            content.innerHTML = `<div class="placeholder-message">Error loading ${subtab}: ${error.message}</div>`;
        }
    }

    renderJobsTable(jobs) {
        if (!jobs || jobs.length === 0) {
            return '<div class="placeholder-message">No jobs in this workflow</div>';
        }

        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Command</th>
                        <th>Started</th>
                        <th>Completed</th>
                    </tr>
                </thead>
                <tbody>
                    ${jobs.map(job => `
                        <tr>
                            <td><code>${this.truncateId(job.id)}</code></td>
                            <td>${this.escapeHtml(job.name || '-')}</td>
                            <td><span class="status-badge status-${statusNames[job.status]?.toLowerCase() || 'unknown'}">${statusNames[job.status] || job.status}</span></td>
                            <td><code>${this.escapeHtml(this.truncate(job.command || '-', 50))}</code></td>
                            <td>${this.formatDate(job.start_time)}</td>
                            <td>${this.formatDate(job.end_time)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderFilesTable(files) {
        if (!files || files.length === 0) {
            return '<div class="placeholder-message">No files in this workflow</div>';
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Path</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
                    ${files.map(file => `
                        <tr>
                            <td><code>${this.truncateId(file.id)}</code></td>
                            <td>${this.escapeHtml(file.name || '-')}</td>
                            <td><code>${this.escapeHtml(file.path || '-')}</code></td>
                            <td>${this.escapeHtml(file.file_type || '-')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderUserDataTable(userData) {
        if (!userData || userData.length === 0) {
            return '<div class="placeholder-message">No user data in this workflow</div>';
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    ${userData.map(ud => `
                        <tr>
                            <td><code>${this.truncateId(ud.id)}</code></td>
                            <td>${this.escapeHtml(ud.name || '-')}</td>
                            <td><code>${this.escapeHtml(this.truncate(JSON.stringify(ud.data) || '-', 100))}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderResultsTable(results) {
        if (!results || results.length === 0) {
            return '<div class="placeholder-message">No results in this workflow</div>';
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Job ID</th>
                        <th>Return Code</th>
                        <th>Stdout</th>
                        <th>Stderr</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map(result => `
                        <tr>
                            <td><code>${this.truncateId(result.id)}</code></td>
                            <td><code>${this.truncateId(result.job_id)}</code></td>
                            <td class="${result.return_code === 0 ? 'return-code-0' : 'return-code-error'}">${result.return_code ?? '-'}</td>
                            <td><code>${this.escapeHtml(this.truncate(result.stdout || '-', 50))}</code></td>
                            <td><code>${this.escapeHtml(this.truncate(result.stderr || '-', 50))}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderSchedulersTable(schedulers) {
        const items = api.extractItems(schedulers);
        if (!items || items.length === 0) {
            return '<div class="placeholder-message">No schedulers in this workflow</div>';
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Account</th>
                        <th>Partition</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(s => `
                        <tr>
                            <td><code>${this.truncateId(s.id)}</code></td>
                            <td>${this.escapeHtml(s.name || '-')}</td>
                            <td>${this.escapeHtml(s.scheduler_type || '-')}</td>
                            <td>${this.escapeHtml(s.account || '-')}</td>
                            <td>${this.escapeHtml(s.partition || '-')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderComputeNodesTable(nodes) {
        const items = api.extractItems(nodes);
        if (!items || items.length === 0) {
            return '<div class="placeholder-message">No compute nodes in this workflow</div>';
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Hostname</th>
                        <th>CPUs</th>
                        <th>Memory</th>
                        <th>GPUs</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(n => `
                        <tr>
                            <td><code>${this.truncateId(n.id)}</code></td>
                            <td>${this.escapeHtml(n.hostname || '-')}</td>
                            <td>${n.num_cpus ?? '-'}</td>
                            <td>${this.escapeHtml(n.memory || '-')}</td>
                            <td>${n.num_gpus ?? '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderResourcesTable(resources) {
        const items = api.extractItems(resources);
        if (!items || items.length === 0) {
            return '<div class="placeholder-message">No resource requirements in this workflow</div>';
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>CPUs</th>
                        <th>Memory</th>
                        <th>GPUs</th>
                        <th>Runtime</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(r => `
                        <tr>
                            <td><code>${this.truncateId(r.id)}</code></td>
                            <td>${this.escapeHtml(r.name || '-')}</td>
                            <td>${r.num_cpus ?? '-'}</td>
                            <td>${this.escapeHtml(r.memory || '-')}</td>
                            <td>${r.num_gpus ?? '-'}</td>
                            <td>${this.escapeHtml(r.runtime || '-')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    // ==================== DAG Tab ====================

    setupDAGTab() {
        document.getElementById('dag-workflow-selector')?.addEventListener('change', async (e) => {
            const workflowId = e.target.value;
            if (workflowId) {
                this.selectedWorkflowId = workflowId;
                dagVisualizer.initialize();
                await this.loadDAG(workflowId);
            }
        });

        document.getElementById('dag-type-selector')?.addEventListener('change', async (e) => {
            if (this.selectedWorkflowId) {
                await this.loadDAG(this.selectedWorkflowId);
            }
        });

        document.getElementById('btn-fit-dag')?.addEventListener('click', () => {
            dagVisualizer.fitToView();
        });
    }

    async loadDAG(workflowId) {
        const type = document.getElementById('dag-type-selector')?.value || 'jobs';

        switch (type) {
            case 'jobs':
                await dagVisualizer.loadJobDependencies(workflowId);
                break;
            case 'files':
                await dagVisualizer.loadFileRelationships(workflowId);
                break;
            case 'userdata':
                await dagVisualizer.loadUserDataRelationships(workflowId);
                break;
        }
    }

    // ==================== Events Tab ====================

    setupEventsTab() {
        document.getElementById('events-workflow-selector')?.addEventListener('change', () => {
            this.events = [];
            this.lastEventId = null;
            this.loadEvents();
        });

        document.getElementById('btn-clear-events')?.addEventListener('click', () => {
            this.events = [];
            this.lastEventId = null;
            this.renderEvents();
        });

        document.getElementById('auto-refresh-events')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startEventPolling();
            } else {
                this.stopEventPolling();
            }
        });

        // Start polling if auto-refresh is checked
        const autoRefresh = document.getElementById('auto-refresh-events');
        if (autoRefresh?.checked) {
            this.startEventPolling();
        }
    }

    startEventPolling() {
        this.stopEventPolling();
        this.loadEvents();
        this.eventPollInterval = setInterval(() => this.loadEvents(), 10000);
    }

    stopEventPolling() {
        if (this.eventPollInterval) {
            clearInterval(this.eventPollInterval);
            this.eventPollInterval = null;
        }
    }

    async loadEvents() {
        try {
            const workflowId = document.getElementById('events-workflow-selector')?.value || null;
            const newEvents = await api.listEvents(workflowId, 0, 50, this.lastEventId);

            if (newEvents && newEvents.length > 0) {
                // Prepend new events
                this.events = [...newEvents, ...this.events].slice(0, 200); // Keep last 200 events
                this.lastEventId = newEvents[0].id;
                this.updateEventBadge(newEvents.length);
            }

            this.renderEvents();
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    renderEvents() {
        const container = document.getElementById('events-list');
        if (!container) return;

        if (this.events.length === 0) {
            container.innerHTML = '<div class="placeholder-message">No events yet</div>';
            return;
        }

        container.innerHTML = this.events.map(event => `
            <div class="event-item">
                <span class="event-time">${this.formatDate(event.timestamp)}</span>
                <span class="event-type">${this.escapeHtml(event.event_type || '-')}</span>
                <span class="event-message">${this.escapeHtml(event.message || '-')}</span>
            </div>
        `).join('');
    }

    updateEventBadge(count) {
        const badge = document.getElementById('event-badge');
        if (badge) {
            if (count > 0 && this.currentTab !== 'events') {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    // ==================== Debugging Tab ====================

    setupDebuggingTab() {
        document.getElementById('debug-workflow-selector')?.addEventListener('change', (e) => {
            this.selectedWorkflowId = e.target.value;
        });

        document.getElementById('btn-generate-report')?.addEventListener('click', () => {
            this.generateDebugReport();
        });

        // Log tab navigation
        document.querySelectorAll('.sub-tab[data-logtab]').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchLogTab(tab.dataset.logtab);
            });
        });
    }

    async generateDebugReport() {
        const workflowId = document.getElementById('debug-workflow-selector')?.value;
        if (!workflowId) {
            this.showToast('Please select a workflow first', 'warning');
            return;
        }

        try {
            // Get jobs and results for the workflow
            const [jobs, results] = await Promise.all([
                api.listJobs(workflowId),
                api.listResults(workflowId),
            ]);

            const failedOnly = document.getElementById('debug-failed-only')?.checked;

            // Build a map of job results
            const resultMap = {};
            results.forEach(r => {
                if (!resultMap[r.job_id]) resultMap[r.job_id] = [];
                resultMap[r.job_id].push(r);
            });

            // Filter and enrich jobs with result data
            this.debugJobs = jobs.map(job => ({
                ...job,
                results: resultMap[job.id] || [],
                latestResult: resultMap[job.id]?.[resultMap[job.id].length - 1],
            }));

            if (failedOnly) {
                this.debugJobs = this.debugJobs.filter(j =>
                    j.latestResult && j.latestResult.return_code !== 0
                );
            }

            this.renderDebugJobsTable();
            document.getElementById('debug-job-count').textContent = `(${this.debugJobs.length})`;
        } catch (error) {
            this.showToast('Error generating report: ' + error.message, 'error');
        }
    }

    renderDebugJobsTable() {
        const container = document.getElementById('debug-jobs-table-container');
        if (!container) return;

        if (this.debugJobs.length === 0) {
            container.innerHTML = '<div class="placeholder-message">No jobs match the criteria</div>';
            return;
        }

        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Job Name</th>
                        <th>Status</th>
                        <th>Return Code</th>
                        <th>Stdout</th>
                        <th>Stderr</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.debugJobs.map((job, idx) => {
                        const result = job.latestResult;
                        return `
                            <tr class="debug-table-row" onclick="app.selectDebugJob(${idx})">
                                <td>${this.escapeHtml(job.name || '-')}</td>
                                <td><span class="status-badge status-${statusNames[job.status]?.toLowerCase() || 'unknown'}">${statusNames[job.status] || '-'}</span></td>
                                <td class="${result?.return_code === 0 ? 'return-code-0' : 'return-code-error'}">${result?.return_code ?? '-'}</td>
                                <td><code>${this.escapeHtml(this.truncate(result?.stdout || '-', 30))}</code></td>
                                <td><code>${this.escapeHtml(this.truncate(result?.stderr || '-', 30))}</code></td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    }

    selectDebugJob(index) {
        this.selectedDebugJob = this.debugJobs[index];

        // Update selection styling
        document.querySelectorAll('.debug-table-row').forEach((row, i) => {
            row.classList.toggle('selected', i === index);
        });

        // Show job info
        const infoEl = document.getElementById('debug-selected-job-info');
        if (infoEl && this.selectedDebugJob) {
            infoEl.innerHTML = `<strong>${this.escapeHtml(this.selectedDebugJob.name)}</strong> (ID: ${this.truncateId(this.selectedDebugJob.id)})`;
            infoEl.classList.remove('placeholder-message');
        }

        // Show log tabs and viewer
        document.getElementById('log-tabs').style.display = 'flex';
        document.getElementById('log-viewer').style.display = 'block';

        // Load current log tab
        this.loadLogContent();
    }

    switchLogTab(logtab) {
        this.currentLogTab = logtab;

        document.querySelectorAll('.sub-tab[data-logtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.logtab === logtab);
        });

        this.loadLogContent();
    }

    loadLogContent() {
        const logPath = document.getElementById('log-path');
        const logContent = document.getElementById('log-content');

        if (!this.selectedDebugJob?.latestResult) {
            logContent.textContent = 'No result data available';
            logPath.textContent = '';
            return;
        }

        const result = this.selectedDebugJob.latestResult;

        if (this.currentLogTab === 'stdout') {
            logPath.textContent = result.stdout_path || '';
            logContent.textContent = result.stdout || '(empty)';
            logContent.classList.remove('stderr');
        } else {
            logPath.textContent = result.stderr_path || '';
            logContent.textContent = result.stderr || '(empty)';
            logContent.classList.add('stderr');
        }
    }

    // ==================== Settings Tab ====================

    setupSettingsTab() {
        document.getElementById('btn-save-settings')?.addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('btn-test-connection')?.addEventListener('click', async () => {
            const apiUrl = document.getElementById('api-url')?.value;
            if (apiUrl) {
                api.setBaseUrl(apiUrl);
            }
            await this.testConnection();
        });

        document.getElementById('dark-mode')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
        });
    }

    // ==================== Modal ====================

    setupModal() {
        document.getElementById('modal-close')?.addEventListener('click', () => {
            this.hideModal('create-workflow-modal');
        });

        document.getElementById('btn-cancel-create')?.addEventListener('click', () => {
            this.hideModal('create-workflow-modal');
        });

        document.getElementById('btn-submit-workflow')?.addEventListener('click', async () => {
            await this.createWorkflow();
        });

        // Close modal on background click
        document.getElementById('create-workflow-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('create-workflow-modal');
            }
        });

        // Create source tabs
        document.querySelectorAll('.sub-tab[data-createtab]').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchCreateTab(tab.dataset.createtab);
            });
        });

        // File upload zone
        this.setupFileUpload();
    }

    setupFileUpload() {
        const zone = document.getElementById('file-upload-zone');
        const input = document.getElementById('spec-file-input');

        if (!zone || !input) return;

        zone.addEventListener('click', () => input.click());

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file) this.handleFileUpload(file);
        });

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) this.handleFileUpload(file);
        });
    }

    handleFileUpload(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.uploadedSpecContent = e.target.result;
            document.getElementById('upload-status').innerHTML = `
                <p style="color: var(--success-color)">Uploaded: ${this.escapeHtml(file.name)} (${(file.size / 1024).toFixed(1)} KB)</p>
            `;
        };
        reader.onerror = () => {
            this.showToast('Error reading file', 'error');
        };
        reader.readAsText(file);
    }

    switchCreateTab(tabName) {
        this.currentCreateTab = tabName;

        document.querySelectorAll('.sub-tab[data-createtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.createtab === tabName);
        });

        document.querySelectorAll('.create-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `create-panel-${tabName}`);
        });
    }

    showModal(modalId) {
        document.getElementById(modalId)?.classList.add('active');
    }

    hideModal(modalId) {
        document.getElementById(modalId)?.classList.remove('active');
    }

    async createWorkflow() {
        let specContent = null;
        let isFilePath = false;

        switch (this.currentCreateTab) {
            case 'upload':
                if (!this.uploadedSpecContent) {
                    this.showToast('Please upload a workflow spec file', 'warning');
                    return;
                }
                specContent = this.uploadedSpecContent;
                break;
            case 'path':
                const pathInput = document.getElementById('workflow-spec-path')?.value?.trim();
                if (!pathInput) {
                    this.showToast('Please enter a spec file path', 'warning');
                    return;
                }
                specContent = pathInput;
                isFilePath = true;
                break;
            case 'inline':
                const textInput = document.getElementById('workflow-spec-text')?.value?.trim();
                if (!textInput) {
                    this.showToast('Please enter a workflow spec', 'warning');
                    return;
                }
                specContent = textInput;
                break;
        }

        try {
            const result = await api.cliCreateWorkflow(specContent, isFilePath);

            if (result.success) {
                this.showToast('Workflow created successfully', 'success');
                this.hideModal('create-workflow-modal');

                // Clear form
                this.uploadedSpecContent = null;
                document.getElementById('upload-status').innerHTML = '';
                const pathInput = document.getElementById('workflow-spec-path');
                const textInput = document.getElementById('workflow-spec-text');
                if (pathInput) pathInput.value = '';
                if (textInput) textInput.value = '';

                await this.loadWorkflows();

                // Check if we should initialize
                const shouldInit = document.getElementById('create-option-initialize')?.checked;
                const shouldRun = document.getElementById('create-option-run')?.checked;

                // Try to extract workflow ID from output
                const idMatch = result.stdout?.match(/workflow[_\s]?id[:\s]+([a-zA-Z0-9-]+)/i);
                if (idMatch) {
                    const workflowId = idMatch[1];
                    if (shouldInit) {
                        await this.initializeWorkflow(workflowId);
                    }
                    if (shouldRun) {
                        await this.runWorkflow(workflowId);
                    }
                }
            } else {
                const errorMsg = result.stderr || result.stdout || 'Unknown error';
                this.showToast('Error: ' + errorMsg, 'error');
            }
        } catch (error) {
            this.showToast('Error creating workflow: ' + error.message, 'error');
        }
    }

    // ==================== Execution Plan Modal ====================

    setupExecutionPlanModal() {
        document.getElementById('plan-modal-close')?.addEventListener('click', () => {
            this.hideModal('execution-plan-modal');
        });

        document.getElementById('btn-close-plan')?.addEventListener('click', () => {
            this.hideModal('execution-plan-modal');
        });

        document.getElementById('execution-plan-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('execution-plan-modal');
            }
        });
    }

    setupInitConfirmModal() {
        document.getElementById('init-confirm-modal-close')?.addEventListener('click', () => {
            this.hideModal('init-confirm-modal');
        });

        document.getElementById('btn-cancel-init')?.addEventListener('click', () => {
            this.hideModal('init-confirm-modal');
        });

        document.getElementById('btn-confirm-init')?.addEventListener('click', async () => {
            this.hideModal('init-confirm-modal');
            if (this.pendingInitializeWorkflowId) {
                await this.initializeWorkflow(this.pendingInitializeWorkflowId, true);
                this.pendingInitializeWorkflowId = null;
            }
        });

        document.getElementById('init-confirm-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('init-confirm-modal');
            }
        });
    }

    async showExecutionPlan(workflowId) {
        this.showModal('execution-plan-modal');
        const content = document.getElementById('execution-plan-content');
        content.innerHTML = '<div class="placeholder-message">Loading execution plan...</div>';

        try {
            // Get jobs and dependencies
            const [jobs, dependencies] = await Promise.all([
                api.listJobs(workflowId),
                api.getJobsDependencies(workflowId),
            ]);

            // Build dependency graph and compute stages
            const stages = this.computeExecutionStages(jobs, dependencies);
            content.innerHTML = this.renderExecutionPlan(stages, jobs);
        } catch (error) {
            content.innerHTML = `<div class="placeholder-message">Error loading execution plan: ${error.message}</div>`;
        }
    }

    computeExecutionStages(jobs, dependencies) {
        // Build a map of job dependencies
        const blockedBy = {};
        dependencies.forEach(dep => {
            if (!blockedBy[dep.job_id]) blockedBy[dep.job_id] = [];
            blockedBy[dep.job_id].push(dep.blocked_by_job_id);
        });

        // Create job map
        const jobMap = {};
        jobs.forEach(j => jobMap[j.id] = j);

        // Compute stages using topological sort levels
        const stages = [];
        const completed = new Set();
        const remaining = new Set(jobs.map(j => j.id));

        let stageNum = 1;
        while (remaining.size > 0) {
            const ready = [];
            remaining.forEach(jobId => {
                const deps = blockedBy[jobId] || [];
                if (deps.every(d => completed.has(d))) {
                    ready.push(jobId);
                }
            });

            if (ready.length === 0 && remaining.size > 0) {
                // Circular dependency or error - break to avoid infinite loop
                break;
            }

            stages.push({
                stageNumber: stageNum++,
                jobs: ready.map(id => jobMap[id]),
            });

            ready.forEach(id => {
                completed.add(id);
                remaining.delete(id);
            });
        }

        return stages;
    }

    renderExecutionPlan(stages, jobs) {
        if (stages.length === 0) {
            return '<div class="placeholder-message">No execution stages computed</div>';
        }

        return `
            <div class="plan-summary" style="margin-bottom: 16px;">
                <strong>Total Stages:</strong> ${stages.length} |
                <strong>Total Jobs:</strong> ${jobs.length}
            </div>
            ${stages.map(stage => `
                <div class="plan-stage">
                    <div class="plan-stage-header">
                        <div class="plan-stage-number">${stage.stageNumber}</div>
                        <div class="plan-stage-trigger">Stage ${stage.stageNumber}</div>
                    </div>
                    <div class="plan-stage-content">
                        <h5>Jobs Ready (${stage.jobs.length})</h5>
                        <ul>
                            ${stage.jobs.slice(0, 10).map(job => `
                                <li>${this.escapeHtml(job.name || job.id)}</li>
                            `).join('')}
                            ${stage.jobs.length > 10 ? `<li>... and ${stage.jobs.length - 10} more</li>` : ''}
                        </ul>
                    </div>
                </div>
            `).join('')}
        `;
    }

    // ==================== Utilities ====================

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    escapeHtml(str) {
        if (str === null || str === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }

    truncateId(id) {
        if (!id) return '-';
        return id.length > 8 ? id.substring(0, 8) + '...' : id;
    }

    truncate(str, maxLen) {
        if (!str) return '';
        return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
    }

    formatDate(dateStr) {
        if (!dateStr) return '-';
        try {
            const date = new Date(dateStr);
            return date.toLocaleString();
        } catch {
            return dateStr;
        }
    }
}

// Initialize application
const app = new TorcDashboard();
document.addEventListener('DOMContentLoaded', () => app.init());
