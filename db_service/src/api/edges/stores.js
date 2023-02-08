const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const {GRAPH_NAME, MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(GRAPH_NAME);
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/stores', function(req, res) {
  const data = req.body;
  const meta = graph.stores.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'stores relationship between a job and a user data object.')
    .response(schemas.edge, 'Edge')
    .summary('Store a stores edge between a job and a user data object.')
    .description('Store a job-user-data relationship in the "stores" edge collection.');

router.get('/stores/:key', function(req, res) {
  try {
    const data = graph.stores.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The stores edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the stores edge.')
    .response(schemas.edge, 'stores edge stored in the collection.')
    .summary('Retrieve a stores edge')
    .description('Retrieves a stores edge from the "stores" collection by key.');

router.get('/stores', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.stores.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.stores.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchEdges)
    .summary('Retrieve all stores edges')
    .description('Retrieves all stores edges from the "stores" collection.');

router.delete('/stores/:key', function(req, res) {
  try {
    const data = graph.stores.document(req.pathParams.key);
    db._remove(`stores/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The stores edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the stores edge.')
    .body(joi.object().optional())
    .response(schemas.edge, 'stores edge stored in the collection.')
    .summary('Delete a stores edge')
    .description('Deletes a stores edge from the "stores" collection by key.');

router.delete('/stores', function(req, res) {
  try {
    db._truncate(`stores`);
    res.send({message: 'Deleted all edges in the "stores" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all stores edges')
    .description('Deletes all edges from the "stores" collection.');
