#!/bin/bash
# Mock AI agent for testing AI-assisted recovery
# This script simulates what the Claude CLI would do:
# 1. Call list_pending_failed_jobs via the torc CLI
# 2. Classify all jobs as "retry" (transient errors)
# 3. Call classify_and_resolve_failures via the torc CLI

# The prompt is passed as the first argument (we ignore it for testing)
PROMPT="$1"

# Extract workflow_id from the prompt (assumes format "Workflow X has jobs")
WORKFLOW_ID=$(echo "$PROMPT" | grep -oE 'Workflow [0-9]+' | grep -oE '[0-9]+')

if [ -z "$WORKFLOW_ID" ]; then
    echo "ERROR: Could not extract workflow_id from prompt"
    exit 1
fi

echo "Mock AI Agent: Processing workflow $WORKFLOW_ID"
echo "Mock AI Agent: Classifying all pending_failed jobs as 'retry'"

# In a real test, we would call the MCP tools here
# For now, we just exit successfully to indicate the agent ran
echo "Mock AI Agent: Classification complete"
exit 0
