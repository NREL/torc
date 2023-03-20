'use strict';
const joi = require('joi');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const schemas = require('../schemas');
const query = require('../../query');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;


router.get('/files/produced_by_job/:key', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const cursor = query.getFilesProducedByJob(req.pathParams.key);
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
    .pathParam('key', joi.string().required(), 'Job key')
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchFiles)
    .summary('Retrieve files produced by a job')
    .description('Retrieves files from the "files" collection produced by a job.');
