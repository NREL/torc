const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require('@arangodb/foxx/router');
const {MAX_TRANSFER_RECORDS} = require('../../defs');
const {getItemsLimit, makeCursorResult} = require('../../utils');
const schemas = require('../schemas');
const router = createRouter();
module.exports = router;

router.post('/events', function(req, res) {
  const data = req.body;
  if (data.timestamp == null) {
    data.timestamp = new Date().toISOString();
  }
  const meta = db.events.save(data);
  res.send(Object.assign(data, meta));
})
    .body(joi.object().required(), 'event.')
    .response(joi.object().required(), 'event')
    .summary('Store an event.')
    .description('Store an event in the "events" collection.');

router.get('/events', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = db.events.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, db.events.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchObjects)
    .summary('Retrieve all events')
    .description('Retrieves all events from the "events" collection.');

router.get('/events/:key', function(req, res) {
  try {
    const key = req.pathParams.key;
    const doc = graph.events.document(key);
    res.send(doc);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the events object')
    .response(joi.object())
    .summary('Retrieve the event for a key.')
    .description('Retrieve the event for a key.');

router.delete('/events/:key', function(req, res) {
  try {
    const cursor = graph.events.document(req.pathParams.key);
    db._remove(`events/${req.pathParams.key}`);
    res.send(cursor);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The user data does not exist', e);
  }
})
    .pathParam('key', joi.string().required(), 'Key of the event.')
    .body(joi.object().optional())
    .response(joi.object().required(), 'Event stored in the collection.')
    .summary('Delete an event')
    .description('Deletes an event from the "events" collection by key.');

router.delete('/events', function(req, res) {
  try {
    db._truncate(`events`);
    res.send({message: 'Deleted all documents in the "events" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all events')
    .description('Deletes all events from the "events" collection.');
