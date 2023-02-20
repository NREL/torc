const joi = require('joi');

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
  runtime_seconds: joi.number().default(0.0),
  // This only exists to all prepareJobsForSubmission to take less time to find
  // jobs with exclusive access.
  internal: jobInternal.validate({}).value,
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
  return_code: joi.number().required(),
  exec_time_minutes: joi.number().required(),
  completion_time: joi.string().required(),
  status: joi.string().required(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

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

const workflowEstimate = joi.object().required().keys({
  estimates_by_round: joi.array().items(readyJobsResourceRequirements),
});

const isComplete = joi.object().required().keys({
  is_complete: joi.boolean().required(),
});

const workflow = joi.object().required().keys({
  jobs: joi.array().items(jobDefinition).default([]),
  files: joi.array().items(file).default([]),
  resource_requirements: joi.array().items(resourceRequirements).default([]),
  schedulers: joi.array().items(hpcConfig).default([]),
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

module.exports = {
  batchComputeNodes,
  batchEdges,
  batchObjects,
  batchFiles,
  batchHpcConfigs,
  batchJobDefinitions,
  batchJobs,
  batchResourceRequirements,
  batchResults,
  batchUserData,
  computeNode,
  edge,
  file,
  hpcConfig,
  isComplete,
  job,
  jobDefinition,
  jobInternal,
  jobUserData,
  readyJobsResourceRequirements,
  resourceRequirements,
  result,
  workerResources,
  workflow,
  workflowEstimate,
};
