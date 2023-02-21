const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/job_process_stats', function(req, res) {
  const doc = req.body;
  const meta = db.job_process_stats.save(doc);
  Object.assign(doc, meta);
  res.send(doc);
})
    .body(schemas.jobProcessStats, 'job process stats')
    .response(schemas.jobProcessStats, 'job process stats')
    .summary('Store utilization stats for a job process.')
    .description('Store utilization stats for a job process.');

router.get('/job_process_stats', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = db.job_process_stats.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, db.job_process_stats.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobProcessStats)
    .summary('Retrieve all job processs')
    .description('Retrieves all job processs from the "job_process_stats" collection.');

router.get('/job_process_stats/:key', function(req, res) {
  try {
    const key = req.pathParams.key;
    const doc = graph.job_process_stats.document(key);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the job process object')
    .response(schemas.jobProcessStats)
    .summary('Retrieve the job process for a key.')
    .description('Retrieve the job process for a key.');

router.delete('/job_process_stats/:key', function(req, res) {
  try {
    const cursor = graph.job_process_stats.document(req.pathParams.key);
    db._remove(`job_process_stats/${req.pathParams.key}`);
    res.send(cursor);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The user data does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the job process.')
    .body(joi.object().optional())
    .response(schemas.jobProcessStats, 'job process stored in the collection.')
    .summary('Delete a job process')
    .description('Deletes a job process from the "job_process_stats" collection by key.');

router.delete('/job_process_stats', function(req, res) {
  try {
    db._truncate(`job_process_stats`);
    res.send({message: 'Deleted all documents in the "job_process_stats" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all job process stats')
    .description('Deletes all job process stats from the "job_process_stats" collection.');
