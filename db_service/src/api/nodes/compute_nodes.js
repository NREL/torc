'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/compute_nodes', function(req, res) {
  const data = req.body;
  const meta = db.compute_nodes.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.computeNode, 'compute node.')
    .response(schemas.computeNode, 'compute node')
    .summary('Store information about a compute node.')
    .description('Store information about a compute node in the "compute_nodes" collection.');

router.put('/compute_nodes/:key', function(req, res) {
  const doc = req.body;
  if (doc._rev == null) {
    res.throw(400, 'Updating a compute_node requires the existing revision');
  }

  try {
    if (req.pathParams.name != doc.name) {
      throw new Error(`name=${req.pathParams.name} does not match ${doc.name}`);
    }
    const meta = db.compute_nodes.update(doc, doc);
    Object.assign(doc, meta);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The compute node does not exist', e);
  }
})
    .body(joi.object().required(), 'Compute node to update in the collection.')
    .response(schemas.computeNode, 'Compute node updated in the collection.')
    .summary('Update compute node')
    .description('Update a compute node in the "compute_nodes" collection.');

router.get('/compute_nodes', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = db.compute_nodes.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, db.compute_nodes.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchComputeNodes)
    .summary('Retrieve all compute nodes')
    .description('Retrieves all compute nodes from the "compute_nodes" collection.');

router.get('/compute_nodes/:key', function(req, res) {
  try {
    const key = req.pathParams.key;
    const doc = graph.compute_nodes.document(key);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the compute node object')
    .response(schemas.computeNode)
    .summary('Retrieve the compute node for a key.')
    .description('Retrieve the compute node for a key.');

router.delete('/compute_nodes/:key', function(req, res) {
  try {
    const cursor = graph.compute_nodes.document(req.pathParams.key);
    db._remove(`compute_nodes/${req.pathParams.key}`);
    res.send(cursor);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The user data does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the compute node.')
    .body(joi.object().optional())
    .response(schemas.computeNode, 'Compute node stored in the collection.')
    .summary('Delete a compute node')
    .description('Deletes a compute node from the "compute_nodes" collection by key.');

router.delete('/compute_nodes', function(req, res) {
  try {
    db._truncate(`compute_nodes`);
    res.send({message: 'Deleted all documents in the "compute_nodes" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all compute nodes')
    .description('Deletes all compute nodes from the "compute_nodes" collection.');
