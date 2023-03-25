#! /usr/bin/env node
const fs = require('fs');
const Mustache = require('Mustache');

const documents = [
  {
    name: 'AWS compute node configuration',
    description: 'AWS compute node configuration',
    collection: 'aws_schedulers',
    schema: 'awsScheduler',
    batch_schema: 'batchAwsSchedulers',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'name',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'compute node',
    description: 'Compute node used for running jobs',
    collection: 'compute_nodes',
    schema: 'computeNode',
    batch_schema: 'batchComputeNodes',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'hostname',
        type: 'joi.string()',
      },
      {
        name: 'is_active',
        type: 'joi.boolean()',
      },
    ],
  },
  {
    name: 'compute node statistics',
    description: 'Compute node resource utilization statistics',
    collection: 'compute_node_stats',
    schema: 'computeNodeStats',
    batch_schema: 'batchComputeNodeStats',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'hostname',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'event',
    description: 'User-defined event',
    collection: 'events',
    schema: 'object',
    batch_schema: 'batchObjects',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'file',
    description: 'Job input or output files',
    collection: 'files',
    schema: 'file',
    batch_schema: 'batchFiles',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'name',
        type: 'joi.string()',
      },
      {
        name: 'path',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'job',
    description: 'Job',
    collection: 'jobs',
    custom_convert: `utils.convertJobForApi`,
    custom_post: `documents.addJob`,
    schema: 'job',
    batch_schema: 'batchJobs',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'name',
        type: 'joi.string()',
      },
      {
        name: 'command',
        type: 'joi.string()',
      },
      {
        name: 'run_id',
        type: 'joi.number().integer()',
      },
      {
        name: 'status',
        type: 'joi.string()',
      },
      {
        name: 'cancel_on_blocking_job_failure',
        type: 'joi.boolean()',
      },
      {
        name: 'interruptible',
        type: 'joi.boolean()',
      },
    ],
  },
  {
    name: 'job process statistics',
    description: 'Job process resource utilization statistics',
    collection: 'job_process_stats',
    schema: 'jobProcessStats',
    batch_schema: 'batchJobProcessStats',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'job_key',
        type: 'joi.string()',
      },
      {
        name: 'run_id',
        type: 'joi.number().integer()',
      },
    ],
  },
  {
    name: 'local compute node configuration',
    description: 'Local compute node configuration',
    collection: 'local_schedulers',
    schema: 'localScheduler',
    batch_schema: 'batchLocalSchedulers',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'memory',
        type: 'joi.string()',
      },
      {
        name: 'num_cpus',
        type: 'joi.number().integer()',
      },
    ],
  },
  {
    name: 'resource requirements',
    description: 'Job resource requirements',
    collection: 'resource_requirements',
    schema: 'resourceRequirements',
    batch_schema: 'batchResourceRequirements',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'name',
        type: 'joi.string()',
      },
      {
        name: 'memory',
        type: 'joi.string()',
      },
      {
        name: 'num_cpus',
        type: 'joi.number().integer()',
      },
      {
        name: 'num_gpus',
        type: 'joi.number().integer()',
      },
      {
        name: 'num_nodes',
        type: 'joi.number().integer()',
      },
      {
        name: 'runtime',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'result',
    description: 'Result of a job',
    collection: 'results',
    schema: 'result',
    batch_schema: 'batchResults',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'job_key',
        type: 'joi.string()',
      },
      {
        name: 'run_id',
        type: 'joi.number().integer()',
      },
      {
        name: 'return_code',
        type: 'joi.number().integer()',
      },
      {
        name: 'status',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'scheduled compute node',
    description: 'Compute nodes scheduled to complete jobs',
    collection: 'scheduled_compute_nodes',
    schema: 'scheduledComputeNode',
    batch_schema: 'batchScheduledComputeNodes',
    filter_fields: ['_key', 'scheduler_id', 'scheduler_config_id', 'status'],
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'scheduler_id',
        type: 'joi.string()',
      },
      {
        name: 'scheduler_config_id',
        type: 'joi.string()',
      },
      {
        name: 'status',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'SLURM compute node configuration',
    description: 'SLURM compute node configuration',
    collection: 'slurm_schedulers',
    schema: 'slurmScheduler',
    batch_schema: 'batchSlurmSchedulers',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
      {
        name: 'name',
        type: 'joi.string()',
      },
      {
        name: 'account',
        type: 'joi.string()',
      },
      {
        name: 'gres',
        type: 'joi.string()',
      },
      {
        name: 'mem',
        type: 'joi.string()',
      },
      {
        name: 'nodes',
        type: 'joi.number().integer()',
      },
      {
        name: 'partition',
        type: 'joi.string()',
      },
      {
        name: 'qos',
        type: 'joi.string()',
      },
      {
        name: 'tmp',
        type: 'joi.string()',
      },
      {
        name: 'walltime',
        type: 'joi.string()',
      },
    ],
  },
  {
    name: 'user data',
    description: 'Input or output user data for a job',
    collection: 'user_data',
    schema: 'object',
    batch_schema: 'batchObjects',
    filter_fields: [
      {
        name: '_key',
        type: 'joi.string()',
      },
    ],
  },
];

/**
 * Render the Mustache template.
 * @param {Object} doc
 */
function renderTemplate(doc) {
  fs.readFile('src/router.mustache', (err, data) => {
    if (err) {
      throw err;
    }
    const vowels = new Set(['a', 'e', 'i', 'o', 'u']);
    doc.a_or_an = vowels.has(doc.name[0]) ? 'an' : 'a';
    const template = data.toString();
    const text = Mustache.render(template, doc);
    const filename = `../src/api/generated/${doc.collection}.js`;
    fs.writeFile(`${filename}`, text, (err) => {
      if (err) {
        throw err;
      } else {
        console.log(`Generated ${filename}`);
      }
    });
  });
}

for (const doc of documents) {
  renderTemplate(doc);
}
