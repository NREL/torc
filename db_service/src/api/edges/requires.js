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

router.post('/requires', function(req, res) {
  const data = req.body;
  const meta = graph.requires.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'requires relationship between a job and a resource.')
    .response(schemas.edge, 'Edge')
    .summary('Store a requires edge between a job and a resource.')
    .description('Store a job-resource relationship in the "requires" edge collection.');

router.get('/requires/:key', function(req, res) {
  try {
    const data = graph.requires.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The requires edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the require.')
    .response(schemas.edge, 'require stored in the collection.')
    .summary('Retrieve a require')
    .description('Retrieves a requires edge edge from the "requires" collection by key.');

router.get('/requires', function(req, res) {
  try {
    const data = graph.requires.toArray();
    res.send(data);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .response(joi.array().items(schemas.edge))
    .summary('Retrieve all requires')
    .description('Retrieves all requires edges from the "requires" collection.');

router.delete('/requires/:key', function(req, res) {
  try {
    const data = graph.requires.document(req.pathParams.key);
    db._remove(`requires/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The requires edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the require.')
    .response(schemas.edge, 'requires edge stored in the collection.')
    .summary('Delete a require')
    .description('Deletes a requires edge from the "requires" collection by key.');

router.delete('/requires', function(req, res) {
  try {
    db._truncate(`requires`);
    res.send({message: 'Deleted all edges in the "requires" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .response(joi.object(), 'message')
    .summary('Delete all requires edges')
    .description('Deletes all edges from the "requires" collection.');
