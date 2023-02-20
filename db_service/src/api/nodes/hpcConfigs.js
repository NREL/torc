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

router.post('/hpc_configs', function(req, res) {
  const doc = query.addHpcConfig(req.body);
  res.send(doc);
})
    .body(schemas.hpcConfig, 'hpc_config to store in the collection')
    .response(schemas.hpcConfig, 'hpc_config stored in the collection')
    .summary('Store an hpc_config.')
    .description('Store an hpc_config in the "hpc_configs" collection.');

router.get('/hpc_configs/:name', function(req, res) {
  const exists = graph.hpc_configs.exists(req.pathParams.name);
  console.log(`TODO: exists=${exists}`);
  if (!exists) {
    if (req.pathParams.name == 'default') {
      const config = {
        name: 'default',
        hpc_type: 'slurm',
        account: 'fill-in-your-account',
      };
      res.send(schemas.hpcConfig.validate(config).value);
    } else {
      res.throw(404, 'Document does not exist');
    }
  } else {
    const data = graph.hpc_configs.document(req.pathParams.name);
    res.send(data);
  }
})
    .response(schemas.hpcConfig)
    .summary('Retrieve an hpc_config document by name')
    .description('Retrieves an hpc_config document from the "hpc_configs" collection.');

router.get('/hpc_configs', function(req, res) {
  try {
    const qp = req.queryParams;
    const limit = getItemsLimit(qp.limit);
    const items = graph.hpc_configs.all().skip(qp.skip).limit(limit).toArray();
    res.send(makeCursorResult(items, qp.skip, limit, graph.hpc_configs.count()));
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Unknown error', e);
  }
})
    .queryParam('skip', joi.number().default(0))
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .response(schemas.batchHpcConfigs)
    .summary('Retrieve all hpc_configs')
    .description('Retrieves all hpc_configs from the "hpc_configs" collection.');

router.delete('/hpc_configs/:name', function(req, res) {
  try {
    const data = graph.hpc_configs.document(req.pathParams.name);
    db._remove(`hpc_configs/${req.pathParams.name}`);
    res.send(data);
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The hpc_config does not exist', e);
  }
})
    .pathParam('name', joi.string().required(), 'Name of the hpc_config.')
    .body(joi.object().optional())
    .response(schemas.hpcConfig, 'hpc_config stored in the collection.')
    .summary('Delete a hpc_config')
    .description('Deletes a hpc_config from the "hpc_configs" collection by name.');

router.delete('/hpc_configs', function(req, res) {
  try {
    db._truncate(`hpc_configs`);
    res.send({message: 'Deleted all documents in the "hpc_configs" collection'});
  } catch (e) {
    if (!e.isArangoError) {
      throw e;
    }
    res.throw(404, 'Error occurred', e);
  }
})
    .body(joi.object().optional())
    .response(joi.object(), 'message')
    .summary('Delete all hpc_configs')
    .description('Deletes all hpc_configs from the "hpc_configs" collection.');
