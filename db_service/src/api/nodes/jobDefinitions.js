const joi = require('joi');
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(defs.GRAPH_NAME);
const query = require('../../query');
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/job_definitions', function(req, res) {
  const doc = query.addJobDefinition(req.body);
  console.log(`Added job ${doc.name}`);
  res.send(doc);
})
    .body(schemas.jobDefinition, 'job definition to store in the collection.')
    .response(schemas.job, 'job stored in the collection.')
    .summary('Store a job and create edges.')
    .description('Store a job in the "jobs" collection and create edges.');

// TODO
// router.put('/jobs/:name', function(req, res) {
// })
//     .body(joi.object().required(), 'job definition to update in the collection.')
//     .response(schemas.job, 'job updated in the collection.')
//     .summary('Update job')
//     .description('Update a job in the "jobs" collection.');

router.get('/job_definitions/:name', function(req, res) {
  try {
    const doc = graph.jobs.document(req.pathParams.name);
    res.send(query.getJobDefinition(doc));
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the job.')
    .response(schemas.job, 'Job stored in the collection.')
    .summary('Retrieve a job')
    .description('Retrieves a job from the "jobs" collection by name.');

router.get('/job_definitions', function(req, res) {
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const cursor = graph.jobs.all().skip(qp.skip).limit(limit);
  const jobDefinitions = [];
  for (const job of cursor) {
    jobDefinitions.push(query.getJobDefinition(job));
  }
  res.send(makeCursorResult(jobDefinitions, qp.skip, limit, graph.jobs.count()));
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobDefinitions)
    .summary('Retrieve all job definitions')
    .description('Retrieves all job definitions. Limit output with skip and limit.');
