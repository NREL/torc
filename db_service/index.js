'use strict';

const eventsRouter = require('./src/api/documents/events');
const resultsRouter = require('./src/api/documents/results');
module.context.use('/', eventsRouter);
module.context.use('/', resultsRouter);

const workflowRouter = require('./src/api/workflow');
const filesRouter = require('./src/api/nodes/files');
const hpcConfigsRouter = require('./src/api/nodes/hpcConfigs');
const jobDefinitionsRouter = require('./src/api/nodes/jobDefinitions');
const jobsRouter = require('./src/api/nodes/jobs');
const resourcesRouter = require('./src/api/nodes/resourceRequirements');
module.context.use('/', workflowRouter);
module.context.use('/', filesRouter);
module.context.use('/', hpcConfigsRouter);
module.context.use('/', jobDefinitionsRouter);
module.context.use('/', jobsRouter);
module.context.use('/', resourcesRouter);

const blocksRouter = require('./src/api/edges/blocks');
const needsRouter = require('./src/api/edges/needs');
const producesRouter = require('./src/api/edges/produces');
const requiresRouter = require('./src/api/edges/requires');
const scheduledBysRouter = require('./src/api/edges/scheduledBys');
module.context.use('/', needsRouter);
module.context.use('/', producesRouter);
module.context.use('/', blocksRouter);
module.context.use('/', scheduledBysRouter);
module.context.use('/', requiresRouter);
