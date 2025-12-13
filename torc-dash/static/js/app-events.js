/**
 * Torc Dashboard - Events Tab
 * Event streaming and display
 */

Object.assign(TorcDashboard.prototype, {
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

        container.innerHTML = this.events.map(event => `
            <div class="event-item">
                <span class="event-time">${this.formatDate(event.timestamp)}</span>
                <span class="event-type">${this.escapeHtml(event.event_type || '-')}</span>
                <span class="event-message">${this.escapeHtml(event.message || '-')}</span>
            </div>
        `).join('');
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
