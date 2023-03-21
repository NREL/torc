'use strict';
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const graphName = 'workflow_graph';

for (const name of [
  'aws_schedulers',
  'events',
  'local_schedulers',
  'scheduled_compute_nodes',
  'slurm_schedulers',
  'workflow_config',
  'workflow_status',
]
) {
  if (!db._collection(name)) {
    db._createDocumentCollection(name);
    console.log(`Created document collection ${name}`);
  }
}

if (!graphModule._list().includes(graphName)) {
  const blocks = graphModule._relation('blocks', 'jobs', 'jobs');
  const executed = graphModule._relation('executed', 'compute_nodes', 'jobs');
  const needs = graphModule._relation('needs', 'jobs', 'files');
  const produces = graphModule._relation('produces', 'jobs', 'files');
  const requires = graphModule._relation('requires', 'jobs', 'resource_requirements');
  const returned = graphModule._relation('returned', 'jobs', 'results');
  const scheduledBys = graphModule._relation('scheduled_bys', 'jobs',
      ['local_schedulers', 'aws_schedulers', 'slurm_schedulers']);
  const stores = graphModule._relation('stores', 'jobs', 'user_data');
  const nodeUsed = graphModule._relation('node_used', 'compute_nodes', 'compute_node_stats');
  const processUsed = graphModule._relation('process_used', 'jobs', 'job_process_stats');
  graphModule._create(
      graphName,
      [
        blocks,
        executed,
        needs,
        nodeUsed,
        processUsed,
        produces,
        requires,
        returned,
        scheduledBys,
        stores,
      ],
  );
  console.log(`Created graph ${graphName}`);
}
