const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(defs.GRAPH_NAME);
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/executed', function(req, res) {
  const data = req.body;
  const meta = graph.executed.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'Executed relationship between a compute node and a job.')
    .response(schemas.edge, 'Edge')
    .summary('Store an executed edge between a compute node and a job.')
    .description('Store a compute_node-job relationship in the "executed" edge collection.');

router.get('/executed/:key', function(req, res) {
  try {
    const data = graph.executed.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The executed edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the executed edge.')
    .response(schemas.edge, 'Edge stored in the collection.')
    .summary('Retrieve an executed edge')
    .description('Retrieves an executed edge from the "executed" collection by key.');

router.get('/executed', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.executed.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.executed.count()));
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
    .summary('Retrieve all executed edges')
    .description('Retrieves all executed edges from the "executed" collection.');

router.delete('/executed/:key', function(req, res) {
  try {
    const data = graph.executed.document(req.pathParams.key);
    db._remove(`executed/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The executed edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the executed edge.')
    .body(joi.object().optional())
    .response(schemas.edge, 'Executed edge stored in the collection.')
    .summary('Delete an executed edge')
    .description('Deletes an executed edge from the "executed" collection by key.');

router.delete('/executed', function(req, res) {
  try {
    db._truncate(`executed`);
    res.send({message: 'Deleted all edges in the "executed" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all executed edges')
    .description('Deletes all edges from the "executed" collection.');
