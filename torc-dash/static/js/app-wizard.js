/**
 * Torc Dashboard - Workflow Wizard
 * Multi-step wizard for creating workflows, including scheduler and action management
 */

Object.assign(TorcDashboard.prototype, {
    // ==================== Workflow Wizard ====================

    setupWizard() {
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
        this.wizardParallelizationStrategy = 'resource_aware';

        this.resourcePresets = {
            'small': { name: 'Small', num_cpus: 1, memory: '1g', num_gpus: 0 },
            'medium': { name: 'Medium', num_cpus: 4, memory: '10g', num_gpus: 0 },
            'large': { name: 'Large', num_cpus: 8, memory: '50g', num_gpus: 0 },
            'gpu': { name: 'GPU', num_cpus: 1, memory: '10g', num_gpus: 1 },
            'custom': { name: 'Custom', num_cpus: 1, memory: '1g', num_gpus: 0 }
        };

        document.getElementById('wizard-parallelization-strategy')?.addEventListener('change', (e) => {
            this.wizardParallelizationStrategy = e.target.value;
            this.wizardRenderJobs();
            this.wizardRenderActions();
        });

        document.getElementById('wizard-prev')?.addEventListener('click', () => this.wizardPrevStep());
        document.getElementById('wizard-next')?.addEventListener('click', () => this.wizardNextStep());
        document.getElementById('wizard-add-job')?.addEventListener('click', () => this.wizardAddJob());
        document.getElementById('wizard-add-scheduler')?.addEventListener('click', () => this.wizardAddScheduler());
        document.getElementById('wizard-add-action')?.addEventListener('click', () => this.wizardAddAction());

        document.getElementById('wizard-monitoring-enabled')?.addEventListener('change', (e) => {
            this.wizardResourceMonitor.enabled = e.target.checked;
            const optionsDiv = document.getElementById('wizard-monitoring-options');
            if (optionsDiv) optionsDiv.style.display = e.target.checked ? 'block' : 'none';
        });

        document.getElementById('wizard-monitoring-granularity')?.addEventListener('change', (e) => {
            this.wizardResourceMonitor.granularity = e.target.value;
        });

        document.getElementById('wizard-monitoring-interval')?.addEventListener('change', (e) => {
            const value = parseInt(e.target.value);
            if (value >= 1 && value <= 300) {
                this.wizardResourceMonitor.sample_interval_seconds = value;
            }
        });
    },

    resetWizard() {
        this.wizardStep = 1;
        this.wizardJobs = [];
        this.wizardJobIdCounter = 0;
        this.wizardSchedulers = [];
        this.wizardSchedulerIdCounter = 0;
        this.wizardActions = [];
        this.wizardActionIdCounter = 0;
        this.wizardResourceMonitor = { enabled: true, granularity: 'summary', sample_interval_seconds: 5 };
        this.wizardParallelizationStrategy = 'resource_aware';

        const nameInput = document.getElementById('wizard-name');
        const descInput = document.getElementById('wizard-description');
        if (nameInput) nameInput.value = '';
        if (descInput) descInput.value = '';

        const strategySelect = document.getElementById('wizard-parallelization-strategy');
        if (strategySelect) strategySelect.value = 'resource_aware';

        const monitoringEnabled = document.getElementById('wizard-monitoring-enabled');
        const monitoringGranularity = document.getElementById('wizard-monitoring-granularity');
        const monitoringInterval = document.getElementById('wizard-monitoring-interval');
        const monitoringOptions = document.getElementById('wizard-monitoring-options');
        if (monitoringEnabled) monitoringEnabled.checked = true;
        if (monitoringGranularity) monitoringGranularity.value = 'summary';
        if (monitoringInterval) monitoringInterval.value = '5';
        if (monitoringOptions) monitoringOptions.style.display = 'block';

        document.querySelectorAll('.wizard-step').forEach((step, i) => {
            step.classList.toggle('active', i === 0);
            step.classList.remove('completed');
        });

        document.querySelectorAll('.wizard-content').forEach((content, i) => {
            content.classList.toggle('active', i === 0);
        });

        document.getElementById('wizard-prev').disabled = true;
        document.getElementById('wizard-next').textContent = 'Next';
        document.getElementById('wizard-jobs-list').innerHTML = '';
        document.getElementById('wizard-schedulers-list').innerHTML = '';
        document.getElementById('wizard-actions-list').innerHTML = '';
    },

    wizardGoToStep(step) {
        this.wizardStep = step;
        document.querySelectorAll('.wizard-step').forEach((el, i) => {
            el.classList.toggle('active', i === step - 1);
            el.classList.toggle('completed', i < step - 1);
        });
        document.querySelectorAll('.wizard-content').forEach((content, i) => {
            content.classList.toggle('active', i === step - 1);
        });

        if (step === 2) this.wizardRenderJobs();
        else if (step === 3) this.wizardRenderSchedulers();
        else if (step === 4) this.wizardRenderActions();

        document.getElementById('wizard-prev').disabled = step === 1;
        const nextBtn = document.getElementById('wizard-next');
        if (step === this.wizardTotalSteps) {
            nextBtn.textContent = 'Create Workflow';
            this.wizardGeneratePreview();
        } else {
            nextBtn.textContent = 'Next';
        }
    },

    wizardPrevStep() {
        if (this.wizardStep > 1) this.wizardGoToStep(this.wizardStep - 1);
    },

    wizardNextStep() {
        if (this.wizardStep === 1) {
            const name = document.getElementById('wizard-name')?.value?.trim();
            if (!name) { this.showToast('Please enter a workflow name', 'warning'); return; }
        } else if (this.wizardStep === 2) {
            if (this.wizardJobs.length === 0) { this.showToast('Please add at least one job', 'warning'); return; }
            for (const job of this.wizardJobs) {
                if (!job.name?.trim()) { this.showToast('All jobs must have a name', 'warning'); return; }
                if (!job.command?.trim()) { this.showToast('All jobs must have a command', 'warning'); return; }
            }
        } else if (this.wizardStep === 3) {
            for (const scheduler of this.wizardSchedulers) {
                if (!scheduler.name?.trim()) { this.showToast('All schedulers must have a name', 'warning'); return; }
                if (!scheduler.account?.trim()) { this.showToast('All schedulers must have an account', 'warning'); return; }
            }
        } else if (this.wizardStep === 4) {
            for (const action of this.wizardActions) {
                if (!action.scheduler?.trim()) { this.showToast('All actions must have a scheduler selected', 'warning'); return; }
                if ((action.trigger_type === 'on_jobs_ready' || action.trigger_type === 'on_jobs_complete') && (!action.jobs || action.jobs.length === 0)) {
                    this.showToast('Actions triggered by job events must have at least one job selected', 'warning'); return;
                }
            }
        } else if (this.wizardStep === this.wizardTotalSteps) {
            this.wizardCreateWorkflow();
            return;
        }
        if (this.wizardStep < this.wizardTotalSteps) this.wizardGoToStep(this.wizardStep + 1);
    },

    wizardAddJob() {
        const jobId = ++this.wizardJobIdCounter;
        const job = {
            id: jobId, name: '', command: '', depends_on: [], resource_preset: 'small',
            num_cpus: 1, memory: '1g', num_gpus: 0, runtime: 'PT1H', parameters: '', parameter_mode: 'product', scheduler: ''
        };
        this.wizardJobs.push(job);
        this.wizardRenderJobs();
        setTimeout(() => {
            const card = document.querySelector(`[data-job-id="${jobId}"]`);
            if (card) { card.classList.add('expanded'); card.querySelector('input[name="job-name"]')?.focus(); }
        }, 50);
    },

    wizardRemoveJob(jobId) {
        this.wizardJobs = this.wizardJobs.filter(j => j.id !== jobId);
        this.wizardJobs.forEach(job => { job.depends_on = job.depends_on.filter(id => id !== jobId); });
        this.wizardRenderJobs();
    },

    wizardToggleJob(jobId) {
        const card = document.querySelector(`[data-job-id="${jobId}"]`);
        if (card) card.classList.toggle('expanded');
    },

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
            this.wizardRenderJobs();
        } else if (field === 'depends_on') {
            job.depends_on = value;
        } else {
            job[field] = value;
            if (['num_cpus', 'memory', 'num_gpus'].includes(field)) {
                job.resource_preset = 'custom';
                const card = document.querySelector(`[data-job-id="${jobId}"]`);
                if (card) {
                    card.querySelectorAll('.resource-preset-btn').forEach(btn => {
                        btn.classList.toggle('selected', btn.dataset.preset === 'custom');
                    });
                }
            }
        }

        if (field === 'name') {
            const card = document.querySelector(`[data-job-id="${jobId}"]`);
            if (card) {
                const titleSpan = card.querySelector('.job-title');
                if (titleSpan) titleSpan.textContent = value || 'Untitled Job';
            }
        }

        if (field === 'parameters') {
            const card = document.querySelector(`[data-job-id="${jobId}"]`);
            if (card) {
                const paramModeSelect = card.querySelector('select[onchange*="parameter_mode"]');
                if (paramModeSelect) paramModeSelect.disabled = !value?.trim();
            }
        }
    },

    wizardRenderJobs() {
        const container = document.getElementById('wizard-jobs-list');
        if (!container) return;

        const expandedJobIds = [];
        container.querySelectorAll('.wizard-job-card.expanded').forEach(card => {
            const jobId = parseInt(card.dataset.jobId);
            if (!isNaN(jobId)) expandedJobIds.push(jobId);
        });

        if (this.wizardJobs.length === 0) {
            container.innerHTML = `<div class="wizard-empty-state"><p>No jobs yet</p><p>Click "+ Add Job" to create your first job</p></div>`;
            return;
        }

        const showResources = this.wizardParallelizationStrategy === 'resource_aware';

        container.innerHTML = this.wizardJobs.map((job, index) => {
            const otherJobs = this.wizardJobs.filter(j => j.id !== job.id);
            const isExpanded = expandedJobIds.includes(job.id);

            return `
                <div class="wizard-job-card${isExpanded ? ' expanded' : ''}" data-job-id="${job.id}">
                    <div class="wizard-job-header" onclick="app.wizardToggleJob(${job.id})">
                        <h5><span class="job-index">${index + 1}</span><span class="job-title">${this.escapeHtml(job.name) || 'Untitled Job'}</span></h5>
                        <div class="wizard-job-actions"><button type="button" class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.wizardRemoveJob(${job.id})">Remove</button></div>
                    </div>
                    <div class="wizard-job-body">
                        <div class="wizard-job-row">
                            <div class="form-group">
                                <label>Job Name *</label>
                                <input type="text" name="job-name" class="text-input" value="${this.escapeHtml(job.name)}" placeholder="e.g., process-data" onchange="app.wizardUpdateJob(${job.id}, 'name', this.value)">
                            </div>
                            <div class="form-group">
                                <label>Depends On</label>
                                <select class="select-input" multiple size="2" onchange="app.wizardUpdateJob(${job.id}, 'depends_on', Array.from(this.selectedOptions).map(o => parseInt(o.value)))">
                                    ${otherJobs.map(j => `<option value="${j.id}" ${job.depends_on.includes(j.id) ? 'selected' : ''}>${this.escapeHtml(j.name) || 'Untitled Job'}</option>`).join('')}
                                </select>
                                <small>Hold Ctrl/Cmd to select multiple</small>
                            </div>
                        </div>
                        <div class="wizard-job-row full">
                            <div class="form-group">
                                <label>Command *</label>
                                <input type="text" class="text-input" value="${this.escapeHtml(job.command)}" placeholder="e.g., python process.py --input data.csv" onchange="app.wizardUpdateJob(${job.id}, 'command', this.value)">
                            </div>
                        </div>
                        <div class="wizard-job-row" style="grid-template-columns: 2fr 1fr;">
                            <div class="form-group">
                                <label>Parameters (for job expansion)</label>
                                <input type="text" class="text-input" value="${this.escapeHtml(job.parameters)}" placeholder="e.g., i: 1:10 or x: [1,2,3], y: [a,b,c]" onchange="app.wizardUpdateJob(${job.id}, 'parameters', this.value)">
                                <small>Creates multiple jobs. Use {param} in name/command.</small>
                            </div>
                            <div class="form-group">
                                <label>Parameter Mode</label>
                                <select class="select-input" ${!job.parameters?.trim() ? 'disabled' : ''} onchange="app.wizardUpdateJob(${job.id}, 'parameter_mode', this.value)">
                                    <option value="product" ${job.parameter_mode !== 'zip' ? 'selected' : ''}>Product</option>
                                    <option value="zip" ${job.parameter_mode === 'zip' ? 'selected' : ''}>Zip</option>
                                </select>
                            </div>
                        </div>
                        <div class="wizard-job-row">
                            <div class="form-group">
                                <label>Scheduler</label>
                                <div class="scheduler-select-row">
                                    <select class="select-input" onchange="app.wizardUpdateJob(${job.id}, 'scheduler', this.value)">
                                        <option value="" ${!job.scheduler ? 'selected' : ''}>Auto</option>
                                        ${this.wizardGetSchedulerNames().map(name => `<option value="${this.escapeHtml(name)}" ${job.scheduler === name ? 'selected' : ''}>${this.escapeHtml(name)}</option>`).join('')}
                                    </select>
                                    <button type="button" class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); app.wizardAddSchedulerFromJob(${job.id})" title="Add a new Slurm scheduler">+ New</button>
                                </div>
                            </div>
                            <div class="form-group"></div>
                        </div>
                        ${showResources ? this.wizardRenderJobResources(job) : ''}
                    </div>
                </div>
            `;
        }).join('');
    },

    wizardRenderJobResources(job) {
        return `
            <div class="form-group">
                <label>Resources</label>
                <div class="resource-presets">
                    ${Object.entries(this.resourcePresets).map(([key, preset]) => `
                        <button type="button" class="resource-preset-btn ${job.resource_preset === key ? 'selected' : ''}" data-preset="${key}" onclick="app.wizardUpdateJob(${job.id}, 'resource_preset', '${key}')">
                            ${preset.name}${key !== 'custom' ? `<small>(${preset.num_cpus} CPU, ${preset.memory}${preset.num_gpus ? ', ' + preset.num_gpus + ' GPU' : ''})</small>` : ''}
                        </button>
                    `).join('')}
                </div>
            </div>
            ${job.resource_preset === 'custom' ? `
                <div class="wizard-job-row">
                    <div class="form-group"><label>CPUs</label><input type="number" class="text-input" min="1" value="${job.num_cpus}" onchange="app.wizardUpdateJob(${job.id}, 'num_cpus', parseInt(this.value))"></div>
                    <div class="form-group"><label>Memory</label><input type="text" class="text-input" value="${this.escapeHtml(job.memory)}" placeholder="e.g., 4g" onchange="app.wizardUpdateJob(${job.id}, 'memory', this.value)"></div>
                </div>
                <div class="wizard-job-row">
                    <div class="form-group"><label>GPUs</label><input type="number" class="text-input" min="0" value="${job.num_gpus}" onchange="app.wizardUpdateJob(${job.id}, 'num_gpus', parseInt(this.value))"></div>
                    <div class="form-group"><label>Runtime</label><input type="text" class="text-input" value="${this.escapeHtml(job.runtime)}" placeholder="PT1H" onchange="app.wizardUpdateJob(${job.id}, 'runtime', this.value)"><small>ISO8601 duration</small></div>
                </div>
            ` : ''}
        `;
    },

    wizardJobNameToRegex(jobName) {
        let pattern = jobName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        pattern = pattern.replace(/\\\{[^}]+\\\}/g, '.*');
        return `^${pattern}$`;
    },

    wizardJobIsParameterized(job) {
        return job.parameters?.trim()?.length > 0;
    },

    // ==================== Scheduler Management ====================

    wizardAddScheduler() {
        const schedulerId = ++this.wizardSchedulerIdCounter;
        const scheduler = {
            id: schedulerId, name: '', account: '', nodes: 1, walltime: '01:00:00',
            partition: '', qos: '', gres: '', mem: '', tmp: '', extra: ''
        };
        this.wizardSchedulers.push(scheduler);
        this.wizardRenderSchedulers();
        setTimeout(() => {
            const card = document.querySelector(`[data-scheduler-id="${schedulerId}"]`);
            if (card) { card.classList.add('expanded'); card.querySelector('input[name="scheduler-name"]')?.focus(); }
        }, 50);
    },

    wizardRemoveScheduler(schedulerId) {
        const scheduler = this.wizardSchedulers.find(s => s.id === schedulerId);
        if (scheduler) {
            this.wizardJobs.forEach(job => { if (job.scheduler === scheduler.name) job.scheduler = ''; });
        }
        this.wizardSchedulers = this.wizardSchedulers.filter(s => s.id !== schedulerId);
        this.wizardRenderSchedulers();
    },

    wizardAddSchedulerFromJob(jobId) {
        const schedulerId = ++this.wizardSchedulerIdCounter;
        const defaultName = `scheduler-${schedulerId}`;
        const schedulerName = prompt('Enter a name for the new scheduler:', defaultName);
        if (!schedulerName || !schedulerName.trim()) {
            // User cancelled or entered only whitespace
            this.wizardSchedulerIdCounter--;
            return;
        }
        const scheduler = {
            id: schedulerId, name: schedulerName.trim(), account: '', nodes: 1, walltime: '01:00:00',
            partition: '', qos: '', gres: '', mem: '', tmp: '', extra: ''
        };
        this.wizardSchedulers.push(scheduler);
        const job = this.wizardJobs.find(j => j.id === jobId);
        if (job) job.scheduler = schedulerName.trim();
        this.wizardRenderJobs();
        this.showToast(`Scheduler "${schedulerName.trim()}" created. Configure it in step 3.`, 'info');
    },

    wizardToggleScheduler(schedulerId) {
        const card = document.querySelector(`[data-scheduler-id="${schedulerId}"]`);
        if (card) card.classList.toggle('expanded');
    },

    wizardUpdateScheduler(schedulerId, field, value) {
        const scheduler = this.wizardSchedulers.find(s => s.id === schedulerId);
        if (!scheduler) return;

        if (field === 'name' && scheduler.name) {
            const oldName = scheduler.name;
            this.wizardJobs.forEach(job => { if (job.scheduler === oldName) job.scheduler = value; });
        }
        scheduler[field] = value;

        if (field === 'name') {
            const card = document.querySelector(`[data-scheduler-id="${schedulerId}"]`);
            if (card) {
                const titleSpan = card.querySelector('.scheduler-title');
                if (titleSpan) titleSpan.textContent = value || 'Untitled Scheduler';
            }
        }
    },

    wizardRenderSchedulers() {
        const container = document.getElementById('wizard-schedulers-list');
        if (!container) return;

        const expandedSchedulerIds = [];
        container.querySelectorAll('.wizard-scheduler-card.expanded').forEach(card => {
            const schedulerId = parseInt(card.dataset.schedulerId);
            if (!isNaN(schedulerId)) expandedSchedulerIds.push(schedulerId);
        });

        if (this.wizardSchedulers.length === 0) {
            container.innerHTML = `<div class="wizard-empty-state"><p>No schedulers defined</p><p>Click "+ Add Scheduler" to define a Slurm scheduler.</p><p class="wizard-help-text">Schedulers are optional.</p></div>`;
            return;
        }

        container.innerHTML = this.wizardSchedulers.map((scheduler, index) => {
            const isExpanded = expandedSchedulerIds.includes(scheduler.id);
            return `
                <div class="wizard-scheduler-card${isExpanded ? ' expanded' : ''}" data-scheduler-id="${scheduler.id}">
                    <div class="wizard-scheduler-header" onclick="app.wizardToggleScheduler(${scheduler.id})">
                        <h5><span class="scheduler-index">${index + 1}</span><span class="scheduler-title">${this.escapeHtml(scheduler.name) || 'Untitled Scheduler'}</span></h5>
                        <div class="wizard-scheduler-actions"><button type="button" class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.wizardRemoveScheduler(${scheduler.id})">Remove</button></div>
                    </div>
                    <div class="wizard-scheduler-body">
                        <div class="wizard-scheduler-row">
                            <div class="form-group"><label>Scheduler Name *</label><input type="text" name="scheduler-name" class="text-input" value="${this.escapeHtml(scheduler.name)}" placeholder="e.g., compute_scheduler" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'name', this.value)"></div>
                            <div class="form-group"><label>Account *</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.account)}" placeholder="e.g., my_project" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'account', this.value)"></div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group"><label>Nodes</label><input type="number" class="text-input" min="1" value="${scheduler.nodes}" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'nodes', parseInt(this.value) || 1)"></div>
                            <div class="form-group"><label>Wall Time</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.walltime)}" placeholder="HH:MM:SS" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'walltime', this.value)"></div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group"><label>Partition</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.partition)}" placeholder="e.g., compute" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'partition', this.value)"></div>
                            <div class="form-group"><label>QoS</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.qos)}" placeholder="e.g., normal" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'qos', this.value)"></div>
                        </div>
                        <div class="wizard-scheduler-row">
                            <div class="form-group"><label>GRES</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.gres)}" placeholder="e.g., gpu:2" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'gres', this.value)"></div>
                            <div class="form-group"><label>Memory</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.mem)}" placeholder="e.g., 256G" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'mem', this.value)"></div>
                        </div>
                        <div class="wizard-scheduler-row full">
                            <div class="form-group"><label>Extra Slurm Options</label><input type="text" class="text-input" value="${this.escapeHtml(scheduler.extra)}" placeholder="e.g., --exclusive" onchange="app.wizardUpdateScheduler(${scheduler.id}, 'extra', this.value)"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    wizardGetSchedulerNames() {
        return this.wizardSchedulers.filter(s => s.name?.trim()).map(s => s.name.trim());
    },

    wizardGetJobNames() {
        return this.wizardJobs.filter(j => j.name?.trim()).map(j => j.name.trim());
    },

    // ==================== Action Management ====================

    wizardAddAction() {
        const actionId = ++this.wizardActionIdCounter;
        const action = {
            id: actionId, trigger_type: 'on_workflow_start', scheduler: '', jobs: [],
            num_allocations: 1, max_parallel_jobs: 10, start_one_worker_per_node: false
        };
        this.wizardActions.push(action);
        this.wizardRenderActions();
        setTimeout(() => {
            const card = document.querySelector(`[data-action-id="${actionId}"]`);
            if (card) card.classList.add('expanded');
        }, 50);
    },

    wizardRemoveAction(actionId) {
        this.wizardActions = this.wizardActions.filter(a => a.id !== actionId);
        this.wizardRenderActions();
    },

    wizardToggleAction(actionId) {
        const card = document.querySelector(`[data-action-id="${actionId}"]`);
        if (card) card.classList.toggle('expanded');
    },

    wizardUpdateAction(actionId, field, value) {
        const action = this.wizardActions.find(a => a.id === actionId);
        if (!action) return;
        action[field] = value;
        if (field === 'trigger_type') {
            if (value === 'on_workflow_start') action.jobs = [];
            this.wizardRenderActions();
        }
    },

    wizardGetTriggerTypeLabel(triggerType) {
        const labels = {
            'on_workflow_start': 'When workflow starts',
            'on_jobs_ready': 'When jobs become ready',
            'on_jobs_complete': 'When jobs complete'
        };
        return labels[triggerType] || triggerType;
    },

    wizardRenderActions() {
        const container = document.getElementById('wizard-actions-list');
        if (!container) return;

        const schedulerNames = this.wizardGetSchedulerNames();
        const jobNames = this.wizardGetJobNames();

        if (this.wizardActions.length === 0) {
            container.innerHTML = `<div class="wizard-empty-state"><p>No actions defined</p><p>Click "+ Add Action" to automatically schedule nodes.</p><p class="wizard-help-text">Actions are optional.</p></div>`;
            return;
        }

        if (schedulerNames.length === 0) {
            container.innerHTML = `<div class="wizard-empty-state"><p>No schedulers available</p><p>Define at least one scheduler in step 3.</p></div>`;
            return;
        }

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
                        <h5><span class="action-index">${index + 1}</span><span class="action-title">${this.wizardGetTriggerTypeLabel(action.trigger_type)}</span>${action.scheduler ? `<span class="action-scheduler-badge">${this.escapeHtml(action.scheduler)}</span>` : ''}</h5>
                        <div class="wizard-action-actions"><button type="button" class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.wizardRemoveAction(${action.id})">Remove</button></div>
                    </div>
                    <div class="wizard-action-body">
                        <div class="wizard-action-row">
                            <div class="form-group">
                                <label>Trigger *</label>
                                <select class="select-input" onchange="app.wizardUpdateAction(${action.id}, 'trigger_type', this.value)">
                                    <option value="on_workflow_start" ${action.trigger_type === 'on_workflow_start' ? 'selected' : ''}>When workflow starts</option>
                                    <option value="on_jobs_ready" ${action.trigger_type === 'on_jobs_ready' ? 'selected' : ''}>When jobs become ready</option>
                                    <option value="on_jobs_complete" ${action.trigger_type === 'on_jobs_complete' ? 'selected' : ''}>When jobs complete</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Scheduler *</label>
                                <select class="select-input" onchange="app.wizardUpdateAction(${action.id}, 'scheduler', this.value)">
                                    <option value="">Select scheduler...</option>
                                    ${schedulerNames.map(name => `<option value="${this.escapeHtml(name)}" ${action.scheduler === name ? 'selected' : ''}>${this.escapeHtml(name)}</option>`).join('')}
                                </select>
                            </div>
                        </div>
                        ${showJobSelector ? `
                            <div class="wizard-action-row full">
                                <div class="form-group">
                                    <label>Jobs *</label>
                                    <select class="select-input" multiple size="4" onchange="app.wizardUpdateAction(${action.id}, 'jobs', Array.from(this.selectedOptions).map(o => o.value))">
                                        ${jobNames.map(name => `<option value="${this.escapeHtml(name)}" ${action.jobs?.includes(name) ? 'selected' : ''}>${this.escapeHtml(name)}</option>`).join('')}
                                    </select>
                                </div>
                            </div>
                        ` : ''}
                        <div class="wizard-action-row">
                            <div class="form-group">
                                <label>Number of Allocations</label>
                                <input type="number" class="text-input" min="1" value="${action.num_allocations || 1}" onchange="app.wizardUpdateAction(${action.id}, 'num_allocations', parseInt(this.value) || 1)">
                            </div>
                            ${this.wizardParallelizationStrategy === 'queue_depth' ? `
                                <div class="form-group">
                                    <label>Max Parallel Jobs</label>
                                    <input type="number" class="text-input" min="1" value="${action.max_parallel_jobs || 10}" onchange="app.wizardUpdateAction(${action.id}, 'max_parallel_jobs', parseInt(this.value) || 10)">
                                </div>
                            ` : '<div class="form-group"></div>'}
                        </div>
                        <div class="wizard-action-row">
                            <div class="form-group checkbox-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" ${action.start_one_worker_per_node ? 'checked' : ''} onchange="app.wizardUpdateAction(${action.id}, 'start_one_worker_per_node', this.checked)">
                                    <span>Start one worker per node</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    wizardGenerateSpec() {
        const name = document.getElementById('wizard-name')?.value?.trim() || 'untitled-workflow';
        const description = document.getElementById('wizard-description')?.value?.trim();
        const useResourceAware = this.wizardParallelizationStrategy === 'resource_aware';

        const jobInfoMap = {};
        this.wizardJobs.forEach(job => {
            const jobName = job.name?.trim() || `job_${job.id}`;
            jobInfoMap[job.id] = { name: jobName, isParameterized: this.wizardJobIsParameterized(job), regex: this.wizardJobNameToRegex(jobName) };
        });

        const resourceReqs = {};
        if (useResourceAware) {
            this.wizardJobs.forEach(job => {
                const runtime = job.runtime || 'PT1H';
                const key = `${job.num_cpus}_${job.memory}_${job.num_gpus}_${runtime}`;
                if (!resourceReqs[key]) {
                    resourceReqs[key] = {
                        name: `res_${job.num_cpus}cpu_${job.memory}${job.num_gpus > 0 ? '_' + job.num_gpus + 'gpu' : ''}_${runtime}`,
                        num_cpus: job.num_cpus, memory: job.memory, num_gpus: job.num_gpus, num_nodes: 1, runtime: runtime
                    };
                }
            });
        }

        const jobs = this.wizardJobs.map(job => {
            const runtime = job.runtime || 'PT1H';
            const resKey = `${job.num_cpus}_${job.memory}_${job.num_gpus}_${runtime}`;
            const jobSpec = { name: job.name?.trim() || `job_${job.id}`, command: job.command?.trim() || 'echo "TODO"' };

            if (job.depends_on.length > 0) {
                const regularDeps = [], regexDeps = [];
                job.depends_on.forEach(depId => {
                    const depInfo = jobInfoMap[depId];
                    if (depInfo.isParameterized) regexDeps.push(depInfo.regex);
                    else regularDeps.push(depInfo.name);
                });
                if (regularDeps.length > 0) jobSpec.depends_on = regularDeps;
                if (regexDeps.length > 0) jobSpec.depends_on_regexes = regexDeps;
            }

            if (useResourceAware) jobSpec.resource_requirements = resourceReqs[resKey].name;
            if (job.scheduler?.trim()) jobSpec.scheduler = job.scheduler.trim();

            if (job.parameters?.trim()) {
                try {
                    const paramStr = job.parameters.trim();
                    const params = {};
                    let i = 0;
                    while (i < paramStr.length) {
                        while (i < paramStr.length && (paramStr[i] === ' ' || paramStr[i] === ',')) i++;
                        if (i >= paramStr.length) break;
                        let keyStart = i;
                        while (i < paramStr.length && /\w/.test(paramStr[i])) i++;
                        const key = paramStr.slice(keyStart, i).trim();
                        if (!key) break;
                        while (i < paramStr.length && (paramStr[i] === ' ' || paramStr[i] === ':')) i++;
                        let value = '';
                        if (paramStr[i] === '"' || paramStr[i] === "'") {
                            const quote = paramStr[i]; i++;
                            let valueStart = i;
                            while (i < paramStr.length && paramStr[i] !== quote) i++;
                            value = paramStr.slice(valueStart, i); i++;
                        } else if (paramStr[i] === '[') {
                            let valueStart = i, depth = 0;
                            while (i < paramStr.length) {
                                if (paramStr[i] === '[') depth++;
                                else if (paramStr[i] === ']') { depth--; if (depth === 0) { i++; break; } }
                                i++;
                            }
                            value = paramStr.slice(valueStart, i);
                        } else {
                            let valueStart = i;
                            while (i < paramStr.length && paramStr[i] !== ',') i++;
                            value = paramStr.slice(valueStart, i).trim();
                        }
                        if (key && value) params[key] = value;
                    }
                    if (Object.keys(params).length > 0) {
                        jobSpec.parameters = params;
                        if (job.parameter_mode === 'zip') jobSpec.parameter_mode = 'zip';
                    }
                } catch (e) { console.warn('Failed to parse parameters:', e); }
            }
            return jobSpec;
        });

        const slurmSchedulers = this.wizardSchedulers.filter(s => s.name?.trim() && s.account?.trim()).map(s => {
            const schedulerSpec = { name: s.name.trim(), account: s.account.trim(), nodes: s.nodes || 1, walltime: s.walltime?.trim() || '01:00:00' };
            if (s.partition?.trim()) schedulerSpec.partition = s.partition.trim();
            if (s.qos?.trim()) schedulerSpec.qos = s.qos.trim();
            if (s.gres?.trim()) schedulerSpec.gres = s.gres.trim();
            if (s.mem?.trim()) schedulerSpec.mem = s.mem.trim();
            if (s.tmp?.trim()) schedulerSpec.tmp = s.tmp.trim();
            if (s.extra?.trim()) schedulerSpec.extra = s.extra.trim();
            return schedulerSpec;
        });

        const actions = this.wizardActions.filter(a => a.scheduler?.trim()).map(a => {
            const actionSpec = {
                trigger_type: a.trigger_type, action_type: 'schedule_nodes', scheduler: a.scheduler.trim(),
                scheduler_type: 'slurm', num_allocations: a.num_allocations || 1
            };
            if ((a.trigger_type === 'on_jobs_ready' || a.trigger_type === 'on_jobs_complete') && a.jobs && a.jobs.length > 0) {
                actionSpec.jobs = a.jobs;
            }
            if (!useResourceAware && a.max_parallel_jobs) actionSpec.max_parallel_jobs = a.max_parallel_jobs;
            if (a.start_one_worker_per_node) actionSpec.start_one_worker_per_node = true;
            return actionSpec;
        });

        const spec = { name, jobs };
        if (useResourceAware && Object.keys(resourceReqs).length > 0) spec.resource_requirements = Object.values(resourceReqs);
        if (description) spec.description = description;
        spec.resource_monitor = this.wizardResourceMonitor.enabled
            ? { enabled: true, granularity: this.wizardResourceMonitor.granularity, sample_interval_seconds: this.wizardResourceMonitor.sample_interval_seconds }
            : { enabled: false };
        if (slurmSchedulers.length > 0) spec.slurm_schedulers = slurmSchedulers;
        if (actions.length > 0) spec.actions = actions;

        return spec;
    },

    wizardGeneratePreview() {
        const spec = this.wizardGenerateSpec();
        const preview = document.getElementById('wizard-preview');
        if (preview) preview.textContent = JSON.stringify(spec, null, 2);
    },

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

                const shouldInit = document.getElementById('create-option-initialize')?.checked;
                const shouldRun = document.getElementById('create-option-run')?.checked;
                const idMatch = result.stdout?.match(/workflow[_\s]?id[:\s]+([a-zA-Z0-9-]+)/i);
                if (idMatch) {
                    const workflowId = idMatch[1];
                    if (shouldInit) await this.initializeWorkflow(workflowId);
                    if (shouldRun) await this.runWorkflow(workflowId);
                }
            } else {
                this.showToast('Error: ' + (result.stderr || result.stdout || 'Unknown error'), 'error');
            }
        } catch (error) {
            this.showToast('Error creating workflow: ' + error.message, 'error');
        }
    },
});
