/**
 * Torc Dashboard - Events Tab
 * Event streaming and display
 *
 * Uses after_timestamp to fetch only new events from the server.
 * Timestamp is milliseconds since epoch (integer).
 */

Object.assign(TorcDashboard.prototype, {
    // ==================== Events Tab ====================

    setupEventsTab() {
        this._lastEventsWorkflowId = null;
        this._afterTimestamp = null;  // UNIX timestamp - fetch events after this time

        document.getElementById('events-workflow-selector')?.addEventListener('change', (e) => {
            const newWorkflowId = e.target.value;
            if (newWorkflowId !== this._lastEventsWorkflowId) {
                this._lastEventsWorkflowId = newWorkflowId;
                this._afterTimestamp = Date.now();  // Current time in milliseconds
                this.events = [];
                this.renderEvents();
            }
        });

        document.getElementById('btn-clear-events')?.addEventListener('click', () => {
            // Clear displayed events
            // _afterTimestamp stays the same, so cleared events won't reappear
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

        document.getElementById('events-poll-interval')?.addEventListener('change', (e) => {
            const autoRefresh = document.getElementById('auto-refresh-events');
            if (autoRefresh?.checked) {
                this.startEventPolling();
            }
        });

        const autoRefresh = document.getElementById('auto-refresh-events');
        if (autoRefresh?.checked) {
            this.startEventPolling();
        }
    },

    getEventsPollInterval() {
        const input = document.getElementById('events-poll-interval');
        const seconds = parseInt(input?.value) || 10;
        return Math.max(1, Math.min(300, seconds)) * 1000;
    },

    startEventPolling() {
        this.stopEventPolling();
        // Set timestamp to now (milliseconds) - only show events created after this moment
        this._afterTimestamp = Date.now();
        this.events = [];
        this.renderEvents();
        const interval = this.getEventsPollInterval();
        this.eventPollInterval = setInterval(() => this.pollNewEvents(), interval);
    },

    stopEventPolling() {
        if (this.eventPollInterval) {
            clearInterval(this.eventPollInterval);
            this.eventPollInterval = null;
        }
    },

    async pollNewEvents() {
        try {
            let workflowId = document.getElementById('events-workflow-selector')?.value;

            if (!workflowId && this._lastEventsWorkflowId) {
                workflowId = this._lastEventsWorkflowId;
            }

            if (!workflowId) {
                return;
            }

            this._lastEventsWorkflowId = workflowId;

            // Fetch events after our timestamp
            const events = await api.listEvents(workflowId, 0, 100, this._afterTimestamp);

            if (events && events.length > 0) {
                // Update timestamp to the latest event's timestamp (in milliseconds)
                // Timestamp is now an integer, no conversion needed
                const maxTimestamp = Math.max(...events.map(e => e.timestamp));
                this._afterTimestamp = maxTimestamp;

                // Prepend new events (newest first)
                this.events = [...events, ...this.events];

                this.updateEventBadge(events.length);
                this.renderEvents();
            }
        } catch (error) {
            console.error('Error polling events:', error);
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
            container.innerHTML = '<div class="placeholder-message">Waiting for new events...</div>';
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.events.map(event => `
                        <tr>
                            <td><code>${event.id ?? '-'}</code></td>
                            <td>${this.formatTimestamp(event.timestamp)}</td>
                            <td>${this.escapeHtml(event.data?.message || '')}</td>
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
