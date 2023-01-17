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

router.post('/blocks', function(req, res) {
  const data = req.body;
  const meta = graph.blocks.save(data);
  res.send(Object.assign(data, meta));
})
    .body(schemas.edge, 'blocks relationship between a job and a file.')
    .response(schemas.edge, 'Edge')
    .summary('Store a blocks edge between a job and a file.')
    .description('Store a job-file relationship in the "blocks" edge collection.');

router.get('/blocks/:key', function(req, res) {
  try {
    const data = graph.blocks.document(req.pathParams.key);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The block does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the block.')
    .response(schemas.edge, 'blocks edge stored in the collection.')
    .summary('Retrieve a blocks edge')
    .description('Retrieves a blocks edge from the "blocks" collection by key.');

router.get('/blocks', function(req, res) {
  try {
    const data = graph.blocks.toArray();
    res.send(data);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .response(joi.array().items(schemas.edge))
    .summary('Retrieve all blocks edges')
    .description('Retrieves all blocks edges from the "blocks" collection.');

router.delete('/blocks/:key', function(req, res) {
  try {
    const data = graph.blocks.document(req.pathParams.key);
    db._remove(`blocks/${req.pathParams.key}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The blocks edge does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the block.')
    .response(schemas.edge, 'block stored in the collection.')
    .summary('Delete a block')
    .description('Deletes a blocks edge from the "blocks" collection by key.');

router.delete('/blocks', function(req, res) {
  try {
    db._truncate(`blocks`);
    res.send({message: 'Deleted all edges in the "blocks" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .response(joi.object(), 'message')
    .summary('Delete all blocks edges')
    .description('Deletes all edges from the "blocks" collection.');
