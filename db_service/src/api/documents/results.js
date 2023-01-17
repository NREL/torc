const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require("@arangodb/foxx/router");
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/results', function(req, res) {
  const data = req.body;
  data._key = data.name;
  const meta = db.results.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.result, 'Job result.')
    .response(schemas.result, 'result')
    .summary('Store a job result.')
    .description('Store a job result in the "results" collection.');

router.get('/results', function(req, res) {
  try {
    const data = db.results.toArray();
    res.send(data);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .response(joi.array().items(joi.object().required()))
    .summary('Retrieve all results')
    .description('Retrieves all results from the "results" collection.');

router.delete('/results', function(req, res) {
  try {
    db._truncate(`results`);
    res.send({message: 'Deleted all documents in the "results" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .response(joi.object(), 'message')
    .summary('Delete all results')
    .description('Deletes all results from the "results" collection.');
