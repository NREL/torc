'use strict';
const joi = require('joi');

const workerResources = joi.object().required().keys({
  num_cpus: joi.number().integer().required(),
  memory_gb: joi.number().required(),
  num_gpus: joi.number().integer().default(0),
  num_nodes: joi.number().integer().default(1),
  time_limit: joi.string().optional().allow(null), // ISO 8601 encoding for timedeltas
  scheduler_config_id: joi.string().optional().default('').allow(null, ''),
});

const computeNode = joi.object().required().keys({
  hostname: joi.string().required(),
  pid: joi.number().integer().required(),
  start_time: joi.string().required(),
  duration_seconds: joi.number().optional(),
  is_active: joi.boolean().optional(),
  resources: workerResources.required(),
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
  data: joi.object().optional(),
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
  needs_to_run_completion_script: joi.boolean().required(),
});

const computeNodeScheduleParams = joi.object().required().keys({
  max_parallel_jobs: joi.number().integer().optional().allow(null),
  num_jobs: joi.number().integer().required(),
  scheduler_id: joi.string().required(),
  start_one_worker_per_node: joi.boolean().default(false),
});

const jobInternal = joi.object().required().keys({
  memory_bytes: joi.number().integer().default(0),
  num_cpus: joi.number().integer().default(0),
  num_gpus: joi.number().integer().default(0),
  num_nodes: joi.number().integer().default(0),
  runtime_seconds: joi.number().default(0.0),
  scheduler_config_id: joi.string().optional().default('').allow(null, ''),
  hash: joi.number().integer().default(0),
});

const job = joi.object().required().keys({
  name: joi.string().optional(),
  command: joi.string().required(),
  invocation_script: joi.string().optional().allow(null),
  status: joi.string(),
  schedule_compute_nodes: computeNodeScheduleParams.optional().allow(null),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  supports_termination: joi.boolean().default(false),
  resource_requirements: joi.string().optional(),
  scheduler: joi.string().optional(),
  input_files: joi.array().items(joi.string()).default([]),
  output_files: joi.array().items(joi.string()).default([]),
  input_user_data: joi.array().items(joi.string()).default([]),
  output_user_data: joi.array().items(joi.string()).default([]),
  blocked_by: joi.array().items(joi.string()).default([]),
  // This only exists to all prepareJobsForSubmission to take less time to find
  // jobs with exclusive access.
  internal: jobInternal.optional().default(jobInternal.validate({}).value),
  // TODO container information
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const jobs = joi.object().required().keys({
  jobs: joi.array().items(job).required(),
});

const jobsResponse = joi.object().required().keys({
  items: joi.array().items(job),
});

// This schema is used in the user workflow construction but is never stored.
const jobSpecification = joi.object().required().keys({
  name: joi.string().optional(),
  key: joi.string().optional(),
  command: joi.string().required(),
  invocation_script: joi.string().optional().allow(null),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  supports_termination: joi.boolean().default(false),
  scheduler: joi.string().optional().allow(null, ''),
  schedule_compute_nodes: computeNodeScheduleParams.optional().allow(null),
  input_user_data: joi.array().items(joi.string()).default([]),
  output_user_data: joi.array().items(joi.string()).default([]),
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
  cpu: joi.boolean().default(true),
  disk: joi.boolean().default(false),
  memory: joi.boolean().default(true),
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
  // TODO: Consider adding workflow on_complete script option.
  // Would have to detect last worker.
  workflow_startup_script: joi.string().optional(),
  workflow_completion_script: joi.string().optional(),
  worker_startup_script: joi.string().optional(),
  compute_node_resource_stats: computeNodeResourceStatConfig.default(
      computeNodeResourceStatConfig.validate({}).value),
  compute_node_expiration_buffer_seconds: joi.number().default(120),
  compute_node_wait_for_new_jobs_seconds: joi.number().default(0),
  compute_node_ignore_workflow_completion: joi.boolean().default(false),
  compute_node_wait_for_healthy_database_minutes: joi.number().default(20),
  prepare_jobs_sort_method: joi.string()
      .default('gpus_runtime_memory').valid('gpus_runtime_memory', 'gpus_memory_runtime', 'none'),
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
  gres: joi.string().optional().allow(null),
  mem: joi.string().optional().allow(null),
  nodes: joi.number().integer().required(),
  ntasks_per_node: joi.number().integer().optional().allow(null),
  partition: joi.string(),
  qos: joi.string().default('normal'),
  tmp: joi.string().optional().allow(null),
  walltime: joi.string(),
  extra: joi.string().optional().allow(null),
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
  name: joi.string().optional().default('').allow(null, ''),
  key: joi.string().optional(),
  user: joi.string().optional().default('').allow(null, ''),
  description: joi.string().optional().default('').allow(null, ''),
  is_archived: joi.boolean().optional().default(false).allow(null),
  jobs: joi.array().items(jobSpecification).default([]),
  files: joi.array().items(file).default([]),
  user_data: joi.array().items(userData).default([]),
  resource_requirements: joi.array().items(resourceRequirements).default([]),
  schedulers: schedulers.optional().default(schedulers.validate({}).value),
  config: workflowConfig.optional().default(workflowConfig.validate({}).value),
});

const workflow = joi.object().required().keys({
  name: joi.string().optional().default('').allow(null, ''),
  user: joi.string().optional().default('').allow(null, ''),
  description: joi.string().optional().default('').allow(null, ''),
  timestamp: joi.string().optional().default('').allow(null, ''),
  is_archived: joi.boolean().optional().default(false).allow(null),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const autoTuneStatus = joi.object().required().keys({
  enabled: joi.boolean().default(false),
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
  has_detected_need_to_run_completion_script: joi.boolean().default(false),
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

const batchJobSpecifications = joi.object().required().keys({
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
  batchJobSpecifications,
  computeNode,
  computeNodeResourceStatConfig,
  computeNodeScheduleParams,
  computeNodeStats,
  dotGraphResponse,
  edge,
  file,
  isComplete,
  job,
  jobs,
  jobsResponse,
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
