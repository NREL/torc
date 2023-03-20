'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const query = require('../../query');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.get('/results/find_by_job/:key', function(req, res) {
  const job = db.jobs.document(req.pathParams.key);
  const result = query.getLatestJobResult(job);
  if (result == null) {
    res.throw(404, `No result is stored for job ${req.pathParams.key}`);
  }
  res.send(result);
})
    .pathParam('key', joi.string().required(), 'Job key')
    .response(schemas.result)
    .summary('Retrieve the latest result for a job')
    .description('Retrieve the latest result for a job. Throws an error if no result is stored.');
