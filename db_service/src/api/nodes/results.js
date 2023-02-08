const joi = require('joi');
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(defs.GRAPH_NAME);
const createRouter = require('@arangodb/foxx/router');
const query = require('../../query');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/results', function(req, res) {
  const doc = query.addResult(req.body);
  res.send(doc);
})
    .body(schemas.result, 'Job result.')
    .response(schemas.result, 'result')
    .summary('Store a job result.')
    .description('Store a job result in the "results" collection.');

router.get('/results', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.results.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.results.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchResults)
    .summary('Retrieve all results')
    .description('Retrieves all results from the "results" collection.');

router.get('/results/:key', function(req, res) {
  try {
    const key = req.pathParams.key;
    const doc = graph.results.document(key);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the results object')
    .response(schemas.result)
    .summary('Retrieve the result for a key.')
    .description('Retrieve the result for a key.');

router.delete('/results/:key', function(req, res) {
  try {
    const cursor = graph.results.document(req.pathParams.key);
    db._remove(`results/${req.pathParams.key}`);
    res.send(cursor);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The user data does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the result object.')
    .body(joi.object().optional())
    .response(schemas.result, 'Result stored in the collection.')
    .summary('Delete a result')
    .description('Deletes a result from the "results" collection by key.');

router.get('/results/find_by_job_name/:name', function(req, res) {
  const job = query.getLatestJobResult(req.pathParams.name);
  if (job == null) {
    res.throw(404, `No result is stored for job ${req.pathParams.name}`);
  }
  res.send(job);
})
    .pathParam('name', joi.string().required(), 'Job name.')
    .response(schemas.result)
    .summary('Retrieve the latest result for a job')
    .description('Retrieve the latest result for a job. Throws an error if no result is stored.');

router.delete('/results', function(req, res) {
  try {
    db._truncate(`results`);
    res.send({message: 'Deleted all documents in the "results" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all results')
    .description('Deletes all results from the "results" collection.');
