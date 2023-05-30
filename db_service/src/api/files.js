'use strict';
const joi = require('joi');
const {MAX_TRANSFER_RECORDS} = require('../defs');
const schemas = require('./schemas');
const config = require('../config');
const documents = require('../documents');
const utils = require('../utils');
const query = require('../query');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;


router.get('/workflows/:workflow/files/produced_by_job/:key', function(req, res) {
  const workflowKey = req.pathParams.workflow;
  const key = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const qp = req.queryParams;

  try {
    const limit = utils.getItemsLimit(qp.limit);
    const job = jobs.document(key);
    const cursor = query.listFilesProducedByJob(job, workflow);
    // TODO: how to do this with Arango cursor?
    const items = [];
    let i = 0;
    for (const item of cursor) {
      if (i > qp.skip) {
        i++;
        continue;
      }
      items.push(item);
      if (items.length == limit) {
        break;
      }
    }
    res.send(utils.makeCursorResult(items, qp.skip, cursor.count()));
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get files produced_by_job key=${key}`);
  }
})
    .pathParam('workflow', joi.string().required(), 'Workflow key')
    .pathParam('key', joi.string().required(), 'Job key')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchFiles)
    .summary('Retrieve files produced by a job')
    .description('Retrieves files from the "files" collection produced by a job.');
