'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const {JobStatus, MAX_TRANSFER_RECORDS} = require('../defs');
const query = require('../query');
const schemas = require('./schemas');
const {convertJobForApi} = require('../utils');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

// TODO: Consider what to do when the full JSON payload is large. May hit transfer limits.

router.post('/workflow', function(req, res) {
  try {
    addWorkflow(req.body);
    query.resetWorkflowStatus();
    res.send({message: 'Added workflow.'});
  } catch (e) {
    res.throw(400, `Error occured: ${e}`);
  }
})
    .body(schemas.workflow, 'New workflow')
    .response(joi.object(), 'message')
    .summary('Store a workflow.')
    .description('Store a workflow, overwriting any existing entries.');

router.get('/workflow', function(req, res) {
  const jobs = [];
  for (const job of db.jobs.all()) {
    jobs.push(query.getJobDefinition(job));
  }

  const data = {
    config: query.getWorkflowConfig(),
    files: db.files.all().toArray(),
    jobs: jobs,
    resource_requirements: db.resource_requirements.all().toArray(),
    schedulers: {
      aws_schedulers: db.aws_schedulers.all().toArray(),
      local_schedulers: db.local_schedulers.all().toArray(),
      slurm_schedulers: db.slurm_schedulers.all().toArray(),
    },
  };
  res.send(data);
})
    .response(schemas.workflow, 'Stored workflow')
    .summary('Retrieve the current workflow')
    .description('Retrieves the current workflow in JSON format.');

router.delete('/workflow', function(req, res) {
  for (const collection of db._collections()) {
    const name = collection.name();
    if (!name.startsWith('_')) {
      db._truncate(name);
    }
  }
  console.log(`Deleted all database objects.`);
  res.send({message: 'Deleted the workflow'});
})
    .body(joi.object())
    .response(joi.object(), 'message')
    .summary('Delete the workflow.')
    .description('Delete all workflow objects from the database.');

router.get('/workflow/is_complete', function(req, res) {
  res.send({is_complete: query.isWorkflowComplete()});
})
    .response(schemas.isComplete)
    .summary('Report whether the workflow is complete')
    .description('Reports true if all jobs in the workflow are complete.');

router.get('/workflow/ready_job_requirements', function(req, res) {
  const result = query.getReadyJobRequirements();
  res.send(result);
})
    .response(schemas.readyJobsResourceRequirements, 'result')
    .summary('Return the resource requirements for ready jobs.')
    .description(`Return the resource requirements for jobs with a status of ready.`);

router.post('/workflow/estimate', function(req, res) {
  const result = query.estimateWorkflow();
  res.send(result);
})
    .response(schemas.workflowEstimate, 'result')
    .summary('Perform a dry run of all jobs to estimate required resources.')
    .description(`Perform a dry run of all jobs to estimate required resources.
      Only valid if jobs have similar runtimes`);

router.post('/workflow/initialize_jobs', function(req, res) {
  query.addBlocksEdgesFromFiles();
  query.initializeJobStatus();
  res.send({message: 'Initialized job status'});
})
    .response(joi.object(), 'message')
    .summary('Initialize job relationships.')
    .description('Initialize job relationships based on file relationships.');

router.post('/workflow/prepare_jobs_for_submission', function(req, res) {
  const status = query.getWorkflowStatus();
  if (status.is_canceled) {
    res.send([]);
  } else {
    const resources = req.body;
    const qp = req.queryParams == null ? {} : req.queryParams;
    const jobs = query.prepareJobsForSubmission(resources, qp.limit);
    const items = [];
    for (const job of jobs) {
      items.push(convertJobForApi(job));
    }
    res.send(jobs);
  }
})
    .queryParam('limit', joi.number().default(MAX_TRANSFER_RECORDS))
    .body(schemas.workerResources, 'Available worker resources.')
    .response(joi.array().items(schemas.job), 'Jobs that are ready for submission.')
    .summary('Return ready jobs')
    .description('Return jobs that are ready for submission. Sets status to submitted_pending');

router.post('/workflow/auto_tune_resource_requirements', function(req, res) {
  query.setupAutoTuneResourceRequirements();
  res.send({message: 'Enabled jobs for auto-tune mode.'});
})
    .response(joi.object(), 'Message')
    .summary('Enable workflow for auto-tuning resource requirements.')
    .description('Enable workflow for auto-tuning resource requirements.');

router.post('/workflow/process_auto_tune_resource_requirements_results', function(req, res) {
  query.processAutoTuneResourceRequirementsResults();
  res.send({message: 'Processed the results of auto-tuning resource requirements.'});
})
    .response(joi.object(), 'Message')
    .summary('Process the results of auto-tuning resource requirements.')
    .description('Process the results of auto-tuning resource requirements.');

router.post('/workflow/reset_status', function(req, res) {
  query.resetJobStatus();
  query.resetWorkflowStatus();
  res.send({message: `Reset job status to ${JobStatus.Uninitialized}`});
})
    .response(joi.object(), 'message')
    .summary('Reset job status.')
    .description(`Reset status for all jobs to ${JobStatus.Uninitialized}.`);

router.get('/workflow/example', function(req, res) {
  const workflow = {
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

  res.send(workflow);
})
    .response(schemas.workflow, 'Example workflow')
    .summary('Retrieve an example workflow')
    .description('Retrieves an example workflow in JSON format.');

/**
 * Add all items defined in a workflow to the database.
 * @param {Object} workflow
 */
function addWorkflow(workflow) {
  // TODO: will not work correctly if items are already stored with different parameters.
  checkDependencies(workflow);

  for (const item of workflow.files) {
    query.addFile(item);
  }
  for (const item of workflow.schedulers.aws_schedulers) {
    query.addScheduler(item, 'aws_schedulers');
  }
  for (const item of workflow.schedulers.local_schedulers) {
    query.addScheduler(item, 'local_schedulers');
  }
  for (const item of workflow.schedulers.slurm_schedulers) {
    query.addScheduler(item, 'slurm_schedulers');
  }
  for (const item of workflow.resource_requirements) {
    query.addResourceRequirements(item);
  }
  for (const item of workflow.jobs) {
    query.addJobDefinition(item);
  }
  query.updateWorkflowConfig(workflow.config);
}

/**
 * Check dependencies for all jobs in the workflow.
 * @param {Object} workflow
 */
function checkDependencies(workflow) {
  const files = new Set();
  const schedulerConfigs = new Set();
  const jobs = new Set();
  const resourceRequirements = new Set();

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

  for (const job of workflow.jobs) {
    for (const filename of job.input_files) {
      if (!files.has(filename) && !db.files.exists(filename)) {
        throw new Error(`Invalid input file=${filename} in ${JSON.stringify(job)}`);
      }
    }
    for (const filename of job.output_files) {
      if (!files.has(filename) && !db.files.exists(filename)) {
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
    const rr = job.resource_requirements;
    if (rr != null && !resourceRequirements.has(rr) && !db.resource_requirements.exists(rr)) {
      throw new Error(`Invalid resource_requirements=${rr} in job ${JSON.stringify(job)}`);
    }
  }
}
