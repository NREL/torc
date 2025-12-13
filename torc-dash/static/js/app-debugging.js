/**
 * Torc Dashboard - Debugging Tab
 * Debug reports and log viewing
 */

Object.assign(TorcDashboard.prototype, {
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
    },

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
    },

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
    },

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
    },

    switchLogTab(logtab) {
        this.currentLogTab = logtab;

        document.querySelectorAll('.sub-tab[data-logtab]').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.logtab === logtab);
        });

        this.loadLogContent();
    },

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
    },
});
