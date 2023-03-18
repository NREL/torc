'use strict';
const joi = require('joi');
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const {GRAPH_NAME, JobStatus, MAX_TRANSFER_RECORDS} = require('../defs');
const graph = graphModule._graph(GRAPH_NAME);
const query = require('../query');
const schemas = require('./schemas');
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
  for (const job of graph.jobs.all()) {
    jobs.push(query.getJobDefinition(job));
  }

  const data = {
    files: graph.files.toArray(),
    jobs: jobs,
    resource_requirements: graph.resource_requirements.toArray(),
    schedulers: graph.scheduled_bys.toArray(),
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
  for (const item of workflow.schedulers) {
    query.addHpcConfig(item);
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
  const hpcConfigs = new Set();
  const jobs = new Set();
  const resourceRequirements = new Set();

  for (const item of workflow.files) {
    files.add(item.name);
  }
  for (const item of workflow.schedulers) {
    hpcConfigs.add(item.name);
  }
  for (const item of workflow.jobs) {
    jobs.add(item.name);
  }
  for (const item of workflow.resource_requirements) {
    resourceRequirements.add(item.name);
  }

  for (const job of workflow.jobs) {
    for (const filename of job.input_files) {
      if (!files.has(filename) && !graph.files.exists(filename)) {
        throw new Error(`job ${job.name} input file ${filename} is not stored`);
      }
    }
    for (const filename of job.output_files) {
      if (!files.has(filename) && !graph.files.exists(filename)) {
        throw new Error(`job ${job.name} output file ${filename} is not stored`);
      }
    }
    for (const jobName of job.blocked_by) {
      if (!jobs.has(jobName) && !graph.jobs.exists(jobName)) {
        throw new Error(`job ${job.name} with blocked_by ${jobName} is not stored`);
      }
    }
    if (job.scheduler != null && !hpcConfigs.has(job.scheduler) &&
      !graph.hpc_configs.exists(job.scheduler)) {
      throw new Error(`job ${job.name} scheduler ${job.scheduler} is not stored`);
    }
    const rr = job.resource_requirements;
    if (rr != null && !resourceRequirements.has(rr) && !graph.resource_requirements.exists(rr)) {
      throw new Error(`job ${job.name} resource_requirements ${rr} is not stored`);
    }
  }
}
