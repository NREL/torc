'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const {MAX_TRANSFER_RECORDS} = require('../defs');
const {convertJobForApi, getItemsLimit, makeCursorResult} = require('../utils');
const query = require('../query');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.get('/job_keys', function(req, res) {
  const jobs = db.jobs.all();
  const names = [];
  for (const job of jobs) {
    names.push(job._key);
  }
  res.send({items: names});
})
    .response(joi.object())
    .summary('Retrieve all job keys')
    .description('Retrieves all job keys from the "jobs" collection.');

router.get('/jobs/find_by_status/:status', function(req, res) {
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const cursor = db.jobs.byExample({status: req.pathParams.status});
  const items = [];
  for (const job of cursor.skip(qp.skip).limit(limit)) {
    items.push(convertJobForApi(job));
  }
  res.send(makeCursorResult(items, qp.skip, limit, cursor.count()));
})
    .pathParam('status', joi.string().required(), 'Job status.')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs with a specific status')
    .description('Retrieves all jobs from the "jobs" collection with a specific status.');

router.get('/jobs/find_by_needs_file/:key', function(req, res) {
  if (!db.files.exists(req.pathParams.key)) {
    res.throw(404, `File ${req.pathParams.key} is not stored`);
  }
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const cursor = query.getJobsThatNeedFile(req.pathParams.key);
  // TODO: how to do this with Arango cursor?
  const items = [];
  let i = 0;
  for (const item of cursor) {
    if (i > qp.skip) {
      i++;
      continue;
    }
    items.push(convertJobForApi(item));
    if (items.length == limit) {
      break;
    }
  }
  res.send(makeCursorResult(items, qp.skip, limit, cursor.count()));
})
    .pathParam('key', joi.string().required(), 'File key.')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs that need a file')
    .description('Retrieves all jobs connected to a file by the needs edge.');

router.get('/jobs/resource_requirements/:key', function(req, res) {
  try {
    const doc = db.jobs.document(req.pathParams.key);
    const rr = query.getJobResourceRequirements(doc);
    res.send(rr);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.resourceRequirements, 'Resource requirements for the job.')
    .summary('Retrieve the resource requirements for a job.')
    .description('Retrieve the resource requirements for a job by its key.');

router.get('/jobs/process_stats/:key', function(req, res) {
  try {
    const doc = db.jobs.document(req.pathParams.key);
    const rr = query.listJobProcessStats(doc);
    res.send(rr);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The job does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Job key')
    .response(joi.array().items(schemas.jobProcessStats), 'Process stats for the job.')
    .summary('Retrieve the job process stats for a job.')
    .description('Retrieve the job process stats for a job by its key.');

router.post('jobs/complete_job/:key/:status/:rev', function(req, res) {
  const status = req.pathParams.status;
  if (!query.isJobStatusComplete(status)) {
    res.throw(400, `status=${status} does not indicate completion`);
    return;
  }
  const job = db.jobs.document(req.pathParams.key);
  if (job._rev != req.pathParams.rev) {
    res.throw(400, `Revision conflict for ${job.key}: _rev=${job._rev}`);
    return;
  }

  if (job.status == status) {
    res.throw(400, `Job ${job.key} already has status=${status}`);
    return;
  }

  const meta = {_key: req.pathParams.key, status: status};
  Object.assign(job, meta);

  // This order is required.
  const result = query.addResult(req.body);
  db.returned.save({_from: job._id, _to: result._id});
  const updatedJob = query.manageJobStatusChange(job);
  res.send(convertJobForApi(updatedJob));
})
    .body(schemas.result, 'Result of the job.')
    .response(schemas.job, 'job completed in the collection.')
    .summary('Complete a job and add a result.')
    .description('Complete a job, connect it to a result, and manage side effects.');

router.put('jobs/manage_status_change/:key/:status/:rev', function(req, res) {
  const status = req.pathParams.status;
  if (query.isJobStatusComplete(status)) {
    res.throw(400, `status=${status} indicates completion. Post complete_job status instead.`);
    return;
  }
  const job = db.jobs.document(req.pathParams.key);
  if (job._rev != req.pathParams.rev) {
    res.throw(400, `Revision conflict for ${job.key}: _rev=${job._rev}`);
    return;
  }
  job.status = status;
  const updatedJob = query.manageJobStatusChange(job);
  res.send(convertJobForApi(updatedJob));
})
    .pathParam('key', joi.string().required(), 'Job key')
    .pathParam('status', joi.string().required(), 'New job status')
    .pathParam('rev', joi.string().required(), 'Current job revision')
    .response(schemas.job, 'Updated job.')
    .summary('Change the status of a job and manage side effects.')
    .description('Change the status of a job and manage side effects.');

router.post('jobs/store_user_data/:key', function(req, res) {
  const job = db.jobs.document(req.pathParams.key);
  const userData = req.body;
  const doc = query.addUserData(userData);
  db.stores.save({_from: job._id, _to: doc._id});
  res.send(doc);
})
    .body(joi.object().required(), 'User data for the job.')
    .response(joi.object().required(), 'Database information for the user data.')
    .summary('Store user data for a job.')
    .description('Store user data for a job and connect the two vertexes.');

router.get('jobs/get_user_data/:key', function(req, res) {
  // Shouldn't need skip and limit, but that could be added.
  const key = req.pathParams.key;
  if (!db.jobs.exists(key)) {
    res.throw(404, `Job ${key} is not stored`);
  } else {
    const job = db.jobs.document(key);
    res.send(query.getUserDataStoredByJob(job));
  }
})
    .pathParam('key', joi.string().required(), 'Job key')
    .response(joi.object().required(), 'All user data stored for the job.')
    .summary('Retrieve all user data for a job.')
    .description('Retrieve all user data for a job.');
