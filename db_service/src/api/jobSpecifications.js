'use strict';
const joi = require('joi');
const {MAX_TRANSFER_RECORDS} = require('../defs');
const {getItemsLimit, makeCursorResult} = require('../utils');
const config = require('../config');
const documents = require('../documents');
const query = require('../query');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.get('/workflows/:workflow/job_specifications/:key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const doc = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  try {
    res.send(query.getjobSpecification(doc, workflow));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get job_specification key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.job, 'Job stored in the collection.')
    .summary('Retrieve a job')
    .description('Retrieves a job from the "jobs" collection by key.');

router.get('/workflows/:workflow/job_specifications', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const workflow = documents.getWorkflow(workflowKey, res);
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  try {
    const cursor = jobs.all().skip(qp.skip).limit(limit);
    const jobSpecifications = [];
    for (const job of cursor) {
      jobSpecifications.push(query.getjobSpecification(job));
    }
    res.send(makeCursorResult(jobSpecifications, qp.skip, jobs.count()));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get job_specifications for workflow_key=${workflowKey}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchJobSpecifications)
    .summary('Retrieve all job definitions')
    .description('Retrieves all job definitions. Limit output with skip and limit.');
