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

router.post('/returned', function(req, res) {
  const data = req.body;
  const meta = graph.returned.save(data);
  Object.assign(data, meta);
  job = graph.jobs.document(data.name);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'returned relationship between a job and a result.')
    .response(schemas.edge, 'Edge')
    .summary('Store a returned edge between a job and a result.')
    .description('Store a job-result relationship in the "returned" edge collection.');

router.get('/returned/:key', function(req, res) {
  try {
    const data = graph.returned.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The returned edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the returned edge.')
    .response(schemas.edge, 'edge stored in the collection.')
    .summary('Retrieve a returned edge')
    .description('Retrieves an edge from the "returned" collection by key.');

router.get('/returned', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.returned.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.returned.count()));
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
    .summary('Retrieve all returned')
    .description('Retrieves all edges from the "returned" collection.');

router.delete('/returned/:key', function(req, res) {
  try {
    const data = graph.returned.document(req.pathParams.key);
    db._remove(`returned/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The returned edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the edge.')
    .body(joi.object().optional())
    .response(schemas.edge, 'edge stored in the collection.')
    .summary('Delete an edge')
    .description('Deletes an edge from the "returned" collection by key.');

router.delete('/returned', function(req, res) {
  try {
    db._truncate(`returned`);
    res.send({message: 'Deleted all edges in the "returned" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all returned edges')
    .description('Deletes all edges from the "returned" collection.');
