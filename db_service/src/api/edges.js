'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const {MAX_TRANSFER_RECORDS} = require('../defs');
const config = require('../config');
const documents = require('../documents');
const utils = require('../utils');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/edges/:workflow/:name', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const name = req.pathParams.name;
  const workflow = documents.getWorkflow(workflowKey, res);
  const edgeCollection = config.getWorkflowCollection(workflow, name);
  const data = req.body;
  try {
    const meta = edgeCollection.save(data);
    res.send(Object.assign(data, meta));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Post ${name} edge`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('name', joi.string().required(), 'Edge name')
    .body(schemas.edge, 'Relationship between two vertexes')
    .response(schemas.edge, 'Edge')
    .summary('Store an edge between two vertexes.')
    .description('Store an edge between two vertexes in the designated collection.');

router.get('/edges/:workflow/:name/:key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const name = req.pathParams.name;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const edgeCollection = config.getWorkflowCollection(workflow, name);
  try {
    const data = edgeCollection.document(key);
    res.send(data);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get ${name} edge key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .pathParam('key', joi.string().required(), 'Edge key')
    .response(schemas.edge, 'Edge stored in the collection.')
    .summary('Retrieve an edge')
    .description('Retrieves an edge from the designated collection by key.');

router.get('/edges/:workflow/:name', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const name = req.pathParams.name;
  const workflow = documents.getWorkflow(workflowKey, res);
  const edgeCollection = config.getWorkflowCollection(workflow, name);
  const qp = req.queryParams;
  const limit = utils.getItemsLimit(qp.limit);
  try {
    const items = edgeCollection.all().skip(qp.skip).limit(limit).toArray();
    res.send(utils.makeCursorResult(items, qp.skip, limit, edgeCollection.count()));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get all ${name} edges`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchEdges)
    .summary('Retrieve all edges from the designated collection.')
    .description('Retrieve all edges from the designated collection.');

router.delete('/edges/:workflow/:name/:key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const name = req.pathParams.name;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const collection = config.getWorkflowCollection(workflow, name);
  try {
    const doc = collection.document(key);
    db._remove(doc._id);
    res.send(doc);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Delete ${name} edge key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('name', joi.string().required(), 'Edge name.')
    .pathParam('key', joi.string().required(), 'Edge key.')
    .body(joi.object().optional())
    .response(schemas.edge, 'Edge stored in the collection.')
    .summary('Delete an edge')
    .description('Deletes an edge from the designated collection by key.');

router.delete('/edges/:workflow/:name', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const name = req.pathParams.name;
  const workflow = documents.getWorkflow(workflowKey, res);
  const edgeCollectionName = config.getWorkflowCollectionName(workflow, name);
  try {
    db._truncate(edgeCollectionName);
    res.send({message: `Deleted all edges in the "${edgeCollectionName}" collection`});
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Delete all ${name} edges`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all edges from the designated collection')
    .description('Deletes all edges from the designated collection.');
