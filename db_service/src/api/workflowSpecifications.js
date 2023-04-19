'use strict';
const joi = require('joi');
const config = require('../config');
const documents = require('../documents');
const query = require('../query');
const utils = require('../utils');
const schemas = require('./schemas');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

// TODO: Consider what to do when the full JSON payload is large. May hit transfer limits.

router.post('/workflow_specifications', function(req, res) {
  const spec = req.body;
  const workflow = {
    name: spec.name,
    user: spec.user,
    description: spec.description,
  };
  if (spec.key != null) {
    workflow._key = spec.key;
  }
  try {
    const meta = documents.addWorkflow(workflow);
    Object.assign(workflow, meta);
    addWorkflowSpecification(spec, workflow);
    res.send(workflow);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Post workflow_specifications`);
  }
})
    .body(schemas.workflowSpecification, 'New workflow')
    .response(schemas.workflow, 'message')
    .summary('Store a workflow.')
    .description('Store a workflow.');

router.get('/workflow_specifications/:key', function(req, res) {
  const workflowKey = req.pathParams.key;
  const workflow = documents.getWorkflow(workflowKey, res);
  const filesCollection = config.getWorkflowCollection(workflow, 'files');
  const rrCollection = config.getWorkflowCollection(workflow, 'resource_requirements');
  const awsCollection = config.getWorkflowCollection(workflow, 'aws_schedulers');
  const localCollection = config.getWorkflowCollection(workflow, 'local_schedulers');
  const slurmCollection = config.getWorkflowCollection(workflow, 'slurm_schedulers');

  try {
    const jobs = [];
    for (const job of query.iterWorkflowDocuments(workflow, 'jobs')) {
      jobs.push(query.getjobSpecification(job, workflow));
    }
    const data = {
      config: query.getWorkflowConfig(workflow),
      files: filesCollection.all().toArray(),
      jobs: jobs,
      resource_requirements: rrCollection.all().toArray(),
      schedulers: {
        aws_schedulers: awsCollection.all().toArray(),
        local_schedulers: localCollection.all().toArray(),
        slurm_schedulers: slurmCollection.all().toArray(),
      },
    };
    res.send(data);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get workflow_specifications workflowKey=${workflowKey}`);
  }
})
    .pathParam('key', joi.string().required(), 'key of the workflow.')
    .response(schemas.workflowSpecification, 'Stored workflow')
    .summary('Retrieve the current workflow')
    .description('Retrieves the current workflow in JSON format.');

router.get('/workflow_specifications/example', function(req, res) {
  const spec = {
    files: [
      {
        name: 'work_script',
        path: 'my_script.sh',
      },
      {
        name: 'postprocess_script',
        path: 'postprocess.sh',
      },
      {
        name: 'f1',
        path: 'dir/f1.json',
      },
      {
        name: 'f2',
        path: 'dir/f2.json',
      },
      {
        name: 'f3',
        path: 'dir/f3.json',
      },
    ],
    jobs: [
      {
        name: 'work',
        command: 'bash my_script.sh -i f1.json -o f2.json',
        input_files: ['work_script', 'f1'],
        output_files: ['f2'],
        resource_requirements: 'medium',
      },
      {
        name: 'postprocess',
        command: 'bash postprocess.sh -i f2.json -o f3.json',
        input_files: ['postprocess_script', 'f2'],
        output_files: ['f3'],
        resource_requirements: 'small',
      },
    ],
    resource_requirements: [
      {
        name: 'small',
        num_cpus: 1,
        memory: '10g',
        runtime: 'P0DT1H',
      },
      {
        name: 'medium',
        num_cpus: 8,
        memory: '30g',
        runtime: 'P0DT4H',
      },
    ],
  };

  res.send(spec);
})
    .response(schemas.workflowSpecification, 'Example workflow')
    .summary('Retrieve an example workflow specification')
    .description('Retrieves an example workflow specification in JSON format.');

router.get('/workflow_specifications/template', function(req, res) {
  const spec = {
    name: '',
    description: '',
    user: '',
    files: [],
    jobs: [],
    resource_requirements: [],
    schedulers: {
      aws_schedulers: [],
      local_schedulers: [],
      slurm_schedulers: [],
    },
    config: schemas.workflowConfig.validate({}).value,
  };

  delete spec.key;
  res.send(spec);
})
    .response(schemas.workflowSpecification, 'Workflow template')
    .summary('Retrieve the workflow specification template')
    .description('Retrieve the workflow specification template in JSON format.');

/**
 * Add all items defined in a workflow to the database.
 * @param {Object} spec
 * @param {Object} workflow
 */
function addWorkflowSpecification(spec, workflow) {
  checkDependencies(spec);

  for (const item of spec.files) {
    documents.addFile(item, workflow);
  }
  for (const item of spec.schedulers.aws_schedulers) {
    documents.addScheduler(item, 'aws_schedulers', workflow);
  }
  for (const item of spec.schedulers.local_schedulers) {
    documents.addScheduler(item, 'local_schedulers', workflow);
  }
  for (const item of spec.schedulers.slurm_schedulers) {
    documents.addScheduler(item, 'slurm_schedulers', workflow);
  }
  for (const item of spec.resource_requirements) {
    documents.addResourceRequirements(item, workflow);
  }
  for (const item of spec.user_data) {
    documents.addUserData(item, workflow);
  }
  for (const item of spec.jobs) {
    documents.addJobSpecification(item, workflow);
  }
  query.updateWorkflowConfig(workflow, spec.config);
}

/**
 * Check dependencies for all times in the workflow.
 * @param {Object} workflow
 */
function checkDependencies(workflow) {
  const files = new Set();
  const schedulerConfigs = new Set();
  const jobs = new Set();
  const resourceRequirements = new Set();
  const userDataNames = new Set();

  for (const item of workflow.files) {
    files.add(item.name);
  }
  for (const item of workflow.schedulers.aws_schedulers) {
    schedulerConfigs.add(`aws_schedulers/${item.name}`);
  }
  for (const item of workflow.schedulers.local_schedulers) {
    schedulerConfigs.add(`local_schedulers/${item.name}`);
  }
  for (const item of workflow.schedulers.slurm_schedulers) {
    schedulerConfigs.add(`slurm_schedulers/${item.name}`);
  }
  for (const item of workflow.jobs) {
    jobs.add(item.name);
  }
  for (const item of workflow.resource_requirements) {
    resourceRequirements.add(item.name);
  }
  for (const item of workflow.user_data) {
    userDataNames.add(item.name);
  }

  for (const job of workflow.jobs) {
    for (const filename of job.input_files) {
      if (!files.has(filename)) {
        throw new Error(`Invalid input file=${filename} in ${JSON.stringify(job)}`);
      }
    }
    for (const filename of job.output_files) {
      if (!files.has(filename)) {
        throw new Error(`Invalid output file=${filename} in ${JSON.stringify(job)}`);
      }
    }
    for (const jobName of job.blocked_by) {
      if (!jobs.has(jobName)) {
        throw new Error(`Invalid blocked_by=${jobName} in job ${JSON.stringify(job)}`);
      }
    }
    if (job.scheduler != '') {
      if (!schedulerConfigs.has(job.scheduler)) {
        throw new Error(`Invalid scheduler=${job.scheduler} in job=${JSON.stringify(job)}`);
      }
    }
    for (const name of job.consumes_user_data) {
      if (!userDataNames.has(name)) {
        throw new Error(`Invalid consumes_user_data=${name} in job ${JSON.stringify(job)}`);
      }
    }
    for (const name of job.stores_user_data) {
      if (!userDataNames.has(name)) {
        throw new Error(`Invalid stores_user_data=${name} in job ${JSON.stringify(job)}`);
      }
    }
    const rr = job.resource_requirements;
    if (rr != null && !resourceRequirements.has(rr)) {
      throw new Error(`Invalid resource_requirements=${rr} in job ${JSON.stringify(job)}`);
    }
  }
}
