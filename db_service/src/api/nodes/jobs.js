'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const {GRAPH_NAME} = require('../../defs');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(GRAPH_NAME);
const query = require('../../query');
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/jobs', function(req, res) {
  const doc = query.addJob(req.body);
  res.send(convertJobforApi(doc));
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
    const meta = db.jobs.update(doc, doc);
    Object.assign(doc, meta);
    res.send(convertJobforApi(doc));
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the job.')
    .body(joi.object().required(), 'job to update in the collection.')
    .response(schemas.job, 'job updated in the collection.')
    .summary('Update job')
    .description('Update a job in the "jobs" collection.');

router.get('/jobs/:name', function(req, res) {
  try {
    const doc = graph.jobs.document(req.pathParams.name);
    res.send(convertJobforApi(doc));
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

router.get('/jobs', function(req, res) {
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const items = [];
  for (const job of graph.jobs.all().skip(qp.skip).limit(limit)) {
    items.push(convertJobforApi(job));
  }
  res.send(makeCursorResult(items, qp.skip, limit, graph.jobs.count()));
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs')
    .description('Retrieve all jobs. Limit output with skip and limit.');

router.get('/job_names', function(req, res) {
  const jobs = graph.jobs.all();
  const names = [];
  for (const job of jobs) {
    names.push(job.name);
  }
  res.send({items: names});
})
    .response(joi.object())
    .summary('Retrieve all job names')
    .description('Retrieves all job names from the "jobs" collection.');

router.get('/jobs/find_by_status/:status', function(req, res) {
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const cursor = graph.jobs.byExample({status: req.pathParams.status});
  const items = [];
  for (const job of cursor.skip(qp.skip).limit(limit)) {
    items.push(convertJobforApi(job));
  }
  res.send(makeCursorResult(items, qp.skip, limit, cursor.count()));
})
    .pathParam('status', joi.string().required(), 'Job status.')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs with a specific status')
    .description('Retrieves all jobs from the "jobs" collection with a specific status.');

router.get('/jobs/find_by_needs_file/:name', function(req, res) {
  if (!graph.files.exists(req.pathParams.name)) {
    res.throw(404, `File ${req.pathParams.name} is not stored`);
  }
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const cursor = query.getJobsThatNeedFile(req.pathParams.name);
  // TODO: how to do this with Arango cursor?
  const items = [];
  let i = 0;
  for (const item of cursor) {
    if (i > qp.skip) {
      i++;
      continue;
    }
    items.push(convertJobforApi(item));
    if (items.length == limit) {
      break;
    }
  }
  res.send(makeCursorResult(items, qp.skip, limit, cursor.count()));
})
    .pathParam('name', joi.string().required(), 'File name.')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs that need a file')
    .description('Retrieves all jobs connected to a file by the needs edge.');

router.delete('/jobs/:name', function(req, res) {
  try {
    const doc = graph.jobs.document(req.pathParams.name);
    db._remove(`jobs/${req.pathParams.name}`);
    res.send(convertJobforApi(doc));
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the job.')
    .body(joi.object().optional())
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
    .body(joi.object().optional())
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
    .response(schemas.resourceRequirements, 'Resource requirements for the job.')
    .summary('Retrieve the resource requirements for a job.')
    .description('Retrieve the resource requirements for a job by its name.');

router.get('/jobs/process_stats/:name', function(req, res) {
  try {
    const doc = graph.jobs.document(req.pathParams.name);
    const rr = query.listJobProcessStats(doc);
    res.send(rr);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the job.')
    .response(joi.array().items(schemas.jobProcessStats), 'Process stats for the job.')
    .summary('Retrieve the job process stats for a job.')
    .description('Retrieve the job process stats for a job by its name.');

router.post('jobs/complete_job/:name/:status/:rev', function(req, res) {
  const status = req.pathParams.status;
  if (!query.isJobStatusComplete(status)) {
    res.throw(400, `status=${status} does not indicate completion`);
    return;
  }
  const job = graph.jobs.document(req.pathParams.name);
  if (job._rev != req.pathParams.rev) {
    res.throw(400, `Revision conflict for ${job.name}: _rev=${job._rev}`);
    return;
  }

  if (job.status == status) {
    res.throw(400, `Job ${job.name} already has status=${status}`);
    return;
  }

  const meta = {name: req.pathParams.name, status: status};
  Object.assign(job, meta);

  // This order is required.
  const result = query.addResult(req.body);
  graph.returned.save({_from: job._id, _to: result._id});
  const updatedJob = query.manageJobStatusChange(job);
  res.send(convertJobforApi(updatedJob));
})
    .body(schemas.result, 'Result of the job.')
    .response(schemas.job, 'job completed in the collection.')
    .summary('Complete a job and add a result.')
    .description('Complete a job, connect it to a result, and manage side effects.');

router.put('jobs/manage_status_change/:name/:status/:rev', function(req, res) {
  const status = req.pathParams.status;
  if (query.isJobStatusComplete(status)) {
    res.throw(400, `status=${status} indicates completion. Post complete_job status instead.`);
    return;
  }
  const job = graph.jobs.document(req.pathParams.name);
  if (job._rev != req.pathParams.rev) {
    res.throw(400, `Revision conflict for ${job.name}: _rev=${job._rev}`);
    return;
  }
  job.status = status;
  const updatedJob = query.manageJobStatusChange(job);
  res.send(convertJobforApi(updatedJob));
})
    .response(schemas.job, 'Updated job.')
    .summary('Change the status of a job and manage side effects.')
    .description('Change the status of a job and manage side effects.');

router.post('jobs/store_user_data/:name', function(req, res) {
  const job = graph.jobs.document(req.pathParams.name);
  const userData = req.pathParams.user_data;
  const doc = query.addUserData(userData);
  graph.stores.save({_from: job._id, _to: doc._id});
  res.send(doc);
})
    .body(schemas.result, 'User data for the job.')
    .response(joi.object().required(), 'Database information for the user data.')
    .summary('Store user data for a job.')
    .description('Store user data for a job and connect the two vertexes.');

router.get('jobs/get_user_data/:name', function(req, res) {
  // Shouldn't need skip and limit, but that could be added.
  if (!graph.jobs.document(req.pathParams.name)) {
    res.throw(404, `Job ${req.pathParams.name} is not stored`);
  } else {
    res.send(query.getUserDataStoredByJob(req.pathParams.name).toArray());
  }
})
    .pathParam('name', joi.string().required(), 'Job name.')
    .response(joi.object().required(), 'All user data stored for the job.')
    .summary('Retrieve all user data for a job.')
    .description('Retrieve all user data for a job.');

/**
 * Convert the job for delivery to an API client.
 * @param {Object} job
 * @return {Object}
 */
function convertJobforApi(job) {
  delete job.internal;
  return job;
}
