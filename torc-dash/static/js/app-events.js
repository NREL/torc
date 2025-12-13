/**
 * Torc Dashboard - Events Tab
 * Event streaming and display
 */

Object.assign(TorcDashboard.prototype, {
    // ==================== Events Tab ====================

    setupEventsTab() {
        document.getElementById('events-workflow-selector')?.addEventListener('change', () => {
            this.events = [];
            this.loadEvents();
        });

        document.getElementById('btn-clear-events')?.addEventListener('click', () => {
            this.events = [];
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
    },

    startEventPolling() {
        this.stopEventPolling();
        this.loadEvents();
        this.eventPollInterval = setInterval(() => this.loadEvents(), 10000);
    },

    stopEventPolling() {
        if (this.eventPollInterval) {
            clearInterval(this.eventPollInterval);
            this.eventPollInterval = null;
        }
    },

    async loadEvents() {
        try {
            const workflowId = document.getElementById('events-workflow-selector')?.value;

            // Workflow ID is required for the events API
            if (!workflowId) {
                this.events = [];
                this.renderEvents();
                return;
            }

            // Fetch latest events (replace, don't accumulate to avoid duplicates)
            const events = await api.listEvents(workflowId, 0, 200, null);

            // Check if there are new events since last load
            const previousCount = this.events.length;
            this.events = events || [];

            if (this.events.length > previousCount) {
                this.updateEventBadge(this.events.length - previousCount);
            }

            this.renderEvents();
        } catch (error) {
            console.error('Error loading events:', error);
        }
    },

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

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.events.map(event => `
                        <tr>
                            <td><code>${event.id ?? '-'}</code></td>
                            <td>${this.formatTimestamp(event.timestamp)}</td>
                            <td><code>${this.escapeHtml(this.truncate(JSON.stringify(event.data) || '-', 100))}</code></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },

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
    },
});
