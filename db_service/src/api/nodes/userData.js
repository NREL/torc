const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(defs.GRAPH_NAME);
const createRouter = require('@arangodb/foxx/router');
const query = require('../../query');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/user_data', function(req, res) {
  const doc = query.addUserData(req.body);
  res.send(doc);
})
    .body(joi.object(), 'User data.')
    .response(joi.object(), 'User data')
    .summary('Store user data for a job.')
    .description('Store user data in the "user_data" collection.');

router.get('/user_data', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.user_data.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.user_data.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchUserData)
    .summary('Retrieve all user data objects')
    .description('Retrieves all user data from the "user_data" collection.');

router.get('/user_data/:key', function(req, res) {
  try {
    const key = req.pathParams.key;
    const doc = graph.user_data.document(key);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the user_data object')
    .response(joi.object())
    .summary('Retrieve the user data object for a key.')
    .description('Retrieve the user data object for a key.');

router.delete('/user_data/:key', function(req, res) {
  try {
    const cursor = graph.user_data.document(req.pathParams.key);
    db._remove(`user_data/${req.pathParams.key}`);
    res.send(cursor);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The user data does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the user data object.')
    .body(joi.object().optional())
    .response(joi.object().required(), 'User data stored in the collection.')
    .summary('Delete a user data object')
    .description('Deletes a user data object from the "user_data" collection by key.');

router.delete('/user_data', function(req, res) {
  try {
    db._truncate(`user_data`);
    res.send({message: 'Deleted all user data in the "user_data" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all user data')
    .description('Deletes all user data from the "user_data" collection.');
