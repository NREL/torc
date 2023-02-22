const {query} = require('@arangodb');
const db = require('@arangodb').db;
const graphModule = require('@arangodb/general-graph');
const {GiB, GRAPH_NAME, JobStatus} = require('./defs');
const graph = graphModule._graph(GRAPH_NAME);
const schemas = require('./api/schemas');
const utils = require('./utils');

/** Add 'blocks' edges between jobs by looking at their file edges. */
function addBlocksEdgesFromFiles() {
  for (const file of graph.files.all()) {
    const fid = file._id;
    const fromVertices = query`
      FOR v
          IN 1
          INBOUND ${fid}
          GRAPH ${GRAPH_NAME}
          OPTIONS { edgeCollections: 'produces' }
          RETURN v._id
    `;
    if (fromVertices.count() > 0) {
      const toVertices = query`
        FOR v
            IN 1
            INBOUND ${file._id}
            GRAPH ${GRAPH_NAME}
            OPTIONS { edgeCollections: 'needs' }
            RETURN v._id
      `;
      for (const item of utils.product(
          fromVertices.toArray(),
          toVertices.toArray(),
      )) {
        const fromVertex = item[0];
        const toVertex = item[1];
        const cursor = query({count: true})`
            FOR edge IN needs
              FILTER edge._from == ${fromVertex} AND edge._to == ${toVertex}
              RETURN edge
            `;
        if (cursor.count() == 0) {
          graph.blocks.save({_from: fromVertex, _to: toVertex});
          console.log(`${fromVertex} blocks ${toVertex}`);
        }
      }
    }
  }
}

/**
 * Add a file document to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addFile(doc) {
  const existing = getDocumentIfAlreadyStored(doc, 'files');
  if (existing != null) {
    return existing;
  }

  doc._key = doc.name;
  const meta = db.files.save(doc);
  Object.assign(doc, meta);
  console.log(`Added file ${doc.name}`);
  return doc;
}

/**
 * Add an hpc config document to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addHpcConfig(doc) {
  const existing = getDocumentIfAlreadyStored(doc, 'hpc_configs');
  if (existing != null) {
    return existing;
  }

  doc._key = doc.name;
  const meta = db.hpc_configs.save(doc);
  Object.assign(doc, meta);
  console.log(`Added hpc_config ${doc.name}`);
  return doc;
}

/**
 * Add a job document to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addJob(doc) {
  const existing = getDocumentIfAlreadyStored(doc, 'jobs');
  if (existing != null) {
    return existing;
  }

  doc._key = doc.name;
  if (doc.status == null) {
    doc.status = JobStatus.Uninitialized;
  }
  const meta = db.jobs.save(doc);
  Object.assign(doc, meta);
  console.log(`Added job ${doc.name}`);
  return doc;
}

/**
 * Add a job from its definition to the database and create edges.
 * @param {Object} jobDef
 * @return {Object}
 */
function addJobDefinition(jobDef) {
  for (const filename of jobDef.input_files) {
    if (!graph.files.exists(filename)) {
      throw new Error(`job ${jobDef.name} input file ${filename} is not stored`);
    }
  }
  for (const filename of jobDef.output_files) {
    if (!graph.files.exists(filename)) {
      throw new Error(`job ${jobDef.name} output file ${filename} is not stored`);
    }
  }
  for (const jobName of jobDef.blocked_by) {
    if (!graph.jobs.exists(jobName)) {
      throw new Error(`job ${jobDef.name} with blocked_by ${jobName} is not stored`);
    }
  }
  if (jobDef.scheduler != null && !graph.hpc_configs.exists(jobDef.scheduler)) {
    throw new Error(`job ${jobDef.name} scheduler ${jobDef.scheduler} is not stored`);
  }
  const rr = jobDef.resource_requirements;
  if (rr != null && !graph.resource_requirements.exists(rr)) {
    throw new Error(`job ${jobDef.name} resource_requirements ${rr} is not stored`);
  }

  const job = addJob({
    name: jobDef.name,
    command: jobDef.command,
    user_data: jobDef.user_data,
    cancel_on_blocking_job_failure: jobDef.cancel_on_blocking_job_failure,
    interruptible: jobDef.interruptible,
    internal: schemas.jobInternal.validate({}).value,
  });
  for (const filename of jobDef.input_files) {
    const file = graph.files.document(filename);
    const edge = {_from: job._id, _to: file._id};
    graph.needs.save(edge);
  }
  for (const filename of jobDef.output_files) {
    const file = graph.files.document(filename);
    const edge = {_from: job._id, _to: file._id};
    graph.produces.save(edge);
  }
  for (const jobName of jobDef.blocked_by) {
    const blockingJob = graph.jobs.document(jobName);
    const edge = {_from: blockingJob._id, _to: job._id};
    graph.blocks.save(edge);
  }
  if (jobDef.resource_requirements != null) {
    const rr = graph.resource_requirements.document(jobDef.resource_requirements);
    const edge = {_from: job._id, _to: rr._id};
    graph.requires.save(edge);
  }
  if (jobDef.scheduler != null) {
    const scheduler = graph.hpc_configs.document(jobDef.scheduler);
    const edge = {_from: job._id, _to: scheduler._id};
    graph.scheduled_bys.save(edge);
  }
  for (const userData of jobDef.user_data) {
    const doc = addUserData(userData);
    graph.stores.save({_from: job._id, _to: doc._id});
  }
  return job;
}

/**
 * Add a resource requirements document to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addResourceRequirements(doc) {
  const existing = getDocumentIfAlreadyStored(doc, 'resource_requirements');
  if (existing != null) {
    return existing;
  }
  doc._key = doc.name;
  utils.getMemoryInBytes(doc.memory);
  const meta = db.resource_requirements.save(doc);
  Object.assign(doc, meta);
  console.log(`Added resource_requirements ${doc.name}`);
  return doc;
}

/**
 * Add a result to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addResult(doc) {
  const meta = db.results.save(doc);
  Object.assign(doc, meta);
  return doc;
}

/**
 * Add a user data object to the database.
 * @param {Object} doc
 * @return {Object}
 */
function addUserData(doc) {
  const meta = db.user_data.save(doc);
  Object.assign(doc, meta);
  return doc;
}

/**
 * Perform a dry run of all jobs to get a rough estimate of how many rounds
 * and resources are required.
 * @return {Object}
 */
function estimateWorkflow() {
  const byRounds = [];
  resetJobStatus();
  initializeJobStatus();

  do {
    const reqs = getReadyJobRequirements();
    byRounds.push(reqs);
    if (reqs.num_jobs == 0) {
      break;
    }
    for (const job of graph.jobs.byExample({status: JobStatus.Ready})) {
      job.status = JobStatus.Done;
      let result = {
        name: job.name,
        return_code: 0,
        completion_time: new Date().toISOString(),
        exec_time_minutes: 5,
        status: job.status,
      };
      result = addResult(result);
      graph.returned.save({_from: job._id, _to: result._id});
      manageJobStatusChange(job);
    }
  } while (!isWorkflowComplete());
  resetJobStatus();
  initializeJobStatus();

  return {estimates_by_round: byRounds};
}

/**
 * Get information about the resources required for currently-available jobs.
 * @return {Object}
 */
function getReadyJobRequirements() {
  let numCpus = 0;
  let numGpus = 0;
  let numJobs = 0;
  let maxMemory = 0;
  let totalMemory = 0;
  let maxRuntime = 0;
  let maxRuntimeDuration = '';
  let maxNumNodes = 0;

  for (const job of graph.jobs.byExample({status: JobStatus.Ready})) {
    const reqs = getJobResourceRequirements(job);
    numJobs += 1;
    numCpus += reqs.num_cpus;
    numGpus += reqs.num_gpus;
    memory = utils.getMemoryInBytes(reqs.memory);
    totalMemory += memory;
    if (memory > maxMemory) {
      maxMemory = memory;
    }
    const runtime = utils.getTimeDurationInSeconds(reqs.runtime);
    if (runtime > maxRuntime) {
      maxRuntime = runtime;
      maxRuntimeDuration = reqs.runtime;
    }
    if (reqs.num_nodes > maxNumNodes) {
      maxNumNodes = reqs.num_nodes;
    }
  }
  return {
    num_jobs: numJobs,
    num_cpus: numCpus,
    num_gpus: numGpus,
    memory_gb: totalMemory / GiB,
    max_memory_gb: maxMemory / GiB,
    max_num_nodes: maxNumNodes,
    max_runtime: maxRuntimeDuration,
  };
}

/**
 * Return all jobs blocking this job.
 * @param {Object} job
 * @return {Array}
 */
function getBlockingJobs(job) {
  const blockingJobs = [];
  const jobId = job._id;
  const cursor = query`
    FOR v, e, p
      IN 1
      INBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'blocks' }
      RETURN p.vertices[1]
  `;
  for (const job of cursor) {
    blockingJobs.push(job);
  }

  return blockingJobs;
}

const filesFields = ['name', 'path', 'file_hash', 'st_mtime'];
const jobsFields = [
  'name',
  'command',
  'status',
  'cancel_on_blocking_job_failure',
];
const hpcConfigsFields = [
  'name',
  'hpc_type',
  'account',
  'partition',
  'qos',
  'walltime',
];
const resourceRequirementsFields = [
  'name',
  'num_cpus',
  'num_gpus',
  'memory',
  'runtime',
];

/**
 * Return the current version of the resource_requirements document if it is already stored.
 * Return null if the _id doesn't exist or the existing document has different content.
 * @param {Object} doc
 * @param {string} collectionName
 * @return {Object}
 */
function getDocumentIfAlreadyStored(doc, collectionName) {
  let collection = '';
  let fields = [];
  switch (collectionName) {
    case 'files':
      collection = graph.files;
      fields = filesFields;
      break;
    case 'hpc_configs':
      collection = graph.hpc_configs;
      fields = hpcConfigsFields;
      break;
    case 'jobs':
      collection = graph.jobs;
      fields = jobsFields;
      break;
    case 'resource_requirements':
      collection = graph.resource_requirements;
      fields = resourceRequirementsFields;
      break;
    default:
      throw new Error(`collection name ${collectionName} is not handled`);
  }
  if (!collection.exists(doc.name)) {
    return null;
  }
  const existing = collection.document(doc.name);
  for (const field of fields) {
    if (doc[field] !== existing[field]) {
      return null;
    }
  }

  return existing;
}

/**
 * Return files needed by the passed job name.
 * @param {string} name - job name
 * @return {ArangoQueryCursor}
 */
function getFilesNeededByJob(name) {
  const jobId = `jobs/${name}`;
  return query({count: true})`
      FOR v
          IN 1
          OUTBOUND ${jobId}
          GRAPH ${GRAPH_NAME}
          OPTIONS { edgeCollections: 'needs' }
          RETURN v
    `;
}

/**
 * Return files needed by the passed job name.
 * @param {string} name - job name
 * @return {ArangoQueryCursor}
 */
function getFilesProducedByJob(name) {
  const jobId = `jobs/${name}`;
  return query({count: true})`
      FOR v
          IN 1
          OUTBOUND ${jobId}
          GRAPH ${GRAPH_NAME}
          OPTIONS { edgeCollections: 'produces' }
          RETURN v
    `;
}

/**
 * Return a job definition.
 * @param {Object} job - Instance of schemas.job
 * @return {Object} - Instance of schemas.jobDefinition
 */
function getJobDefinition(job) {
  const blockingJobs = [];
  const inputFiles = [];
  const outputFiles = [];
  const userData = [];

  for (const blockingJob of getBlockingJobs(job)) {
    blockingJobs.push(blockingJob.name);
  }
  for (const file of getFilesNeededByJob(job.name)) {
    inputFiles.push(file.name);
  }
  for (const file of getFilesProducedByJob(job.name)) {
    outputFiles.push(file.name);
  }
  for (const data of getUserDataStoredByJob(job.name)) {
    delete(data._id);
    delete(data._key);
    delete(data._rev);
    userData.push(data);
  }

  const scheduler = getJobScheduler(job);
  return {
    name: job.name,
    command: job.command,
    cancel_on_blocking_job_failure: job.cancel_on_blocking_job_failure,
    blocked_by: blockingJobs,
    input_files: inputFiles,
    output_files: outputFiles,
    resource_requirements: getJobResourceRequirements(job).name,
    scheduler: scheduler == null ? null : scheduler.name,
  };
}

/**
 * Return the job's resource requirements, using default values if none are assigned.
 * @param {Object} job
 * @return {Object}
 */
function getJobResourceRequirements(job) {
  const jobId = job._id;
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'requires' }
      RETURN p.vertices[1]
  `;
  if (cursor.count() == 0) {
    const res = schemas.resourceRequirements.validate({name: 'default'});
    if (res.error !== null) {
      throw new Error('BUG: Failed to create default resourceRequirements');
    }
    return res.value;
  } else if (cursor.count() > 1) {
    // TODO: check at post
    throw new Error(
        'BUG: Only one resource requirement can be assigned to a job.',
    );
  }
  return cursor.toArray()[0];
}

/**
 * Return the job's scheduler, returning null if one isn't defined.
 * @param {Object} job
 * @return {string}
 */
function getJobScheduler(job) {
  const jobId = job._id;
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'scheduled_bys' }
      RETURN p.vertices[1]
  `;
  if (cursor.count() == 0) {
    return null;
  } else if (cursor.count() > 1) {
    throw new Error('BUG: Only one scheduler can be assigned to a job.');
  }
  return cursor.toArray()[0];
}

/**
 * Return jobs that need the file.
 * @param {string} name - file name
 * @return {ArangoQueryCursor}
 */
function getJobsThatNeedFile(name) {
  const fileId = `files/${name}`;
  return query({count: true})`
      FOR v
          IN 1
          INBOUND ${fileId}
          GRAPH ${GRAPH_NAME}
          OPTIONS { edgeCollections: 'needs' }
          RETURN v
    `;
}

/**
 * Return all result documents connected to the job, sorted by completion time.
 * Return null if the job does not have a result.
 * @param {string} jobName
 * @return {Object}
 */
function getJobResults(jobName) {
  const jobId = `jobs/${jobName}`;
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'returned' }
      RETURN p.vertices[1]
  `;
  const count = cursor.count();
  if (count == 0) {
    return null;
  }

  results = cursor.toArray();
  if (results.length > 1) {
    results.sort(compareTimestamp);
  }
  return results;
}

/**
 * Comparison function for sorting timestamp strings.
 * @param {Object} result1
 * @param {Object} result2
 * @return {number}
 */
function compareTimestamp(result1, result2) {
  t1 = new Date(result1.completion_time).getTime();
  t2 = new Date(result2.completion_time).getTime();
  return t1 - t2;
}

/**
 * Return the latest job result.
 * Return null if the job does not have a result.
 * @param {string} jobName
 * @return {Object}
 */
function getLatestJobResult(jobName) {
  const results = getJobResults(jobName);
  if (results == null) {
    return results;
  }

  return results.slice(-1)[0];
}

/**
 * Return the user data that is connected to the job.
 * @param {string} jobName
 * @return {ArangoQueryCursor}
 */
function getUserDataStoredByJob(jobName) {
  const jobId = `jobs/${jobName}`;
  return query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'stores' }
      RETURN p.vertices[1]
  `;
}

/** Set initial job status. */
function initializeJobStatus() {
  // TODO: Can this be more efficient with one traversal?
  for (const job of graph.jobs.all()) {
    const jobResources = getJobResourceRequirements(job);
    if (job.internal == null) {
      job.internal = schemas.jobInternal.validate({}).value;
    }
    job.internal.memory_bytes = utils.getMemoryInBytes(jobResources.memory);
    job.internal.runtime_seconds = utils.getTimeDurationInSeconds(jobResources.runtime);
    job.internal.num_cpus = jobResources.num_cpus;
    if (isJobInitiallyBlocked(job._id)) {
      job.status = JobStatus.Blocked;
    } else if (job.status != JobStatus.Done) {
      job.status = JobStatus.Ready;
    }
    graph.jobs.update(job, job);
  }
  console.log(
      `Initialized all incomplete job status to ${JobStatus.Ready} or ${JobStatus.Blocked}`,
  );
}

/**
 * Return true if the job is blocked by another job.
 * @param {string} jobId - job ID
 * @return {bool}
 *
 **/
function isJobBlocked(jobId) {
  const cursor = query`
    FOR v
        IN 1
        INBOUND ${jobId}
        GRAPH ${GRAPH_NAME}
        OPTIONS { edgeCollections: 'blocks' }
        RETURN v.status
  `;
  for (const status of cursor) {
    if (!isJobStatusComplete(status)) {
      return true;
    }
  }

  return false;
}

/**
 * Return true if the job is initially blocked by another job.
 * @param {string} jobId - job ID
 * @return {bool}
 *
 **/
function isJobInitiallyBlocked(jobId) {
  const cursor = query({count: true})`
    FOR v
        IN 1
        INBOUND ${jobId}
        GRAPH ${GRAPH_NAME}
        OPTIONS { edgeCollections: 'blocks' }
        FILTER v.status != ${JobStatus.Done}
        RETURN v._id
  `;
  return cursor.count() > 0;
}

/**
 * Return true if the job status indicates completion.
 * @param {string} status
 * @return {bool}
 */
function isJobStatusComplete(status) {
  return status == JobStatus.Done || status == JobStatus.Canceled;
}

/**
 * Return true if the workflow is complete.
 * @return {bool}
 */
function isWorkflowComplete() {
  // TODO: Store a status object in the database that stores these things:
  // - is_canceled: allows the user to cancel a workflow and workers to cancel jobs
  // - compute node scheduler IDs: this will allow us to cancel them
  // - run ID: every time a workflow is restarted, bump the ID
  const cursor = query({count: true})`
    FOR job in jobs
        FILTER !(job.status == ${JobStatus.Done} OR job.status == ${JobStatus.Canceled})
        LIMIT 1
        RETURN job.name
  `;
  return cursor.count() == 0;
}

/**
 * Update a job status and manage all downstream consequences.
 * @param {Object} job
 * @return {Object}
 */
function manageJobStatusChange(job) {
  const oldStatus = graph.jobs.document(job.name).status;
  if (job.status == oldStatus) {
    return job;
  }
  const meta = db.jobs.update(job, job);
  Object.assign(job, meta);

  if (!isJobStatusComplete(oldStatus) && isJobStatusComplete(job.status)) {
    const result = getLatestJobResult(job.name);
    if (result == null) {
      throw new Error(
          `A job must have a result before it is completed: ${job.name}.`,
      );
    }
    updateBlockedJobsFromCompletion(job);
  } else if (isJobStatusComplete(oldStatus) && job.status == JobStatus.Uninitialized) {
    updateJobsFromCompletionReversal(job);
  }
  return job;
}

/**
 * Prepare a list of jobs for submission that meet the worker resource availability.
 * @param {Object} workerResources
 * @param {Number} limit
 * @return {Array}
 */
function prepareJobsForSubmission(workerResources, limit) {
  const jobs = [];
  let availableCpus = workerResources.num_cpus;
  let availableMemory = workerResources.memory_gb * GiB;
  const queryLimit = limit == null ? availableCpus : limit;
  const workerTimeLimit =
    workerResources.time_limit == null ?
      Number.MAX_SAFE_INTEGER : utils.getTimeDurationInSeconds(workerResources.time_limit);
  // TODO: numNodes and numGpus
  db._executeTransaction({
    collections: {
      exclusive: 'jobs',
      allowImplicit: false,
    },
    action: function() {
      const db = require('@arangodb').db;
      const cursor = query`
        FOR job IN jobs
          FILTER job.status == ${JobStatus.Ready}
            && job.internal.memory_bytes < ${availableMemory}
            && job.internal.num_cpus < ${availableCpus}
            && job.internal.runtime_seconds < ${workerTimeLimit}
          LIMIT ${queryLimit}
          RETURN job
      `;

      // This implementation stores the job resource information in the internal object
      // so that it doesn't have to run a graph query while holding an exclusive lock.
      for (const job of cursor) {
        if (
          job.internal.num_cpus <= availableCpus &&
          job.internal.memory_bytes <= availableMemory
        ) {
          job.status = JobStatus.SubmittedPending;
          const meta = db.jobs.update(job, job);
          Object.assign(job, meta);
          jobs.push(job);
          availableCpus -= job.internal.num_cpus;
          availableMemory -= job.internal.memory_bytes;
          if (availableCpus == 0 || availableMemory == 0) {
            break;
          }
        }
      }
    },
  });

  // console.log(`Prepared ${jobs.length} jobs for submission.`);
  return jobs;
}

/** Reset job status to uninitialized. */
function resetJobStatus() {
  for (const job of graph.jobs.all()) {
    job.status = JobStatus.Unknown;
    graph.jobs.update(job, job);
  }
  console.log(`Reset all job status to ${JobStatus.Uninitialized}`);
}

/**
 * Update blocked jobs after a job completion.
 * @param {Object} job
 */
function updateBlockedJobsFromCompletion(job) {
  const jobId = job._id;
  const cursor = query`
    FOR v, e, p
      IN 1
      OUTBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'blocks', uniqueVertices: 'global', order: 'bfs' }
      RETURN p.vertices[1]
  `;
  const result = getLatestJobResult(job.name);
  // TODO: should other queries use bfs?
  for (const blockedJob of cursor) {
    if (!isJobBlocked(blockedJob._id)) {
      if (result.return_code != 0 && blockedJob.cancel_on_blocking_job_failure) {
        blockedJob.status = JobStatus.Canceled;
      } else {
        blockedJob.status = JobStatus.Ready;
      }
      graph.jobs.update(blockedJob, blockedJob);
    }
  }
}

/**
 * Update jobs after a job completion reversal.
 * @param {Object} job
 */
function updateJobsFromCompletionReversal(job) {
  const jobId = job._id;
  const numJobs = graph.jobs.count();
  const cursor = query`
    FOR v, e, p
      IN 1..${numJobs}
      OUTBOUND ${jobId}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'blocks', uniqueVertices: 'global', order: 'bfs' }
      RETURN v
  `;
  for (const downstreamJob of cursor) {
    if (downstreamJob.status != JobStatus.Uninitialized) {
      downstreamJob.status = JobStatus.Uninitialized;
      graph.jobs.update(downstreamJob, downstreamJob);
      console.log(`Reset job=${downstreamJob.name} status to ${JobStatus.Uninitialized}`);
    }
  }
}

module.exports = {
  addBlocksEdgesFromFiles,
  addFile,
  addHpcConfig,
  addJob,
  addJobDefinition,
  addResourceRequirements,
  addResult,
  addUserData,
  estimateWorkflow,
  getReadyJobRequirements,
  getBlockingJobs,
  getDocumentIfAlreadyStored,
  getFilesNeededByJob,
  getFilesProducedByJob,
  getJobDefinition,
  getJobResourceRequirements,
  getJobScheduler,
  getJobsThatNeedFile,
  getJobResults,
  getLatestJobResult,
  getUserDataStoredByJob,
  initializeJobStatus,
  isJobBlocked,
  isJobInitiallyBlocked,
  isJobStatusComplete,
  isWorkflowComplete,
  manageJobStatusChange,
  prepareJobsForSubmission,
  resetJobStatus,
  updateBlockedJobsFromCompletion,
};
