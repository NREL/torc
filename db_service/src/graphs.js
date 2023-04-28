'use strict';
const config = require('./config');

/**
 * Make a string representing a DOT graph.
 * @param {Object} workflow
 * @param {string} graphName
 * @return {string}
 */
function makeDotGraph(workflow, graphName) {
  const graph = makeGraph(workflow, graphName);
  const lines = [
    `strict digraph "${graphName}" {`,
    'node [label="\\N"];',
  ];
  for (const node of graph.nodes) {
    lines.push(`"${node.id}" [label=${node.label}];`);
  }
  for (const edge of graph.edges) {
    lines.push(`"${edge.from}" -> "${edge.to}" [label=${edge.label}];`);
  }
  lines.push('labelloc="t";');
  lines.push(`label="${graph.title}";`);
  lines.push('}');
  return lines.join('\n');
}

/**
 * Make a graph from the workflow.
 * @param {Object} workflow
 * @param {string} graphName
 * @return {Object}
 */
function makeGraph(workflow, graphName) {
  const graph = {title: '', nodes: [], edges: []};
  if (graphName == 'job_job_dependencies') {
    makeJobBlocksGraph(graph, workflow);
  } else if (graphName == 'job_file_dependencies') {
    makeJobFilesGraph(graph, workflow);
  } else if (graphName == 'job_user_data_dependencies') {
    makeJobUserDataGraph(graph, workflow);
  } else {
    throw new Error(`graph name ${graphName} is not supported`);
  }
  return graph;
}

/**
 * Fill out a graph object for a job sequence graph based on blocks edges.
 * @param {Object} graph
 * @param {Object} workflow
 * @param {Object} jobFilters
 */
function makeJobBlocksGraph(graph, workflow, jobFilters) {
  graph.title = 'Job - Job Dependencies';
  addNodesToGraph(graph, workflow, 'jobs', jobFilters);
  const jobIds = new Set();
  let useSubset = false;
  if (jobFilters != null) {
    useSubset = true;
    for (const node of graph.nodes) {
      jobIds.add(node.id);
    }
  }
  addEdgesToGraph(graph, workflow, 'blocks', jobIds, useSubset);
}

/**
 * Fill out a graph object for a job-file dependency graph based on produces/needs edges.
 * @param {Object} graph
 * @param {Object} workflow
 * @param {Object} jobFilters
 */
function makeJobFilesGraph(graph, workflow, jobFilters) {
  graph.title = 'Job - File Dependencies';
  addNodesToGraph(graph, workflow, 'jobs', jobFilters, null);
  const jobIds = new Set();
  let useSubset = false;
  if (jobFilters != null) {
    useSubset = true;
    for (const node of graph.nodes) {
      jobIds.add(node.id);
    }
  }
  addEdgesToGraph(graph, workflow, 'produces', jobIds, useSubset);
  addEdgesToGraph(graph, workflow, 'needs', jobIds, useSubset);
  const fileIds = new Set();
  for (const edge of graph.edges) {
    fileIds.add(edge.to);
  }
  addNodesToGraph(graph, workflow, 'files', null, fileIds);
}

/**
 * Fill out a graph object for a job-user_data dependency graph based on stores/consumes edges.
 * @param {Object} graph
 * @param {Object} workflow
 * @param {Object} jobFilters
 */
function makeJobUserDataGraph(graph, workflow, jobFilters) {
  graph.title = 'Job - User Data Dependencies';
  const jobIds = addNodesToGraph(graph, workflow, 'jobs', jobFilters, null);
  addEdgesToGraph(graph, workflow, 'stores', jobIds);
  addEdgesToGraph(graph, workflow, 'consumes', jobIds);
  const udIds = new Set();
  for (const edge of graph.edges) {
    udIds.add(edge.to);
  }
  addNodesToGraph(graph, workflow, 'user_data', jobFilters, udIds);
}

/**
 * Add nodes to the graph.
 * @param {Object} graph
 * @param {Object} workflow
 * @param {string} collectionBasename
 * @param {Object} filters
 * @param {Set} ids
 */
function addNodesToGraph(graph, workflow, collectionBasename, filters, ids) {
  const collection = config.getWorkflowCollection(workflow, collectionBasename);
  const documents = filters == null ? collection.all() : collection.byExample(filters);
  for (const doc of documents) {
    if (ids == null || ids.has(doc._id)) {
      graph.nodes.push({id: doc._id, label: doc.name == null ? doc._key : doc.name});
    }
  }
}

/**
 * Add edges to the graph.
 * @param {Object} graph
 * @param {Object} workflow
 * @param {string} collectionBasename
 * @param {Set} fromSubset
 * @param {Boolean} useSubset
 */
function addEdgesToGraph(graph, workflow, collectionBasename, fromSubset, useSubset) {
  const collection = config.getWorkflowCollection(workflow, collectionBasename);
  for (const edge of collection.all()) {
    if (!useSubset || fromSubset.has(edge._from)) {
      graph.edges.push({from: edge._from, to: edge._to, label: collectionBasename});
    }
  }
}

module.exports = {
  makeDotGraph,
  makeGraph,
};
