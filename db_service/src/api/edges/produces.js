const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const graph = graphModule._graph(defs.GRAPH_NAME);
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/produces', function(req, res) {
  const data = req.body;
  const meta = graph.produces.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'produces relationship between a job and a file.')
    .response(schemas.edge, 'Edge')
    .summary('Store a produces edge between a job and a file.')
    .description('Store a job-file relationship in the "produces" edge collection.');

router.get('/produces/:key', function(req, res) {
  try {
    const data = graph.produces.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The produce does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the produces edge.')
    .response(schemas.edge, 'produces edge stored in the collection.')
    .summary('Retrieve a produces edge')
    .description('Retrieves a produces edge from the "produces" collection by key.');

router.get('/produces', function(req, res) {
  try {
    const data = graph.produces.toArray();
    res.send(data);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .response(joi.array().items(schemas.edge))
    .summary('Retrieve all produces edges')
    .description('Retrieves all produces edges from the "produces" collection.');

router.delete('/produces/:key', function(req, res) {
  try {
    const data = graph.produces.document(req.pathParams.key);
    db._remove(`produces/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The produce does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the produce.')
    .response(schemas.edge, 'produces edge stored in the collection.')
    .summary('Delete a produces edge')
    .description('Deletes a produces edge from the "produces" collection by key.');

router.delete('/produces', function(req, res) {
  try {
    db._truncate(`produces`);
    res.send({message: 'Deleted all edges in the "produces" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .response(joi.object(), 'message')
    .summary('Delete all produces edges')
    .description('Deletes all edges from the "produces" collection.');
