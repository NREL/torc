// Manages documents in the database.

'use strict';
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const {JobStatus} = require('./defs');
const utils = require('./utils');
const config = require('./config');
const schemas = require('./api/schemas');
const query = require('./query');

/**
 * Add a file document to the database.
 * @param {Object} doc
 * @param {Object} workflow
 * @return {Object}
 */
function addFile(doc, workflow) {
  return addWorkflowDocument(doc, 'files', workflow, true, true);
}

/**
 * Add a job from its specification to the database and create edges.
 * @param {Object} jobSpec
 * @param {Object} workflow
 * @return {Object}
 */
function addJobSpecification(jobSpec, workflow) {
  const filesCollection = config.getWorkflowCollection(workflow, 'files');
  const jobsCollection = config.getWorkflowCollection(workflow, 'jobs');
  const rrCollection = config.getWorkflowCollection(workflow, 'resource_requirements');
  const scheduledBysCollection = config.getWorkflowCollection(workflow, 'scheduled_bys');
  const userDataCollection = config.getWorkflowCollection(workflow, 'user_data');

  let schedulerConfigId = null;

  for (const fileName of jobSpec.input_files) {
    // Will throw if not correct.
    getDocumentByUniqueFilter(filesCollection, {name: fileName});
  }
  for (const fileName of jobSpec.output_files) {
    getDocumentByUniqueFilter(filesCollection, {name: fileName});
  }
  for (const jobName of jobSpec.blocked_by) {
    getDocumentByUniqueFilter(jobsCollection, {name: jobName});
  }
  if (jobSpec.scheduler != '' && jobSpec.scheduler != null) {
    schedulerConfigId = getSchedulerConfig(jobSpec.scheduler, workflow)._id;
  }
  for (const name of jobSpec.input_user_data) {
    getDocumentByUniqueFilter(userDataCollection, {name: name});
  }
  for (const name of jobSpec.output_user_data) {
    getDocumentByUniqueFilter(userDataCollection, {name: name});
  }
  if (jobSpec.resource_requirements != null) {
    getDocumentByUniqueFilter(rrCollection, {name: jobSpec.resource_requirements});
  }

  const newJob = {
    name: jobSpec.name,
    command: jobSpec.command,
    invocation_script: jobSpec.invocation_script,
    cancel_on_blocking_job_failure: jobSpec.cancel_on_blocking_job_failure,
    needs_compute_node_schedule: jobSpec.needs_compute_node_schedule,
    supports_termination: jobSpec.supports_termination,
    blocked_by: [],
    input_files: [],
    output_files: [],
    input_user_data: [],
    output_user_data: [],
    resource_requirements: null,
    scheduler: null,
    internal: schemas.jobInternal.validate({}).value,
  };
  if (jobSpec.key != null) {
    newJob._key = jobSpec._key;
  }

  for (const fileName of jobSpec.input_files) {
    const file = getDocumentByUniqueFilter(filesCollection, {name: fileName});
    newJob.input_files.push(file._id);
  }
  for (const fileName of jobSpec.output_files) {
    const file = getDocumentByUniqueFilter(filesCollection, {name: fileName});
    newJob.output_files.push(file._id);
  }
  for (const jobName of jobSpec.blocked_by) {
    const blockingJob = getDocumentByUniqueFilter(jobsCollection, {name: jobName});
    newJob.blocked_by.push(blockingJob._id);
  }
  for (const name of jobSpec.input_user_data) {
    const userData = getDocumentByUniqueFilter(userDataCollection, {name: name});
    newJob.input_user_data.push(userData._id);
  }
  for (const name of jobSpec.output_user_data) {
    const userData = getDocumentByUniqueFilter(userDataCollection, {name: name});
    newJob.output_user_data.push(userData._id);
  }
  if (jobSpec.resource_requirements != null) {
    const rr = getDocumentByUniqueFilter(rrCollection, {name: jobSpec.resource_requirements});
    newJob.resource_requirements = rr._id;
  }
  if (schedulerConfigId != null) {
    newJob.scheduler = schedulerConfigId;
  }
  return addJob(newJob, workflow);
}

/**
 * Add a job with its edge definitions.
 * @param {schemas.job} job
 * @param {Object} workflow
 * @return {string}
 */
function addJob(job, workflow) {
  const blocksCollection = config.getWorkflowCollection(workflow, 'blocks');
  const needsCollection = config.getWorkflowCollection(workflow, 'needs');
  const producesCollection = config.getWorkflowCollection(workflow, 'produces');
  const requiresCollection = config.getWorkflowCollection(workflow, 'requires');
  const consumesCollection = config.getWorkflowCollection(workflow, 'consumes');
  const scheduledBysCollection = config.getWorkflowCollection(workflow, 'scheduled_bys');
  const storesCollection = config.getWorkflowCollection(workflow, 'stores');

  if (job.status == null) {
    job.status = JobStatus.Uninitialized;
  }
  const dbJob = JSON.parse(JSON.stringify(job));
  const toRemove = [
    'blocked_by', 'input_files', 'output_files', 'input_user_data', 'output_user_data',
    'resource_requirements', 'scheduler',
  ];
  for (const field of toRemove) {
    delete dbJob[field];
  }
  const addedJob = addWorkflowDocument(dbJob, 'jobs', workflow, false, true);
  const jobId = addedJob._id;

  if (job.resource_requirements != null) {
    requiresCollection.save({_from: jobId, _to: job.resource_requirements});
  }
  if (job.scheduler != null) {
    scheduledBysCollection.save({_from: jobId, _to: job.scheduler});
  }
  for (const id of job.input_files) {
    needsCollection.save({_from: jobId, _to: id});
  }
  for (const id of job.output_files) {
    producesCollection.save({_from: jobId, _to: id});
  }
  for (const id of job.input_user_data) {
    consumesCollection.save({_from: jobId, _to: id});
  }
  for (const id of job.output_user_data) {
    storesCollection.save({_from: jobId, _to: id});
  }
  for (const id of job.blocked_by) {
    blocksCollection.save({_from: id, _to: jobId});
  }

  return addedJob;
}

/**
 * Add jobs in bulk with all edge definitions.
 * This is essentially required for large workflows because it reduces network traffic
 * significantly, and so is much faster.
 * @param {Array} jobs
 * @param {Object} workflow
 * @return {Array}
 */
function addJobs(jobs, workflow) {
  const addedJobs = [];
  for (const job of jobs) {
    addedJobs.push(addJob(job, workflow));
  }
  return addedJobs;
}

/**
 * Add a resource requirements document to the database.
 * @param {Object} doc
 * @param {Object} workflow
 * @return {Object}
 */
function addResourceRequirements(doc, workflow) {
  utils.getMemoryInBytes(doc.memory);
  return addWorkflowDocument(doc, 'resource_requirements', workflow, true, true);
}

/**
 * Add a result to the database.
 * @param {Object} doc
 * @param {Object} workflow
 * @return {Object}
 */
function addResult(doc, workflow) {
  return addWorkflowDocument(doc, 'results', workflow, false, true);
}

/**
 * Add a scheduler document to the database.
 * @param {Object} doc
 * @param {String} collectionName
 * @param {Object} workflow
 * @return {Object}
 */
function addScheduler(doc, collectionName, workflow) {
  return addWorkflowDocument(doc, collectionName, workflow, true, true);
}

/**
 * Add a user data object to the database.
 * @param {Object} doc
 * @param {Object} workflow
 * @return {Object}
 */
function addUserData(doc, workflow) {
  return addWorkflowDocument(doc, 'user_data', workflow, false, true);
}

/**
 * Add a document to the database.
 * @param {Object} doc
 * @param {string} collectionName
 * @param {Object} workflow
 * @param {bool} checkExisting
 * @param {bool} allowCustomKey
 * @return {Object}
 */
function addWorkflowDocument(doc, collectionName, workflow, checkExisting, allowCustomKey) {
  const collection = config.getWorkflowCollection(workflow, collectionName);
  if (checkExisting) {
    const existing = getDocumentIfAlreadyStored(doc, collection);
    if (existing != null) {
      return existing;
    }
  }
  if (!allowCustomKey && doc._key != null) {
    throw new Error(`key=${doc._key} cannot be set on document insertion`);
  }
  const meta = collection.save(doc);
  const newDoc = JSON.parse(JSON.stringify(doc));
  Object.assign(newDoc, meta);
  return newDoc;
}

/**
 * Add a workflow document to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addWorkflow(doc) {
  if (doc.timestamp == null || doc.timestamp == '') {
    doc.timestamp = (new Date()).toISOString();
  }
  const meta = db.workflows.save(doc);
  Object.assign(doc, meta);

  const workflowConfig = schemas.workflowConfig.validate({}).value;
  const configMeta = db.workflow_configs.save(workflowConfig);
  Object.assign(workflowConfig, configMeta);

  const status = {
    run_id: 0,
    is_canceled: false,
    scheduled_compute_node_ids: [],
    auto_tune_status: schemas.autoTuneStatus.validate({}).value,
  };
  const statusMeta = db.workflow_statuses.save(status);
  Object.assign(status, statusMeta);

  const configEdge = {_from: doc._id, _to: workflowConfig._id};
  const statusEdge = {_from: doc._id, _to: status._id};
  db.has_workflow_config.save(configEdge);
  db.has_workflow_status.save(statusEdge);

  config.createWorkflowCollections(doc);
  console.debug(`Added workflow ${doc._key}`);
  return doc;
}

/**
 * Cancel the workflow and all active jobs.
 * @param {Object} workflow
 */
function cancelWorkflow(workflow) {
  const status = query.getWorkflowStatus(workflow);
  status.is_canceled = true;
  db.workflow_statuses.update(status, status, {mergeObjects: false});
  query.cancelWorkflowJobs(workflow);
}

/**
 * Compute a hash of all job inputs that can affect results.
 * @param {Object} job
 * @param {Object} workflow
 * @return {number}
 */
function computeJobInputHash(job, workflow) {
  const data = {
    command: job.command,
    invocation_script: job.invocation_script,
    input_user_data_keys: query.listConsumesUserDataRevisions(job, workflow),
    output_user_data_keys: query.listStoresUserDataRevisions(job, workflow),
    needs_file_keys: query.listNeedsFileRevisions(job, workflow),
  };
  return utils.hashCode(JSON.stringify(data));
}

/**
 * Delete all documents connected to the workflow.
 * @param {Object} workflow
 */
function deleteWorkflow(workflow) {
  const workflowGraphName = config.getWorkflowGraphName(workflow);
  if (graphModule._list().includes(workflowGraphName)) {
    graphModule._drop(workflowGraphName, true);
  }
  for (const name of config.DOCUMENT_COLLECTION_NAMES) {
    const collectionName = config.getWorkflowCollectionName(workflow, name);
    if (db._collection(collectionName)) {
      db._drop(collectionName);
    }
  }

  const workflowConfig = query.getWorkflowConfig(workflow);
  const status = query.getWorkflowStatus(workflow);
  const graph = graphModule._graph(config.GRAPH_NAME);
  graph.workflow_configs.remove(workflowConfig._id);
  graph.workflow_statuses.remove(status._id);
  graph.workflows.remove(workflow._id);
}

/**
 * Return the document matching the fitler. Throws if there is not exactly one match.
 * @param {Object} collection
 * @param {Object} filter
 * @return {Object}
 */
function getDocumentByUniqueFilter(collection, filter) {
  const result = collection.byExample(filter).toArray();
  if (result.length == 0) {
    throw new Error(`filter = ${JSON.stringify(filter)} does not match any documents`);
  } else if (result.length != 1) {
    throw new Error(`filter = ${JSON.stringify(filter)} matches ${result.length} documents`);
  }
  return result[0];
}

/**
 * Return the current version of the resource_requirements document if it is already stored.
 * Return null if the _id doesn't exist or the existing document has different content.
 * @param {Object} doc
 * @param {Object} collection
 * @return {Object}
 */
function getDocumentIfAlreadyStored(doc, collection) {
  const filter = JSON.parse(JSON.stringify(doc));
  for (const property of ['_key', '_id', '_rev']) {
    delete filter[property];
  }
  const result = collection.byExample(filter);
  if (result.count() == 0) {
    return null;
  }
  if (result.count() > 1) {
    throw new Error(`filter ${JSON.stringify(filter)} returned ${result.count()} matches`);
  }
  return result.next();
}

/**
 * Return the scheduler config for the scheduler config reference.
 * @param {string} schedulerConfigId
 * @param {Object} workflow
 * @return {Object}
 */
function getSchedulerConfig(schedulerConfigId, workflow) {
  const fields = schedulerConfigId.split('/');
  if (fields.length != 2) {
    throw new Error(`${schedulerConfigId} must be split by /`);
  }
  const collectionName = fields[0];
  const name = fields[1];
  const collection = config.getWorkflowCollection(workflow, collectionName);
  return getDocumentByUniqueFilter(collection, {name: name});
}

/**
 * Return the workflow matching key. Throws if the key does not exist.
 * @param {string} key
 * @param {Object} res
 * @return {Object}
 */
function getWorkflow(key, res) {
  return getDocument(db.workflows, 'workflows', key, res);
}

/**
 * Return the workflow document matching key. Throws if the key does not exist.
 * @param {Object} workflow
 * @param {string} documentType
 * @param {string} key
 * @param {Object} res
 * @return {Object}
 */
function getWorkflowDocument(workflow, documentType, key, res) {
  const collection = config.getWorkflowCollection(workflow, documentType);
  return getDocument(collection, documentType, key, res);
}

/**
 * Return the document matching key. Throws if the key does not exist.
 * @param {Object} collection
 * @param {string} documentType
 * @param {string} key
 * @param {Object} res
 * @return {Object}
 */
function getDocument(collection, documentType, key, res) {
  try {
    return collection.document(key);
  } catch (e) {
    utils.handleArangoApiErrors(e, res, `Get ${documentType} with key=${key}`);
  }
}

/**
 * Return all collection names for a workflow.
 * @param {Object} workflow
 * @return {Array}
 */
function listWorkflowCollectionNames(workflow) {
  const names = [];
  for (const name of config.DOCUMENT_COLLECTION_NAMES) {
    names.push(config.getWorkflowCollectionName(workflow, name));
  }
  for (const name of config.VERTEX_NAMES) {
    names.push(config.getWorkflowCollectionName(workflow, name));
  }
  for (const name of config.EDGE_NAMES) {
    names.push(config.getWorkflowCollectionName(workflow, name));
  }
  return names;
}

/**
 * Check for completed jobs that have had input changes and reinitialize them.
 * There is no protection for concurrent requests.
 * @param {Object} workflow
 * @return {Array}
 */
function processChangedJobInputs(workflow) {
  const jobsCollection = config.getWorkflowCollection(workflow, 'jobs');
  const reinitializedJobs = [];

  for (const job of jobsCollection.byExample({'status': JobStatus.Done})) {
    // The query below will update all downstream jobs.
    const curJob = reinitializedJobs.length == 0 ? job : jobsCollection.document(job._key);
    if (curJob.status == JobStatus.Uninitialized) {
      reinitializedJobs.push(job._key);
      continue;
    }
    const hash = computeJobInputHash(job, workflow);
    if (hash != job.internal.hash) {
      job.status = JobStatus.Uninitialized;
      updateWorkflowDocument(workflow, 'jobs', job);
      query.updateJobsFromCompletionReversal(job, workflow);
      reinitializedJobs.push(job._key);
    }
  }
  return reinitializedJobs;
}

/**
 * Update the workflow document.
 * @param {Object} workflow
 * @param {String} documentType
 * @param {String} doc
 * @return {Object}
 */
function updateWorkflowDocument(workflow, documentType, doc) {
  const collection = config.getWorkflowCollection(workflow, documentType);
  const meta = collection.update(doc, doc, {mergeObjects: false});
  Object.assign(doc, meta);
  return doc;
}

module.exports = {
  addFile,
  addJobSpecification,
  addJob,
  addJobs,
  addResourceRequirements,
  addResult,
  addScheduler,
  addUserData,
  addWorkflow,
  cancelWorkflow,
  computeJobInputHash,
  deleteWorkflow,
  getSchedulerConfig,
  getWorkflow,
  getWorkflowDocument,
  listWorkflowCollectionNames,
  processChangedJobInputs,
  updateWorkflowDocument,
};
