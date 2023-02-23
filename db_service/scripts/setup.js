'use strict';
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const graphName = 'workflow_graph';

for (const name of ['events']) {
  if (!db._collection(name)) {
    db._createDocumentCollection(name);
    console.log(`Created document collection ${name}`);
  }
}

if (!db._collection('workflow_status')) {
  db._createDocumentCollection('workflow_status');
  db.workflow_status.save({is_canceled: false, run_id: 0, scheduled_compute_node_ids: []});
  console.log(`Created document collection workflow_status`);
}

if (!graphModule._list().includes(graphName)) {
  const blocks = graphModule._relation('blocks', 'jobs', 'jobs');
  const executed = graphModule._relation('executed', 'compute_nodes', 'jobs');
  const needs = graphModule._relation('needs', 'jobs', 'files');
  const produces = graphModule._relation('produces', 'jobs', 'files');
  const requires = graphModule._relation('requires', 'jobs', 'resource_requirements');
  const returned = graphModule._relation('returned', 'jobs', 'results');
  const scheduledBys = graphModule._relation('scheduled_bys', 'jobs', 'hpc_configs');
  const stores = graphModule._relation('stores', 'jobs', 'user_data');
  const nodeUsed = graphModule._relation('node_used', 'compute_nodes', 'compute_node_stats');
  const processUsed = graphModule._relation('process_used', 'job', 'job_process_stats');
  graphModule._create(
      graphName,
      [
        blocks,
        executed,
        needs,
        produces,
        requires,
        returned,
        scheduledBys,
        stores,
        nodeUsed,
        processUsed,
      ],
  );
  console.log(`Created graph ${graphName}`);
}
