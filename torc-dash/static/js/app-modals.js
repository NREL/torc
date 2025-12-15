/**
 * Torc Dashboard - Modal Handling
 * Create workflow modal, execution plan modal, job details modal, file viewer modal
 */

Object.assign(TorcDashboard.prototype, {
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

        // Close modal on background click (use mousedown to avoid closing when selecting text)
        document.getElementById('create-workflow-modal')?.addEventListener('mousedown', (e) => {
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
    },

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
    },

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
    },

    switchCreateTab(tabName) {
        this.currentCreateTab = tabName;

        document.querySelectorAll('.sub-tab[data-createtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.createtab === tabName);
        });

        document.querySelectorAll('.create-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `create-panel-${tabName}`);
        });
    },

    showModal(modalId) {
        document.getElementById(modalId)?.classList.add('active');
    },

    hideModal(modalId) {
        document.getElementById(modalId)?.classList.remove('active');
    },

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
    },

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
    },

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
    },

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
    },

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
    },

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
    },

    async showExecutionPlan(workflowId) {
        this.showModal('execution-plan-modal');
        const content = document.getElementById('execution-plan-content');
        content.innerHTML = '<div class="placeholder-message">Loading execution plan...</div>';

        try {
            // Get execution plan from CLI (includes scheduler allocations)
            const result = await api.cliExecutionPlan(workflowId);

            if (!result.success) {
                content.innerHTML = `<div class="placeholder-message">Error: ${this.escapeHtml(result.stderr || result.stdout || 'Unknown error')}</div>`;
                return;
            }

            // Parse the JSON output
            const plan = JSON.parse(result.stdout);
            content.innerHTML = this.renderExecutionPlan(plan);
        } catch (error) {
            content.innerHTML = `<div class="placeholder-message">Error loading execution plan: ${error.message}</div>`;
        }
    },

    renderExecutionPlan(plan) {
        if (!plan.stages || plan.stages.length === 0) {
            return '<div class="placeholder-message">No execution stages computed</div>';
        }

        return `
            <div class="plan-summary" style="margin-bottom: 16px;">
                <strong>Workflow:</strong> ${this.escapeHtml(plan.workflow_name || 'Unnamed')} |
                <strong>Total Stages:</strong> ${plan.total_stages} |
                <strong>Total Jobs:</strong> ${plan.total_jobs}
            </div>
            ${plan.stages.map(stage => `
                <div class="plan-stage">
                    <div class="plan-stage-header">
                        <div class="plan-stage-number">${stage.stage_number}</div>
                        <div class="plan-stage-trigger">${this.escapeHtml(stage.trigger)}</div>
                    </div>
                    <div class="plan-stage-content">
                        <h5>Jobs Becoming Ready (${stage.jobs_becoming_ready.length})</h5>
                        <ul>
                            ${stage.jobs_becoming_ready.slice(0, 10).map(jobName => `
                                <li>${this.escapeHtml(jobName)}</li>
                            `).join('')}
                            ${stage.jobs_becoming_ready.length > 10 ? `<li>... and ${stage.jobs_becoming_ready.length - 10} more</li>` : ''}
                        </ul>
                        ${this.renderSchedulerAllocations(stage.scheduler_allocations)}
                    </div>
                </div>
            `).join('')}
        `;
    },

    renderSchedulerAllocations(allocations) {
        if (!allocations || allocations.length === 0) {
            return '';
        }

        return `
            <div class="scheduler-allocations" style="margin-top: 12px;">
                <h5>Scheduler Allocations</h5>
                ${allocations.map(alloc => `
                    <div class="scheduler-allocation" style="margin-left: 16px; margin-bottom: 8px; padding: 8px; background: var(--surface-color); border-radius: 4px;">
                        <div><strong>Scheduler:</strong> ${this.escapeHtml(alloc.scheduler)} (${this.escapeHtml(alloc.scheduler_type)})</div>
                        <div><strong>Allocations:</strong> ${alloc.num_allocations}</div>
                        ${alloc.job_names && alloc.job_names.length > 0 ? `
                            <div><strong>Jobs:</strong> ${alloc.job_names.slice(0, 5).map(n => this.escapeHtml(n)).join(', ')}${alloc.job_names.length > 5 ? ` ... and ${alloc.job_names.length - 5} more` : ''}</div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    },
});
