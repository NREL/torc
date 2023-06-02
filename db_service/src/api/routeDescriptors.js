'use strict';
const joi = require('joi');
const schemas = require('./schemas');
const documents = require('../documents');

const ROUTE_DESCRIPTORS = [
  {
    name: 'AWS compute node configuration',
    description: 'AWS compute node configuration',
    collection: 'aws_schedulers',
    schema: schemas.awsScheduler,
    batchSchema: schemas.batchAwsSchedulers,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'name',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'compute node',
    description: 'Compute node used for running jobs',
    collection: 'compute_nodes',
    schema: schemas.computeNode,
    batchSchema: schemas.batchComputeNodes,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'hostname',
        type: joi.string(),
      },
      {
        name: 'is_active',
        type: joi.boolean(),
      },
    ],
  },
  {
    name: 'compute node statistics',
    description: 'Compute node resource utilization statistics',
    collection: 'compute_node_stats',
    schema: schemas.computeNodeStats,
    batchSchema: schemas.batchComputeNodeStats,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'hostname',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'event',
    description: 'User-defined event',
    collection: 'events',
    schema: joi.object().required(),
    batchSchema: schemas.batchObjects,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'category',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'file',
    description: 'Job input or output files',
    collection: 'files',
    schema: schemas.file,
    batchSchema: schemas.batchFiles,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'name',
        type: joi.string(),
      },
      {
        name: 'path',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'job',
    description: 'Job',
    collection: 'jobs',
    customPost: documents.addJob,
    schema: schemas.job,
    batchSchema: schemas.batchJobs,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'name',
        type: joi.string(),
      },
      {
        name: 'command',
        type: joi.string(),
      },
      {
        name: 'status',
        type: joi.string(),
      },
      {
        name: 'cancel_on_blocking_job_failure',
        type: joi.boolean(),
      },
      {
        name: 'supports_termination',
        type: joi.boolean(),
      },
    ],
  },
  {
    name: 'job process statistics',
    description: 'Job process resource utilization statistics',
    collection: 'job_process_stats',
    schema: schemas.jobProcessStats,
    batchSchema: schemas.batchJobProcessStats,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'job_key',
        type: joi.string(),
      },
      {
        name: 'run_id',
        type: joi.number().integer(),
      },
    ],
  },
  {
    name: 'local compute node configuration',
    description: 'Local compute node configuration',
    collection: 'local_schedulers',
    schema: schemas.localScheduler,
    batchSchema: schemas.batchLocalSchedulers,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'memory',
        type: joi.string(),
      },
      {
        name: 'num_cpus',
        type: joi.number().integer(),
      },
    ],
  },
  {
    name: 'resource requirements',
    description: 'Job resource requirements',
    collection: 'resource_requirements',
    schema: schemas.resourceRequirements,
    batchSchema: schemas.batchResourceRequirements,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'name',
        type: joi.string(),
      },
      {
        name: 'memory',
        type: joi.string(),
      },
      {
        name: 'num_cpus',
        type: joi.number().integer(),
      },
      {
        name: 'num_gpus',
        type: joi.number().integer(),
      },
      {
        name: 'num_nodes',
        type: joi.number().integer(),
      },
      {
        name: 'runtime',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'result',
    description: 'Result of a job',
    collection: 'results',
    schema: schemas.result,
    batchSchema: schemas.batchResults,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'job_key',
        type: joi.string(),
      },
      {
        name: 'run_id',
        type: joi.number().integer(),
      },
      {
        name: 'return_code',
        type: joi.number().integer(),
      },
      {
        name: 'status',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'scheduled compute node',
    description: 'Compute nodes scheduled to complete jobs',
    collection: 'scheduled_compute_nodes',
    schema: schemas.scheduledComputeNode,
    batchSchema: schemas.batchScheduledComputeNodes,
    filterFields: ['_key', 'scheduler_id', 'scheduler_config_id', 'status'],
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'scheduler_id',
        type: joi.string(),
      },
      {
        name: 'scheduler_config_id',
        type: joi.string(),
      },
      {
        name: 'status',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'Slurm compute node configuration',
    description: 'Slurm compute node configuration',
    collection: 'slurm_schedulers',
    schema: schemas.slurmScheduler,
    batchSchema: schemas.batchSlurmSchedulers,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'name',
        type: joi.string(),
      },
      {
        name: 'account',
        type: joi.string(),
      },
      {
        name: 'gres',
        type: joi.string(),
      },
      {
        name: 'mem',
        type: joi.string(),
      },
      {
        name: 'nodes',
        type: joi.number().integer(),
      },
      {
        name: 'partition',
        type: joi.string(),
      },
      {
        name: 'qos',
        type: joi.string(),
      },
      {
        name: 'tmp',
        type: joi.string(),
      },
      {
        name: 'walltime',
        type: joi.string(),
      },
    ],
  },
  {
    name: 'user data',
    description: 'Input or output user data for a job',
    collection: 'user_data',
    schema: schemas.userData,
    batchSchema: schemas.batchUserData,
    filterFields: [
      {
        name: '_key',
        type: joi.string(),
      },
      {
        name: 'name',
        type: joi.string(),
      },
      {
        name: 'is_ephemeral',
        type: joi.boolean(),
      },
    ],
  },
];

module.exports = {
  ROUTE_DESCRIPTORS,
};
