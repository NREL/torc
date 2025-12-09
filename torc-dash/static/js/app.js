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
        this.uploadedSpecExtension = null;
        this.currentCreateTab = 'upload';
        this.debugJobs = [];
        this.selectedDebugJob = null;
        this.currentLogTab = 'stdout';
        // Resource plots state
        this.resourceDatabases = [];
        this.selectedDatabases = [];
        this.resourcePlots = [];
        this.currentPlotIndex = 0;
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
        this.setupResourcePlotsTab();
        this.setupSettingsTab();
        this.setupModal();
        this.setupWizard();
        this.setupExecutionPlanModal();
        this.setupInitConfirmModal();
        this.setupReinitConfirmModal();
        this.setupExecutionPanel();
        this.setupFileViewerModal();
        this.setupJobDetailsModal();

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
            // Sort by id descending (newer workflows first)
            this.workflows.sort((a, b) => {
                const idA = parseInt(a.id) || 0;
                const idB = parseInt(b.id) || 0;
                return idB - idA;
            });
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
            (w.user || '').toLowerCase().includes(lowerFilter) ||
            String(w.id || '').toLowerCase().includes(lowerFilter) ||
            (w.description || '').toLowerCase().includes(lowerFilter)
        );
        this.renderWorkflowsTable(filtered);
    }

    renderWorkflowsTable(workflows) {
        const tbody = document.getElementById('workflows-body');
        if (!tbody) return;

        if (!workflows || workflows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="placeholder-message">No workflows found</td></tr>';
            return;
        }

        tbody.innerHTML = workflows.map(workflow => `
            <tr data-workflow-id="${workflow.id}">
                <td><code>${workflow.id ?? '-'}</code></td>
                <td>${this.escapeHtml(workflow.name || 'Unnamed')}</td>
                <td>${this.formatTimestamp(workflow.timestamp)}</td>
                <td>${this.escapeHtml(workflow.user || '-')}</td>
                <td title="${this.escapeHtml(workflow.description || '')}">${this.escapeHtml(this.truncate(workflow.description || '-', 40))}</td>
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
        // Show the execution output panel
        this.showExecutionPanel();
        this.appendExecutionOutput(`Starting workflow ${workflowId}...\n`, 'info');

        // Create EventSource for streaming
        const eventSource = new EventSource(`/api/cli/run-stream?workflow_id=${workflowId}`);
        this.currentEventSource = eventSource;

        eventSource.addEventListener('start', (e) => {
            this.appendExecutionOutput(`${e.data}\n`, 'info');
        });

        eventSource.addEventListener('stdout', (e) => {
            this.appendExecutionOutput(`${e.data}\n`, 'stdout');
        });

        eventSource.addEventListener('stderr', (e) => {
            this.appendExecutionOutput(`${e.data}\n`, 'stderr');
        });

        eventSource.addEventListener('status', (e) => {
            // Status updates from periodic API polling - shown in a different color
            this.appendExecutionOutput(`[Status] ${e.data}\n`, 'info');
        });

        eventSource.addEventListener('error', (e) => {
            if (e.data) {
                this.appendExecutionOutput(`Error: ${e.data}\n`, 'error');
            }
        });

        eventSource.addEventListener('end', (e) => {
            const status = e.data;
            if (status === 'success') {
                this.appendExecutionOutput(`\n✓ Workflow completed successfully\n`, 'success');
                this.showToast('Workflow completed successfully', 'success');
            } else {
                this.appendExecutionOutput(`\n✗ Workflow ${status}\n`, 'error');
                this.showToast(`Workflow ${status}`, 'error');
            }
            eventSource.close();
            this.currentEventSource = null;
            this.hideExecutionCancelButton();
            // Refresh workflow details
            this.loadWorkflows();
            this.loadWorkflowDetails(workflowId);
        });

        eventSource.onerror = (e) => {
            if (eventSource.readyState === EventSource.CLOSED) {
                // Normal close
                return;
            }
            this.appendExecutionOutput(`\nConnection error\n`, 'error');
            eventSource.close();
            this.currentEventSource = null;
            this.hideExecutionCancelButton();
        };
    }

    showExecutionPanel() {
        const panel = document.getElementById('execution-output-panel');
        const output = document.getElementById('execution-output');
        if (panel) {
            panel.style.display = 'block';
            output.textContent = '';
        }
        // Show cancel button
        const cancelBtn = document.getElementById('btn-cancel-execution');
        if (cancelBtn) cancelBtn.style.display = 'inline-block';
    }

    hideExecutionPanel() {
        const panel = document.getElementById('execution-output-panel');
        if (panel) {
            panel.style.display = 'none';
        }
        // Close any active event source
        if (this.currentEventSource) {
            this.currentEventSource.close();
            this.currentEventSource = null;
        }
    }

    hideExecutionCancelButton() {
        const cancelBtn = document.getElementById('btn-cancel-execution');
        if (cancelBtn) cancelBtn.style.display = 'none';
    }

    appendExecutionOutput(text, type = 'stdout') {
        const output = document.getElementById('execution-output');
        if (!output) return;

        const span = document.createElement('span');
        span.textContent = text;
        span.className = `output-${type}`;
        output.appendChild(span);

        // Auto-scroll to bottom
        output.scrollTop = output.scrollHeight;
    }

    setupExecutionPanel() {
        document.getElementById('btn-close-output')?.addEventListener('click', () => {
            this.hideExecutionPanel();
        });

        document.getElementById('btn-cancel-execution')?.addEventListener('click', () => {
            if (this.currentEventSource) {
                this.currentEventSource.close();
                this.currentEventSource = null;
                this.appendExecutionOutput(`\n⚠ Execution cancelled by user\n`, 'warning');
                this.hideExecutionCancelButton();
            }
        });
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
                await this.loadWorkflowDetails(workflowId);
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

    async reinitializeWorkflow(workflowId, force = false) {
        try {
            // If not forcing, first check if there are existing output files
            if (!force) {
                const checkResult = await api.cliCheckReinitialize(workflowId);

                // Parse the JSON response from stdout
                if (checkResult.success && checkResult.stdout) {
                    try {
                        const dryRunData = JSON.parse(checkResult.stdout);
                        const fileCount = dryRunData.existing_output_file_count || 0;

                        if (fileCount > 0) {
                            // Show confirmation modal (reuse the same modal for reinitialize)
                            this.showReinitializeConfirmModal(workflowId, fileCount, dryRunData.existing_output_files || []);
                            return;
                        }
                    } catch (parseError) {
                        // JSON parse failed, continue with reinitialization
                        console.warn('Could not parse dry-run response:', parseError);
                    }
                }
            }

            // Proceed with actual reinitialization
            const result = await api.cliReinitializeWorkflow(workflowId, force);
            if (result.success) {
                this.showToast('Workflow reinitialized', 'success');
                await this.loadWorkflows();
                await this.loadWorkflowDetails(workflowId);
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout), 'error');
            }
        } catch (error) {
            this.showToast('Error reinitializing workflow: ' + error.message, 'error');
        }
    }

    showReinitializeConfirmModal(workflowId, fileCount, files) {
        // Store for use by confirm button
        this.pendingReinitializeWorkflowId = workflowId;

        // Update modal content
        const content = document.getElementById('reinit-confirm-content');
        if (content) {
            const fileList = files.slice(0, 10).map(f => `<li><code>${this.escapeHtml(f)}</code></li>`).join('');
            const moreFiles = files.length > 10 ? `<li>... and ${files.length - 10} more</li>` : '';

            content.innerHTML = `
                <p>This workflow has <strong>${fileCount}</strong> existing output file(s) that will be deleted:</p>
                <ul class="file-list">${fileList}${moreFiles}</ul>
                <p>Do you want to proceed and delete these files?</p>
            `;
        }

        this.showModal('reinit-confirm-modal');
    }

    async resetWorkflow(workflowId) {
        if (!confirm('Reset workflow status? This will set all jobs back to uninitialized state.')) {
            return;
        }
        try {
            const result = await api.cliResetStatus(workflowId);
            if (result.success) {
                this.showToast('Workflow status reset', 'success');
                await this.loadWorkflows();
                await this.loadWorkflowDetails(workflowId);
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout), 'error');
            }
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
                        <div class="value">${workflow.id ?? '-'}</div>
                        <div class="label">ID</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">${this.escapeHtml(workflow.name || 'Unnamed')}</div>
                        <div class="label">Name</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">${this.escapeHtml(workflow.user || '-')}</div>
                        <div class="label">User</div>
                    </div>
                    <div class="summary-card">
                        <div class="value">${this.formatTimestamp(workflow.timestamp)}</div>
                        <div class="label">Timestamp</div>
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

        // Reset table state for this tab
        this.tableState = {
            data: [],
            filteredData: [],
            sortColumn: null,
            sortDirection: 'asc',
            filterText: '',
            tabType: subtab,
            jobNameMap: {}
        };

        try {
            switch (subtab) {
                case 'jobs':
                    this.tableState.data = await api.listJobs(workflowId);
                    break;
                case 'results':
                    const [results, resultJobs] = await Promise.all([
                        api.listResults(workflowId),
                        api.listJobs(workflowId),
                    ]);
                    this.tableState.data = results;
                    // Build job name map for results
                    if (resultJobs) {
                        resultJobs.forEach(job => {
                            this.tableState.jobNameMap[job.id] = job.name;
                        });
                    }
                    break;
                case 'events':
                    const events = await api.listWorkflowEvents(workflowId);
                    this.tableState.data = api.extractItems(events);
                    break;
                case 'files':
                    this.tableState.data = await api.listFiles(workflowId);
                    break;
                case 'user-data':
                    this.tableState.data = await api.listUserData(workflowId);
                    break;
                case 'resources':
                    this.tableState.data = await api.listResourceRequirements(workflowId);
                    break;
                case 'schedulers':
                    this.tableState.data = await api.listSlurmSchedulers(workflowId);
                    break;
                case 'compute-nodes':
                    this.tableState.data = await api.listComputeNodes(workflowId);
                    break;
            }
            this.tableState.filteredData = [...this.tableState.data];
            this.renderCurrentTable();
        } catch (error) {
            content.innerHTML = `<div class="placeholder-message">Error loading ${subtab}: ${error.message}</div>`;
        }
    }

    renderCurrentTable() {
        const content = document.getElementById('details-content');
        const { filteredData, tabType, jobNameMap } = this.tableState;

        switch (tabType) {
            case 'jobs':
                content.innerHTML = this.renderJobsTable(filteredData);
                break;
            case 'results':
                content.innerHTML = this.renderResultsTable(filteredData, null, jobNameMap);
                break;
            case 'events':
                content.innerHTML = this.renderWorkflowEventsTable(filteredData);
                break;
            case 'files':
                content.innerHTML = this.renderFilesTable(filteredData);
                break;
            case 'user-data':
                content.innerHTML = this.renderUserDataTable(filteredData);
                break;
            case 'resources':
                content.innerHTML = this.renderResourcesTable(filteredData);
                break;
            case 'schedulers':
                content.innerHTML = this.renderSchedulersTable(filteredData);
                break;
            case 'compute-nodes':
                content.innerHTML = this.renderComputeNodesTable(filteredData);
                break;
        }

        // Set up event listeners for sorting and filtering
        this.setupTableInteractions();
    }

    setupTableInteractions() {
        // Set up sortable headers
        document.querySelectorAll('#details-content th[data-sort]').forEach(th => {
            th.addEventListener('click', () => this.handleSort(th.dataset.sort));
        });

        // Set up filter input
        const filterInput = document.getElementById('table-filter-input');
        if (filterInput) {
            filterInput.value = this.tableState.filterText;
            filterInput.addEventListener('input', (e) => this.handleFilter(e.target.value));
        }

        // Set up quick filters
        document.querySelectorAll('.quick-filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const filterInput = document.getElementById('table-filter-input');
                if (filterInput) {
                    filterInput.value = btn.dataset.filter;
                    this.handleFilter(btn.dataset.filter);
                }
            });
        });
    }

    handleSort(column) {
        const { sortColumn, sortDirection } = this.tableState;

        // Toggle direction if same column, otherwise default to ascending
        if (sortColumn === column) {
            this.tableState.sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.tableState.sortColumn = column;
            this.tableState.sortDirection = 'asc';
        }

        this.applySortAndFilter();
        this.renderCurrentTable();
    }

    handleFilter(filterText) {
        this.tableState.filterText = filterText;
        this.applySortAndFilter();
        this.renderCurrentTableBody();
    }

    // Re-render just the table body and count, preserving filter input focus
    renderCurrentTableBody() {
        const { filteredData, tabType, jobNameMap } = this.tableState;

        // Update count
        const countEl = document.querySelector('#details-content .table-count');
        if (countEl) {
            const itemName = this.getItemNameForTab(tabType);
            countEl.textContent = `${filteredData.length} ${itemName}${filteredData.length !== 1 ? 's' : ''}`;
        }

        // Update table body only
        const tbody = document.querySelector('#details-content .data-table tbody');
        if (tbody) {
            tbody.innerHTML = this.renderTableBodyRows(filteredData, tabType, jobNameMap);
        }
    }

    getItemNameForTab(tabType) {
        const names = {
            'jobs': 'job',
            'results': 'result',
            'events': 'event',
            'files': 'file',
            'user-data': 'record',
            'resources': 'requirement',
            'schedulers': 'scheduler',
            'compute-nodes': 'node',
        };
        return names[tabType] || 'item';
    }

    renderTableBodyRows(items, tabType, jobNameMap) {
        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];

        switch (tabType) {
            case 'jobs':
                return items.map(job => `
                    <tr>
                        <td><code>${job.id ?? '-'}</code></td>
                        <td>${this.escapeHtml(job.name || '-')}</td>
                        <td><span class="status-badge status-${statusNames[job.status]?.toLowerCase() || 'unknown'}">${statusNames[job.status] || job.status}</span></td>
                        <td><code>${this.escapeHtml(this.truncate(job.command || '-', 80))}</code></td>
                        <td><button class="btn-job-details" data-job-id="${job.id}" data-job-name="${this.escapeHtml(job.name || '')}">Details</button></td>
                    </tr>
                `).join('');

            case 'results':
                return items.map(result => `
                    <tr>
                        <td><code>${result.job_id ?? '-'}</code></td>
                        <td>${this.escapeHtml(jobNameMap[result.job_id] || '-')}</td>
                        <td>${result.run_id ?? '-'}</td>
                        <td class="${result.return_code === 0 ? 'return-code-0' : 'return-code-error'}">${result.return_code ?? '-'}</td>
                        <td><span class="status-badge status-${statusNames[result.status]?.toLowerCase() || 'unknown'}">${statusNames[result.status] || result.status}</span></td>
                        <td>${result.exec_time_minutes != null ? result.exec_time_minutes.toFixed(2) : '-'}</td>
                        <td>${this.formatBytes(result.peak_memory_bytes)}</td>
                        <td>${result.peak_cpu_percent != null ? result.peak_cpu_percent.toFixed(1) : '-'}</td>
                    </tr>
                `).join('');

            case 'events':
                return items.map(event => `
                    <tr>
                        <td><code>${event.id ?? '-'}</code></td>
                        <td>${this.formatTimestamp(event.timestamp)}</td>
                        <td><code>${this.escapeHtml(this.truncate(JSON.stringify(event.data) || '-', 100))}</code></td>
                    </tr>
                `).join('');

            case 'files':
                return items.map(file => `
                    <tr>
                        <td><code>${file.id ?? '-'}</code></td>
                        <td>${this.escapeHtml(file.name || '-')}</td>
                        <td><code>${this.escapeHtml(file.path || '-')}</code></td>
                        <td>${this.formatUnixTimestamp(file.st_mtime)}</td>
                        <td>${file.path ? `<button class="btn-view-file" data-path="${this.escapeHtml(file.path)}" data-name="${this.escapeHtml(file.name || 'File')}">View</button>` : '-'}</td>
                    </tr>
                `).join('');

            case 'user-data':
                return items.map(ud => `
                    <tr>
                        <td><code>${ud.id ?? '-'}</code></td>
                        <td>${this.escapeHtml(ud.name || '-')}</td>
                        <td><code>${this.escapeHtml(this.truncate(JSON.stringify(ud.data) || '-', 100))}</code></td>
                    </tr>
                `).join('');

            case 'resources':
                return items.map(r => `
                    <tr>
                        <td><code>${r.id ?? '-'}</code></td>
                        <td>${this.escapeHtml(r.name || '-')}</td>
                        <td>${r.num_cpus ?? '-'}</td>
                        <td>${this.escapeHtml(r.memory || '-')}</td>
                        <td>${r.num_gpus ?? '-'}</td>
                        <td>${this.escapeHtml(r.runtime || '-')}</td>
                    </tr>
                `).join('');

            case 'schedulers':
                return items.map(s => `
                    <tr>
                        <td><code>${s.id ?? '-'}</code></td>
                        <td>${this.escapeHtml(s.name || '-')}</td>
                        <td>${this.escapeHtml(s.account || '-')}</td>
                        <td>${this.escapeHtml(s.partition || '-')}</td>
                        <td>${this.escapeHtml(s.walltime || '-')}</td>
                        <td>${s.nodes ?? '-'}</td>
                        <td>${this.escapeHtml(s.mem || '-')}</td>
                    </tr>
                `).join('');

            case 'compute-nodes':
                return items.map(n => `
                    <tr>
                        <td><code>${n.id ?? '-'}</code></td>
                        <td>${this.escapeHtml(n.hostname || '-')}</td>
                        <td>${n.num_cpus ?? '-'}</td>
                        <td>${n.memory_gb ?? '-'}</td>
                        <td>${n.num_gpus ?? '-'}</td>
                        <td>${n.is_active != null ? (n.is_active ? 'Yes' : 'No') : '-'}</td>
                    </tr>
                `).join('');

            default:
                return '';
        }
    }

    applySortAndFilter() {
        const { data, sortColumn, sortDirection, filterText, tabType, jobNameMap } = this.tableState;
        let filtered = [...data];

        // Apply filter
        if (filterText.trim()) {
            const lowerFilter = filterText.toLowerCase().trim();

            // Check for special filter syntax:
            // - column:value (substring match)
            // - column~value (substring match)
            // - column=value (exact match)
            // - column!=value, column>value, etc. (comparison operators)
            const operatorMatch = lowerFilter.match(/^(\w+)\s*(!=|>=|<=|>|<|=|~|:)\s*(.+)$/);

            if (operatorMatch) {
                const [, field, operator, value] = operatorMatch;
                filtered = this.applyOperatorFilter(filtered, field, operator, value, tabType, jobNameMap);
            } else {
                // General text search across all fields
                filtered = filtered.filter(item => {
                    return this.getSearchableText(item, tabType, jobNameMap).toLowerCase().includes(lowerFilter);
                });
            }
        }

        // Apply sort
        if (sortColumn) {
            filtered.sort((a, b) => {
                let aVal = this.getSortValue(a, sortColumn, tabType, jobNameMap);
                let bVal = this.getSortValue(b, sortColumn, tabType, jobNameMap);

                // Handle nulls
                if (aVal == null && bVal == null) return 0;
                if (aVal == null) return 1;
                if (bVal == null) return -1;

                // Compare
                let result;
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    result = aVal - bVal;
                } else {
                    result = String(aVal).localeCompare(String(bVal));
                }

                return sortDirection === 'desc' ? -result : result;
            });
        }

        this.tableState.filteredData = filtered;
    }

    applyOperatorFilter(data, field, operator, value, tabType, jobNameMap) {
        const numValue = parseFloat(value);
        const isNumeric = !isNaN(numValue);

        return data.filter(item => {
            let itemValue = this.getFieldValue(item, field, tabType, jobNameMap);

            // For status fields, allow matching by name or number
            if (field === 'status') {
                const statusNames = ['uninitialized', 'blocked', 'ready', 'pending', 'running', 'completed', 'failed', 'canceled', 'terminated', 'disabled'];
                const filterStatusName = value.toLowerCase();

                // Get the item's status as a lowercase string for comparison
                let itemStatusName;
                if (typeof item.status === 'number') {
                    itemStatusName = statusNames[item.status] || '';
                } else {
                    itemStatusName = String(item.status).toLowerCase();
                }

                switch (operator) {
                    case '=': return itemStatusName === filterStatusName;
                    case '!=': return itemStatusName !== filterStatusName;
                    default: return true;
                }
            }

            // Numeric comparison - convert itemValue to number if needed
            if (isNumeric) {
                const itemNumValue = typeof itemValue === 'number' ? itemValue : parseFloat(itemValue);
                if (!isNaN(itemNumValue)) {
                    switch (operator) {
                        case '=': return itemNumValue === numValue;
                        case '!=': return itemNumValue !== numValue;
                        case '>': return itemNumValue > numValue;
                        case '<': return itemNumValue < numValue;
                        case '>=': return itemNumValue >= numValue;
                        case '<=': return itemNumValue <= numValue;
                    }
                }
            }

            // String comparison
            const strValue = String(itemValue ?? '').toLowerCase();
            const compareValue = value.toLowerCase();
            switch (operator) {
                case '=': return strValue === compareValue;
                case '!=': return strValue !== compareValue;
                case '~':
                case ':': return strValue.includes(compareValue);
                default: return strValue.includes(compareValue);
            }
        });
    }

    getFieldValue(item, field, tabType, jobNameMap) {
        // Handle special field mappings
        const fieldMap = {
            'job_name': () => jobNameMap[item.job_id] || '',
            'return_code': () => item.return_code,
            'exec_time': () => item.exec_time_minutes,
            'peak_mem': () => item.peak_memory_bytes,
            'peak_cpu': () => item.peak_cpu_percent,
            'modified': () => item.st_mtime,
        };

        if (fieldMap[field]) {
            return fieldMap[field]();
        }

        return item[field];
    }

    getSortValue(item, column, tabType, jobNameMap) {
        return this.getFieldValue(item, column, tabType, jobNameMap);
    }

    getSearchableText(item, tabType, jobNameMap) {
        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];
        const parts = [];

        // Add common fields
        if (item.id != null) parts.push(String(item.id));
        if (item.name) parts.push(item.name);
        if (item.status != null) parts.push(statusNames[item.status] || '');

        // Add tab-specific fields
        switch (tabType) {
            case 'jobs':
                if (item.command) parts.push(item.command);
                break;
            case 'results':
                if (item.job_id != null) parts.push(String(item.job_id));
                if (jobNameMap[item.job_id]) parts.push(jobNameMap[item.job_id]);
                if (item.return_code != null) parts.push(String(item.return_code));
                break;
            case 'files':
                if (item.path) parts.push(item.path);
                break;
            case 'events':
                if (item.timestamp) parts.push(item.timestamp);
                if (item.data) parts.push(JSON.stringify(item.data));
                break;
        }

        return parts.join(' ');
    }

    renderTableControls(tabType) {
        const quickFilters = this.getQuickFilters(tabType);
        const quickFilterHtml = quickFilters.map(f =>
            `<button class="quick-filter-btn btn btn-sm btn-secondary" data-filter="${this.escapeHtml(f.filter)}" title="${this.escapeHtml(f.title)}">${this.escapeHtml(f.label)}</button>`
        ).join('');

        return `
            <div class="table-controls">
                <div class="filter-group">
                    <input type="text" id="table-filter-input" class="text-input" placeholder="Filter... (e.g., name:work, status=ready, id>5)" style="width: 300px;">
                    <button class="btn btn-sm btn-secondary" onclick="app.clearTableFilter()">Clear</button>
                </div>
                ${quickFilterHtml ? `<div class="quick-filters">${quickFilterHtml}</div>` : ''}
            </div>
        `;
    }

    getQuickFilters(tabType) {
        switch (tabType) {
            case 'jobs':
                return [
                    { label: 'Failed', filter: 'status=failed', title: 'Show only failed jobs' },
                    { label: 'Running', filter: 'status=running', title: 'Show only running jobs' },
                    { label: 'Ready', filter: 'status=ready', title: 'Show only ready jobs' },
                    { label: 'Blocked', filter: 'status=blocked', title: 'Show only blocked jobs' },
                ];
            case 'results':
                return [
                    { label: 'Errors', filter: 'return_code!=0', title: 'Show results with non-zero return code' },
                    { label: 'Success', filter: 'return_code=0', title: 'Show results with return code 0' },
                    { label: 'Failed', filter: 'status=failed', title: 'Show failed results' },
                ];
            case 'events':
                return [
                    { label: 'Errors', filter: 'error', title: 'Show error events' },
                ];
            default:
                return [];
        }
    }

    clearTableFilter() {
        const filterInput = document.getElementById('table-filter-input');
        if (filterInput) {
            filterInput.value = '';
        }
        this.handleFilter('');
    }

    renderSortableHeader(label, column) {
        const { sortColumn, sortDirection } = this.tableState;
        const isActive = sortColumn === column;
        const arrow = isActive ? (sortDirection === 'asc' ? ' ▲' : ' ▼') : '';
        return `<th data-sort="${column}" class="sortable${isActive ? ' sorted' : ''}">${label}${arrow}</th>`;
    }

    renderJobsTable(jobs) {
        const controls = this.renderTableControls('jobs');
        const count = `<span class="table-count">${jobs.length} job${jobs.length !== 1 ? 's' : ''}</span>`;

        if (!jobs || jobs.length === 0) {
            return `${controls}<div class="placeholder-message">No jobs in this workflow</div>`;
        }

        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Name', 'name')}
                        ${this.renderSortableHeader('Status', 'status')}
                        ${this.renderSortableHeader('Command', 'command')}
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${jobs.map(job => `
                        <tr>
                            <td><code>${job.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(job.name || '-')}</td>
                            <td><span class="status-badge status-${statusNames[job.status]?.toLowerCase() || 'unknown'}">${statusNames[job.status] || job.status}</span></td>
                            <td><code>${this.escapeHtml(this.truncate(job.command || '-', 80))}</code></td>
                            <td><button class="btn-job-details" data-job-id="${job.id}" data-job-name="${this.escapeHtml(job.name || '')}">Details</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderFilesTable(files) {
        const controls = this.renderTableControls('files');
        const count = `<span class="table-count">${files.length} file${files.length !== 1 ? 's' : ''}</span>`;

        if (!files || files.length === 0) {
            return `${controls}<div class="placeholder-message">No files in this workflow</div>`;
        }

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Name', 'name')}
                        ${this.renderSortableHeader('Path', 'path')}
                        ${this.renderSortableHeader('Modified Time', 'st_mtime')}
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${files.map(file => `
                        <tr>
                            <td><code>${file.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(file.name || '-')}</td>
                            <td><code>${this.escapeHtml(file.path || '-')}</code></td>
                            <td>${this.formatUnixTimestamp(file.st_mtime)}</td>
                            <td>
                                ${file.path ? `<button class="btn-view-file" data-path="${this.escapeHtml(file.path)}" data-name="${this.escapeHtml(file.name || 'File')}">View</button>` : '-'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderUserDataTable(userData) {
        const controls = this.renderTableControls('user-data');
        const count = `<span class="table-count">${userData.length} record${userData.length !== 1 ? 's' : ''}</span>`;

        if (!userData || userData.length === 0) {
            return `${controls}<div class="placeholder-message">No user data in this workflow</div>`;
        }

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Name', 'name')}
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    ${userData.map(ud => `
                        <tr>
                            <td><code>${ud.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(ud.name || '-')}</td>
                            <td><code>${this.escapeHtml(this.truncate(JSON.stringify(ud.data) || '-', 100))}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderResultsTable(results, jobs, jobNameMapOverride) {
        const controls = this.renderTableControls('results');
        const count = `<span class="table-count">${results.length} result${results.length !== 1 ? 's' : ''}</span>`;

        if (!results || results.length === 0) {
            return `${controls}<div class="placeholder-message">No results in this workflow</div>`;
        }

        // Build a map of job IDs to job names (use override if provided, or build from jobs)
        const jobNameMap = jobNameMapOverride || {};
        if (!jobNameMapOverride && jobs) {
            jobs.forEach(job => {
                jobNameMap[job.id] = job.name;
            });
        }

        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('Job ID', 'job_id')}
                        ${this.renderSortableHeader('Job Name', 'job_name')}
                        ${this.renderSortableHeader('Run ID', 'run_id')}
                        ${this.renderSortableHeader('Return Code', 'return_code')}
                        ${this.renderSortableHeader('Status', 'status')}
                        ${this.renderSortableHeader('Exec Time (min)', 'exec_time_minutes')}
                        ${this.renderSortableHeader('Peak Mem', 'peak_memory_bytes')}
                        ${this.renderSortableHeader('Peak CPU %', 'peak_cpu_percent')}
                    </tr>
                </thead>
                <tbody>
                    ${results.map(result => `
                        <tr>
                            <td><code>${result.job_id ?? '-'}</code></td>
                            <td>${this.escapeHtml(jobNameMap[result.job_id] || '-')}</td>
                            <td>${result.run_id ?? '-'}</td>
                            <td class="${result.return_code === 0 ? 'return-code-0' : 'return-code-error'}">${result.return_code ?? '-'}</td>
                            <td><span class="status-badge status-${statusNames[result.status]?.toLowerCase() || 'unknown'}">${statusNames[result.status] || result.status}</span></td>
                            <td>${result.exec_time_minutes != null ? result.exec_time_minutes.toFixed(2) : '-'}</td>
                            <td>${this.formatBytes(result.peak_memory_bytes)}</td>
                            <td>${result.peak_cpu_percent != null ? result.peak_cpu_percent.toFixed(1) : '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderSchedulersTable(schedulers) {
        const controls = this.renderTableControls('schedulers');
        const count = `<span class="table-count">${schedulers.length} scheduler${schedulers.length !== 1 ? 's' : ''}</span>`;

        if (!schedulers || schedulers.length === 0) {
            return `${controls}<div class="placeholder-message">No Slurm schedulers configured for this workflow</div>`;
        }

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Name', 'name')}
                        ${this.renderSortableHeader('Account', 'account')}
                        ${this.renderSortableHeader('Partition', 'partition')}
                        ${this.renderSortableHeader('Walltime', 'walltime')}
                        ${this.renderSortableHeader('Nodes', 'nodes')}
                        ${this.renderSortableHeader('Mem', 'mem')}
                    </tr>
                </thead>
                <tbody>
                    ${schedulers.map(s => `
                        <tr>
                            <td><code>${s.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(s.name || '-')}</td>
                            <td>${this.escapeHtml(s.account || '-')}</td>
                            <td>${this.escapeHtml(s.partition || '-')}</td>
                            <td>${this.escapeHtml(s.walltime || '-')}</td>
                            <td>${s.nodes ?? '-'}</td>
                            <td>${this.escapeHtml(s.mem || '-')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderComputeNodesTable(nodes) {
        const controls = this.renderTableControls('compute-nodes');
        const count = `<span class="table-count">${nodes.length} node${nodes.length !== 1 ? 's' : ''}</span>`;

        if (!nodes || nodes.length === 0) {
            return `${controls}<div class="placeholder-message">No compute nodes in this workflow</div>`;
        }

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Hostname', 'hostname')}
                        ${this.renderSortableHeader('CPUs', 'num_cpus')}
                        ${this.renderSortableHeader('Memory (GB)', 'memory_gb')}
                        ${this.renderSortableHeader('GPUs', 'num_gpus')}
                        ${this.renderSortableHeader('Active', 'is_active')}
                    </tr>
                </thead>
                <tbody>
                    ${nodes.map(n => `
                        <tr>
                            <td><code>${n.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(n.hostname || '-')}</td>
                            <td>${n.num_cpus ?? '-'}</td>
                            <td>${n.memory_gb ?? '-'}</td>
                            <td>${n.num_gpus ?? '-'}</td>
                            <td>${n.is_active != null ? (n.is_active ? 'Yes' : 'No') : '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderResourcesTable(resources) {
        const controls = this.renderTableControls('resources');
        const count = `<span class="table-count">${resources.length} requirement${resources.length !== 1 ? 's' : ''}</span>`;

        if (!resources || resources.length === 0) {
            return `${controls}<div class="placeholder-message">No resource requirements in this workflow</div>`;
        }

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Name', 'name')}
                        ${this.renderSortableHeader('CPUs', 'num_cpus')}
                        ${this.renderSortableHeader('Memory', 'memory')}
                        ${this.renderSortableHeader('GPUs', 'num_gpus')}
                        ${this.renderSortableHeader('Runtime', 'runtime')}
                    </tr>
                </thead>
                <tbody>
                    ${resources.map(r => `
                        <tr>
                            <td><code>${r.id ?? '-'}</code></td>
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
            const workflowId = document.getElementById('events-workflow-selector')?.value;

            // Workflow ID is required for the events API
            if (!workflowId) {
                this.events = [];
                this.renderEvents();
                return;
            }

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

        const workflowId = document.getElementById('events-workflow-selector')?.value;

        if (!workflowId) {
            container.innerHTML = '<div class="placeholder-message">Select a workflow to view events</div>';
            return;
        }

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

        // Get output directory from the input field
        this.debugOutputDir = document.getElementById('debug-output-dir')?.value || 'output';

        try {
            // Get jobs and results for the workflow
            const [jobs, results] = await Promise.all([
                api.listJobs(workflowId),
                api.listResults(workflowId),
            ]);

            const failedOnly = document.getElementById('debug-failed-only')?.checked;

            // Build a map of job results, adding stdout/stderr paths
            const resultMap = {};
            results.forEach(r => {
                if (!resultMap[r.job_id]) resultMap[r.job_id] = [];
                // Construct stdout/stderr file paths based on naming convention:
                // {output_dir}/job_stdio/job_{workflow_id}_{job_id}_{run_id}.o (stdout)
                // {output_dir}/job_stdio/job_{workflow_id}_{job_id}_{run_id}.e (stderr)
                const stdioBase = `${this.debugOutputDir}/job_stdio/job_${r.workflow_id}_${r.job_id}_${r.run_id}`;
                resultMap[r.job_id].push({
                    ...r,
                    stdoutPath: `${stdioBase}.o`,
                    stderrPath: `${stdioBase}.e`,
                });
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
            const failedOnly = document.getElementById('debug-failed-only')?.checked;
            const message = failedOnly
                ? 'No failed jobs found. Uncheck "Show only failed jobs" to see all jobs with results.'
                : 'No jobs match the criteria';
            container.innerHTML = `<div class="placeholder-message">${message}</div>`;
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
                                <td><code>${result?.stdoutPath ? this.escapeHtml(this.truncate(result.stdoutPath, 40)) : '-'}</code></td>
                                <td><code>${result?.stderrPath ? this.escapeHtml(this.truncate(result.stderrPath, 40)) : '-'}</code></td>
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

    async loadLogContent() {
        const logPath = document.getElementById('log-path');
        const logContent = document.getElementById('log-content');

        if (!this.selectedDebugJob?.latestResult) {
            logContent.textContent = 'No result data available';
            logPath.textContent = '';
            return;
        }

        const result = this.selectedDebugJob.latestResult;
        const isStdout = this.currentLogTab === 'stdout';
        const filePath = isStdout ? result.stdoutPath : result.stderrPath;

        logPath.textContent = filePath || '';
        logContent.classList.toggle('stderr', !isStdout);

        if (!filePath) {
            logContent.textContent = 'No file path available';
            return;
        }

        logContent.textContent = 'Loading...';

        try {
            const response = await fetch('/api/cli/read-file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filePath }),
            });

            const data = await response.json();

            if (!data.exists) {
                logContent.textContent = '(file does not exist)';
            } else if (!data.success) {
                logContent.textContent = `Error: ${data.error || 'Unknown error'}`;
            } else if (!data.content || data.content.trim() === '') {
                logContent.textContent = '(empty)';
            } else {
                logContent.textContent = data.content;
            }
        } catch (error) {
            logContent.textContent = `Error loading file: ${error.message}`;
        }
    }

    // ==================== Resource Plots Tab ====================

    setupResourcePlotsTab() {
        document.getElementById('btn-scan-dbs')?.addEventListener('click', () => {
            this.scanResourceDatabases();
        });

        document.getElementById('btn-generate-plots')?.addEventListener('click', () => {
            this.generateResourcePlots();
        });
    }

    async scanResourceDatabases() {
        const baseDir = document.getElementById('resource-db-dir')?.value || 'output/resource_utilization';
        const listContainer = document.getElementById('resource-db-list');

        if (!listContainer) return;

        listContainer.innerHTML = '<div class="placeholder-message">Scanning...</div>';

        try {
            const response = await api.listResourceDatabases(baseDir);

            if (!response.success) {
                listContainer.innerHTML = `<div class="placeholder-message" style="color: var(--danger-color)">Error: ${response.error}</div>`;
                return;
            }

            this.resourceDatabases = response.databases || [];
            this.selectedDatabases = [];

            if (this.resourceDatabases.length === 0) {
                listContainer.innerHTML = '<div class="placeholder-message">No database files found in this directory</div>';
                document.getElementById('btn-generate-plots').disabled = true;
                return;
            }

            listContainer.innerHTML = this.resourceDatabases.map((db, idx) => `
                <label class="resource-db-item">
                    <input type="checkbox" value="${idx}" onchange="app.toggleDatabaseSelection(${idx}, this.checked)">
                    <div class="db-info">
                        <div class="db-name">${this.escapeHtml(db.name)}</div>
                        <div class="db-path">${this.escapeHtml(db.path)}</div>
                    </div>
                    <div class="db-meta">
                        <div>${this.formatBytes(db.size_bytes)}</div>
                        <div>${db.modified}</div>
                    </div>
                </label>
            `).join('');

            // If there's only one database, auto-select it
            if (this.resourceDatabases.length === 1) {
                this.toggleDatabaseSelection(0, true);
                const checkbox = listContainer.querySelector('input[type="checkbox"]');
                if (checkbox) checkbox.checked = true;
            }

        } catch (error) {
            listContainer.innerHTML = `<div class="placeholder-message" style="color: var(--danger-color)">Error: ${error.message}</div>`;
        }
    }

    toggleDatabaseSelection(index, selected) {
        if (selected) {
            if (!this.selectedDatabases.includes(index)) {
                this.selectedDatabases.push(index);
            }
        } else {
            this.selectedDatabases = this.selectedDatabases.filter(i => i !== index);
        }

        // Enable/disable generate button
        const btn = document.getElementById('btn-generate-plots');
        if (btn) {
            btn.disabled = this.selectedDatabases.length === 0;
        }
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    async generateResourcePlots() {
        const btn = document.getElementById('btn-generate-plots');
        const plotsSection = document.getElementById('plots-section');
        const plotContainer = document.getElementById('plot-container');
        const plotTabs = document.getElementById('plot-tabs');

        if (this.selectedDatabases.length === 0) {
            this.showToast('Please select at least one database', 'warning');
            return;
        }

        // Get paths for selected databases
        const dbPaths = this.selectedDatabases.map(idx => this.resourceDatabases[idx].path);

        // Show loading state
        btn.disabled = true;
        btn.textContent = 'Generating...';
        plotsSection.style.display = 'block';
        plotContainer.innerHTML = '<div class="plot-loading">Generating plots</div>';
        plotTabs.innerHTML = '';

        try {
            const response = await api.generateResourcePlots(dbPaths);

            if (!response.success) {
                plotContainer.innerHTML = `<div class="placeholder-message" style="color: var(--danger-color)">Error: ${response.error}</div>`;
                return;
            }

            this.resourcePlots = response.plots || [];

            if (this.resourcePlots.length === 0) {
                plotContainer.innerHTML = '<div class="placeholder-message">No plots generated. The database may not contain any resource data.</div>';
                return;
            }

            // Create tabs for each plot
            plotTabs.innerHTML = this.resourcePlots.map((plot, idx) => {
                // Extract a friendly name from the filename
                const friendlyName = this.getPlotFriendlyName(plot.name);
                return `<button class="plot-tab ${idx === 0 ? 'active' : ''}" onclick="app.showPlot(${idx})">${friendlyName}</button>`;
            }).join('');

            // Show first plot
            this.currentPlotIndex = 0;
            this.showPlot(0);

        } catch (error) {
            plotContainer.innerHTML = `<div class="placeholder-message" style="color: var(--danger-color)">Error: ${error.message}</div>`;
        } finally {
            btn.disabled = false;
            btn.textContent = 'Generate Plots';
        }
    }

    getPlotFriendlyName(filename) {
        // Remove prefix and .json extension, then make human readable
        // e.g., "resource_plot_summary.json" -> "Summary"
        // e.g., "resource_plot_job_1.json" -> "Job 1"
        // e.g., "resource_plot_cpu_all_jobs.json" -> "CPU All Jobs"
        let name = filename.replace(/^resource_plot_?/, '').replace(/\.json$/, '');
        if (!name) return 'Summary';

        // Convert underscores to spaces and capitalize
        return name.split('_').map(word => {
            // Keep "cpu" and "gpu" uppercase
            if (['cpu', 'gpu'].includes(word.toLowerCase())) {
                return word.toUpperCase();
            }
            return word.charAt(0).toUpperCase() + word.slice(1);
        }).join(' ');
    }

    showPlot(index) {
        if (index < 0 || index >= this.resourcePlots.length) return;

        this.currentPlotIndex = index;

        // Update tab active state
        document.querySelectorAll('.plot-tab').forEach((tab, idx) => {
            tab.classList.toggle('active', idx === index);
        });

        // Get the plot data
        const plot = this.resourcePlots[index];
        const container = document.getElementById('plot-container');

        if (!plot || !plot.data) {
            container.innerHTML = '<div class="placeholder-message">No data available for this plot</div>';
            return;
        }

        // Clear container and create plot div
        container.innerHTML = '<div class="plot-wrapper"><div id="plotly-chart" style="width: 100%; height: 500px;"></div></div>';

        try {
            // Plotly expects data and layout from the JSON
            const plotData = plot.data.data || plot.data;
            const layout = plot.data.layout || {};

            // Adjust layout for better display
            layout.autosize = true;
            layout.margin = layout.margin || { l: 60, r: 60, t: 50, b: 60 };

            // Use responsive mode
            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['sendDataToCloud'],
            };

            Plotly.newPlot('plotly-chart', plotData, layout, config);
        } catch (error) {
            console.error('Error rendering plot:', error);
            container.innerHTML = `<div class="placeholder-message" style="color: var(--danger-color)">Error rendering plot: ${error.message}</div>`;
        }
    }

    // ==================== Configuration Tab ====================

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

        // Server management
        document.getElementById('btn-start-server')?.addEventListener('click', () => {
            this.startServer();
        });

        document.getElementById('btn-stop-server')?.addEventListener('click', () => {
            this.stopServer();
        });

        // Check server status on init
        this.checkServerStatus();
    }

    async checkServerStatus() {
        const status = await api.getServerStatus();
        this.updateServerStatusUI(status);
    }

    updateServerStatusUI(status) {
        const panel = document.getElementById('server-status-panel');
        const dot = document.getElementById('server-status-dot');
        const text = document.getElementById('server-status-text');
        const startBtn = document.getElementById('btn-start-server');
        const stopBtn = document.getElementById('btn-stop-server');
        const outputDiv = document.getElementById('server-output');
        const outputContent = document.getElementById('server-output-content');

        if (status.running && status.managed) {
            panel?.classList.remove('stopped');
            panel?.classList.add('running');
            dot?.classList.remove('disconnected');
            dot?.classList.add('connected');
            if (text) text.textContent = `Server running (PID: ${status.pid}, Port: ${status.port})`;
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;

            // Show output
            if (outputDiv && status.output_lines?.length > 0) {
                outputDiv.style.display = 'block';
                if (outputContent) {
                    outputContent.textContent = status.output_lines.join('\n');
                }
            }
        } else if (status.managed && !status.running) {
            // Server was managed but has stopped
            panel?.classList.remove('running');
            panel?.classList.add('stopped');
            dot?.classList.remove('connected');
            dot?.classList.add('disconnected');
            if (text) text.textContent = 'Server stopped (was managed)';
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
        } else {
            panel?.classList.remove('running');
            panel?.classList.remove('stopped');
            dot?.classList.remove('connected');
            dot?.classList.add('disconnected');
            if (text) text.textContent = 'No managed server';
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
            if (outputDiv) outputDiv.style.display = 'none';
        }
    }

    async startServer() {
        const port = parseInt(document.getElementById('server-port')?.value) || 8080;
        const database = document.getElementById('server-database')?.value || '';
        const completionInterval = parseInt(document.getElementById('server-completion-interval')?.value) || 5;
        const logLevel = document.getElementById('server-log-level')?.value || 'info';

        const startBtn = document.getElementById('btn-start-server');
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.textContent = 'Starting...';
        }

        const result = await api.startServer({
            port,
            database: database || null,
            completion_check_interval_secs: completionInterval,
            log_level: logLevel,
        });

        if (result.success) {
            this.showToast(result.message, 'success');

            // Update API URL to point to the new server
            const newApiUrl = `http://localhost:${port}/torc-service/v1`;
            document.getElementById('api-url').value = newApiUrl;
            api.setBaseUrl(newApiUrl);

            // Wait a moment for server to start, then check status
            setTimeout(() => {
                this.checkServerStatus();
                this.testConnection();
            }, 1000);
        } else {
            this.showToast('Failed to start server: ' + result.message, 'error');
            if (startBtn) {
                startBtn.disabled = false;
            }
        }

        if (startBtn) {
            startBtn.textContent = 'Start Server';
        }
    }

    async stopServer() {
        const stopBtn = document.getElementById('btn-stop-server');
        if (stopBtn) {
            stopBtn.disabled = true;
            stopBtn.textContent = 'Stopping...';
        }

        const result = await api.stopServer();

        if (result.success) {
            this.showToast(result.message, 'success');
        } else {
            this.showToast('Failed to stop server: ' + result.message, 'error');
        }

        // Check status
        await this.checkServerStatus();
        await this.testConnection();

        if (stopBtn) {
            stopBtn.textContent = 'Stop Server';
        }
    }

    // ==================== Modal ====================

    setupModal() {
        document.getElementById('modal-close')?.addEventListener('click', () => {
            this.hideModal('create-workflow-modal');
            this.resetWizard();
        });

        document.getElementById('btn-cancel-create')?.addEventListener('click', () => {
            this.hideModal('create-workflow-modal');
            this.resetWizard();
        });

        document.getElementById('btn-submit-workflow')?.addEventListener('click', async () => {
            await this.createWorkflow();
        });

        // Close modal on background click
        document.getElementById('create-workflow-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('create-workflow-modal');
                this.resetWizard();
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
            // Extract the file extension to preserve format when creating temp file
            const dotIndex = file.name.lastIndexOf('.');
            this.uploadedSpecExtension = dotIndex >= 0 ? file.name.substring(dotIndex) : '.json';
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
        let fileExtension = null;

        switch (this.currentCreateTab) {
            case 'upload':
                if (!this.uploadedSpecContent) {
                    this.showToast('Please upload a workflow spec file', 'warning');
                    return;
                }
                specContent = this.uploadedSpecContent;
                fileExtension = this.uploadedSpecExtension;
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
            case 'wizard':
                // Use the wizard's create workflow function
                await this.wizardCreateWorkflow();
                return;
        }

        try {
            const result = await api.cliCreateWorkflow(specContent, isFilePath, fileExtension);

            if (result.success) {
                this.showToast('Workflow created successfully', 'success');
                this.hideModal('create-workflow-modal');

                // Clear form
                this.uploadedSpecContent = null;
                this.uploadedSpecExtension = null;
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

    setupReinitConfirmModal() {
        document.getElementById('reinit-confirm-modal-close')?.addEventListener('click', () => {
            this.hideModal('reinit-confirm-modal');
        });

        document.getElementById('btn-cancel-reinit')?.addEventListener('click', () => {
            this.hideModal('reinit-confirm-modal');
        });

        document.getElementById('btn-confirm-reinit')?.addEventListener('click', async () => {
            this.hideModal('reinit-confirm-modal');
            if (this.pendingReinitializeWorkflowId) {
                await this.reinitializeWorkflow(this.pendingReinitializeWorkflowId, true);
                this.pendingReinitializeWorkflowId = null;
            }
        });

        document.getElementById('reinit-confirm-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('reinit-confirm-modal');
            }
        });
    }

    setupFileViewerModal() {
        // Close button handlers
        document.getElementById('file-viewer-modal-close')?.addEventListener('click', () => {
            this.hideModal('file-viewer-modal');
        });

        document.getElementById('btn-close-file-viewer')?.addEventListener('click', () => {
            this.hideModal('file-viewer-modal');
        });

        // Close on background click
        document.getElementById('file-viewer-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('file-viewer-modal');
            }
        });

        // Delegate click events for "View" buttons in the files table
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('btn-view-file')) {
                const path = e.target.dataset.path;
                const name = e.target.dataset.name;
                if (path) {
                    await this.viewFile(path, name);
                }
            }
        });
    }

    async viewFile(path, name) {
        this.showModal('file-viewer-modal');
        const titleEl = document.getElementById('file-viewer-title');
        const pathEl = document.getElementById('file-viewer-path');
        const contentEl = document.getElementById('file-viewer-content');

        titleEl.textContent = name || 'File Contents';
        pathEl.textContent = path;
        contentEl.innerHTML = '<span class="placeholder-message">Loading file contents...</span>';

        try {
            const response = await fetch('/api/cli/read-file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path }),
            });

            const result = await response.json();

            if (!result.exists) {
                contentEl.innerHTML = '<span class="file-not-found">File does not exist</span>';
                return;
            }

            if (!result.success) {
                contentEl.innerHTML = `<span class="file-not-found">Error: ${this.escapeHtml(result.error || 'Unknown error')}</span>`;
                return;
            }

            if (result.is_json) {
                // Apply JSON syntax highlighting
                contentEl.innerHTML = this.highlightJson(result.content);
            } else {
                contentEl.textContent = result.content;
            }
        } catch (error) {
            contentEl.innerHTML = `<span class="file-not-found">Error loading file: ${this.escapeHtml(error.message)}</span>`;
        }
    }

    highlightJson(jsonString) {
        // Escape HTML first
        let escaped = this.escapeHtml(jsonString);

        // Replace JSON syntax elements with colored spans
        // Order matters here - we do replacements in a specific order

        // Strings (both keys and values) - careful with the pattern
        escaped = escaped.replace(
            /(&quot;)([^&]*?)(&quot;)/g,
            (match, q1, content, q2) => {
                return `<span class="json-string">${q1}${content}${q2}</span>`;
            }
        );

        // Numbers
        escaped = escaped.replace(
            /(?<![a-zA-Z\-])(-?\d+\.?\d*)(?![a-zA-Z])/g,
            '<span class="json-number">$1</span>'
        );

        // Booleans
        escaped = escaped.replace(/\b(true|false)\b/g, '<span class="json-boolean">$1</span>');

        // Null
        escaped = escaped.replace(/\bnull\b/g, '<span class="json-null">null</span>');

        // Brackets and braces
        escaped = escaped.replace(/([{}\[\]])/g, '<span class="json-bracket">$1</span>');

        return escaped;
    }

    // ==================== Job Details Modal ====================

    setupJobDetailsModal() {
        // Close button handlers
        document.getElementById('job-details-modal-close')?.addEventListener('click', () => {
            this.hideModal('job-details-modal');
        });

        document.getElementById('btn-close-job-details')?.addEventListener('click', () => {
            this.hideModal('job-details-modal');
        });

        // Close on background click
        document.getElementById('job-details-modal')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal('job-details-modal');
            }
        });

        // Tab navigation within modal
        document.querySelectorAll('.sub-tab[data-jobdetailtab]').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchJobDetailTab(tab.dataset.jobdetailtab);
            });
        });

        // Delegate click events for "Details" buttons in the jobs table
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('btn-job-details')) {
                const jobId = e.target.dataset.jobId;
                const jobName = e.target.dataset.jobName;
                if (jobId) {
                    await this.showJobDetails(jobId, jobName);
                }
            }
        });
    }

    async showJobDetails(jobId, jobName) {
        this.showModal('job-details-modal');
        this.currentJobDetailTab = 'results';
        this.jobDetailsData = null;

        // Convert jobId to number for comparisons (data attributes are strings)
        const jobIdNum = parseInt(jobId, 10);

        // Update title
        const titleEl = document.getElementById('job-details-title');
        titleEl.textContent = jobName ? `Job: ${jobName}` : `Job Details`;

        // Reset tab selection
        document.querySelectorAll('.sub-tab[data-jobdetailtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.jobdetailtab === 'results');
        });

        // Show loading
        const summaryEl = document.getElementById('job-details-summary');
        const contentEl = document.getElementById('job-details-content');
        summaryEl.innerHTML = '<div class="placeholder-message">Loading job details...</div>';
        contentEl.innerHTML = '';

        try {
            // Load all job-related data in parallel
            const workflowId = this.selectedWorkflowId;
            const [
                job,
                results,
                allFiles,
                fileRelationships,
                allUserData,
                userDataRelationships,
                resourceRequirements,
                allJobs,
                jobDependencies,
            ] = await Promise.all([
                api.getJob(jobId),
                api.listResults(workflowId),
                api.listFiles(workflowId),
                api.getJobFileRelationships(workflowId),
                api.listUserData(workflowId),
                api.getJobUserDataRelationships(workflowId),
                api.listResourceRequirements(workflowId),
                api.listJobs(workflowId),
                api.getJobsDependencies(workflowId),
            ]);

            // Filter results for this job
            const jobResults = results.filter(r => r.job_id === jobIdNum);

            // Filter file relationships for this job
            // API returns: producer_job_id (output), consumer_job_id (input)
            const inputFileIds = new Set(
                fileRelationships
                    .filter(r => r.consumer_job_id === jobIdNum)
                    .map(r => r.file_id)
            );
            const outputFileIds = new Set(
                fileRelationships
                    .filter(r => r.producer_job_id === jobIdNum)
                    .map(r => r.file_id)
            );
            const inputFiles = allFiles.filter(f => inputFileIds.has(f.id));
            const outputFiles = allFiles.filter(f => outputFileIds.has(f.id));

            // Filter user data relationships for this job
            // API returns: producer_job_id (output), consumer_job_id (input)
            const inputUserDataIds = new Set(
                userDataRelationships
                    .filter(r => r.consumer_job_id === jobIdNum)
                    .map(r => r.user_data_id)
            );
            const outputUserDataIds = new Set(
                userDataRelationships
                    .filter(r => r.producer_job_id === jobIdNum)
                    .map(r => r.user_data_id)
            );
            const inputUserData = allUserData.filter(ud => inputUserDataIds.has(ud.id));
            const outputUserData = allUserData.filter(ud => outputUserDataIds.has(ud.id));

            // Get resource requirement for this job
            const jobResourceReq = job.resource_requirements_id
                ? resourceRequirements.find(r => r.id === job.resource_requirements_id)
                : null;

            // Get job dependencies (jobs this job is blocked by)
            const blockedByJobIds = jobDependencies
                .filter(d => d.job_id === jobIdNum)
                .map(d => d.depends_on_job_id);
            const blockedByJobs = allJobs.filter(j => blockedByJobIds.includes(j.id));

            // Get jobs blocked by this job
            const blocksJobIds = jobDependencies
                .filter(d => d.depends_on_job_id === jobIdNum)
                .map(d => d.job_id);
            const blocksJobs = allJobs.filter(j => blocksJobIds.includes(j.id));

            // Store data for tab switching
            this.jobDetailsData = {
                job,
                results: jobResults,
                inputFiles,
                outputFiles,
                inputUserData,
                outputUserData,
                resourceReq: jobResourceReq,
                blockedByJobs,
                blocksJobs,
            };

            // Render summary
            this.renderJobDetailsSummary(job);

            // Render initial tab (results)
            this.renderJobDetailTabContent('results');

        } catch (error) {
            summaryEl.innerHTML = `<div class="placeholder-message">Error loading job details: ${this.escapeHtml(error.message)}</div>`;
        }
    }

    renderJobDetailsSummary(job) {
        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];
        const summaryEl = document.getElementById('job-details-summary');

        summaryEl.innerHTML = `
            <div class="job-details-summary-grid">
                <div class="job-details-summary-item">
                    <span class="label">ID</span>
                    <span class="value"><code>${job.id ?? '-'}</code></span>
                </div>
                <div class="job-details-summary-item">
                    <span class="label">Name</span>
                    <span class="value">${this.escapeHtml(job.name || '-')}</span>
                </div>
                <div class="job-details-summary-item">
                    <span class="label">Status</span>
                    <span class="value"><span class="status-badge status-${statusNames[job.status]?.toLowerCase() || 'unknown'}">${statusNames[job.status] || job.status}</span></span>
                </div>
                <div class="job-details-summary-item">
                    <span class="label">Command</span>
                    <span class="value"><code>${this.escapeHtml(this.truncate(job.command || '-', 50))}</code></span>
                </div>
            </div>
        `;
    }

    switchJobDetailTab(tabName) {
        this.currentJobDetailTab = tabName;

        document.querySelectorAll('.sub-tab[data-jobdetailtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.jobdetailtab === tabName);
        });

        this.renderJobDetailTabContent(tabName);
    }

    renderJobDetailTabContent(tabName) {
        const contentEl = document.getElementById('job-details-content');

        if (!this.jobDetailsData) {
            contentEl.innerHTML = '<div class="job-details-empty">No data available</div>';
            return;
        }

        const data = this.jobDetailsData;
        const statusNames = ['Uninitialized', 'Blocked', 'Ready', 'Pending', 'Running', 'Completed', 'Failed', 'Canceled', 'Terminated', 'Disabled'];

        switch (tabName) {
            case 'results':
                if (data.results.length === 0) {
                    contentEl.innerHTML = '<div class="job-details-empty">No results for this job</div>';
                } else {
                    contentEl.innerHTML = `
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Run ID</th>
                                    <th>Return Code</th>
                                    <th>Status</th>
                                    <th>Exec Time (min)</th>
                                    <th>Peak Mem</th>
                                    <th>Peak CPU %</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.results.map(r => `
                                    <tr>
                                        <td>${r.run_id ?? '-'}</td>
                                        <td class="${r.return_code === 0 ? 'return-code-0' : 'return-code-error'}">${r.return_code ?? '-'}</td>
                                        <td><span class="status-badge status-${statusNames[r.status]?.toLowerCase() || 'unknown'}">${statusNames[r.status] || r.status}</span></td>
                                        <td>${r.exec_time_minutes != null ? r.exec_time_minutes.toFixed(2) : '-'}</td>
                                        <td>${this.formatBytes(r.peak_memory_bytes)}</td>
                                        <td>${r.peak_cpu_percent != null ? r.peak_cpu_percent.toFixed(1) : '-'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                }
                break;

            case 'input-files':
                if (data.inputFiles.length === 0) {
                    contentEl.innerHTML = '<div class="job-details-empty">No input files for this job</div>';
                } else {
                    contentEl.innerHTML = this.renderJobDetailFilesTable(data.inputFiles);
                }
                break;

            case 'output-files':
                if (data.outputFiles.length === 0) {
                    contentEl.innerHTML = '<div class="job-details-empty">No output files for this job</div>';
                } else {
                    contentEl.innerHTML = this.renderJobDetailFilesTable(data.outputFiles);
                }
                break;

            case 'input-user-data':
                if (data.inputUserData.length === 0) {
                    contentEl.innerHTML = '<div class="job-details-empty">No input user data for this job</div>';
                } else {
                    contentEl.innerHTML = this.renderJobDetailUserDataTable(data.inputUserData);
                }
                break;

            case 'output-user-data':
                if (data.outputUserData.length === 0) {
                    contentEl.innerHTML = '<div class="job-details-empty">No output user data for this job</div>';
                } else {
                    contentEl.innerHTML = this.renderJobDetailUserDataTable(data.outputUserData);
                }
                break;

            case 'resource-req':
                if (!data.resourceReq) {
                    contentEl.innerHTML = '<div class="job-details-empty">No resource requirement assigned to this job</div>';
                } else {
                    const r = data.resourceReq;
                    contentEl.innerHTML = `
                        <table class="data-table">
                            <tbody>
                                <tr><th>ID</th><td><code>${r.id ?? '-'}</code></td></tr>
                                <tr><th>Name</th><td>${this.escapeHtml(r.name || '-')}</td></tr>
                                <tr><th>CPUs</th><td>${r.num_cpus ?? '-'}</td></tr>
                                <tr><th>Memory</th><td>${this.escapeHtml(r.memory || '-')}</td></tr>
                                <tr><th>GPUs</th><td>${r.num_gpus ?? '-'}</td></tr>
                                <tr><th>Runtime</th><td>${this.escapeHtml(r.runtime || '-')}</td></tr>
                            </tbody>
                        </table>
                    `;
                }
                break;

            case 'dependencies':
                let depsHtml = '';

                if (data.blockedByJobs.length > 0) {
                    depsHtml += `
                        <div class="job-details-section">
                            <h4>Blocked By (${data.blockedByJobs.length})</h4>
                            <table class="data-table">
                                <thead>
                                    <tr><th>ID</th><th>Name</th><th>Status</th></tr>
                                </thead>
                                <tbody>
                                    ${data.blockedByJobs.map(j => `
                                        <tr>
                                            <td><code>${j.id ?? '-'}</code></td>
                                            <td>${this.escapeHtml(j.name || '-')}</td>
                                            <td><span class="status-badge status-${statusNames[j.status]?.toLowerCase() || 'unknown'}">${statusNames[j.status] || j.status}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                } else {
                    depsHtml += '<div class="job-details-section"><h4>Blocked By</h4><div class="job-details-empty">This job has no dependencies</div></div>';
                }

                if (data.blocksJobs.length > 0) {
                    depsHtml += `
                        <div class="job-details-section">
                            <h4>Blocks (${data.blocksJobs.length})</h4>
                            <table class="data-table">
                                <thead>
                                    <tr><th>ID</th><th>Name</th><th>Status</th></tr>
                                </thead>
                                <tbody>
                                    ${data.blocksJobs.map(j => `
                                        <tr>
                                            <td><code>${j.id ?? '-'}</code></td>
                                            <td>${this.escapeHtml(j.name || '-')}</td>
                                            <td><span class="status-badge status-${statusNames[j.status]?.toLowerCase() || 'unknown'}">${statusNames[j.status] || j.status}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                } else {
                    depsHtml += '<div class="job-details-section"><h4>Blocks</h4><div class="job-details-empty">No jobs depend on this job</div></div>';
                }

                contentEl.innerHTML = depsHtml;
                break;
        }
    }

    renderJobDetailFilesTable(files) {
        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Path</th>
                        <th>Modified Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${files.map(f => `
                        <tr>
                            <td><code>${f.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(f.name || '-')}</td>
                            <td><code>${this.escapeHtml(f.path || '-')}</code></td>
                            <td>${this.formatUnixTimestamp(f.st_mtime)}</td>
                            <td>${f.path ? `<button class="btn-view-file" data-path="${this.escapeHtml(f.path)}" data-name="${this.escapeHtml(f.name || 'File')}">View</button>` : '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderJobDetailUserDataTable(userData) {
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
                            <td><code>${ud.id ?? '-'}</code></td>
                            <td>${this.escapeHtml(ud.name || '-')}</td>
                            <td><code>${this.escapeHtml(this.truncate(JSON.stringify(ud.data) || '-', 100))}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
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
            blockedBy[dep.job_id].push(dep.depends_on_job_id);
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

    // ==================== Workflow Wizard ====================

    setupWizard() {
        // Wizard state
        this.wizardStep = 1;
        this.wizardTotalSteps = 6;
        this.wizardJobs = [];
        this.wizardJobIdCounter = 0;
        this.wizardSchedulers = [];
        this.wizardSchedulerIdCounter = 0;
        this.wizardActions = [];
        this.wizardActionIdCounter = 0;
        this.wizardResourceMonitor = {
            enabled: true,
            granularity: 'summary',
            sample_interval_seconds: 5
        };
        // Parallelization strategy: 'resource_aware' or 'queue_depth'
        this.wizardParallelizationStrategy = 'resource_aware';

        // Resource presets
        this.resourcePresets = {
            'small': { name: 'Small', num_cpus: 1, memory: '1g', num_gpus: 0 },
            'medium': { name: 'Medium', num_cpus: 8, memory: '50g', num_gpus: 0 },
            'gpu': { name: 'GPU', num_cpus: 1, memory: '10g', num_gpus: 1 },
            'custom': { name: 'Custom', num_cpus: 1, memory: '1g', num_gpus: 0 }
        };

        // Parallelization strategy change handler
        document.getElementById('wizard-parallelization-strategy')?.addEventListener('change', (e) => {
            this.wizardParallelizationStrategy = e.target.value;
            // Re-render jobs to show/hide resource requirements
            this.wizardRenderJobs();
            // Re-render actions to show/hide max_parallel_jobs
            this.wizardRenderActions();
        });

        // Navigation buttons
        document.getElementById('wizard-prev')?.addEventListener('click', () => {
            this.wizardPrevStep();
        });

        document.getElementById('wizard-next')?.addEventListener('click', () => {
            this.wizardNextStep();
        });

        // Add job button
        document.getElementById('wizard-add-job')?.addEventListener('click', () => {
            this.wizardAddJob();
        });

        // Add scheduler button
        document.getElementById('wizard-add-scheduler')?.addEventListener('click', () => {
            this.wizardAddScheduler();
        });

        // Add action button
        document.getElementById('wizard-add-action')?.addEventListener('click', () => {
            this.wizardAddAction();
        });

        // Resource monitoring checkbox
        document.getElementById('wizard-monitoring-enabled')?.addEventListener('change', (e) => {
            this.wizardResourceMonitor.enabled = e.target.checked;
            const optionsDiv = document.getElementById('wizard-monitoring-options');
            if (optionsDiv) {
                optionsDiv.style.display = e.target.checked ? 'block' : 'none';
            }
        });

        // Resource monitoring granularity
        document.getElementById('wizard-monitoring-granularity')?.addEventListener('change', (e) => {
            this.wizardResourceMonitor.granularity = e.target.value;
        });

        // Resource monitoring interval
        document.getElementById('wizard-monitoring-interval')?.addEventListener('change', (e) => {
            const value = parseInt(e.target.value);
            if (value >= 1 && value <= 300) {
                this.wizardResourceMonitor.sample_interval_seconds = value;
            }
        });
    }

    resetWizard() {
        this.wizardStep = 1;
        this.wizardJobs = [];
        this.wizardJobIdCounter = 0;
        this.wizardSchedulers = [];
        this.wizardSchedulerIdCounter = 0;
        this.wizardActions = [];
        this.wizardActionIdCounter = 0;
        this.wizardResourceMonitor = {
            enabled: true,
            granularity: 'summary',
            sample_interval_seconds: 5
        };
        this.wizardParallelizationStrategy = 'resource_aware';

        // Clear form fields
        const nameInput = document.getElementById('wizard-name');
        const descInput = document.getElementById('wizard-description');
        if (nameInput) nameInput.value = '';
        if (descInput) descInput.value = '';

        // Reset parallelization strategy selector
        const strategySelect = document.getElementById('wizard-parallelization-strategy');
        if (strategySelect) strategySelect.value = 'resource_aware';

        // Reset resource monitoring form (enabled by default)
        const monitoringEnabled = document.getElementById('wizard-monitoring-enabled');
        const monitoringGranularity = document.getElementById('wizard-monitoring-granularity');
        const monitoringInterval = document.getElementById('wizard-monitoring-interval');
        const monitoringOptions = document.getElementById('wizard-monitoring-options');
        if (monitoringEnabled) monitoringEnabled.checked = true;
        if (monitoringGranularity) monitoringGranularity.value = 'summary';
        if (monitoringInterval) monitoringInterval.value = '5';
        if (monitoringOptions) monitoringOptions.style.display = 'block';

        // Reset step indicators
        document.querySelectorAll('.wizard-step').forEach((step, i) => {
            step.classList.toggle('active', i === 0);
            step.classList.remove('completed');
        });

        // Reset step content
        document.querySelectorAll('.wizard-content').forEach((content, i) => {
            content.classList.toggle('active', i === 0);
        });

        // Reset navigation buttons
        document.getElementById('wizard-prev').disabled = true;
        document.getElementById('wizard-next').textContent = 'Next';

        // Clear jobs list
        document.getElementById('wizard-jobs-list').innerHTML = '';

        // Clear schedulers list
        document.getElementById('wizard-schedulers-list').innerHTML = '';

        // Clear actions list
        document.getElementById('wizard-actions-list').innerHTML = '';
    }

    wizardGoToStep(step) {
        this.wizardStep = step;

        // Update step indicators
        document.querySelectorAll('.wizard-step').forEach((el, i) => {
            el.classList.toggle('active', i === step - 1);
            el.classList.toggle('completed', i < step - 1);
        });

        // Update content
        document.querySelectorAll('.wizard-content').forEach((content, i) => {
            content.classList.toggle('active', i === step - 1);
        });

        // Render the content for the current step
        if (step === 2) {
            this.wizardRenderJobs();
        } else if (step === 3) {
            this.wizardRenderSchedulers();
        } else if (step === 4) {
            this.wizardRenderActions();
        }

        // Update navigation
        document.getElementById('wizard-prev').disabled = step === 1;

        const nextBtn = document.getElementById('wizard-next');
        if (step === this.wizardTotalSteps) {
            nextBtn.textContent = 'Create Workflow';
            this.wizardGeneratePreview();
        } else {
            nextBtn.textContent = 'Next';
        }
    }

    wizardPrevStep() {
        if (this.wizardStep > 1) {
            this.wizardGoToStep(this.wizardStep - 1);
        }
    }

    wizardNextStep() {
        // Validate current step
        if (this.wizardStep === 1) {
            const name = document.getElementById('wizard-name')?.value?.trim();
            if (!name) {
                this.showToast('Please enter a workflow name', 'warning');
                return;
            }
        } else if (this.wizardStep === 2) {
            if (this.wizardJobs.length === 0) {
                this.showToast('Please add at least one job', 'warning');
                return;
            }
            // Validate all jobs have names and commands
            for (const job of this.wizardJobs) {
                if (!job.name?.trim()) {
                    this.showToast('All jobs must have a name', 'warning');
                    return;
                }
                if (!job.command?.trim()) {
                    this.showToast('All jobs must have a command', 'warning');
                    return;
                }
            }
        } else if (this.wizardStep === 3) {
            // Schedulers step - validate scheduler names and accounts if any exist
            for (const scheduler of this.wizardSchedulers) {
                if (!scheduler.name?.trim()) {
                    this.showToast('All schedulers must have a name', 'warning');
                    return;
                }
                if (!scheduler.account?.trim()) {
                    this.showToast('All schedulers must have an account', 'warning');
                    return;
                }
            }
        } else if (this.wizardStep === 4) {
            // Actions step - validate actions if any exist
            for (const action of this.wizardActions) {
                if (!action.scheduler?.trim()) {
                    this.showToast('All actions must have a scheduler selected', 'warning');
                    return;
                }
                // For on_jobs_ready and on_jobs_complete, jobs must be selected
                if ((action.trigger_type === 'on_jobs_ready' || action.trigger_type === 'on_jobs_complete')
                    && (!action.jobs || action.jobs.length === 0)) {
                    this.showToast('Actions triggered by job events must have at least one job selected', 'warning');
                    return;
                }
            }
        } else if (this.wizardStep === this.wizardTotalSteps) {
            // Create the workflow
            this.wizardCreateWorkflow();
            return;
        }

        if (this.wizardStep < this.wizardTotalSteps) {
            this.wizardGoToStep(this.wizardStep + 1);
        }
    }

    wizardAddJob() {
        const jobId = ++this.wizardJobIdCounter;
        const job = {
            id: jobId,
            name: '',
            command: '',
            depends_on: [],
            resource_preset: 'small',
            num_cpus: 1,
            memory: '1g',
            num_gpus: 0,
            runtime: 'PT1H',
            parameters: '',
            scheduler: ''
        };
        this.wizardJobs.push(job);
        this.wizardRenderJobs();

        // Expand the new job
        setTimeout(() => {
            const card = document.querySelector(`[data-job-id="${jobId}"]`);
            if (card) {
                card.classList.add('expanded');
                card.querySelector('input[name="job-name"]')?.focus();
            }
        }, 50);
    }

    wizardRemoveJob(jobId) {
        this.wizardJobs = this.wizardJobs.filter(j => j.id !== jobId);
        // Remove this job from any depends_on references
        this.wizardJobs.forEach(job => {
            job.depends_on = job.depends_on.filter(id => id !== jobId);
        });
        this.wizardRenderJobs();
    }

    wizardToggleJob(jobId) {
        const card = document.querySelector(`[data-job-id="${jobId}"]`);
        if (card) {
            card.classList.toggle('expanded');
        }
    }

    wizardUpdateJob(jobId, field, value) {
        const job = this.wizardJobs.find(j => j.id === jobId);
        if (!job) return;

        if (field === 'resource_preset') {
            job.resource_preset = value;
            if (value !== 'custom') {
                const preset = this.resourcePresets[value];
                job.num_cpus = preset.num_cpus;
                job.memory = preset.memory;
                job.num_gpus = preset.num_gpus;
            }
            // Re-render to update preset buttons and resource fields
            this.wizardRenderJobs();
        } else if (field === 'depends_on') {
            // Value is an array of job IDs
            job.depends_on = value;
        } else {
            job[field] = value;
            // If user modifies resources, switch to custom preset
            if (['num_cpus', 'memory', 'num_gpus'].includes(field)) {
                job.resource_preset = 'custom';
                // Update preset buttons without full re-render
                const card = document.querySelector(`[data-job-id="${jobId}"]`);
                if (card) {
                    card.querySelectorAll('.resource-preset-btn').forEach(btn => {
                        btn.classList.toggle('selected', btn.dataset.preset === 'custom');
                    });
                }
            }
        }

        // Update job header title
        if (field === 'name') {
            const card = document.querySelector(`[data-job-id="${jobId}"]`);
            if (card) {
                const titleSpan = card.querySelector('.job-title');
                if (titleSpan) {
                    titleSpan.textContent = value || 'Untitled Job';
                }
            }
        }
    }

    wizardRenderJobs() {
        const container = document.getElementById('wizard-jobs-list');
        if (!container) return;

        // Track which cards are expanded before re-rendering
        const expandedJobIds = [];
        container.querySelectorAll('.wizard-job-card.expanded').forEach(card => {
            const jobId = parseInt(card.dataset.jobId);
            if (!isNaN(jobId)) expandedJobIds.push(jobId);
        });

        if (this.wizardJobs.length === 0) {
            container.innerHTML = `
                <div class="wizard-empty-state">
                    <p>No jobs yet</p>
                    <p>Click "+ Add Job" to create your first job</p>
                </div>
            `;
            return;
        }

        const showResources = this.wizardParallelizationStrategy === 'resource_aware';

        container.innerHTML = this.wizardJobs.map((job, index) => {
            // Get other jobs for depends_on dropdown
            const otherJobs = this.wizardJobs.filter(j => j.id !== job.id);
            const isExpanded = expandedJobIds.includes(job.id);

            return `
                <div class="wizard-job-card${isExpanded ? ' expanded' : ''}" data-job-id="${job.id}">
                    <div class="wizard-job-header" onclick="app.wizardToggleJob(${job.id})">
                        <h5>
                            <span class="job-index">${index + 1}</span>
                            <span class="job-title">${this.escapeHtml(job.name) || 'Untitled Job'}</span>
                        </h5>
                        <div class="wizard-job-actions">
                            <button type="button" class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.wizardRemoveJob(${job.id})">Remove</button>
                        </div>
                    </div>
                    <div class="wizard-job-body">
                        <div class="wizard-job-row">
                            <div class="form-group">
                                <label>Job Name *</label>
                                <input type="text" name="job-name" class="text-input"
                                       value="${this.escapeHtml(job.name)}"
                                       placeholder="e.g., process-data"
                                       onchange="app.wizardUpdateJob(${job.id}, 'name', this.value)">
                            </div>
                            <div class="form-group">
                                <label>Depends On</label>
                                <select class="select-input" multiple size="2"
                                        onchange="app.wizardUpdateJob(${job.id}, 'depends_on', Array.from(this.selectedOptions).map(o => parseInt(o.value)))">
                                    ${otherJobs.map(j => `
                                        <option value="${j.id}" ${job.depends_on.includes(j.id) ? 'selected' : ''}>
                                            ${this.escapeHtml(j.name) || 'Untitled Job'}
                                        </option>
                                    `).join('')}
                                </select>
                                <small>Hold Ctrl/Cmd to select multiple</small>
                            </div>
                        </div>
                        <div class="wizard-job-row full">
                            <div class="form-group">
                                <label>Command *</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(job.command)}"
                                       placeholder="e.g., python process.py --input data.csv"
                                       onchange="app.wizardUpdateJob(${job.id}, 'command', this.value)">
                            </div>
                        </div>
                        <div class="wizard-job-row full">
                            <div class="form-group">
                                <label>Parameters (for job expansion)</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(job.parameters)}"
                                       placeholder='e.g., i: "1:10", lr: "[0.001, 0.01, 0.1]"'
                                       onchange="app.wizardUpdateJob(${job.id}, 'parameters', this.value)">
                                <small>Creates multiple jobs. Use {param} in name/command. Formats: "1:10" (range), "[a,b,c]" (list)</small>
                            </div>
                        </div>
                        <div class="wizard-job-row">
                            <div class="form-group">
                                <label>Scheduler</label>
                                <div class="scheduler-select-row">
                                    <select class="select-input"
                                            onchange="app.wizardUpdateJob(${job.id}, 'scheduler', this.value)">
                                        <option value="" ${!job.scheduler ? 'selected' : ''}>Auto (any compatible runner)</option>
                                        ${this.wizardGetSchedulerNames().map(name => `
                                            <option value="${this.escapeHtml(name)}" ${job.scheduler === name ? 'selected' : ''}>
                                                ${this.escapeHtml(name)}
                                            </option>
                                        `).join('')}
                                    </select>
                                    <button type="button" class="btn btn-sm btn-secondary"
                                            onclick="event.stopPropagation(); app.wizardAddSchedulerFromJob(${job.id})"
                                            title="Add a new Slurm scheduler">+ New</button>
                                </div>
                                <small>Runs on any compatible runner. <a href="https://nrel.github.io/torc/explanation/parallelization.html#job-allocation-ambiguity-two-approaches" target="_blank">Learn more</a></small>
                            </div>
                            <div class="form-group"></div>
                        </div>
                        ${showResources ? `
                            <div class="form-group">
                                <label>Resources</label>
                                <div class="resource-presets">
                                    ${Object.entries(this.resourcePresets).map(([key, preset]) => `
                                        <button type="button" class="resource-preset-btn ${job.resource_preset === key ? 'selected' : ''}"
                                                data-preset="${key}"
                                                onclick="app.wizardUpdateJob(${job.id}, 'resource_preset', '${key}')">
                                            ${preset.name}
                                            ${key !== 'custom' ? `<small>(${preset.num_cpus} CPU, ${preset.memory}${preset.num_gpus ? ', ' + preset.num_gpus + ' GPU' : ''})</small>` : ''}
                                        </button>
                                    `).join('')}
                                </div>
                            </div>
                            ${job.resource_preset === 'custom' ? `
                                <div class="wizard-job-row">
                                    <div class="form-group">
                                        <label>CPUs</label>
                                        <input type="number" class="text-input" min="1" value="${job.num_cpus}"
                                               onchange="app.wizardUpdateJob(${job.id}, 'num_cpus', parseInt(this.value))">
                                    </div>
                                    <div class="form-group">
                                        <label>Memory</label>
                                        <input type="text" class="text-input" value="${this.escapeHtml(job.memory)}"
                                               placeholder="e.g., 4g, 512m"
                                               onchange="app.wizardUpdateJob(${job.id}, 'memory', this.value)">
                                    </div>
                                </div>
                                <div class="wizard-job-row">
                                    <div class="form-group">
                                        <label>GPUs</label>
                                        <input type="number" class="text-input" min="0" value="${job.num_gpus}"
                                               onchange="app.wizardUpdateJob(${job.id}, 'num_gpus', parseInt(this.value))">
                                    </div>
                                    <div class="form-group">
                                        <label>Runtime</label>
                                        <input type="text" class="text-input" value="${this.escapeHtml(job.runtime)}"
                                               placeholder="PT1H (1 hour)"
                                               onchange="app.wizardUpdateJob(${job.id}, 'runtime', this.value)">
                                        <small>ISO8601 duration: PT1H (1hr), PT30M (30min), P1D (1 day)</small>
                                    </div>
                                </div>
                            ` : ''}
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Convert a parameterized job name template to a regex pattern.
     * E.g., "job_{i}" -> "^job_.*$", "train_{lr}_{batch}" -> "^train_.*_.*$"
     */
    wizardJobNameToRegex(jobName) {
        // Escape regex special characters except for our placeholders
        let pattern = jobName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        // Replace parameter placeholders like {i}, {i:03d}, {lr:.4f} with .*
        pattern = pattern.replace(/\\\{[^}]+\\\}/g, '.*');
        return `^${pattern}$`;
    }

    /**
     * Check if a job has parameters (is parameterized)
     */
    wizardJobIsParameterized(job) {
        return job.parameters?.trim()?.length > 0;
    }

    // ==================== Scheduler Management ====================

    wizardAddScheduler() {
        const schedulerId = ++this.wizardSchedulerIdCounter;
        const scheduler = {
            id: schedulerId,
            name: '',
            account: '',
            nodes: 1,
            walltime: '01:00:00',
            partition: '',
            qos: '',
            gres: '',
            mem: '',
            tmp: '',
            extra: ''
        };
        this.wizardSchedulers.push(scheduler);
        this.wizardRenderSchedulers();

        // Expand the new scheduler
        setTimeout(() => {
            const card = document.querySelector(`[data-scheduler-id="${schedulerId}"]`);
            if (card) {
                card.classList.add('expanded');
                card.querySelector('input[name="scheduler-name"]')?.focus();
            }
        }, 50);
    }

    wizardRemoveScheduler(schedulerId) {
        this.wizardSchedulers = this.wizardSchedulers.filter(s => s.id !== schedulerId);
        // Clear scheduler reference from jobs that used this scheduler
        const scheduler = this.wizardSchedulers.find(s => s.id === schedulerId);
        if (scheduler) {
            this.wizardJobs.forEach(job => {
                if (job.scheduler === scheduler.name) {
                    job.scheduler = '';
                }
            });
        }
        this.wizardRenderSchedulers();
    }

    /**
     * Add a new scheduler from within a job card.
     * Creates a new scheduler with a default name, adds it, and re-renders jobs
     * so the dropdown updates.
     */
    wizardAddSchedulerFromJob(jobId) {
        const schedulerId = ++this.wizardSchedulerIdCounter;
        const schedulerName = `scheduler-${schedulerId}`;
        const scheduler = {
            id: schedulerId,
            name: schedulerName,
            account: '',
            nodes: 1,
            walltime: '01:00:00',
            partition: '',
            qos: '',
            gres: '',
            mem: '',
            tmp: '',
            extra: ''
        };
        this.wizardSchedulers.push(scheduler);

        // Auto-assign this scheduler to the job
        const job = this.wizardJobs.find(j => j.id === jobId);
        if (job) {
            job.scheduler = schedulerName;
        }

        // Re-render jobs to update scheduler dropdowns
        this.wizardRenderJobs();

        // Show a toast to guide the user
        this.showToast(`Scheduler "${schedulerName}" created. Configure it in step 3 (Schedulers).`, 'info');
    }

    wizardToggleScheduler(schedulerId) {
        const card = document.querySelector(`[data-scheduler-id="${schedulerId}"]`);
        if (card) {
            card.classList.toggle('expanded');
        }
    }

    wizardUpdateScheduler(schedulerId, field, value) {
        const scheduler = this.wizardSchedulers.find(s => s.id === schedulerId);
        if (!scheduler) return;

        // If updating name, update any jobs referencing the old name
        if (field === 'name' && scheduler.name) {
            const oldName = scheduler.name;
            this.wizardJobs.forEach(job => {
                if (job.scheduler === oldName) {
                    job.scheduler = value;
                }
            });
        }

        scheduler[field] = value;

        // Update scheduler header title
        if (field === 'name') {
            const card = document.querySelector(`[data-scheduler-id="${schedulerId}"]`);
            if (card) {
                const titleSpan = card.querySelector('.scheduler-title');
                if (titleSpan) {
                    titleSpan.textContent = value || 'Untitled Scheduler';
                }
            }
        }
    }

    wizardRenderSchedulers() {
        const container = document.getElementById('wizard-schedulers-list');
        if (!container) return;

        // Track which cards are expanded before re-rendering
        const expandedSchedulerIds = [];
        container.querySelectorAll('.wizard-scheduler-card.expanded').forEach(card => {
            const schedulerId = parseInt(card.dataset.schedulerId);
            if (!isNaN(schedulerId)) expandedSchedulerIds.push(schedulerId);
        });

        if (this.wizardSchedulers.length === 0) {
            container.innerHTML = `
                <div class="wizard-empty-state">
                    <p>No schedulers defined</p>
                    <p>Click "+ Add Scheduler" to define a Slurm scheduler configuration.</p>
                    <p class="wizard-help-text">Schedulers are optional - you can run workflows locally without them.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.wizardSchedulers.map((scheduler, index) => {
            const isExpanded = expandedSchedulerIds.includes(scheduler.id);
            return `
                <div class="wizard-scheduler-card${isExpanded ? ' expanded' : ''}" data-scheduler-id="${scheduler.id}">
                    <div class="wizard-scheduler-header" onclick="app.wizardToggleScheduler(${scheduler.id})">
                        <h5>
                            <span class="scheduler-index">${index + 1}</span>
                            <span class="scheduler-title">${this.escapeHtml(scheduler.name) || 'Untitled Scheduler'}</span>
                        </h5>
                        <div class="wizard-scheduler-actions">
                            <button type="button" class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.wizardRemoveScheduler(${scheduler.id})">Remove</button>
                        </div>
                    </div>
                    <div class="wizard-scheduler-body">
                        <div class="wizard-scheduler-row">
                            <div class="form-group">
                                <label>Scheduler Name *</label>
                                <input type="text" name="scheduler-name" class="text-input"
                                       value="${this.escapeHtml(scheduler.name)}"
                                       placeholder="e.g., compute_scheduler"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'name', this.value)">
                            </div>
                            <div class="form-group">
                                <label>Account *</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.account)}"
                                       placeholder="e.g., my_project"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'account', this.value)">
                            </div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group">
                                <label>Nodes</label>
                                <input type="number" class="text-input" min="1" value="${scheduler.nodes}"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'nodes', parseInt(this.value) || 1)">
                            </div>
                            <div class="form-group">
                                <label>Wall Time</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.walltime)}"
                                       placeholder="HH:MM:SS (e.g., 04:00:00)"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'walltime', this.value)">
                            </div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group">
                                <label>Partition</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.partition)}"
                                       placeholder="e.g., compute, gpu"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'partition', this.value)">
                            </div>
                            <div class="form-group">
                                <label>QoS</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.qos)}"
                                       placeholder="e.g., normal, high"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'qos', this.value)">
                            </div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group">
                                <label>GRES (GPU Resources)</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.gres)}"
                                       placeholder="e.g., gpu:2"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'gres', this.value)">
                            </div>
                            <div class="form-group">
                                <label>Memory</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.mem)}"
                                       placeholder="e.g., 256G"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'mem', this.value)">
                            </div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group">
                                <label>Temp Storage</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.tmp)}"
                                       placeholder="e.g., 100G"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'tmp', this.value)">
                            </div>
                            <div class="form-group"></div>
                        </div>
                        <div class="wizard-scheduler-row full">
                            <div class="form-group">
                                <label>Extra Slurm Options</label>
                                <input type="text" class="text-input"
                                       value="${this.escapeHtml(scheduler.extra)}"
                                       placeholder="e.g., --exclusive --constraint=skylake"
                                       onchange="app.wizardUpdateScheduler(${scheduler.id}, 'extra', this.value)">
                                <small>Additional sbatch options passed directly to Slurm</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Get list of scheduler names for dropdown selection
     */
    wizardGetSchedulerNames() {
        return this.wizardSchedulers
            .filter(s => s.name?.trim())
            .map(s => s.name.trim());
    }

    /**
     * Get list of job names for dropdown selection
     */
    wizardGetJobNames() {
        return this.wizardJobs
            .filter(j => j.name?.trim())
            .map(j => j.name.trim());
    }

    // ==================== Action Management ====================

    wizardAddAction() {
        const actionId = ++this.wizardActionIdCounter;
        const action = {
            id: actionId,
            trigger_type: 'on_workflow_start',
            scheduler: '',
            jobs: [],
            num_allocations: 1,
            max_parallel_jobs: 10
        };
        this.wizardActions.push(action);
        this.wizardRenderActions();

        // Expand the new action
        setTimeout(() => {
            const card = document.querySelector(`[data-action-id="${actionId}"]`);
            if (card) {
                card.classList.add('expanded');
            }
        }, 50);
    }

    wizardRemoveAction(actionId) {
        this.wizardActions = this.wizardActions.filter(a => a.id !== actionId);
        this.wizardRenderActions();
    }

    wizardToggleAction(actionId) {
        const card = document.querySelector(`[data-action-id="${actionId}"]`);
        if (card) {
            card.classList.toggle('expanded');
        }
    }

    wizardUpdateAction(actionId, field, value) {
        const action = this.wizardActions.find(a => a.id === actionId);
        if (!action) return;

        action[field] = value;

        // If trigger type changed, clear jobs if switching to/from workflow_start
        if (field === 'trigger_type') {
            if (value === 'on_workflow_start') {
                action.jobs = [];
            }
            this.wizardRenderActions();
        }
    }

    wizardGetTriggerTypeLabel(triggerType) {
        const labels = {
            'on_workflow_start': 'When workflow starts',
            'on_jobs_ready': 'When jobs become ready',
            'on_jobs_complete': 'When jobs complete'
        };
        return labels[triggerType] || triggerType;
    }

    wizardRenderActions() {
        const container = document.getElementById('wizard-actions-list');
        if (!container) return;

        const schedulerNames = this.wizardGetSchedulerNames();
        const jobNames = this.wizardGetJobNames();

        if (this.wizardActions.length === 0) {
            container.innerHTML = `
                <div class="wizard-empty-state">
                    <p>No actions defined</p>
                    <p>Click "+ Add Action" to automatically schedule Slurm nodes on workflow events.</p>
                    <p class="wizard-help-text">Actions are optional - you can manually start workflows without them.</p>
                </div>
            `;
            return;
        }

        if (schedulerNames.length === 0) {
            container.innerHTML = `
                <div class="wizard-empty-state">
                    <p>No schedulers available</p>
                    <p>Please define at least one scheduler in step 3 before creating actions.</p>
                </div>
            `;
            return;
        }

        // Track which cards are expanded before re-rendering
        const expandedActionIds = [];
        container.querySelectorAll('.wizard-action-card.expanded').forEach(card => {
            const actionId = parseInt(card.dataset.actionId);
            if (!isNaN(actionId)) expandedActionIds.push(actionId);
        });

        container.innerHTML = this.wizardActions.map((action, index) => {
            const showJobSelector = action.trigger_type === 'on_jobs_ready' || action.trigger_type === 'on_jobs_complete';
            const isExpanded = expandedActionIds.includes(action.id);

            return `
                <div class="wizard-action-card${isExpanded ? ' expanded' : ''}" data-action-id="${action.id}">
                    <div class="wizard-action-header" onclick="app.wizardToggleAction(${action.id})">
                        <h5>
                            <span class="action-index">${index + 1}</span>
                            <span class="action-title">${this.wizardGetTriggerTypeLabel(action.trigger_type)}</span>
                            ${action.scheduler ? `<span class="action-scheduler-badge">${this.escapeHtml(action.scheduler)}</span>` : ''}
                        </h5>
                        <div class="wizard-action-actions">
                            <button type="button" class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.wizardRemoveAction(${action.id})">Remove</button>
                        </div>
                    </div>
                    <div class="wizard-action-body">
                        <div class="wizard-action-row">
                            <div class="form-group">
                                <label>Trigger *</label>
                                <select class="select-input"
                                        onchange="app.wizardUpdateAction(${action.id}, 'trigger_type', this.value)">
                                    <option value="on_workflow_start" ${action.trigger_type === 'on_workflow_start' ? 'selected' : ''}>
                                        When workflow starts
                                    </option>
                                    <option value="on_jobs_ready" ${action.trigger_type === 'on_jobs_ready' ? 'selected' : ''}>
                                        When jobs become ready
                                    </option>
                                    <option value="on_jobs_complete" ${action.trigger_type === 'on_jobs_complete' ? 'selected' : ''}>
                                        When jobs complete
                                    </option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Scheduler *</label>
                                <select class="select-input"
                                        onchange="app.wizardUpdateAction(${action.id}, 'scheduler', this.value)">
                                    <option value="">Select scheduler...</option>
                                    ${schedulerNames.map(name => `
                                        <option value="${this.escapeHtml(name)}" ${action.scheduler === name ? 'selected' : ''}>
                                            ${this.escapeHtml(name)}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                        </div>
                        ${showJobSelector ? `
                            <div class="wizard-action-row full">
                                <div class="form-group">
                                    <label>Jobs *</label>
                                    <select class="select-input" multiple size="4"
                                            onchange="app.wizardUpdateAction(${action.id}, 'jobs', Array.from(this.selectedOptions).map(o => o.value))">
                                        ${jobNames.map(name => `
                                            <option value="${this.escapeHtml(name)}" ${action.jobs?.includes(name) ? 'selected' : ''}>
                                                ${this.escapeHtml(name)}
                                            </option>
                                        `).join('')}
                                    </select>
                                    <small>Hold Ctrl/Cmd to select multiple jobs. Action triggers when ${action.trigger_type === 'on_jobs_ready' ? 'these jobs become ready' : 'these jobs complete'}.</small>
                                </div>
                            </div>
                        ` : ''}
                        <div class="wizard-action-row">
                            <div class="form-group">
                                <label>Number of Allocations</label>
                                <input type="number" class="text-input" min="1" value="${action.num_allocations || 1}"
                                       onchange="app.wizardUpdateAction(${action.id}, 'num_allocations', parseInt(this.value) || 1)">
                                <small>How many Slurm job allocations to request</small>
                            </div>
                            ${this.wizardParallelizationStrategy === 'queue_depth' ? `
                                <div class="form-group">
                                    <label>Max Parallel Jobs</label>
                                    <input type="number" class="text-input" min="1" value="${action.max_parallel_jobs || 10}"
                                           onchange="app.wizardUpdateAction(${action.id}, 'max_parallel_jobs', parseInt(this.value) || 10)">
                                    <small>Maximum concurrent jobs per allocation (--max-parallel-jobs)</small>
                                </div>
                            ` : '<div class="form-group"></div>'}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    wizardGenerateSpec() {
        const name = document.getElementById('wizard-name')?.value?.trim() || 'untitled-workflow';
        const description = document.getElementById('wizard-description')?.value?.trim();
        const useResourceAware = this.wizardParallelizationStrategy === 'resource_aware';

        // Build job info map for resolving depends_on references
        const jobInfoMap = {};
        this.wizardJobs.forEach(job => {
            const jobName = job.name?.trim() || `job_${job.id}`;
            jobInfoMap[job.id] = {
                name: jobName,
                isParameterized: this.wizardJobIsParameterized(job),
                regex: this.wizardJobNameToRegex(jobName)
            };
        });

        // Build unique resource requirements (only for resource-aware strategy)
        const resourceReqs = {};
        if (useResourceAware) {
            this.wizardJobs.forEach(job => {
                const runtime = job.runtime || 'PT1H';
                const key = `${job.num_cpus}_${job.memory}_${job.num_gpus}_${runtime}`;
                if (!resourceReqs[key]) {
                    resourceReqs[key] = {
                        name: `res_${job.num_cpus}cpu_${job.memory}${job.num_gpus > 0 ? '_' + job.num_gpus + 'gpu' : ''}_${runtime}`,
                        num_cpus: job.num_cpus,
                        memory: job.memory,
                        num_gpus: job.num_gpus,
                        num_nodes: 1,
                        runtime: runtime
                    };
                }
            });
        }

        // Build jobs array
        const jobs = this.wizardJobs.map(job => {
            const runtime = job.runtime || 'PT1H';
            const resKey = `${job.num_cpus}_${job.memory}_${job.num_gpus}_${runtime}`;
            const jobSpec = {
                name: job.name?.trim() || `job_${job.id}`,
                command: job.command?.trim() || 'echo "TODO"'
            };

            // Add depends_on - separate parameterized deps (use regex) from regular deps
            if (job.depends_on.length > 0) {
                const regularDeps = [];
                const regexDeps = [];

                job.depends_on.forEach(depId => {
                    const depInfo = jobInfoMap[depId];
                    if (depInfo.isParameterized) {
                        // Parameterized job - use regex to match all expanded instances
                        regexDeps.push(depInfo.regex);
                    } else {
                        // Regular job - use exact name
                        regularDeps.push(depInfo.name);
                    }
                });

                if (regularDeps.length > 0) {
                    jobSpec.depends_on = regularDeps;
                }
                if (regexDeps.length > 0) {
                    jobSpec.depends_on_regexes = regexDeps;
                }
            }

            // Add resource requirements only for resource-aware strategy
            if (useResourceAware) {
                jobSpec.resource_requirements = resourceReqs[resKey].name;
            }

            // Add scheduler if specified
            if (job.scheduler?.trim()) {
                jobSpec.scheduler = job.scheduler.trim();
            }

            // Add parameters if present
            // Format: parameters is an object like {"i": "1:100", "lr": "[0.001,0.01,0.1]"}
            if (job.parameters?.trim()) {
                try {
                    const paramStr = job.parameters.trim();
                    const params = {};

                    // Parse key: value pairs
                    // Supports: i: "1:10", lr: "[0.001, 0.01]", name: "['a','b']"
                    // Use a state machine approach to handle nested brackets/quotes
                    let i = 0;
                    while (i < paramStr.length) {
                        // Skip whitespace and commas
                        while (i < paramStr.length && (paramStr[i] === ' ' || paramStr[i] === ',')) i++;
                        if (i >= paramStr.length) break;

                        // Read key (word characters)
                        let keyStart = i;
                        while (i < paramStr.length && /\w/.test(paramStr[i])) i++;
                        const key = paramStr.slice(keyStart, i).trim();
                        if (!key) break;

                        // Skip whitespace and colon
                        while (i < paramStr.length && (paramStr[i] === ' ' || paramStr[i] === ':')) i++;

                        // Read value - handle quotes and brackets
                        let value = '';
                        if (paramStr[i] === '"' || paramStr[i] === "'") {
                            // Quoted string
                            const quote = paramStr[i];
                            i++; // skip opening quote
                            let valueStart = i;
                            while (i < paramStr.length && paramStr[i] !== quote) i++;
                            value = paramStr.slice(valueStart, i);
                            i++; // skip closing quote
                        } else if (paramStr[i] === '[') {
                            // Array - find matching bracket
                            let valueStart = i;
                            let depth = 0;
                            while (i < paramStr.length) {
                                if (paramStr[i] === '[') depth++;
                                else if (paramStr[i] === ']') {
                                    depth--;
                                    if (depth === 0) { i++; break; }
                                }
                                i++;
                            }
                            value = paramStr.slice(valueStart, i);
                        } else {
                            // Unquoted value - read until comma or end
                            let valueStart = i;
                            while (i < paramStr.length && paramStr[i] !== ',') i++;
                            value = paramStr.slice(valueStart, i).trim();
                        }

                        if (key && value) {
                            params[key] = value;
                        }
                    }

                    if (Object.keys(params).length > 0) {
                        jobSpec.parameters = params;
                    }
                } catch (e) {
                    console.warn('Failed to parse parameters:', e);
                }
            }

            return jobSpec;
        });

        // Build slurm_schedulers array
        const slurmSchedulers = this.wizardSchedulers
            .filter(s => s.name?.trim() && s.account?.trim())
            .map(s => {
                const schedulerSpec = {
                    name: s.name.trim(),
                    account: s.account.trim(),
                    nodes: s.nodes || 1,
                    walltime: s.walltime?.trim() || '01:00:00'
                };
                // Add optional fields only if they have values
                if (s.partition?.trim()) schedulerSpec.partition = s.partition.trim();
                if (s.qos?.trim()) schedulerSpec.qos = s.qos.trim();
                if (s.gres?.trim()) schedulerSpec.gres = s.gres.trim();
                if (s.mem?.trim()) schedulerSpec.mem = s.mem.trim();
                if (s.tmp?.trim()) schedulerSpec.tmp = s.tmp.trim();
                if (s.extra?.trim()) schedulerSpec.extra = s.extra.trim();
                return schedulerSpec;
            });

        // Build actions array
        const actions = this.wizardActions
            .filter(a => a.scheduler?.trim())
            .map(a => {
                const actionSpec = {
                    trigger_type: a.trigger_type,
                    action_type: 'schedule_nodes',
                    scheduler: a.scheduler.trim(),
                    scheduler_type: 'slurm',
                    num_allocations: a.num_allocations || 1
                };
                // Add jobs only for job-based triggers
                if ((a.trigger_type === 'on_jobs_ready' || a.trigger_type === 'on_jobs_complete')
                    && a.jobs && a.jobs.length > 0) {
                    actionSpec.jobs = a.jobs;
                }
                // Add max_parallel_jobs for queue-depth strategy
                if (!useResourceAware && a.max_parallel_jobs) {
                    actionSpec.max_parallel_jobs = a.max_parallel_jobs;
                }
                return actionSpec;
            });

        // Build the spec
        const spec = {
            name,
            jobs
        };

        // Add resource_requirements only for resource-aware strategy
        if (useResourceAware && Object.keys(resourceReqs).length > 0) {
            spec.resource_requirements = Object.values(resourceReqs);
        }

        if (description) {
            spec.description = description;
        }

        // Add resource_monitor config (always include to explicitly enable or disable)
        if (this.wizardResourceMonitor.enabled) {
            spec.resource_monitor = {
                enabled: true,
                granularity: this.wizardResourceMonitor.granularity,
                sample_interval_seconds: this.wizardResourceMonitor.sample_interval_seconds
            };
        } else {
            spec.resource_monitor = {
                enabled: false
            };
        }

        // Add slurm_schedulers if any are defined
        if (slurmSchedulers.length > 0) {
            spec.slurm_schedulers = slurmSchedulers;
        }

        // Add actions if any are defined
        if (actions.length > 0) {
            spec.actions = actions;
        }

        return spec;
    }

    wizardGeneratePreview() {
        const spec = this.wizardGenerateSpec();
        const preview = document.getElementById('wizard-preview');
        if (preview) {
            preview.textContent = JSON.stringify(spec, null, 2);
        }
    }

    async wizardCreateWorkflow() {
        const spec = this.wizardGenerateSpec();
        const specJson = JSON.stringify(spec, null, 2);

        try {
            const result = await api.cliCreateWorkflow(specJson, false, '.json');

            if (result.success) {
                this.showToast('Workflow created successfully', 'success');
                this.hideModal('create-workflow-modal');
                this.resetWizard();
                await this.loadWorkflows();

                // Check if we should initialize/run
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

    formatTimestamp(timestamp) {
        if (!timestamp) return '-';
        try {
            const date = new Date(timestamp);
            return date.toISOString().replace('T', ' ').substring(0, 19);
        } catch {
            return timestamp;
        }
    }

    formatUnixTimestamp(unixTime) {
        if (unixTime == null) return '-';
        try {
            // Unix timestamp is in seconds (as a float)
            const date = new Date(unixTime * 1000);
            return date.toISOString().replace('T', ' ').substring(0, 19);
        } catch {
            return '-';
        }
    }

    formatBytes(bytes) {
        if (bytes == null) return '-';
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    renderWorkflowEventsTable(events) {
        // Events may be an array or need extraction
        const items = Array.isArray(events) ? events : api.extractItems(events);
        const controls = this.renderTableControls('events');
        const count = `<span class="table-count">${items.length} event${items.length !== 1 ? 's' : ''}</span>`;

        if (!items || items.length === 0) {
            return `${controls}<div class="placeholder-message">No events in this workflow</div>`;
        }

        return `
            ${controls}
            ${count}
            <table class="data-table">
                <thead>
                    <tr>
                        ${this.renderSortableHeader('ID', 'id')}
                        ${this.renderSortableHeader('Timestamp', 'timestamp')}
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(event => `
                        <tr>
                            <td><code>${event.id ?? '-'}</code></td>
                            <td>${this.formatTimestamp(event.timestamp)}</td>
                            <td><code>${this.escapeHtml(this.truncate(JSON.stringify(event.data) || '-', 100))}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

// Initialize application
const app = new TorcDashboard();
document.addEventListener('DOMContentLoaded', () => app.init());
