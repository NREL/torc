'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const CONFLICTING_REV = errors.ERROR_ARANGO_CONFLICT.code;
const graphModule = require('@arangodb/general-graph');
const defs = require('../../defs');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const graph = graphModule._graph(defs.GRAPH_NAME);
const schemas = require('../schemas');
const query = require('../../query');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

router.post('/files', function(req, res) {
  const doc = query.addFile(req.body);
  res.send(doc);
})
    .body(schemas.file, 'file to store in the collection.')
    .response(schemas.file, 'file stored in the collection.')
    .summary('Store file')
    .description('Store a file in the "files" collection.');

router.put('/files/:name', function(req, res) {
  const doc = req.body;
  if (doc._rev == null) {
    res.throw(400, 'Updating a file requires the existing revision');
  }

  try {
    const existingDoc = graph.files.document(req.pathParams.name);
    Object.assign(existingDoc, doc);
    try {
      const meta = db.files.update(doc, existingDoc);
      res.send(Object.assign(doc, meta));
    } catch (e) {
      if (!e.isArangoError || e.errorNum !== CONFLICTING_REV) {
        throw e;
      }
      res.throw(400, `Update contains a conflicting revision: ${doc._rev}`, e);
    }
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The file does not exist', e);
  }
})
    .body(joi.object().required(), 'file to update in the collection.')
    .response(schemas.file, 'file updated in the collection.')
    .summary('Update file')
    .description('Update a file in the "files" collection.');

router.get('/files/:name', function(req, res) {
  try {
    const data = graph.files.document(req.pathParams.name);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The file does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the file.')
    .response(schemas.file, 'file stored in the collection.')
    .summary('Retrieve a file')
    .description('Retrieves a file from the "files" collection by name.');

router.get('/files', function(req, res) {
  const qp = req.queryParams;
  const limit = getItemsLimit(qp.limit);
  const items = graph.files.all().skip(qp.skip).limit(limit).toArray();
  res.send(makeCursorResult(items, qp.skip, limit, graph.files.count()));
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchFiles)
    .summary('Retrieve all files')
    .description('Retrieves all files from the "files" collection.');

router.get('/files/produced_by_job/:name', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const cursor = query.getFilesProducedByJob(req.pathParams.name);
    // TODO: how to do this with Arango cursor?
    const items = [];
    let i = 0;
    for (const item of cursor) {
      if (i > qp.skip) {
        i++;
        continue;
      }
      items.push(item);
      if (items.length == limit) {
        break;
      }
    }
    res.send(makeCursorResult(items, qp.skip, limit, cursor.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchFiles)
    .summary('Retrieve files produced by a job')
    .description('Retrieves files from the "files" collection produced by a job.');

router.delete('/files/:name', function(req, res) {
  try {
    const data = graph.files.document(req.pathParams.name);
    db._remove(`files/${req.pathParams.name}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The file does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the file.')
    .body(joi.object().optional())
    .response(schemas.file, 'file stored in the collection.')
    .summary('Delete a file')
    .description('Deletes a file from the "files" collection by name.');

router.delete('/files', function(req, res) {
  try {
    db._truncate(`files`);
    res.send({message: 'Deleted all documents in the "files" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all files')
    .description('Deletes all files from the "files" collection.');
