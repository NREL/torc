#! /usr/bin/env node
const fs = require('fs');
const Mustache = require('Mustache');

const documents = [
  {
    name: 'AWS compute node configuration',
    description: 'AWS compute node configuration',
    collection: 'aws_schedulers',
    collection_var_name: 'awsSchedulers',
    schema: 'awsScheduler',
    batch_schema: 'batchAwsSchedulers',
    key: 'name',
  },
  {
    name: 'compute node',
    description: 'Compute node used for running jobs',
    collection: 'compute_nodes',
    collection_var_name: 'computeNodes',
    schema: 'computeNode',
    batch_schema: 'batchComputeNodes',
  },
  {
    name: 'compute node statistics',
    description: 'Compute node resource utilization statistics',
    collection: 'compute_node_stats',
    collection_var_name: 'computeNodeStats',
    schema: 'computeNodeStats',
    batch_schema: 'batchComputeNodeStats',
  },
  {
    name: 'event',
    description: 'User-defined event',
    collection: 'events',
    collection_var_name: 'events',
    schema: 'object',
    batch_schema: 'batchObjects',
  },
  {
    name: 'file',
    description: 'Job input or output files',
    collection: 'files',
    collection_var_name: 'files',
    schema: 'file',
    batch_schema: 'batchFiles',
    key: 'name',
  },
  {
    name: 'job',
    description: 'Job',
    collection: 'jobs',
    collection_var_name: 'jobs',
    custom_imports: `const query = require('../../query');\nconst utils = require('../../utils');`,
    custom_convert: `utils.convertJobForApi`,
    custom_post: `query.addJob`,
    schema: 'job',
    batch_schema: 'batchJobs',
  },
  {
    name: 'job process statistics',
    description: 'Job process resource utilization statistics',
    collection: 'job_process_stats',
    collection_var_name: 'jobProcessStats',
    schema: 'jobProcessStats',
    batch_schema: 'batchJobProcessStats',
  },
  {
    name: 'local compute node configuration',
    description: 'Local compute node configuration',
    collection: 'local_schedulers',
    collection_var_name: 'localSchedulers',
    schema: 'localScheduler',
    batch_schema: 'batchLocalSchedulers',
    key: 'name',
  },
  {
    name: 'resource requirements',
    description: 'Job resource requirements',
    collection: 'resource_requirements',
    collection_var_name: 'resourceRequirements',
    schema: 'resourceRequirements',
    batch_schema: 'batchResourceRequirements',
    key: 'name',
  },
  {
    name: 'result',
    description: 'Result of a job',
    collection: 'results',
    collection_var_name: 'results',
    schema: 'result',
    batch_schema: 'batchResults',
  },
  {
    name: 'scheduled compute node',
    description: 'Compute nodes scheduled to complete jobs',
    collection: 'scheduled_compute_nodes',
    collection_var_name: 'scheduledComputeNodes',
    schema: 'scheduledComputeNode',
    batch_schema: 'batchScheduledComputeNodes',
    key: 'scheduler_id',
  },
  {
    name: 'SLURM compute node configuration',
    description: 'SLURM compute node configuration',
    collection: 'slurm_schedulers',
    collection_var_name: 'slurmSchedulers',
    schema: 'slurmScheduler',
    batch_schema: 'batchSlurmSchedulers',
    key: 'name',
  },
  {
    name: 'user data',
    description: 'Input or output user data for a job',
    collection: 'user_data',
    collection_var_name: 'userData',
    schema: 'object',
    batch_schema: 'batchObjects',
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
    const filename = `../src/api/generated/${doc.collection_var_name}.js`;
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
