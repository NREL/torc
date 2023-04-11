'use strict';
const joi = require('joi');
const createRouter = require('@arangodb/foxx/router');
const documents = require('../documents');
const query = require('../query');
const schemas = require('./schemas');
const router = createRouter();
module.exports = router;

router.get('/workflows/:workflow/results/find_by_job/:key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const job = documents.getWorkflowDocument(workflow, 'jobs', key, res);
  const result = query.getLatestJobResult(job, workflow);
  if (result == null) {
    res.throw(404, `No result is stored for job ${key}`);
  }
  res.send(result);
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.result)
    .summary('Retrieve the latest result for a job')
    .description('Retrieve the latest result for a job. Throws an error if no result is stored.');
