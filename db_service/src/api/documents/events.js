const joi = require('joi');
const db = require('@arangodb').db;
const createRouter = require("@arangodb/foxx/router");
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
    const data = db.events.toArray();
    res.send(data);
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .response(joi.array().items(joi.object().required()))
    .summary('Retrieve all events')
    .description('Retrieves all events from the "events" collection.');

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
    .response(joi.object(), 'message')
    .summary('Delete all events')
    .description('Deletes all events from the "events" collection.');
