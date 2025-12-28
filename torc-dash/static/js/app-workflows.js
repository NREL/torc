/**
 * Torc Dashboard - Workflows Tab
 * Workflow listing, running, and management
 */

Object.assign(TorcDashboard.prototype, {
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

        // Select all checkbox
        document.getElementById('workflows-select-all')?.addEventListener('change', (e) => {
            this.toggleSelectAllWorkflows(e.target.checked);
        });

        // Bulk action buttons
        document.getElementById('btn-bulk-delete')?.addEventListener('click', () => {
            this.bulkDeleteWorkflows();
        });

        document.getElementById('btn-clear-selection')?.addEventListener('click', () => {
            this.clearWorkflowSelection();
        });
    },

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
    },

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
    },

    renderWorkflowsTable(workflows) {
        const tbody = document.getElementById('workflows-body');
        if (!tbody) return;

        if (!workflows || workflows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="placeholder-message">No workflows found</td></tr>';
            this.updateBulkActionBar();
            return;
        }

        tbody.innerHTML = workflows.map(workflow => {
            const isSelected = this.selectedWorkflowIds.has(workflow.id);
            return `
            <tr data-workflow-id="${workflow.id}" class="${isSelected ? 'selected' : ''}">
                <td class="checkbox-column">
                    <input type="checkbox"
                           class="workflow-checkbox"
                           data-workflow-id="${workflow.id}"
                           ${isSelected ? 'checked' : ''}
                           onchange="app.toggleWorkflowSelection('${workflow.id}', this.checked)">
                </td>
                <td><code>${workflow.id ?? '-'}</code></td>
                <td>${this.escapeHtml(workflow.name || 'Unnamed')}</td>
                <td>${this.formatTimestamp(workflow.timestamp)}</td>
                <td>${this.escapeHtml(workflow.user || '-')}</td>
                <td title="${this.escapeHtml(workflow.description || '')}">${this.escapeHtml(this.truncate(workflow.description || '-', 40))}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-success" onclick="app.runWorkflow('${workflow.id}')" title="Run Locally">Run</button>
                        <button class="btn btn-sm btn-primary" onclick="app.submitWorkflow('${workflow.id}')" title="Submit to Scheduler">Submit</button>
                        <button class="btn btn-sm btn-warning" onclick="app.recoverWorkflow('${workflow.id}')" title="Recover Failed Jobs">Recover</button>
                        <button class="btn btn-sm btn-secondary" onclick="app.viewWorkflow('${workflow.id}')" title="View Details">View</button>
                        <button class="btn btn-sm btn-secondary" onclick="app.viewDAG('${workflow.id}')" title="View DAG">DAG</button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteWorkflow('${workflow.id}')" title="Delete">Del</button>
                    </div>
                </td>
            </tr>
        `;
        }).join('');

        this.updateSelectAllCheckbox();
        this.updateBulkActionBar();
    },

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
    },

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
    },

    async viewWorkflow(workflowId) {
        this.selectedWorkflowId = workflowId;
        document.getElementById('workflow-selector').value = workflowId;
        this.switchTab('details');
        await this.loadWorkflowDetails(workflowId);
    },

    async viewDAG(workflowId) {
        this.selectedWorkflowId = workflowId;
        document.getElementById('dag-workflow-selector').value = workflowId;
        this.switchTab('dag');
        dagVisualizer.initialize();
        await dagVisualizer.loadJobDependencies(workflowId);
    },

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
    },

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
    },

    async recoverWorkflow(workflowId) {
        // First run dry-run to show what would be done
        this.showExecutionPanel();
        this.appendExecutionOutput(`Analyzing workflow ${workflowId} for recovery...\n`, 'info');
        this.hideExecutionCancelButton();

        try {
            const response = await fetch('/api/cli/recover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    workflow_id: workflowId.toString(),
                    dry_run: true
                })
            });

            const result = await response.json();

            if (!result.success) {
                this.appendExecutionOutput(`\nError: ${result.error || 'Recovery check failed'}\n`, 'error');
                this.showToast('Recovery check failed', 'error');
                return;
            }

            // Display dry-run results
            const data = result.data;
            if (!data || !data.result) {
                this.appendExecutionOutput(`\nNo recovery data available.\n`, 'error');
                return;
            }

            const r = data.result;
            this.appendExecutionOutput(`\n[DRY RUN] Recovery Analysis for Workflow ${workflowId}\n`, 'info');
            this.appendExecutionOutput(`${'─'.repeat(50)}\n`, 'info');

            if (r.jobs_to_retry && r.jobs_to_retry.length > 0) {
                this.appendExecutionOutput(`\nJobs to retry: ${r.jobs_to_retry.length}\n`, 'stdout');

                if (r.oom_fixed > 0) {
                    this.appendExecutionOutput(`  • ${r.oom_fixed} job(s) would have memory increased\n`, 'stdout');
                }
                if (r.timeout_fixed > 0) {
                    this.appendExecutionOutput(`  • ${r.timeout_fixed} job(s) would have runtime increased\n`, 'stdout');
                }
                if (r.unknown_retried > 0) {
                    this.appendExecutionOutput(`  • ${r.unknown_retried} job(s) with unknown failures would be reset\n`, 'stdout');
                }

                // Show detailed adjustments if available
                if (r.adjustments && r.adjustments.length > 0) {
                    this.appendExecutionOutput(`\nResource Adjustments:\n`, 'info');
                    for (const adj of r.adjustments) {
                        const jobNames = adj.job_names.slice(0, 3).join(', ');
                        const moreJobs = adj.job_names.length > 3 ? ` (+${adj.job_names.length - 3} more)` : '';
                        this.appendExecutionOutput(`  RR #${adj.resource_requirements_id}: ${jobNames}${moreJobs}\n`, 'stdout');
                        if (adj.memory_adjusted) {
                            this.appendExecutionOutput(`    Memory: ${adj.original_memory} → ${adj.new_memory}\n`, 'stdout');
                        }
                        if (adj.runtime_adjusted) {
                            this.appendExecutionOutput(`    Runtime: ${adj.original_runtime} → ${adj.new_runtime}\n`, 'stdout');
                        }
                    }
                }

                this.appendExecutionOutput(`\n${'─'.repeat(50)}\n`, 'info');
                this.appendExecutionOutput(`Would reset ${r.jobs_to_retry.length} job(s) and regenerate Slurm schedulers.\n`, 'info');

                // Show confirm/cancel buttons
                this.appendExecutionOutput(`\n`, 'stdout');
                this.showRecoverConfirmButtons(workflowId);
            } else {
                if (r.other_failures > 0) {
                    this.appendExecutionOutput(`\n${r.other_failures} job(s) failed with unknown causes.\n`, 'stderr');
                    this.appendExecutionOutput(`Use --retry-unknown flag to retry these jobs.\n`, 'info');
                } else {
                    this.appendExecutionOutput(`\nNo recoverable jobs found.\n`, 'info');
                }
            }

        } catch (error) {
            this.appendExecutionOutput(`\nError: ${error.message}\n`, 'error');
            this.showToast('Recovery check failed', 'error');
        }
    },

    showRecoverConfirmButtons(workflowId) {
        const output = document.getElementById('execution-output');
        if (!output) return;

        // Create button container
        const btnContainer = document.createElement('div');
        btnContainer.className = 'recover-confirm-buttons';
        btnContainer.style.cssText = 'margin-top: 10px; display: flex; gap: 10px;';

        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'btn btn-success';
        confirmBtn.textContent = 'Apply Recovery';
        confirmBtn.onclick = () => this.executeRecovery(workflowId, btnContainer);

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn btn-secondary';
        cancelBtn.textContent = 'Cancel';
        cancelBtn.onclick = () => {
            this.appendExecutionOutput('\nRecovery cancelled.\n', 'info');
            btnContainer.remove();
        };

        btnContainer.appendChild(confirmBtn);
        btnContainer.appendChild(cancelBtn);
        output.appendChild(btnContainer);
    },

    async executeRecovery(workflowId, btnContainer) {
        // Remove the confirm buttons
        if (btnContainer) btnContainer.remove();

        this.appendExecutionOutput(`\nApplying recovery to workflow ${workflowId}...\n`, 'info');

        try {
            const response = await fetch('/api/cli/recover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    workflow_id: workflowId.toString(),
                    dry_run: false
                })
            });

            const result = await response.json();

            if (!result.success) {
                this.appendExecutionOutput(`\nError: ${result.error || 'Recovery failed'}\n`, 'error');
                this.showToast('Recovery failed', 'error');
                return;
            }

            const data = result.data;
            const r = data.result;

            this.appendExecutionOutput(`\n✓ Recovery complete!\n`, 'success');
            if (r.oom_fixed > 0) {
                this.appendExecutionOutput(`  • ${r.oom_fixed} job(s) had memory increased\n`, 'success');
            }
            if (r.timeout_fixed > 0) {
                this.appendExecutionOutput(`  • ${r.timeout_fixed} job(s) had runtime increased\n`, 'success');
            }
            if (r.unknown_retried > 0) {
                this.appendExecutionOutput(`  • ${r.unknown_retried} job(s) with unknown failures reset\n`, 'success');
            }
            if (r.jobs_to_retry && r.jobs_to_retry.length > 0) {
                this.appendExecutionOutput(`  • Reset ${r.jobs_to_retry.length} job(s). Slurm schedulers regenerated and submitted.\n`, 'success');
            }

            this.showToast('Recovery complete', 'success');

            // Refresh workflow data
            this.loadWorkflows();
            this.loadWorkflowDetails(workflowId);

        } catch (error) {
            this.appendExecutionOutput(`\nError: ${error.message}\n`, 'error');
            this.showToast('Recovery failed', 'error');
        }
    },

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
    },

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
    },

    hideExecutionCancelButton() {
        const cancelBtn = document.getElementById('btn-cancel-execution');
        if (cancelBtn) cancelBtn.style.display = 'none';
    },

    appendExecutionOutput(text, type = 'stdout') {
        const output = document.getElementById('execution-output');
        if (!output) return;

        const span = document.createElement('span');
        span.textContent = text;
        span.className = `output-${type}`;
        output.appendChild(span);

        // Auto-scroll to bottom
        output.scrollTop = output.scrollHeight;
    },

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
    },

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
    },

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
    },

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
    },

    // ==================== Multi-Select and Bulk Operations ====================

    toggleWorkflowSelection(workflowId, isSelected) {
        if (isSelected) {
            this.selectedWorkflowIds.add(workflowId);
        } else {
            this.selectedWorkflowIds.delete(workflowId);
        }

        // Update row styling
        const row = document.querySelector(`tr[data-workflow-id="${workflowId}"]`);
        if (row) {
            row.classList.toggle('selected', isSelected);
        }

        this.updateSelectAllCheckbox();
        this.updateBulkActionBar();
    },

    toggleSelectAllWorkflows(selectAll) {
        const checkboxes = document.querySelectorAll('.workflow-checkbox');

        if (selectAll) {
            // Select all currently visible workflows
            checkboxes.forEach(cb => {
                const workflowId = cb.dataset.workflowId;
                this.selectedWorkflowIds.add(workflowId);
                cb.checked = true;
                cb.closest('tr')?.classList.add('selected');
            });
        } else {
            // Deselect all
            this.selectedWorkflowIds.clear();
            checkboxes.forEach(cb => {
                cb.checked = false;
                cb.closest('tr')?.classList.remove('selected');
            });
        }

        this.updateBulkActionBar();
    },

    clearWorkflowSelection() {
        this.selectedWorkflowIds.clear();
        document.querySelectorAll('.workflow-checkbox').forEach(cb => {
            cb.checked = false;
            cb.closest('tr')?.classList.remove('selected');
        });
        const selectAll = document.getElementById('workflows-select-all');
        if (selectAll) selectAll.checked = false;
        this.updateBulkActionBar();
    },

    updateSelectAllCheckbox() {
        const selectAll = document.getElementById('workflows-select-all');
        const checkboxes = document.querySelectorAll('.workflow-checkbox');
        if (!selectAll || checkboxes.length === 0) return;

        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        const someChecked = Array.from(checkboxes).some(cb => cb.checked);

        selectAll.checked = allChecked;
        selectAll.indeterminate = someChecked && !allChecked;
    },

    updateBulkActionBar() {
        const bar = document.getElementById('workflows-bulk-actions');
        const countSpan = document.getElementById('workflows-selection-count');
        const count = this.selectedWorkflowIds.size;

        if (bar) {
            bar.style.display = count > 0 ? 'flex' : 'none';
        }
        if (countSpan) {
            countSpan.textContent = count;
        }
    },

    async bulkDeleteWorkflows() {
        const count = this.selectedWorkflowIds.size;
        if (count === 0) return;

        const plural = count === 1 ? 'workflow' : 'workflows';
        if (!confirm(`Delete ${count} ${plural}? This action cannot be undone.`)) {
            return;
        }

        const idsToDelete = Array.from(this.selectedWorkflowIds);
        let successCount = 0;
        let errorCount = 0;

        this.showToast(`Deleting ${count} ${plural}...`, 'info');

        // Delete in parallel with a reasonable concurrency limit
        const results = await Promise.allSettled(
            idsToDelete.map(id => api.cliDeleteWorkflow(id))
        );

        results.forEach((result, index) => {
            if (result.status === 'fulfilled' && result.value.success) {
                successCount++;
                this.selectedWorkflowIds.delete(idsToDelete[index]);
            } else {
                errorCount++;
                console.error(`Failed to delete workflow ${idsToDelete[index]}:`, result);
            }
        });

        if (successCount > 0) {
            this.showToast(`Deleted ${successCount} ${successCount === 1 ? 'workflow' : 'workflows'}`, 'success');
        }
        if (errorCount > 0) {
            this.showToast(`Failed to delete ${errorCount} ${errorCount === 1 ? 'workflow' : 'workflows'}`, 'error');
        }

        await this.loadWorkflows();
    },
});
