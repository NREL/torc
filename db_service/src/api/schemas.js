'use strict';
const joi = require('joi');

const workerResources = joi.object().required().keys({
  num_cpus: joi.number().required(),
  memory_gb: joi.number().required(),
  num_gpus: joi.number().default(0),
  num_nodes: joi.number().default(1),
  time_limit: [joi.string().optional(), joi.allow(null)], // ISO 8601 encoding for timedeltas
});

const computeNode = joi.object().required().keys({
  hostname: joi.string().required(),
  start_time: joi.string().required(),
  is_active: joi.boolean().optional(),
  resources: workerResources,
  scheduler: joi.object().default({}),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const resourceStats = joi.object().required().keys({
  resourceType: joi.string().required(),
  average: joi.object().required({}),
  minimum: joi.object().required({}),
  maximum: joi.object().required({}),
  num_samples: joi.number().required(),
  // Only applies to process stats. Consider something better.
  job_name: joi.string().optional(),
});

const computeNodeStats = joi.object().required().keys({
  name: joi.string().required(),
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
  name: joi.string().required(),
  path: joi.string().required(),
  file_hash: joi.string().optional(),
  st_mtime: joi.number().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
  // Keep changes in sync with getDocumentIfAlreadyStored
});

const hpcConfig = joi.object().required().keys({
  name: joi.string().required(),
  hpc_type: joi.string().required(),
  account: joi.string().required(),
  partition: joi.string(),
  qos: joi.string().default('normal'),
  walltime: joi.string(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const isComplete = joi.object().required().keys({
  is_complete: joi.boolean().required(),
});

const jobInternal = joi.object().required().keys({
  memory_bytes: joi.number().default(0.0),
  num_cpus: joi.number().default(0.0),
  num_gpus: joi.number().default(0.0),
  runtime_seconds: joi.number().default(0.0),
});

const job = joi.object().required().keys({
  name: joi.string().required(),
  command: joi.string().required(),
  status: joi.string(),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  interruptible: joi.boolean().default(false),
  run_id: joi.number().default(0),
  // This only exists to all prepareJobsForSubmission to take less time to find
  // jobs with exclusive access.
  internal: jobInternal.validate({}).value, // TODO DT: seems wrong
  // TODO container information
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

// This schema is used in the user workflow construction but is never stored.
const jobDefinition = joi.object().required().keys({
  name: joi.string().required(),
  command: joi.string().required(),
  user_data: joi.array().items(joi.object()).default([]),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  interruptible: joi.boolean().default(false),
  scheduler: joi.string().optional(),
  resource_requirements: joi.string().optional(),
  input_files: joi.array().items(joi.string()).default([]),
  output_files: joi.array().items(joi.string()).default([]),
  blocked_by: joi.array().items(joi.string()).default([]),
});

const jobProcessStats = joi.object().required().keys({
  job_name: joi.string().required(),
  run_id: joi.number().required(),
  avg_cpu_percent: joi.number().required(),
  max_cpu_percent: joi.number().required(),
  avg_rss: joi.number().required(),
  max_rss: joi.number().required(),
  num_samples: joi.number().required(),
  timestamp: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const jobUserData = joi.object().required().keys({
  items: joi.array().items(joi.object()),
  name: joi.string(),
  count: joi.number(),
});

const readyJobsResourceRequirements = joi.object().required().keys({
  num_jobs: joi.number().required(),
  num_cpus: joi.number().required(),
  num_gpus: joi.number().required(),
  memory_gb: joi.number().required(),
  max_memory_gb: joi.number().required(),
  max_num_nodes: joi.number().required(),
  max_runtime: joi.string().required(),
});

const resourceRequirements = joi.object().required().keys({
  name: joi.string().required(),
  num_cpus: joi.number().default(1),
  num_gpus: joi.number().default(0),
  num_nodes: joi.number().default(1),
  memory: joi.string().default('1m'),
  runtime: joi.string().default('P0DT1H'), // ISO 8601 encoding for duration
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const result = joi.object().required().keys({
  name: joi.string().required(),
  run_id: joi.number().required(),
  return_code: joi.number().required(),
  exec_time_minutes: joi.number().required(),
  completion_time: joi.string().required(),
  status: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const workflowEstimate = joi.object().required().keys({
  estimates_by_round: joi.array().items(readyJobsResourceRequirements),
});

const workflow = joi.object().required().keys({
  // TODO: allow specifying compute node resource stat config here
  jobs: joi.array().items(jobDefinition).default([]),
  files: joi.array().items(file).default([]),
  resource_requirements: joi.array().items(resourceRequirements).default([]),
  schedulers: joi.array().items(hpcConfig).default([]),
});

const autoTuneStatus = joi.object().required().keys({
  enabled: joi.boolean().default(true),
  job_names: joi.array().items(joi.string()).default([]),
});

const computeNodeResourceStatConfig = joi.object().required().keys({
  cpu: joi.boolean().default(false),
  disk: joi.boolean().default(false),
  memory: joi.boolean().default(false),
  network: joi.boolean().default(false),
  process: joi.boolean().default(false),
  include_child_processes: joi.boolean().default(true),
  recurse_child_processes: joi.boolean().default(false),
  interval: joi.number().default(10),
});

const workflowConfig = joi.object().required().keys({
  compute_node_resource_stat_config: computeNodeResourceStatConfig,
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const workflowStatus = joi.object().required().keys({
  is_canceled: joi.boolean().required(),
  run_id: joi.number().required(),
  scheduled_compute_node_ids: joi.array().items(joi.number()),
  auto_tune_status: autoTuneStatus,
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const batchComputeNodes = joi.object().required().keys({
  items: joi.array().items(computeNode),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchJobDefinitions = joi.object().required().keys({
  items: joi.array().items(jobDefinition),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchJobs = joi.object().required().keys({
  items: joi.array().items(job),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchEdges = joi.object().required().keys({
  items: joi.array().items(edge),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchObjects = joi.object().required().keys({
  items: joi.array().items(joi.object()),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchFiles = joi.object().required().keys({
  items: joi.array().items(file),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchHpcConfigs = joi.object().required().keys({
  items: joi.array().items(hpcConfig),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchResourceRequirements = joi.object().required().keys({
  items: joi.array().items(resourceRequirements),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchResults = joi.object().required().keys({
  items: joi.array().items(result),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchUserData = joi.object().required().keys({
  items: joi.array().items(joi.object()),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchComputeNodeStats = joi.object().required().keys({
  items: joi.array().items(computeNodeStats),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

const batchJobProcessStats = joi.object().required().keys({
  items: joi.array().items(jobProcessStats),
  skip: joi.number().required(),
  max_limit: joi.number().required(),
  count: joi.number().required(),
  total_count: joi.number().required(),
  has_more: joi.boolean().required(),
});

module.exports = {
  autoTuneStatus,
  batchComputeNodeStats,
  batchComputeNodes,
  batchEdges,
  batchFiles,
  batchHpcConfigs,
  batchJobDefinitions,
  batchJobProcessStats,
  batchJobs,
  batchObjects,
  batchResourceRequirements,
  batchResults,
  batchUserData,
  computeNode,
  computeNodeResourceStatConfig,
  computeNodeStats,
  edge,
  file,
  hpcConfig,
  isComplete,
  job,
  jobDefinition,
  jobInternal,
  jobProcessStats,
  jobUserData,
  readyJobsResourceRequirements,
  resourceRequirements,
  result,
  workerResources,
  workflow,
  workflowConfig,
  workflowEstimate,
  workflowStatus,
};
