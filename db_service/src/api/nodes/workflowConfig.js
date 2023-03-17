'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const schemas = require('../schemas');
const query = require('../../query');
const router = createRouter();
module.exports = router;

router.post('/workflow_config', function(req, res) {
  const doc = req.body;
  if (doc._key != null) {
    res.throw(400, `${doc._key} cannot be set on POST for workflow_config`);
    return;
  }

  if (query.getWorkflowConfig() != null) {
    res.throw(400, 'POST workflow_config is not allowed if it is already set');
    return;
  }

  const meta = db.workflow_config.save(doc);
  Object.assign(doc, meta);
  res.send(doc);
})
    .body(schemas.workflowConfig, 'Workflow config')
    .response(schemas.workflowConfig, 'Workflow config')
    .summary('Set workflow config')
    .description('Set workflow config in the "workflow_config" collection.');

router.put('/workflow_config', function(req, res) {
  const doc = req.body;
  try {
    if (query.getWorkflowConfig() == null) {
      const meta = db.workflow_config.save(doc);
      Object.assign(doc, meta);
    } else {
      const meta = db.workflow_config.update(doc, doc);
      Object.assign(doc, meta);
    }
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The workflow config does not exist', e);
  }
})
    .body(schemas.workflowConfig, 'Updated workflow config')
    .response(schemas.workflowConfig, 'Updated workflow config')
    .summary('Update workflow config')
    .description('Update workflow config in the "workflow_config" collection.');

router.get('/workflow_config', function(req, res) {
  let doc = query.getWorkflowConfig();
  if (doc == null) {
    doc = {
      computeNodeResourceStatConfig: schemas.computeNodeResourceStatConfig.validate({}).value,
    };
  }
  res.send(doc);
})
    .response(schemas.workflowConfig)
    .summary('Retrieve the current workflow config.')
    .description('Retrieve the current workflow config.');

router.put('/workflow_config/reset', function(req, res) {
  query.resetWorkflowConfig();
  const config = query.getWorkflowConfig();
  res.send(config);
})
    .response(schemas.workflowConfig, 'Updated workflow config')
    .summary('Reset workflow config')
    .description('Rest workflow config in the "workflow_config" collection.');
