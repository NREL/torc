const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const graph = graphModule._graph(defs.GRAPH_NAME);
const query = require('../../query');
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/jobs', function(req, res) {
  const doc = query.addJob(req.body);
  console.log(`Added job ${doc.name}`);
})
    .body(schemas.job, 'job to store in the collection.')
    .response(schemas.job, 'job stored in the collection.')
    .summary('Store job')
    .description('Store a job in the "jobs" collection.');

router.put('/jobs/:name', function(req, res) {
  const doc = req.body;
  if (doc._rev == null) {
    res.throw(400, 'Updating a job requires the existing revision');
  }

  try {
    if (req.pathParams.name != doc.name) {
      throw new Error(`name=${req.pathParams.name} does not match ${doc.name}`);
    }
    const updatedDoc = query.updateJobStatus(doc);
    res.send(updatedDoc);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .body(joi.object().required(), 'job to update in the collection.')
    .response(schemas.job, 'job updated in the collection.')
    .summary('Update job')
    .description('Update a job in the "jobs" collection.');

router.get('/jobs/:name', function(req, res) {
  try {
    const cursor = graph.jobs.document(req.pathParams.name);
    res.send(cursor);
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

// TODO: provide a way to change the starting point.
router.get('/jobs', function(req, res) {
  const qp = req.queryParams == null ? {} : req.queryParams;
  const skip = qp.skip == null ? 0 : parseInt(qp.skip);
  if (skip > graph.jobs.count()) {
    res.throw(400, `skip=${qp.skip} is greater than count=${graph.jobs.count()}`);
  }

  const cursor = graph.jobs.all().skip(skip);
  if (qp.limit != null) {
    cursor = cursor.limit(qp.limit);
  }
  res.send(cursor);
})
    .response(joi.array().items(schemas.job))
    .summary('Retrieve all jobs')
    .description('Retrieve all jobs. Limit output with skip and limit.');

router.get('/job_names', function(req, res) {
  const jobs = graph.jobs.all();
  const names = [];
  for (const job of jobs) {
    names.push(job.name);
  }
  res.send(names);
})
    .response(joi.array().items(joi.string()))
    .summary('Retrieve all job names')
    .description('Retrieves all job names from the "jobs" collection.');

router.get('/jobs/find_by_status/:status', function(req, res) {
  const qp = req.queryParams == null ? {} : req.queryParams;

  let cursor = graph.jobs.byExample({status: req.pathParams.status});
  if (qp.limit != null) {
    cursor = cursor.limit(qp.limit);
  }
  res.send(cursor);
})
    .pathParam('status', joi.string().required(), 'Job status.')
    .response(joi.array().items(schemas.job))
    .summary('Retrieve all jobs with a specific status')
    .description('Retrieves all jobs from the "jobs" collection with a specific status.');

router.delete('/jobs/:name', function(req, res) {
  try {
    const cursor = graph.jobs.document(req.pathParams.name);
    db._remove(`jobs/${req.pathParams.name}`);
    res.send(cursor);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the job.')
    .response(schemas.job, 'Job stored in the collection.')
    .summary('Delete a job')
    .description('Deletes a job from the "jobs" collection by name.');

router.delete('/jobs', function(req, res) {
  try {
    db._truncate(`jobs`);
    res.send({message: 'Deleted all documents in the "jobs" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .response(joi.object(), 'message')
    .summary('Delete all jobs')
    .description('Deletes all jobs from the "jobs" collection.');

router.get('/jobs/resource_requirements/:name', function(req, res) {
  try {
    const doc = graph.jobs.document(req.pathParams.name);
    const rr = query.getJobResourceRequirements(doc);
    res.send(rr);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the job.')
    .response(schemas.resourceRequirements, 'Resource requirements for job.')
    .summary('Retrieve the resource requirements for a job.')
    .description('Retrieve the resource requirements for a job by its name.');
