/**
 * Torc Dashboard - DAG Tab
 * DAG visualization controls
 */

Object.assign(TorcDashboard.prototype, {
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

        document.getElementById('btn-dag-back')?.addEventListener('click', () => {
            this.goBackFromDAG();
        });
    },

    updateDAGBackButton() {
        const backBtn = document.getElementById('btn-dag-back');
        if (backBtn) {
            // Show back button only when in DAG tab and there's a previous tab to go back to
            backBtn.style.display = (this.currentTab === 'dag' && this.previousTab) ? 'inline-block' : 'none';
        }
    },

    goBackFromDAG() {
        if (this.previousTab) {
            this.switchTab(this.previousTab, true);  // skipHistory=true to avoid infinite back loop
            this.previousTab = null;
        } else {
            // Default to details if no previous tab
            this.switchTab('details', true);
        }
    },

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
    },
});
