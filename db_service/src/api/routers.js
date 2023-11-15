'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const {MAX_TRANSFER_RECORDS} = require('../defs');
const utils = require('../utils');
const config = require('../config');
const documents = require('../documents');

/**
 * Add router methods for an endpoint from a descriptor.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addRouterMethods(router, descriptor) {
  if (!('excludePost' in descriptor && descriptor['excludePost'])) {
    addPostMethod(router, descriptor);
  }
  addPutMethod(router, descriptor);
  addGetOneMethod(router, descriptor);
  addGetAllMethod(router, descriptor);
  addDeleteOneMethod(router, descriptor);
  addDeleteAllMethod(router, descriptor);
}

/**
 * Generate a POST method.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addPostMethod(router, descriptor) {
  router.post(`/workflows/:workflow/${descriptor.collection}`, function(req, res) {
    const workflowKey = req.pathParams.workflow;
    const workflow = documents.getWorkflow(workflowKey, res);
    let doc = req.body;

    if (descriptor.collection == 'events') {
      doc.timestamp = Date.now();
    }
    try {
      if (descriptor.customPost != null) {
        doc = descriptor.customPost(doc, workflow);
      } else {
        const collection = config.getWorkflowCollection(workflow, descriptor.collection);
        const meta = collection.save(doc);
        Object.assign(doc, meta);
      }
      if (descriptor.customConvert != null) {
        doc = descriptor.customConvert(doc);
      }
      res.send(doc);
    } catch (e) {
      utils.handleArangoApiErrors(e, res, `Post ${descriptor.collection} document`);
    }
  })
      .pathParam('workflow', joi.string().required(), 'Workflow key')
      .body(descriptor.schema, `${descriptor.name}.`)
      .response(descriptor.schema, `Response from posting an instance of ${descriptor.name}.`)
      .summary(`Store a ${descriptor.name}.`)
      .description(`Store a ${descriptor.name} in the "${descriptor.collection}" collection.`);
}

/**
 * Generate a PUT method.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addPutMethod(router, descriptor) {
  router.put(`/workflows/:workflow/${descriptor.collection}/:key`, function(req, res) {
    const key = req.pathParams.key;
    const workflowKey = req.pathParams.workflow;
    const workflow = documents.getWorkflow(workflowKey, res);
    const collection = config.getWorkflowCollection(workflow, descriptor.collection);
    let doc = req.body;
    if (doc._rev == null) {
      res.throw(400, `Updating a document requires the existing revision`);
    }
    if (key != doc._key) {
      res.throw(400, `key=${key} does not match ${doc._key}`);
    }

    try {
      const meta = collection.update(doc, doc, {mergeObjects: false});
      Object.assign(doc, meta);
      if (descriptor.customConvert) {
        doc = descriptor.customConvert(doc);
      }
      res.send(doc);
    } catch (e) {
      utils.handleArangoApiErrors(e, res, `Update ${descriptor.collection} key=${key}`);
    }
  })
      .pathParam('workflow', joi.string().required(), 'Workflow key.')
      .pathParam('key', joi.string().required(), `key of the ${descriptor.name}.`)
      .body(descriptor.schema, `${descriptor.name} to update in the collection.`)
      .response(descriptor.schema, `${descriptor.name} updated in the collection.`)
      .summary(`Update ${descriptor.name}`)
      .description(`Update a document in the "${descriptor.collection}" collection.`);
}

/**
 * Generate a GET method for one document.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addGetOneMethod(router, descriptor) {
  router.get(`/workflows/:workflow/${descriptor.collection}/:key`, function(req, res) {
    const workflowKey = req.pathParams.workflow;
    const key = req.pathParams.key;
    const workflow = documents.getWorkflow(workflowKey, res);
    let doc = documents.getWorkflowDocument(workflow, descriptor.collection, key, res);
    try {
      if (descriptor.customConvert != null) {
        doc = descriptor.customConvert(doc);
      }
      res.send(doc);
    } catch (e) {
      utils.handleArangoApiErrors(e, res, `Get ${descriptor.collection} document with key=${key}`);
    }
  })
      .pathParam('workflow', joi.string().required(), 'Workflow key')
      .pathParam('key', joi.string().required(), `key of the ${descriptor.collection} document`)
      .response(descriptor.schema)
      .summary(`Retrieve the ${descriptor.name} for a key.`)
      .description(`Retrieve the document from the "${descriptor.collection}" collection by key.`);
}

/**
 * Generate a GET method for all documents with filters.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addGetAllMethod(router, descriptor) {
  const getAll = router.get(`/workflows/:workflow/${descriptor.collection}`, function(req, res) {
    const qp = req.queryParams;
    const limit = utils.getItemsLimit(qp.limit);
    const workflowKey = req.pathParams.workflow;
    const workflow = documents.getWorkflow(workflowKey, res);
    const collection = config.getWorkflowCollection(workflow, descriptor.collection);
    try {
      const example = {};
      for (const filterField of descriptor.filterFields) {
        if (qp[filterField.name] != null) {
          example[filterField.name] = qp[filterField.name];
        }
      }
      const totalCount = Object.keys(example).length == 0 ? collection.count() :
        collection.byExample(example).count();
      let cursor = Object.keys(example).length == 0 ?
        collection.all().skip(qp.skip) :
        collection.byExample(example).skip(qp.skip);

      if (limit != null) {
        cursor = cursor.limit(limit);
      }

      const items = [];
      for (const doc of cursor) {
        if (descriptor.customConvert) {
          items.push(descriptor.customConvert(doc));
        } else {
          items.push(doc);
        }
      }
      res.send(utils.makeCursorResult(items, qp.skip, totalCount, qp.sort_by, qp.reverse_sort));
    } catch (e) {
      utils.handleArangoApiErrors(e, res, `Get ${descriptor.collection} documents`);
    }
  })
      .pathParam('workflow', joi.string().required(), 'Workflow key')
      .queryParam('skip', joi.number().default(0))
      .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
      .queryParam('sort_by', joi.string().default(null))
      .queryParam('reverse_sort', joi.boolean().default(false))
      .response(descriptor.batchSchema)
      .summary(`Retrieve all ${descriptor.name} documents`)
      .description(`Retrieve all documents from the "${descriptor.collection}" collection for ` +
      `one workflow.`);
  for (const filterField of descriptor.filterFields) {
    getAll.queryParam(filterField.name, filterField.type);
  }
}

/**
 * Generate a DELETE method for one document.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addDeleteOneMethod(router, descriptor) {
  router.delete(`/workflows/:workflow/${descriptor.collection}/:key`, function(req, res) {
    const workflowKey = req.pathParams.workflow;
    const key = req.pathParams.key;
    const workflow = documents.getWorkflow(workflowKey, res);
    const doc = documents.getWorkflowDocument(workflow, `${descriptor.collection}`, key, res);
    const collectionName = config.getWorkflowCollectionName(workflow, descriptor.collection);
    const graph = config.getWorkflowGraph(workflow);
    try {
      if (config.DOCUMENT_COLLECTION_NAMES.includes(descriptor.collection)) {
        db._remove(doc._id);
      } else {
        // This removes all connected edges.
        graph[collectionName].remove(doc._key);
      }
      res.send(doc);
    } catch (e) {
      utils.handleArangoApiErrors(e, res,
          `Delete ${descriptor.collection} document with key=${key}`);
    }
  })
      .pathParam('workflow', joi.string().required(), 'Workflow key')
      .pathParam('key', joi.string().required(), `key of the ${descriptor.name} document.`)
      .body(joi.object().optional())
      .response(descriptor.schema, `${descriptor.name} stored in the collection.`)
      .summary(`Delete a document of type ${descriptor.name}`)
      .description(`Deletes a document from the "${descriptor.collection}" collection by key.`);
}

/**
 * Generate a DELETE method for all documents.
 * @param {Object} router
 * @param {Object} descriptor
 */
function addDeleteAllMethod(router, descriptor) {
  router.delete(`/workflows/:workflow/${descriptor.collection}`, function(req, res) {
    const workflowKey = req.pathParams.workflow;
    const workflow = documents.getWorkflow(workflowKey, res);
    const graph = config.getWorkflowGraph(workflow);
    const collectionName = config.getWorkflowCollectionName(workflow, descriptor.collection);
    try {
      if (config.DOCUMENT_COLLECTION_NAMES.includes(descriptor.collection)) {
        db._truncate(collectionName);
      } else {
        for (const doc of graph[collectionName].all()) {
          // This removes all connected edges.
          graph[collectionName].remove(doc._key);
        }
      }
      res.send({message: `Deleted all documents in the "${descriptor.collection}" collection ` +
      `for workflow ${workflowKey}`});
    } catch (e) {
      utils.handleArangoApiErrors(e, res, `Delete all ${collectionName} documents`);
    }
  })
      .pathParam('workflow', joi.string().required(), 'Workflow key')
      .body(joi.object().optional())
      .response(joi.object(), 'message')
      .summary(`Delete all documents of type ${descriptor.name} for a workflow`)
      .description(`Delete all documents from the "${descriptor.collection}" collection for a ` +
        `workflow.`);
}

module.exports = {
  addRouterMethods,
};
