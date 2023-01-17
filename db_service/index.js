'use strict';

const eventsRouter = require('./api/documents/events');
const resultsRouter = require('./api/documents/results');
module.context.use('/', eventsRouter);
module.context.use('/', resultsRouter);

const workflowRouter = require('./api/workflow');
const filesRouter = require('./api/nodes/files');
const hpcConfigsRouter = require('./api/nodes/hpcConfigs');
const jobDefinitionsRouter = require('./api/nodes/jobDefinitions');
const jobsRouter = require('./api/nodes/jobs');
const resourcesRouter = require('./api/nodes/resourceRequirements');
module.context.use('/', workflowRouter);
module.context.use('/', filesRouter);
module.context.use('/', hpcConfigsRouter);
module.context.use('/', jobDefinitionsRouter);
module.context.use('/', jobsRouter);
module.context.use('/', resourcesRouter);

const blocksRouter = require('./api/edges/blocks');
const needsRouter = require('./api/edges/needs');
const producesRouter = require('./api/edges/produces');
const requiresRouter = require('./api/edges/requires');
const scheduledBysRouter = require('./api/edges/scheduledBys');
module.context.use('/', needsRouter);
module.context.use('/', producesRouter);
module.context.use('/', blocksRouter);
module.context.use('/', scheduledBysRouter);
module.context.use('/', requiresRouter);
