'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const {MAX_TRANSFER_RECORDS} = require('../defs');
const {getItemsLimit, makeCursorResult} = require('../utils');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/edges/:name', function(req, res) {
  const edgeCollection = db._collection(req.pathParams.name);
  const data = req.body;
  const meta = edgeCollection.save(data);
  res.send(Object.assign(data, meta));
})
    .pathParam('name', joi.string().required(), 'Edge name')
    .body(schemas.edge, 'Relationship between two vertexes')
    .response(schemas.edge, 'Edge')
    .summary('Store an edge between two vertexes.')
    .description('Store an edge between two vertexes in the designated collection.');

router.get('/edges/:name/:key', function(req, res) {
  try {
    const edgeCollection = db._collection(req.pathParams.name);
    const data = edgeCollection.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The edge does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .pathParam('key', joi.string().required(), 'Edge key')
    .response(schemas.edge, 'Edge stored in the collection.')
    .summary('Retrieve an edge')
    .description('Retrieves an edge from the designated collection by key.');

router.get('/edges/:name', function(req, res) {
  try {
    const edgeCollection = db._collection(req.pathParams.name);
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = edgeCollection.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, edgeCollection.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchEdges)
    .summary('Retrieve all edges from the designated collection.')
    .description('Retrieve all edges from the designated collection.');

router.delete('/edges/:name/:key', function(req, res) {
  try {
    const name = req.pathParams.name;
    const key = req.pathParams.key;
    const edgeCollection = db._collection(name);
    const data = edgeCollection.document(key);
    db._remove(`${name}/${key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The edge does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .pathParam('key', joi.string().required(), 'Edge key.')
    .body(joi.object().optional())
    .response(schemas.edge, 'Edge stored in the collection.')
    .summary('Delete an edge')
    .description('Deletes an edge from the designated collection by key.');

router.delete('/edges/:name', function(req, res) {
  try {
    const name = req.pathParams.name;
    db._truncate(name);
    res.send({message: `Deleted all edges in the "${name}" collection`});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .pathParam('name', joi.string().required(), 'Edge collection name')
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all edges from the designated collection')
    .description('Deletes all edges from the designated collection.');
