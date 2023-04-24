'use strict';
const joi = require('joi');
const {MAX_TRANSFER_RECORDS} = require('../defs');
const config = require('../config');
const documents = require('../documents');
const utils = require('../utils');
const query = require('../query');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.get('workflows/:workflow/job_keys', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const workflow = documents.getWorkflow(workflowKey, res);
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const keys = [];
  for (const job of jobs) {
    keys.push(job._key);
  }
  res.send({items: keys});
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .response(joi.object())
    .summary('Retrieve all job keys for a workflow.')
    .description('Retrieves all job keys from the "jobs" collection for a workflow.');

router.get('/workflows/:workflow/jobs/find_by_status/:status', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const workflow = documents.getWorkflow(workflowKey, res);
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const qp = req.queryParams;
  const limit = utils.getItemsLimit(qp.limit);
  try {
    const cursor = jobs.byExample({status: req.pathParams.status});
    const items = [];
    for (const job of cursor.skip(qp.skip).limit(limit)) {
      items.push(job);
    }
    res.send(utils.makeCursorResult(items, qp.skip, limit, cursor.count()));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get jobs find_by_status status=${status}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('status', joi.string().required(), 'Job status.')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs with a specific status')
    .description('Retrieves all jobs from the "jobs" collection with a specific status.');

router.get('/workflows/:workflow/jobs/find_by_needs_file/:key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const files = config.getWorkflowCollection(workflow, 'files');
  if (!files.exists(key)) {
    res.throw(404, `File ${key} is not stored`);
  }
  const file = documents.getWorkflowDocument(workflow, 'files', key, res);
  const qp = req.queryParams;
  const limit = utils.getItemsLimit(qp.limit);
  try {
    const cursor = query.getJobsThatNeedFile(file, workflow);
    res.send(utils.makeCursorResultFromIteration(cursor, qp.skip, limit));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get jobs find_by_needs_file key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'File key')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobs)
    .summary('Retrieve all jobs that need a file')
    .description('Retrieves all jobs connected to a file by the needs edge.');

router.get('/workflows/:workflow/jobs/:key/resource_requirements', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const doc = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  try {
    const rr = query.getJobResourceRequirements(doc, workflow);
    res.send(rr);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get jobs resource_requirements key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.resourceRequirements, 'Resource requirements for the job.')
    .summary('Retrieve the resource requirements for a job.')
    .description('Retrieve the resource requirements for a job by its key.');

router.put('/workflows/:workflow/jobs/:key/resource_requirements/:rr_key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const rrKey = req.pathParams.rr_key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  const rr = documents.getWorkflowDocument(workflow, 'resource_requirements', rrKey, res);
  try {
    const edge = query.setOrReplaceJobResourceRequirements(job, rr, workflow);
    res.send(edge);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Update jobs resource_requirements key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.edge, 'Requires edge that connects the job and resource requirements.')
    .summary('Set the resource requirements for a job.')
    .description('Set the resource requirements for a job, replacing any current value.');

router.get('/workflows/:workflow/jobs/:key/process_stats', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const doc = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  try {
    const result = query.listJobProcessStats(doc, workflow);
    res.send(result);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Update jobs process_stats key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(joi.array().items(schemas.jobProcessStats), 'Process stats for the job.')
    .summary('Retrieve the job process stats for a job.')
    .description('Retrieve the job process stats for a job by its key.');

router.post('/workflows/:workflow/jobs/:key/complete_job/:status/:rev', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const status = req.pathParams.status;
  const rev = req.pathParams.rev;
  const result = req.body;
  const workflow = documents.getWorkflow(workflowKey, res);
  if (!query.isJobStatusComplete(status)) {
    res.throw(400, `status=${status} does not indicate completion`);
  }
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  if (job._rev != rev) {
    res.throw(409, `Revision conflict for ${job._id}: _rev=${job._rev}`);
  }

  job.status = status;
  try {
    const meta = documents.addResult(result, workflow);
    Object.assign(result, meta);

    const returned = config.getWorkflowCollection(workflow, 'returned');
    returned.save({_from: job._id, _to: result._id});
    const updatedJob = query.manageJobStatusChange(job, workflow);
    updatedJob.internal.hash = documents.computeJobInputHash(updatedJob, workflow);
    documents.updateWorkflowDocument(workflow, 'jobs', updatedJob);
    res.send(updatedJob);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Complete job key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .pathParam('status', joi.string().required(), 'New job status.')
    .pathParam('rev', joi.string().required(), 'Current job revision.')
    .body(schemas.result, 'Result of the job.')
    .response(schemas.job, 'job completed in the collection.')
    .summary('Complete a job and add a result.')
    .description('Complete a job, connect it to a result, and manage side effects.');

router.put('/workflows/:workflow/jobs/:key/manage_status_change/:status/:rev', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const status = req.pathParams.status;
  const rev = req.pathParams.rev;
  const workflow = documents.getWorkflow(workflowKey, res);
  if (query.isJobStatusComplete(status)) {
    res.throw(400, `status=${status} indicates completion. Post complete_job status instead.`);
    return;
  }
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  if (job._rev != rev) {
    res.throw(400, `Revision conflict for ${job._id}: _rev=${job._rev}`);
    return;
  }
  job.status = status;
  try {
    const updatedJob = query.manageJobStatusChange(job, workflow);
    res.send(updatedJob);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Put jobs manage_status_change key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .pathParam('status', joi.string().required(), 'New job status')
    .pathParam('rev', joi.string().required(), 'Current job revision')
    .response(schemas.job, 'Updated job.')
    .summary('Change the status of a job and manage side effects.')
    .description('Change the status of a job and manage side effects.');

router.post('/workflows/:workflow/jobs/:key/user_data', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  const userData = req.body;
  try {
    const doc = documents.addUserData(userData, workflow);
    const stores = config.getWorkflowCollection(workflow, 'stores');
    stores.save({_from: job._id, _to: doc._id});
    res.send(doc);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Post jobs user_data key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .body(schemas.userData, 'User data for the job.')
    .response(schemas.userData, 'Database information for the user data.')
    .summary('Store user data for a job.')
    .description('Store user data for a job and connect the two vertexes.');

router.get('/workflows/:workflow/jobs/:key/user_data_stores', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  try {
    // Shouldn't need skip and limit, but that could be added.
    const items = query.listUserDataStoredByJob(job, workflow).toArray();
    if (items.length > MAX_TRANSFER_RECORDS) {
      throw new Error(`Bug: unhandled case where length of items is too big: ${items.length}`);
    }
    res.send(utils.makeCursorResult(items, 0, MAX_TRANSFER_RECORDS, items.length));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get jobs user_data stored key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.batchUserData, 'All user data stored for the job.')
    .summary('Retrieve all user data for a job.')
    .description('Retrieve all user data for a job.');

router.get('/workflows/:workflow/jobs/:key/user_data_consumes', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  try {
    // Shouldn't need skip and limit, but that could be added.
    const items = query.listUserDataConsumedByJob(job, workflow).toArray();
    if (items.length > MAX_TRANSFER_RECORDS) {
      throw new Error(`Bug: unhandled case where length of items is too big: ${items.length}`);
    }
    res.send(utils.makeCursorResult(items, 0, MAX_TRANSFER_RECORDS, items.length));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get jobs user_data consumed key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.batchUserData, 'All user data consumed by the job.')
    .summary('Retrieve all user data consumed by a job.')
    .description('Retrieve all user data consumed by a job.');
