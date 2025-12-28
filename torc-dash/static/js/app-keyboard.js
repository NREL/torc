/**
 * Torc Dashboard - Keyboard Shortcuts
 * Global keyboard shortcuts for navigation and common actions
 */

Object.assign(TorcDashboard.prototype, {
    setupKeyboardShortcuts() {
        // Use capture phase to intercept Alt+D before browser handles it
        document.addEventListener('keydown', (e) => {
            // Alt/Option + d to cycle through themes - needs capture to beat browser's Alt+D
            if (e.altKey && (e.code === 'KeyD' || e.key === 'd' || e.key === '∂')) {
                e.preventDefault();
                e.stopPropagation();
                this.cycleTheme();
                return;
            }
        }, true); // capture phase

        // Make the keyboard hint clickable
        document.getElementById('keyboard-hint')?.addEventListener('click', () => {
            this.showKeyboardShortcutsHelp();
        });

        document.addEventListener('keydown', (e) => {

            // Ignore shortcuts when typing in input fields
            if (this.isTypingInInput(e.target)) {
                // Allow Escape to blur inputs
                if (e.key === 'Escape') {
                    e.target.blur();
                }
                return;
            }

            // Handle modal-specific shortcuts
            if (this.isModalOpen()) {
                if (e.key === 'Escape') {
                    this.closeAllModals();
                    return;
                }

                // Handle create workflow modal navigation
                const createModal = document.getElementById('create-workflow-modal');
                if (createModal && (createModal.style.display === 'flex' || createModal.classList.contains('active'))) {
                    this.handleCreateModalKeyboard(e);
                }
                return;
            }

            // Global shortcuts
            switch (e.key) {
                // Tab navigation (1-6)
                case '1':
                    this.switchTab('workflows');
                    break;
                case '2':
                    this.switchTab('details');
                    break;
                case '3':
                    this.switchTab('events');
                    break;
                case '4':
                    this.switchTab('debugging');
                    break;
                case '5':
                    this.switchTab('resource-plots');
                    break;
                case '6':
                    this.switchTab('config');
                    break;

                // Refresh current view
                case 'r':
                    if (!e.ctrlKey && !e.metaKey) {
                        e.preventDefault();
                        this.refreshCurrentView();
                    }
                    break;

                // Create new workflow (on workflows tab)
                case 'n':
                    if (this.currentTab === 'workflows') {
                        e.preventDefault();
                        this.showModal('create-workflow-modal');
                    }
                    break;

                // Go to DAG view
                case 'g':
                    if (this.selectedWorkflowId) {
                        e.preventDefault();
                        this.switchTab('dag');
                    }
                    break;

                // Focus filter/search input
                case '/':
                    e.preventDefault();
                    this.focusCurrentFilter();
                    break;

                // Show help
                case '?':
                    e.preventDefault();
                    this.showKeyboardShortcutsHelp();
                    break;

                // Back (like browser back within the app)
                case 'Backspace':
                    if (this.previousTab && this.currentTab === 'dag') {
                        e.preventDefault();
                        this.switchTab(this.previousTab, true);
                    }
                    break;

            }
        });
    },

    isTypingInInput(target) {
        const tagName = target.tagName.toLowerCase();
        return (
            tagName === 'input' ||
            tagName === 'textarea' ||
            tagName === 'select' ||
            target.isContentEditable
        );
    },

    isModalOpen() {
        const modals = document.querySelectorAll('.modal');
        for (const modal of modals) {
            if (modal.style.display === 'flex' || modal.classList.contains('active')) {
                return true;
            }
        }
        return false;
    },

    closeAllModals() {
        // Close all modals by removing 'active' class and setting display to none
        const modalIds = [
            'create-workflow-modal',
            'execution-plan-modal',
            'init-confirm-modal',
            'reinit-confirm-modal',
            'recover-modal',
            'file-viewer-modal',
            'job-details-modal',
            'keyboard-help-modal'
        ];

        modalIds.forEach(id => {
            const modal = document.getElementById(id);
            if (modal) {
                modal.classList.remove('active');
                modal.style.display = 'none';
            }
        });
    },

    refreshCurrentView() {
        switch (this.currentTab) {
            case 'workflows':
                this.loadWorkflows();
                this.showToast('Workflows refreshed', 'success');
                break;
            case 'details':
                if (this.selectedWorkflowId) {
                    this.loadWorkflowDetails(this.selectedWorkflowId);
                    this.showToast('Details refreshed', 'success');
                }
                break;
            case 'dag':
                if (dagVisualizer && this.selectedWorkflowId) {
                    dagVisualizer.refresh();
                    this.showToast('DAG refreshed', 'success');
                }
                break;
            case 'events':
                if (this.loadEvents) {
                    this.loadEvents();
                    this.showToast('Events refreshed', 'success');
                }
                break;
            default:
                this.showToast('No refresh action for this tab', 'info');
        }
    },

    focusCurrentFilter() {
        let filterInput = null;
        switch (this.currentTab) {
            case 'workflows':
                filterInput = document.getElementById('workflow-filter');
                break;
            case 'details':
                filterInput = document.getElementById('table-filter');
                break;
        }
        if (filterInput) {
            filterInput.focus();
            filterInput.select();
        }
    },

    toggleDarkMode() {
        const checkbox = document.getElementById('dark-mode');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
            // Trigger the change event so theme listeners fire
            checkbox.dispatchEvent(new Event('change'));
            this.saveSettings();
        }
    },

    handleCreateModalKeyboard(e) {
        // Don't intercept when typing in inputs
        if (this.isTypingInInput(e.target)) {
            return;
        }

        const createTabs = ['upload', 'path', 'inline', 'wizard'];
        const currentTabIndex = createTabs.indexOf(this.currentCreateTab);

        // Tab / Shift+Tab to navigate source tabs
        if (e.key === 'Tab' && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            let newIndex;
            if (e.shiftKey) {
                // Shift+Tab: go to previous tab
                newIndex = currentTabIndex <= 0 ? createTabs.length - 1 : currentTabIndex - 1;
            } else {
                // Tab: go to next tab
                newIndex = currentTabIndex >= createTabs.length - 1 ? 0 : currentTabIndex + 1;
            }
            this.switchCreateTab(createTabs[newIndex]);
            this.focusFirstInputInCreatePanel();
            return;
        }

        // Arrow keys for navigation
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            e.preventDefault();
            let newIndex;
            if (e.key === 'ArrowLeft') {
                newIndex = currentTabIndex <= 0 ? createTabs.length - 1 : currentTabIndex - 1;
            } else {
                newIndex = currentTabIndex >= createTabs.length - 1 ? 0 : currentTabIndex + 1;
            }
            this.switchCreateTab(createTabs[newIndex]);
            this.focusFirstInputInCreatePanel();
            return;
        }

        // When on wizard tab, use ArrowUp/ArrowDown or [ ] for wizard steps
        if (this.currentCreateTab === 'wizard') {
            if (e.key === 'ArrowUp' || e.key === '[') {
                e.preventDefault();
                this.wizardPrevStep();
                return;
            }
            if (e.key === 'ArrowDown' || e.key === ']') {
                e.preventDefault();
                this.wizardNextStep();
                return;
            }
        }

        // Number keys 1-4 to jump directly to source tabs
        if (e.key >= '1' && e.key <= '4') {
            e.preventDefault();
            const tabIndex = parseInt(e.key) - 1;
            if (tabIndex < createTabs.length) {
                this.switchCreateTab(createTabs[tabIndex]);
                this.focusFirstInputInCreatePanel();
            }
            return;
        }

        // Enter to focus first input in current panel (or submit if on last wizard step)
        if (e.key === 'Enter') {
            e.preventDefault();
            // On wizard last step, submit
            if (this.currentCreateTab === 'wizard' && this.wizardStep === this.wizardTotalSteps) {
                document.getElementById('btn-submit-workflow')?.click();
            } else {
                // Focus first input in current panel
                this.focusFirstInputInCreatePanel();
            }
            return;
        }
    },

    focusFirstInputInCreatePanel() {
        let panel;
        if (this.currentCreateTab === 'wizard') {
            // Focus input in current wizard step
            panel = document.querySelector(`.wizard-content.active`);
        } else {
            panel = document.getElementById(`create-panel-${this.currentCreateTab}`);
        }

        if (panel) {
            const firstInput = panel.querySelector('input:not([type="hidden"]):not([type="file"]), textarea, select');
            if (firstInput) {
                firstInput.focus();
                if (firstInput.select) firstInput.select();
            }
        }
    },

    showKeyboardShortcutsHelp() {
        // Create modal if it doesn't exist
        let modal = document.getElementById('keyboard-help-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'keyboard-help-modal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 500px;">
                    <div class="modal-header">
                        <h3>Keyboard Shortcuts</h3>
                        <button class="modal-close" id="keyboard-help-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="shortcuts-list">
                            <div class="shortcut-section">
                                <h4>Navigation</h4>
                                <div class="shortcut-row"><kbd>1</kbd> Workflows tab</div>
                                <div class="shortcut-row"><kbd>2</kbd> Details tab</div>
                                <div class="shortcut-row"><kbd>3</kbd> Events tab</div>
                                <div class="shortcut-row"><kbd>4</kbd> Debugging tab</div>
                                <div class="shortcut-row"><kbd>5</kbd> Resource Plots tab</div>
                                <div class="shortcut-row"><kbd>6</kbd> Configuration tab</div>
                                <div class="shortcut-row"><kbd>g</kbd> Go to DAG view</div>
                                <div class="shortcut-row"><kbd>Backspace</kbd> Back from DAG</div>
                            </div>
                            <div class="shortcut-section">
                                <h4>Actions</h4>
                                <div class="shortcut-row"><kbd>r</kbd> Refresh current view</div>
                                <div class="shortcut-row"><kbd>n</kbd> New workflow (on Workflows tab)</div>
                                <div class="shortcut-row"><kbd>/</kbd> Focus filter input</div>
                                <div class="shortcut-row"><kbd>Alt</kbd>+<kbd>d</kbd> Cycle color themes</div>
                            </div>
                            <div class="shortcut-section">
                                <h4>Create Workflow Modal</h4>
                                <div class="shortcut-row"><kbd>Tab</kbd> Next source tab + focus input</div>
                                <div class="shortcut-row"><kbd>Shift</kbd>+<kbd>Tab</kbd> Previous source tab</div>
                                <div class="shortcut-row"><kbd>&larr;</kbd> <kbd>&rarr;</kbd> Navigate source tabs</div>
                                <div class="shortcut-row"><kbd>1</kbd>-<kbd>4</kbd> Jump to source tab</div>
                                <div class="shortcut-row"><kbd>Enter</kbd> Focus first input field</div>
                                <div class="shortcut-row"><kbd>&uarr;</kbd> <kbd>&darr;</kbd> Wizard prev/next step</div>
                            </div>
                            <div class="shortcut-section">
                                <h4>General</h4>
                                <div class="shortcut-row"><kbd>?</kbd> Show this help</div>
                                <div class="shortcut-row"><kbd>Esc</kbd> Close modal / blur input</div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" id="btn-close-keyboard-help">Close</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Setup close handlers
            modal.querySelector('#keyboard-help-close').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            modal.querySelector('#btn-close-keyboard-help').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }

        modal.style.display = 'flex';
    }
});
