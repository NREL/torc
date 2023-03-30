'use strict';

const routers = require('./src/api/routersFromDescriptors.js');
const edgesRouter = require('./src/api/edges');
const filesRouter = require('./src/api/files');
const jobSpecificationsRouter = require('./src/api/jobSpecifications');
const jobsRouter = require('./src/api/jobs');
const resultsRouter = require('./src/api/results');
const workflowConfigRouter = require('./src/api/workflowConfig');
const workflowSpecificationsRouter = require('./src/api/workflowSpecifications');
const workflowsRouter = require('./src/api/workflows');

module.context.use('/', routers);
module.context.use('/', edgesRouter);
module.context.use('/', filesRouter);
module.context.use('/', jobSpecificationsRouter);
module.context.use('/', jobsRouter);
module.context.use('/', resultsRouter);
module.context.use('/', workflowConfigRouter);
module.context.use('/', workflowSpecificationsRouter);
module.context.use('/', workflowsRouter);
