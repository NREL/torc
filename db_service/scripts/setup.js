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

if (!graphModule._list().includes(graphName)) {
  const blocks = graphModule._relation('blocks', 'jobs', 'jobs');
  const needs = graphModule._relation('needs', 'jobs', 'files');
  const produces = graphModule._relation('produces', 'jobs', 'files');
  const requires = graphModule._relation('requires', 'jobs', 'resource_requirements');
  const returned = graphModule._relation('returned', 'jobs', 'results');
  const scheduledBys = graphModule._relation('scheduled_bys', 'jobs', 'hpc_configs');
  const stores = graphModule._relation('stores', 'jobs', 'user_data');
  graphModule._create(
      graphName,
      [
        blocks,
        needs,
        produces,
        requires,
        returned,
        scheduledBys,
        stores,
      ],
  );
  console.log(`Created graph ${graphName}`);
}
