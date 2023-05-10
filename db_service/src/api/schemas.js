'use strict';
const joi = require('joi');

const workerResources = joi.object().required().keys({
  num_cpus: joi.number().integer().required(),
  memory_gb: joi.number().required(),
  num_gpus: joi.number().integer().default(0),
  num_nodes: joi.number().integer().default(1),
  time_limit: joi.string().optional().allow(null), // ISO 8601 encoding for timedeltas
  scheduler_config_id: joi.string().optional(),
});

const computeNode = joi.object().required().keys({
  hostname: joi.string().required(),
  pid: joi.number().integer().required(),
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

const dotGraphResponse = joi.object().required().keys({
  graph: joi.string().required(),
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
  scheduler_config_id: joi.string().optional().default('').allow(null, ''),
  hash: joi.number().integer().default(0),
});

const job = joi.object().required().keys({
  name: joi.string().optional(),
  command: joi.string().required(),
  invocation_script: joi.string().optional().allow(null),
  status: joi.string(),
  needs_compute_node_schedule: joi.boolean().default(false),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  supports_termination: joi.boolean().default(false),
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
  invocation_script: joi.string().optional().allow(null),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  supports_termination: joi.boolean().default(false),
  scheduler: joi.string().default('').allow(''),
  // If this is true, scheduler must be set.
  needs_compute_node_schedule: joi.boolean().default(false),
  consumes_user_data: joi.array().items(joi.string()).optional().default([]),
  stores_user_data: joi.array().items(joi.string()).optional().default([]),
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

const listItemsResponse = joi.object().required().keys({
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

const userData = joi.object().required().keys({
  is_ephemeral: joi.boolean().default(false),
  name: joi.string().optional(),
  data: joi.object().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const resourceRequirements = joi.object().required().keys({
  name: joi.string().optional(),
  num_cpus: joi.number().integer().default(1),
  num_gpus: joi.number().integer().default(0),
  num_nodes: joi.number().integer().default(1),
  memory: joi.string().default('1m'),
  runtime: joi.string().default('P0DT1M'), // ISO 8601 encoding for duration
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const result = joi.object().required().keys({
  job_key: joi.string().required(),
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

const missingUserDataResponse = joi.object().required().keys({
  user_data: joi.array().items(joi.string()),
});

const processChangedJobInputsResponse = joi.object().required().keys({
  reinitialized_jobs: joi.array().items(joi.string()),
});

const requiredExistingFilesResponse = joi.object().required().keys({
  files: joi.array().items(joi.string()),
});

const workflowConfig = joi.object().required().keys({
  compute_node_resource_stats: computeNodeResourceStatConfig.default(
      computeNodeResourceStatConfig.validate({}).value),
  // This buffer is the value used by the worker app to cleanup and exit before the timeout.
  compute_node_worker_buffer_seconds: joi.number().default(120),
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
  extra: joi.string().allow(null),
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
  name: joi.string().optional().allow(null, ''),
  key: joi.string().optional(),
  user: joi.string().optional().allow(null, ''),
  description: joi.string().optional().allow(null, ''),
  jobs: joi.array().items(jobSpecification).default([]),
  files: joi.array().items(file).default([]),
  user_data: joi.array().items(userData).default([]),
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

const batchUserData = joi.object().required().keys({
  items: joi.array().items(userData),
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
  batchJobProcessStats,
  batchJobs,
  batchLocalSchedulers,
  batchObjects,
  batchResourceRequirements,
  batchResults,
  batchScheduledComputeNodes,
  batchSlurmSchedulers,
  batchUserData,
  batchWorkflows,
  batchjobSpecifications,
  computeNode,
  computeNodeResourceStatConfig,
  computeNodeStats,
  dotGraphResponse,
  edge,
  file,
  isComplete,
  job,
  jobInternal,
  jobProcessStats,
  jobSpecification,
  listItemsResponse,
  localScheduler,
  missingUserDataResponse,
  object,
  processChangedJobInputsResponse,
  readyJobsResourceRequirements,
  requiredExistingFilesResponse,
  resourceRequirements,
  result,
  scheduledComputeNode,
  schedulers,
  slurmScheduler,
  userData,
  workerResources,
  workflow,
  workflowConfig,
  workflowSpecification,
  workflowStatus,
};
