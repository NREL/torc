'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const graphModule = require('@arangodb/general-graph');
const {GRAPH_NAME, MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(GRAPH_NAME);
const query = require('../../query');
const schemas = require('../schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/resource_requirements', function(req, res) {
  try {
    const doc = query.addResourceRequirements(req.body);
    res.send(doc);
  } catch (e) {
    res.throw(400, 'Error', e);
  }
})
    .body(schemas.resourceRequirements, 'resource to store in the collection')
    .response(schemas.resourceRequirements, 'resource stored in the collection')
    .summary('Store a resource.')
    .description('Store a resource in the "resource_requirements" collection.');

router.get('/resource_requirements/:name', function(req, res) {
  const exists = graph.resource_requirements.exists(req.pathParams.name);
  if (!exists) {
    if (req.pathParams.name == 'default') {
      res.send(schemas.resourceRequirements.validate({name: 'default'}).value);
    } else {
      res.throw(404, 'Document does not exist');
    }
  } else {
    const data = graph.resource_requirements.document(req.pathParams.name);
    res.send(data);
  }
})
    .response(schemas.resourceRequirements)
    .summary('Retrieve a resource requirements document by name')
    .description('Retrieve a resource requirements document by name.');

router.get('/resource_requirements', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.resource_requirements.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.resource_requirements.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchResourceRequirements)
    .summary('Retrieve all resource requirements')
    .description('Retrieves all requirement from the "resource_requirements" collection.');

router.delete('/resource_requirements/:name', function(req, res) {
  try {
    const data = graph.resource_requirements.document(req.pathParams.name);
    db._remove(`resource_requirements/${req.pathParams.name}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The resource does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the resource.')
    .body(joi.object().optional())
    .response(schemas.resourceRequirements, 'resource stored in the collection.')
    .summary('Delete a resource')
    .description('Deletes a resource from the "resource_requirements" collection by name.');

router.delete('/resource_requirements', function(req, res) {
  try {
    db._truncate(`resource_requirements`);
    res.send({message: 'Deleted all documents in the "resource_requirements" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all resource_requirements')
    .description('Deletes all documents from the "resource_requirements" collection.');
