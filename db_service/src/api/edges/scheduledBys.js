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

router.post('/scheduled_bys', function(req, res) {
  const data = req.body;
  const meta = graph.scheduled_bys.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'scheduled_by relationship between a job and an hpc_config.')
    .response(schemas.edge, 'Edge')
    .summary('Store a scheduled_by edge between a job and an hpc_config.')
    .description('Store a job-hpc_config relationship in the "scheduled_by" edge collection.');

router.get('/scheduled_bys/:key', function(req, res) {
  try {
    const data = graph.scheduled_bys.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The scheduled_by edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the scheduled_by.')
    .response(schemas.edge, 'scheduled_by stored in the collection.')
    .summary('Retrieve a scheduled_by edge')
    .description('Retrieves an edge from the "scheduled_by" collection by key.');

router.get('/scheduled_bys', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.scheduled_bys.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.scheduled_bys.count()));
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
    .summary('Retrieve all scheduled_by edges')
    .description('Retrieves all edges from the "scheduled_by" collection.');

router.delete('/scheduled_bys/:key', function(req, res) {
  try {
    const data = graph.scheduled_bys.document(req.pathParams.key);
    db._remove(`scheduled_bys/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The scheduled_by edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the scheduled_by.')
    .body(joi.object().optional())
    .response(schemas.edge, 'scheduled_by stored in the collection.')
    .summary('Delete a scheduled_by')
    .description('Deletes a scheduled_by edge from the "scheduled_by" collection by key.');

router.delete('/scheduled_bys', function(req, res) {
  try {
    db._truncate(`scheduled_bys`);
    res.send({message: 'Deleted all edges in the "scheduled_by" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all scheduled_by edges')
    .description('Deletes all edges from the "scheduled_by" collection.');
