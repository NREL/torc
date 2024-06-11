'use strict';
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const graphName = 'workflow_graph';

for (const name of [
  'workflows',
  'workflow_configs',
  'workflow_statuses',
]
) {
  if (!db._collection(name)) {
    db._createDocumentCollection(name);
  }
}

if (!graphModule._list().includes(graphName)) {
  const config = graphModule._relation('has_workflow_config', 'workflows', 'workflow_configs');
  const status = graphModule._relation('has_workflow_status', 'workflows', 'workflow_statuses');
  graphModule._create(
      graphName,
      [
        config,
        status,
      ],
  );
}

// This can be removed when all databases have been upgraded.
const workflows = db._collection('workflows');
for (const doc of workflows.all()) {
  if (doc.is_archived == null) {
    doc.is_archived = false;
    workflows.update(doc, doc);
  }
}
