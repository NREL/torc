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
  st_mtime: joi.string().optional(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
  // Keep changes in sync with getDocumentIfAlreadyStored
});

const job = joi.object().required().keys({
  name: joi.string().required(),
  command: joi.string().required(),
  status: joi.string(),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  return_code: joi.number().default(0),
  // TODO container information
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

// This schema is used in the user workflow construction but is never stored.
const jobDefinition = joi.object().required().keys({
  name: joi.string().required(),
  command: joi.string().required(),
  cancel_on_blocking_job_failure: joi.boolean().default(true),
  scheduler: joi.string().optional(),
  resource_requirements: joi.string().optional(),
  input_files: joi.array().items(joi.string()).default([]),
  output_files: joi.array().items(joi.string()).default([]),
  blocked_by: joi.array().items(joi.string()).default([]),
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

const jobEstimate = joi.object().required().keys({
  num_jobs: joi.number().required(),
  num_cpus: joi.number().required(),
  num_gpus: joi.number().required(),
  memory_gb: joi.number().required(),
  status: joi.string(),
  _key: joi.string(),
  _id: joi.string(),
  _rev: joi.string(),
});

const resourceRequirements = joi.object().required().keys({
  name: joi.string().required(),
  num_cpus: joi.number().default(1),
  num_gpus: joi.number().default(0),
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

const workflowEstimate = joi.object().required().keys({
  estimates_by_round: [jobEstimate],
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

module.exports = {
  edge,
  file,
  isComplete,
  job,
  jobDefinition,
  hpcConfig,
  jobEstimate,
  resourceRequirements,
  result,
  workerResources,
  workflow,
  workflowEstimate,
};
