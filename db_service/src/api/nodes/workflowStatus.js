'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const schemas = require('../schemas');
const query = require('../../query');
const router = createRouter();
module.exports = router;

router.put('/workflow_status', function(req, res) {
  const doc = req.body;
  if (doc._rev == null) {
    res.throw(400, 'Updating workflow status requires the existing revision');
    return;
  }

  try {
    const meta = db.workflow_status.update(doc, doc);
    Object.assign(doc, meta);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The workflow status does not exist', e);
  }
})
    .body(joi.object().required(), 'Updated workflow status')
    .response(schemas.workflowStatus, 'Updated workflow status')
    .summary('Update workflow status')
    .description('Update workflow status in the "workflow_status" collection.');

router.get('/workflow_status', function(req, res) {
  let doc = query.getWorkflowStatus();
  if (doc == null) {
    doc = {
      run_id: 0,
      is_canceled: false,
      scheduled_compute_node_ids: [],
      auto_tune_status: schemas.autoTuneStatus.validate({}).value,
    };
  }
  res.send(doc);
})
    .response(schemas.workflowStatus)
    .summary('Retrieve the current workflow status.')
    .description('Retrieve the current workflow status.');

router.put('/workflow_status/reset', function(req, res) {
  query.resetWorkflowStatus();
  res.send(query.getWorkflowStatus());
})
    .response(schemas.workflowStatus, 'Updated workflow status')
    .summary('Reset workflow status')
    .description('Rest workflow status in the "workflow_status" collection.');
