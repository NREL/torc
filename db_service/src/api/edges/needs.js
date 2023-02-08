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

router.post('/needs', function(req, res) {
  const data = req.body;
  const meta = graph.needs.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'Needs relationship between a job and a file.')
    .response(schemas.edge, 'Edge')
    .summary('Store a needs edge between a job and a file.')
    .description('Store a job-file relationship in the "needs" edge collection.');

router.get('/needs/:key', function(req, res) {
  try {
    const data = graph.needs.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The need does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the needs edge.')
    .response(schemas.edge, 'Edge stored in the collection.')
    .summary('Retrieve a needs edge')
    .description('Retrieves a need edge from the "needs" collection by key.');

router.get('/needs', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.needs.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.needs.count()));
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
    .summary('Retrieve all needs')
    .description('Retrieves all needs from the "needs" collection.');

router.delete('/needs/:key', function(req, res) {
  try {
    const data = graph.needs.document(req.pathParams.key);
    db._remove(`needs/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The need does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the need.')
    .body(joi.object().optional())
    .response(schemas.edge, 'need stored in the collection.')
    .summary('Delete a need')
    .description('Deletes a need from the "needs" collection by key.');

router.delete('/needs', function(req, res) {
  try {
    db._truncate(`needs`);
    res.send({message: 'Deleted all edges in the "needs" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all needs edges')
    .description('Deletes all edges from the "needs" collection.');
