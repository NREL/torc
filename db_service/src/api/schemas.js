'use strict';
const joi = require('joi');

const workerResources = joi.object().required().keys({
  num_cpus: joi.number().integer().required(),
  memory_gb: joi.number().required(),
  num_gpus: joi.number().integer().default(0),
  num_nodes: joi.number().integer().default(1),
  time_limit: [joi.string().optional(), joi.allow(null)], // ISO 8601 encoding for timedeltas
  scheduler_config_id: joi.string().optional(),
});

const computeNode = joi.object().required().keys({
  hostname: joi.string().required(),
  start_time: joi.string().required(),
  duration_seconds: joi.number().optional(),
  is_active: joi.boolean().optional(),
  resources: workerResources,
  scheduler: joi.object().default({}),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const object = joi.object().required();

const resourceStats = joi.object().required().keys({
  resource_type: joi.string().required(),
  average: joi.object().required({}),
  minimum: joi.object().required({}),
  maximum: joi.object().required({}),
  num_samples: joi.number().integer().required(),
  // Only applies to process stats. Consider something better.
  job_key: joi.string().optional(),
});

const computeNodeStats = joi.object().required().keys({
  hostname: joi.string().required(),
  stats: joi.array().items(resourceStats),
  timestamp: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const edge = joi.object().required().keys({
  _from: joi.string().required(),
  _to: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const file = joi.object().required().keys({
  name: joi.string().optional(),
  path: joi.string().required(),
  // file_hash: joi.string().optional(),
  st_mtime: joi.number().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const isComplete = joi.object().required().keys({
  is_canceled: joi.boolean().required(),
  is_complete: joi.boolean().required(),
});

const jobInternal = joi.object().required().keys({
  memory_bytes: joi.number().integer().default(0.0),
  num_cpus: joi.number().integer().default(0.0),
  num_gpus: joi.number().integer().default(0.0),
  runtime_seconds: joi.number().default(0.0),
  scheduler_config_id: joi.string().optional().default(''),
});

const job = joi.object().required().keys({
  name: joi.string().optional(),
  command: joi.string().required(),
  status: joi.string(),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  interruptible: joi.boolean().default(false),
  run_id: joi.number().integer().default(0),
  // This only exists to all prepareJobsForSubmission to take less time to find
  // jobs with exclusive access.
  internal: jobInternal.optional().default(jobInternal.validate({}).value),
  // TODO container information
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

// This schema is used in the user workflow construction but is never stored.
const jobSpecification = joi.object().required().keys({
  name: joi.string().optional(),
  key: joi.string().optional(),
  command: joi.string().required(),
  user_data: joi.array().items(joi.object()).default([]),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  interruptible: joi.boolean().default(false),
  scheduler: joi.string().default('').allow(''),
  resource_requirements: joi.string().optional(),
  input_files: joi.array().items(joi.string()).default([]),
  output_files: joi.array().items(joi.string()).default([]),
  blocked_by: joi.array().items(joi.string()).default([]),
});

const jobProcessStats = joi.object().required().keys({
  job_key: joi.string().required(),
  run_id: joi.number().integer().required(),
  avg_cpu_percent: joi.number().required(),
  max_cpu_percent: joi.number().required(),
  avg_rss: joi.number().required(),
  max_rss: joi.number().required(),
  num_samples: joi.number().integer().required(),
  timestamp: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const jobUserDataResponse = joi.object().required().keys({
  items: joi.object(),
});

const readyJobsResourceRequirements = joi.object().required().keys({
  num_jobs: joi.number().integer().required(),
  num_cpus: joi.number().integer().required(),
  num_gpus: joi.number().integer().required(),
  memory_gb: joi.number().required(),
  max_memory_gb: joi.number().required(),
  max_num_nodes: joi.number().integer().required(),
  max_runtime: joi.string().required(),
});

const resourceRequirements = joi.object().required().keys({
  name: joi.string().optional(),
  num_cpus: joi.number().integer().default(1),
  num_gpus: joi.number().integer().default(0),
  num_nodes: joi.number().integer().default(1),
  memory: joi.string().default('1m'),
  runtime: joi.string().default('P0DT1H'), // ISO 8601 encoding for duration
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const result = joi.object().required().keys({
  job_key: joi.string().required(),
  job_name: joi.string().required(),
  run_id: joi.number().integer().required(),
  return_code: joi.number().integer().required(),
  exec_time_minutes: joi.number().required(),
  completion_time: joi.string().required(),
  status: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const computeNodeResourceStatConfig = joi.object().keys({
  cpu: joi.boolean().default(false),
  disk: joi.boolean().default(false),
  memory: joi.boolean().default(false),
  network: joi.boolean().default(false),
  process: joi.boolean().default(false),
  include_child_processes: joi.boolean().default(true),
  recurse_child_processes: joi.boolean().default(false),
  monitor_type: joi.string().default('aggregation'),
  make_plots: joi.boolean().default(true),
  interval: joi.number().default(10),
});

const workflowConfig = joi.object().required().keys({
  compute_node_resource_stats: computeNodeResourceStatConfig.default(
      computeNodeResourceStatConfig.validate({}).value),
  _key: joi.string().optional(),
  _id: joi.string().optional(),
  _rev: joi.string().optional(),
});

const awsScheduler = joi.object().required().keys({
  // TODO
  name: joi.string().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const localScheduler = joi.object().required().keys({
  name: joi.string().optional().default('default'),
  memory: joi.string().optional(),
  num_cpus: joi.number().integer().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const slurmScheduler = joi.object().required().keys({
  name: joi.string().optional(),
  account: joi.string().required(),
  gres: joi.string().optional(),
  mem: joi.string().optional(),
  nodes: joi.number().integer().required(),
  partition: joi.string(),
  qos: joi.string().default('normal'),
  tmp: joi.string(),
  walltime: joi.string(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const schedulers = joi.object().required().keys({
  aws_schedulers: joi.array().items(awsScheduler).default([]),
  local_schedulers: joi.array().items(localScheduler).default([]),
  slurm_schedulers: joi.array().items(slurmScheduler).default([]),
});

const workflowSpecification = joi.object().required().keys({
  name: joi.string().optional(),
  key: joi.string().optional(),
  user: joi.string().optional(),
  description: joi.string().optional(),
  jobs: joi.array().items(jobSpecification).default([]),
  files: joi.array().items(file).default([]),
  resource_requirements: joi.array().items(resourceRequirements).default([]),
  schedulers: schedulers.optional().default(schedulers.validate({}).value),
  config: joi.object().default(workflowConfig.validate({}).value),
});

const workflow = joi.object().required().keys({
  name: joi.string().optional(),
  user: joi.string().optional(),
  description: joi.string().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const autoTuneStatus = joi.object().required().keys({
  enabled: joi.boolean().default(true),
  job_keys: joi.array().items(joi.string()).default([]),
});

const scheduledComputeNode = joi.object().required().keys({
  scheduler_id: joi.string().optional(),
  scheduler_config_id: joi.string().required(),
  status: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const workflowStatus = joi.object().required().keys({
  is_canceled: joi.boolean().required(),
  run_id: joi.number().integer().required(),
  auto_tune_status: autoTuneStatus,
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const batchAwsSchedulers = joi.object().required().keys({
  items: joi.array().items(awsScheduler),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchLocalSchedulers = joi.object().required().keys({
  items: joi.array().items(localScheduler),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchSlurmSchedulers = joi.object().required().keys({
  items: joi.array().items(slurmScheduler),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchComputeNodes = joi.object().required().keys({
  items: joi.array().items(computeNode),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchjobSpecifications = joi.object().required().keys({
  items: joi.array().items(jobSpecification),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchJobs = joi.object().required().keys({
  items: joi.array().items(job),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchEdges = joi.object().required().keys({
  items: joi.array().items(edge),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchObjects = joi.object().required().keys({
  items: joi.array().items(joi.object()),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchFiles = joi.object().required().keys({
  items: joi.array().items(file),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchResourceRequirements = joi.object().required().keys({
  items: joi.array().items(resourceRequirements),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchResults = joi.object().required().keys({
  items: joi.array().items(result),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchScheduledComputeNodes = joi.object().required().keys({
  items: joi.array().items(scheduledComputeNode),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchComputeNodeStats = joi.object().required().keys({
  items: joi.array().items(computeNodeStats),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchJobProcessStats = joi.object().required().keys({
  items: joi.array().items(jobProcessStats),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

const batchWorkflows = joi.object().required().keys({
  items: joi.array().items(workflow),
  skip: joi.number().integer().required(),
  max_limit: joi.number().integer().required(),
  count: joi.number().integer().required(),
  total_count: joi.number().integer().required(),
  has_more: joi.boolean().required(),
});

module.exports = {
  autoTuneStatus,
  awsScheduler,
  batchAwsSchedulers,
  batchComputeNodeStats,
  batchComputeNodes,
  batchEdges,
  batchFiles,
  batchjobSpecifications,
  batchJobProcessStats,
  batchJobs,
  batchLocalSchedulers,
  batchObjects,
  batchResourceRequirements,
  batchResults,
  batchScheduledComputeNodes,
  batchSlurmSchedulers,
  batchWorkflows,
  computeNode,
  computeNodeResourceStatConfig,
  computeNodeStats,
  edge,
  file,
  isComplete,
  job,
  jobSpecification,
  jobInternal,
  jobProcessStats,
  jobUserDataResponse,
  localScheduler,
  object,
  readyJobsResourceRequirements,
  resourceRequirements,
  result,
  scheduledComputeNode,
  schedulers,
  slurmScheduler,
  workerResources,
  workflow,
  workflowSpecification,
  workflowConfig,
  workflowStatus,
};
