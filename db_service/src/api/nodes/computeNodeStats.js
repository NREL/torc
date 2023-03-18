'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/compute_node_stats', function(req, res) {
  const doc = req.body;
  const meta = db.compute_node_stats.save(doc);
  Object.assign(doc, meta);
  res.send(doc);
})
    .body(schemas.computeNodeStats, 'compute node stats')
    .response(schemas.computeNodeStats, 'compute node stats')
    .summary('Store utilization stats for a compute node.')
    .description('Store utilization stats for a compute node.');

router.get('/compute_node_stats', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = db.compute_node_stats.all().skip(qp.skip).limit(limit);
    res.send(makeCursorResult(items, qp.skip, limit, db.compute_node_stats.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchComputeNodeStats)
    .summary('Retrieve all compute nodes')
    .description('Retrieves all compute nodes from the "compute_node_stats" collection.');

router.get('/compute_node_stats/:key', function(req, res) {
  try {
    const key = req.pathParams.key;
    const doc = graph.compute_node_stats.document(key);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the compute node object')
    .response(schemas.computeNodeStats)
    .summary('Retrieve the compute node for a key.')
    .description('Retrieve the compute node for a key.');

router.delete('/compute_node_stats/:key', function(req, res) {
  try {
    const cursor = graph.compute_node_stats.document(req.pathParams.key);
    db._remove(`compute_node_stats/${req.pathParams.key}`);
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
    .response(schemas.computeNodeStats, 'Compute node stored in the collection.')
    .summary('Delete a compute node')
    .description('Deletes a compute node from the "compute_node_stats" collection by key.');

router.delete('/compute_node_stats', function(req, res) {
  try {
    db._truncate(`compute_node_stats`);
    res.send({message: 'Deleted all documents in the "compute_node_stats" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all compute node stats')
    .description('Deletes all compute node stats from the "compute_node_stats" collection.');
