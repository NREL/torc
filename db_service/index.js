'use strict';

const eventsRouter = require('./src/api/documents/events');
module.context.use('/', eventsRouter);

const workflowRouter = require('./src/api/workflow');
const filesRouter = require('./src/api/nodes/files');
const hpcConfigsRouter = require('./src/api/nodes/hpcConfigs');
const jobDefinitionsRouter = require('./src/api/nodes/jobDefinitions');
const jobsRouter = require('./src/api/nodes/jobs');
const resourcesRouter = require('./src/api/nodes/resourceRequirements');
const resultsRouter = require('./src/api/nodes/results');
const userDataRouter = require('./src/api/nodes/userData');
module.context.use('/', workflowRouter);
module.context.use('/', filesRouter);
module.context.use('/', hpcConfigsRouter);
module.context.use('/', jobDefinitionsRouter);
module.context.use('/', jobsRouter);
module.context.use('/', resourcesRouter);
module.context.use('/', resultsRouter);
module.context.use('/', userDataRouter);

const blocksRouter = require('./src/api/edges/blocks');
const needsRouter = require('./src/api/edges/needs');
const producesRouter = require('./src/api/edges/produces');
const requiresRouter = require('./src/api/edges/requires');
const returnedRouter = require('./src/api/edges/returned');
const scheduledBysRouter = require('./src/api/edges/scheduledBys');
const storesRouter = require('./src/api/edges/stores');
module.context.use('/', needsRouter);
module.context.use('/', producesRouter);
module.context.use('/', blocksRouter);
module.context.use('/', requiresRouter);
module.context.use('/', returnedRouter);
module.context.use('/', scheduledBysRouter);
module.context.use('/', storesRouter);
