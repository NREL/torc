const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const {GRAPH_NAME} = require('./defs');
const EDGE_NAMES = [
  'blocks',
  'consumes',
  'executed',
  'needs',
  'node_used',
  'process_used',
  'produces',
  'requires',
  'returned',
  'scheduled_bys',
  'stores',
];
const VERTEX_NAMES = [
  'aws_schedulers',
  'compute_nodes',
  'compute_node_stats',
  'files',
  'job_process_stats',
  'jobs',
  'local_schedulers',
  'resource_requirements',
  'results',
  'slurm_schedulers',
  'user_data',
];

const DOCUMENT_COLLECTION_NAMES = [
  'events',
  'scheduled_compute_nodes',
];

/**
 * Create the collections specific to one workflow.
 * @param {Object} workflow
 */
function createWorkflowCollections(workflow) {
  const graphName = getWorkflowGraphName(workflow);

  const names = {
    // vertexes
    awsSchedulers: getWorkflowCollectionName(workflow, 'aws_schedulers'),
    computeNodes: getWorkflowCollectionName(workflow, 'compute_nodes'),
    computeNodeStats: getWorkflowCollectionName(workflow, 'compute_node_stats'),
    files: getWorkflowCollectionName(workflow, 'files'),
    jobProcessStats: getWorkflowCollectionName(workflow, 'job_process_stats'),
    jobs: getWorkflowCollectionName(workflow, 'jobs'),
    localSchedulers: getWorkflowCollectionName(workflow, 'local_schedulers'),
    resourceRequirements: getWorkflowCollectionName(workflow, 'resource_requirements'),
    results: getWorkflowCollectionName(workflow, 'results'),
    slurmSchedulers: getWorkflowCollectionName(workflow, 'slurm_schedulers'),
    userData: getWorkflowCollectionName(workflow, 'user_data'),
    // edges between vertexes
    blocks: getWorkflowCollectionName(workflow, 'blocks'),
    consumes: getWorkflowCollectionName(workflow, 'consumes'),
    executed: getWorkflowCollectionName(workflow, 'executed'),
    needs: getWorkflowCollectionName(workflow, 'needs'),
    produces: getWorkflowCollectionName(workflow, 'produces'),
    requires: getWorkflowCollectionName(workflow, 'requires'),
    returned: getWorkflowCollectionName(workflow, 'returned'),
    scheduledBys: getWorkflowCollectionName(workflow, 'scheduled_bys'),
    stores: getWorkflowCollectionName(workflow, 'stores'),
    nodeUsed: getWorkflowCollectionName(workflow, 'node_used'),
    processUsed: getWorkflowCollectionName(workflow, 'process_used'),
  };
  const blocks = graphModule._relation(names.blocks, names.jobs, names.jobs);
  // Note that there could be multiple edges between the same compute node and job vertexes.
  // It would only happen if a user restarted a workflow while holding on to the same nodes.
  const executed = graphModule._relation(names.executed, names.computeNodes, names.jobs);
  const needs = graphModule._relation(names.needs, names.jobs, names.files);
  const produces = graphModule._relation(names.produces, names.jobs, names.files);
  const requires = graphModule._relation(names.requires, names.jobs, names.resourceRequirements);
  const returned = graphModule._relation(names.returned, names.jobs, names.results);
  const scheduledBys = graphModule._relation(names.scheduledBys, names.jobs,
      [names.localSchedulers, names.awsSchedulers, names.slurmSchedulers]);
  const consumes = graphModule._relation(names.consumes, names.jobs, names.userData);
  const stores = graphModule._relation(names.stores, names.jobs, names.userData);
  const nodeUsed = graphModule._relation(
      names.nodeUsed,
      names.computeNodes,
      names.computeNodeStats,
  );
  const processUsed = graphModule._relation(names.processUsed, names.jobs, names.jobProcessStats);

  const actual = Object.keys(names).length;
  const expected = EDGE_NAMES.length + VERTEX_NAMES.length;
  if (actual != expected) {
    throw new Error(`Inconsistent collection counts: actual = ${actual} expected = ${expected}`);
  }

  graphModule._create(
      graphName,
      [
        blocks,
        consumes,
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

  for (const name of DOCUMENT_COLLECTION_NAMES) {
    db._createDocumentCollection(getWorkflowCollectionName(workflow, name));
  }
}

/**
 * Create the workflow-specific name for a collection.
 * @param {object} workflow
 * @param {string} baseName
 * @return {string}
 */
function getWorkflowCollectionName(workflow, baseName) {
  return `${baseName}__${workflow._key}`;
}

/**
 * Return the database collection for the workflow.
 * @param {object} workflow
 * @param {string} baseName
 * @return {Object}
 */
function getWorkflowCollection(workflow, baseName) {
  const collection = db._collection(getWorkflowCollectionName(workflow, baseName));
  if (collection == null) {
    throw new Error(`Failed to find collection for workflow ${workflow._key} ${baseName}`);
  }
  return collection;
}

/**
 *
 * @param {Object} workflow
 * @return {Object}
 */
function getWorkflowGraph(workflow) {
  return graphModule._graph(getWorkflowGraphName(workflow));
}

/**
 *
 * @param {Object} workflow
 * @return {string}
 */
function getWorkflowGraphName(workflow) {
  return getWorkflowCollectionName(workflow, GRAPH_NAME);
}

module.exports = {
  DOCUMENT_COLLECTION_NAMES,
  EDGE_NAMES,
  GRAPH_NAME,
  VERTEX_NAMES,
  createWorkflowCollections,
  getWorkflowCollection,
  getWorkflowCollectionName,
  getWorkflowGraph,
  getWorkflowGraphName,
};
