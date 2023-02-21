'use strict';

const eventsRouter = require('./src/api/documents/events');
module.context.use('/', eventsRouter);

const workflowRouter = require('./src/api/workflow');
const computeNodesRouter = require('./src/api/nodes/compute_nodes');
const computeNodeStatsRouter = require('./src/api/nodes/compute_node_stats');
const filesRouter = require('./src/api/nodes/files');
const hpcConfigsRouter = require('./src/api/nodes/hpcConfigs');
const jobDefinitionsRouter = require('./src/api/nodes/jobDefinitions');
const jobProcessStatsRouter = require('./src/api/nodes/job_process_stats');
const jobsRouter = require('./src/api/nodes/jobs');
const resourcesRouter = require('./src/api/nodes/resourceRequirements');
const resultsRouter = require('./src/api/nodes/results');
const userDataRouter = require('./src/api/nodes/userData');
const edgesRouter = require('./src/api/edges');
module.context.use('/', workflowRouter);
module.context.use('/', computeNodesRouter);
module.context.use('/', computeNodeStatsRouter);
module.context.use('/', filesRouter);
module.context.use('/', hpcConfigsRouter);
module.context.use('/', jobDefinitionsRouter);
module.context.use('/', jobProcessStatsRouter);
module.context.use('/', jobsRouter);
module.context.use('/', resourcesRouter);
module.context.use('/', resultsRouter);
module.context.use('/', userDataRouter);
module.context.use('/', edgesRouter);
