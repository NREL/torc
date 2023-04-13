'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const {MAX_TRANSFER_RECORDS} = require('../defs');
const {JobStatus} = require('../defs');
const utils = require('../utils');
const query = require('../query');
const documents = require('../documents');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
const collection = db._collection('workflows');
module.exports = router;

router.post('/workflows', function(req, res) {
  try {
    const doc = documents.addWorkflow(req.body);
    res.send(doc);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, 'Post new workflow');
  }
})
    .body(schemas.workflow, 'Collection of jobs and dependent resources.')
    .response(schemas.workflow, 'Collection of jobs and dependent resources')
    .summary('Store a workflow.')
    .description('Store a workflow in the "workflows" collection.');

router.put('/workflows/:key', function(req, res) {
  const key = req.pathParams.key;
  const doc = req.body;
  if (key != doc._key) {
    res.throw(400, `key=${key} does not match ${doc._key}`);
  }
  if (doc._rev == null) {
    res.throw(400, `Updating a workflow requires the existing revision`);
  }
  try {
    const meta = collection.update(doc, doc);
    Object.assign(doc, meta);
    res.send(doc);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Update workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the workflow.')
    .body(schemas.workflow, 'workflow to update in the collection.')
    .response(schemas.workflow, 'workflow updated in the collection.')
    .summary('Update workflow')
    .description('Update a document in the "workflows" collection.');

router.get('/workflows/:key', function(req, res) {
  res.send(documents.getWorkflow(req.pathParams.key, res));
})
    .pathParam('key', joi.string().required(), 'key of the workflows document')
    .response(schemas.workflow)
    .summary('Retrieve the workflow for an key.')
    .description('Retrieve the document for a key from the "workflows" collection.');

router.get('/workflows', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = utils.getItemsLimit(qp.limit);
    const example = {};
    for (const filterField of ['description', 'name', 'user']) {
      if (qp[filterField] != null) {
        example[filterField] = qp[filterField];
      }
    }
    const items = Object.keys(example).length == 0 ?
      collection.all().skip(qp.skip).limit(limit) :
      collection.byExample(example).skip(qp.skip).limit(limit);
    res.send(utils.makeCursorResult(items.toArray(), qp.skip, limit, collection.count()));
  } catch (e) {
    if (e.isArangoError) {
      res.throw(400, `${e}`, e);
    }
    throw e;
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .queryParam('name', joi.string())
    .queryParam('user', joi.string())
    .queryParam('description', joi.string())
    .response(schemas.batchWorkflows)
    .summary('Retrieve all workflows')
    .description('Retrieves all documents from the "workflows" collection.');

router.delete('/workflows/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    documents.deleteWorkflow(workflow);
    res.send(workflow);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Delete workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key.')
    .body(joi.object().optional())
    .response(schemas.workflow, 'workflow stored in the collection.')
    .summary('Delete a workflow')
    .description('Deletes a document from the "workflows" collection by key.');

router.get('/workflows/is_complete/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  const status = query.getWorkflowStatus(workflow);
  try {
    res.send({is_canceled: status.is_canceled, is_complete: query.isWorkflowComplete(workflow)});
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Check workflow is_complete key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(schemas.isComplete)
    .summary('Report whether the workflow is complete')
    .description('Reports true if all jobs in the workflow are complete.');

router.get('/workflows/ready_job_requirements/:key', function(req, res) {
  const key = req.pathParams.key;
  const schedulerConfigId = req.queryParams.scheduler_config_id;
  const workflow = documents.getWorkflow(key, res);
  try {
    const result = query.getReadyJobRequirements(workflow, schedulerConfigId);
    res.send(result);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get ready_job_requirements key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .queryParam('scheduler_config_id', joi.string().optional().allow(null, ''),
        'Limit output to jobs assigned this scheduler.')
    .response(schemas.readyJobsResourceRequirements, 'result')
    .summary('Return the resource requirements for ready jobs.')
    .description(`Return the resource requirements for jobs with a status of ready.`);

router.post('/workflows/initialize_jobs/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    query.addBlocksEdgesFromFiles(workflow);
    query.initializeJobStatus(workflow);
    res.send({message: 'Initialized job status'});
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Initialize jobs for workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(joi.object(), 'message')
    .summary('Initialize job relationships.')
    .description('Initialize job relationships based on file relationships.');

router.post('/workflows/prepare_jobs_for_submission/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    const status = query.getWorkflowStatus(workflow);
    if (status.is_canceled) {
      res.send([]);
    } else {
      const resources = req.body;
      const qp = req.queryParams == null ? {} : req.queryParams;
      const reason = {message: ''};
      const jobs = query.prepareJobsForSubmission(workflow, resources, qp.limit, reason);
      const items = [];
      for (const job of jobs) {
        items.push(utils.convertJobForApi(job));
      }
      res.send({jobs: jobs, reason: reason.message});
    }
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `prepare_jobs_for_submission workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .body(schemas.workerResources, 'Available worker resources.')
    .response(joi.object().required().keys(
        {jobs: joi.array().items(schemas.job), reason: joi.string()}),
    'Jobs that are ready for submission.',
    )
    .summary('Return ready jobs')
    .description('Return jobs that are ready for submission. Sets status to submitted_pending');

router.post('/workflows/auto_tune_resource_requirements/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    query.setupAutoTuneResourceRequirements(workflow);
    res.send({message: 'Enabled jobs for auto-tune mode.'});
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `auto_tune_resource_requirements workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(joi.object(), 'Message')
    .summary('Enable workflow for auto-tuning resource requirements.')
    .description('Enable workflow for auto-tuning resource requirements.');

router.post('/workflows/process_auto_tune_resource_requirements_results/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    query.processAutoTuneResourceRequirementsResults(workflow);
    res.send({message: 'Processed the results of auto-tuning resource requirements.'});
  } catch (e) {
    const tag = `process_auto_tune_resource_requirements_results workflow key=${key}`;
    utils.handleArangoApiErrors(e, res, tag);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(joi.object(), 'Message')
    .summary('Process the results of auto-tuning resource requirements.')
    .description('Process the results of auto-tuning resource requirements.');

router.get('/workflows/config/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    const config = query.getWorkflowConfig(workflow);
    res.send(config);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get workflow config key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(schemas.workflowConfig)
    .summary('Reports the workflow config.')
    .description('Reports the workflow config.');

router.put('/workflows/cancel/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    documents.cancelWorkflow(workflow);
    res.send({message: `Canceled workflow`});
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Cancel workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(joi.object(), 'message')
    .summary('Cancel workflow.')
    .description(`Cancel workflow. Workers will detect the status change and cancel jobs.`);

router.put('/workflows/config/:key', function(req, res) {
  const key = req.pathParams.key;
  const config = req.body;
  // Validate that the workflow key is correct.
  documents.getWorkflow(key, res);
  try {
    db.workflow_configs.update(config, config);
    res.send(config);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Update workflow config key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .body(schemas.workflowConfig, 'Updated workflow config')
    .response(schemas.workflowConfig)
    .summary('Reports the workflow config.')
    .description('Reports the workflow config.');

router.post('/workflows/reset_status/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    query.resetJobStatus(workflow);
    query.resetWorkflowStatus(workflow);
    res.send({message: `Reset job status to ${JobStatus.Uninitialized}`});
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Reset job status workflow key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(joi.object(), 'message')
    .summary('Reset job status.')
    .description(`Reset status for all jobs to ${JobStatus.Uninitialized}.`);

router.get('/workflows/status/:key', function(req, res) {
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(key, res);
  try {
    const status = query.getWorkflowStatus(workflow);
    res.send(status);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get workflow status key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(schemas.workflowStatus)
    .summary('Reports the workflow status.')
    .description('Reports the workflow status.');

router.put('/workflows/status/:key', function(req, res) {
  const status = req.body;
  const key = req.pathParams.key;
  // Validate that the workflow key is correct.
  documents.getWorkflow(key, res);
  try {
    db.workflow_statuses.update(status, status);
    res.send(status);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Update workflow status key=${key}`);
  }
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .body(schemas.workflowStatus, 'Updated workflow status')
    .response(schemas.workflowStatus)
    .summary('Reports the workflow status.')
    .description('Reports the workflow status.');

router.get('/workflows/collection_names/:key', function(req, res) {
  const workflow = documents.getWorkflow(req.pathParams.key, res);
  res.send({names: documents.listWorkflowCollectionNames(workflow)});
})
    .pathParam('key', joi.string().required(), 'Workflow key')
    .response(joi.object().required().keys({names: joi.array().items(joi.string())}))
    .summary('Retrieve all collection names for one workflow.')
    .description('Retrieve all collection names for one workflow.');
