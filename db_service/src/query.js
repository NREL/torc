'use strict';
const {aql, query} = require('@arangodb');
const errors = require('@arangodb').errors;
const CONFLICTING_REV = errors.ERROR_ARANGO_CONFLICT.code;
const db = require('@arangodb').db;
const {GiB, JobStatus, GRAPH_NAME} = require('./defs');
const schemas = require('./api/schemas');
const utils = require('./utils');
const config = require('./config');

/**
 * Add 'blocks' edges between jobs by looking at their file edges.
 * Safe to call multiple times; will skip duplicates.
 * @param {Object} workflow
 */
function addBlocksEdgesFromFiles(workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const blocksCollection = config.getWorkflowCollection(workflow, 'blocks');
  const needs = config.getWorkflowCollectionName(workflow, 'needs');
  const produces = config.getWorkflowCollectionName(workflow, 'produces');
  const files = config.getWorkflowCollection(workflow, 'files');
  // PERF: This is slow and needs to be made into one query.
  for (const file of files.all()) {
    const fid = file._id;
    const fromVertices = query`
      FOR v
          IN 1
          INBOUND ${fid}
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${produces} }
          RETURN v._id
    `;
    if (fromVertices.count() > 0) {
      const toVertices = query`
        FOR v
            IN 1
            INBOUND ${file._id}
            GRAPH ${graphName}
            OPTIONS { edgeCollections: ${needs} }
            RETURN v._id
      `;
      for (const item of utils.product(fromVertices.toArray(), toVertices.toArray())) {
        const fromVertex = item[0];
        const toVertex = item[1];
        if (blocksCollection.firstExample({_from: fromVertex, _to: toVertex}) === null) {
          blocksCollection.save({_from: fromVertex, _to: toVertex});
        }
      }
    }
  }
}

/**
 * Add 'blocks' edges between jobs by looking at their user_data consumes/stores edges.
 * Safe to call multiple times; will skip duplicates.
 * @param {Object} workflow
 */
function addBlocksEdgesFromUserData(workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const blocksCollection = config.getWorkflowCollection(workflow, 'blocks');
  const consumes = config.getWorkflowCollectionName(workflow, 'consumes');
  const stores = config.getWorkflowCollectionName(workflow, 'stores');
  const userData = config.getWorkflowCollection(workflow, 'user_data');
  // PERF: This is slow and needs to be made into one query.
  for (const item of userData.all()) {
    const fromVertices = query`
      FOR v
          IN 1
          INBOUND ${item._id}
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${stores} }
          RETURN v._id
    `;
    if (fromVertices.count() > 0) {
      const toVertices = query`
        FOR v
            IN 1
            INBOUND ${item._id}
            GRAPH ${graphName}
            OPTIONS { edgeCollections: ${consumes} }
            RETURN v._id
      `;
      for (const item of utils.product(fromVertices.toArray(), toVertices.toArray())) {
        const fromVertex = item[0];
        const toVertex = item[1];
        if (blocksCollection.firstExample({_from: fromVertex, _to: toVertex}) === null) {
          blocksCollection.save({_from: fromVertex, _to: toVertex});
        }
      }
    }
  }
}

/**
 * Cancel all active jobs in the workflow.
 * @param {Object} workflow
 */
function cancelWorkflowJobs(workflow) {
  const collection = config.getWorkflowCollection(workflow, 'jobs');
  const collectionName = config.getWorkflowCollectionName(workflow, 'jobs');

  db._executeTransaction({
    collections: {
      exclusive: collectionName,
      allowImplicit: false,
    },
    action: function() {
      query`
        FOR job IN ${collection}
          FILTER job.status == ${JobStatus.Submitted}
          || job.status == ${JobStatus.SubmittedPending}
          UPDATE job WITH { status: ${JobStatus.Canceled} } IN ${collection}
      `;
    },
  });
}

/**
 * Get information about the resources required for currently-available jobs.
 * @param {Object} workflow
 * @param {string} schedulerConfigId
 * @return {Object}
 */
function getReadyJobRequirements(workflow, schedulerConfigId) {
  let numCpus = 0;
  let numGpus = 0;
  let numJobs = 0;
  let totalMemory = 0;
  let maxRuntime = 0;
  let maxRuntimeDuration = '';
  let maxNumNodes = 0;

  const collection = config.getWorkflowCollection(workflow, 'jobs');
  for (const job of collection.byExample({status: JobStatus.Ready})) {
    if (
      schedulerConfigId != null &&
        job.internal.scheduler_config_id != '' &&
        job.internal.scheduler_config_id != schedulerConfigId
    ) {
      continue;
    }
    const reqs = getJobResourceRequirements(job, workflow);
    numJobs += 1;
    numCpus += reqs.num_cpus;
    numGpus += reqs.num_gpus;
    const memory = utils.getMemoryInBytes(reqs.memory);
    totalMemory += memory;
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
    max_num_nodes: maxNumNodes,
    max_runtime: maxRuntimeDuration,
  };
}

/**
 * Return all jobs blocking this job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Array}
 */
function getBlockingJobs(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const blockingJobs = [];
  const cursor = query`
    FOR v, e, p
      IN 1
      INBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN p.vertices[1]
  `;
  for (const job of cursor) {
    blockingJobs.push(job);
  }

  return blockingJobs;
}

/**
 * Return files needed by the passed job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {ArangoQueryCursor}
 */
function listFilesNeededByJob(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'needs');
  return query({count: true})`
      FOR v
          IN 1
          OUTBOUND ${job._id}
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          RETURN v
    `;
}

/**
 * Return files needed by the passed job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {ArangoQueryCursor}
 */
function listFilesProducedByJob(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'produces');
  return query({count: true})`
      FOR v
          IN 1
          OUTBOUND ${job._id}
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          RETURN v
    `;
}

/**
 * Return a job specification.
 * @param {Object} job - Instance of schemas.job
 * @param {Object} workflow
 * @return {Object} - Instance of schemas.jobSpecification
 */
function getJobSpecification(job, workflow) {
  const blockingJobs = [];
  const inputFiles = [];
  const outputFiles = [];
  const inputUserData = [];
  const outputUserData = [];

  for (const blockingJob of getBlockingJobs(job, workflow)) {
    blockingJobs.push(blockingJob.name);
  }
  for (const file of listFilesNeededByJob(job, workflow)) {
    inputFiles.push(file.name);
  }
  for (const file of listFilesProducedByJob(job, workflow)) {
    outputFiles.push(file.name);
  }
  for (const data of listUserDataConsumedByJob(job, workflow)) {
    delete(data._id);
    delete(data._key);
    delete(data._rev);
    inputUserData.push(data.name);
  }
  for (const data of listUserDataStoredByJob(job, workflow)) {
    delete(data._id);
    delete(data._key);
    delete(data._rev);
    outputUserData.push(data.name);
  }

  const scheduler = getJobScheduler(job, workflow);
  return {
    name: job.name,
    command: job.command,
    cancel_on_blocking_job_failure: job.cancel_on_blocking_job_failure,
    blocked_by: blockingJobs,
    input_files: inputFiles,
    output_files: outputFiles,
    schedule_compute_nodes: job.schedule_compute_nodes,
    resource_requirements: getJobResourceRequirements(job, workflow).name,
    scheduler: scheduler == null ? '' : scheduler._id,
    input_user_data: inputUserData,
    output_user_data: outputUserData,
  };
}

/**
 * Return the job's resource requirements, using default values if none are assigned.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Object}
 */
function getJobResourceRequirements(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'requires');
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN p.vertices[1]
  `;
  if (cursor.count() == 0) {
    const res = schemas.resourceRequirements.validate({name: 'default'});
    if (res.error !== null) {
      throw new Error('BUG: Failed to create default resourceRequirements');
    }
    return res.value;
  } else if (cursor.count() > 1) {
    throw new Error(
        'BUG: Only one resource requirement can be assigned to a job.',
    );
  }
  return cursor.toArray()[0];
}

/**
 * Set the job's resource requirements, removing any current requires edge.
 * @param {Object} job
 * @param {Object} resourceRequirements
 * @param {Object} workflow
 * @return {Object}
 */
function setOrReplaceJobResourceRequirements(job, resourceRequirements, workflow) {
  const graph = config.getWorkflowGraph(workflow);
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'requires');
  const requiresCollection = config.getWorkflowCollection(workflow, 'requires');
  const cursor = query({count: true})`
    FOR v, e
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN e._id
  `;
  const count = cursor.count();
  if (count == 1) {
    graph[edgeName].remove(cursor.next());
  } else if (count > 1) {
    throw new Error(`Bug: requires edge count for ${job._id} cannot be greater than 1: ${count}`);
  }
  const edge = {_from: job._id, _to: resourceRequirements._id};
  const meta = requiresCollection.save(edge);
  Object.assign(edge, meta);
  return edge;
}

/**
 * Return the job's scheduler, returning null if one isn't defined.
 * @param {Object} job
 * @param {Object} workflow
 * @return {string}
 */
function getJobScheduler(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'scheduled_bys');
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
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
 * @param {Object} file
 * @param {Object} workflow
 * @param {skip} skip
 * @param {number} limit
 * @return {ArangoQueryCursor}
 */
function getJobsThatNeedFile(file, workflow, skip, limit) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'needs');
  return query({count: true})`
      FOR v
          IN 1
          INBOUND ${file._id}
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          LIMIT ${skip}, ${limit}
          RETURN v
    `;
}

/**
 * Return the timestamp of the latest event.
 * @param {string} workflow
 * @return {string}
 */
function getLatestEventTimestamp(workflow) {
  const collection = config.getWorkflowCollection(workflow, 'events');
  const cursor = query`
    FOR event in ${collection}
    COLLECT AGGREGATE max = MAX(event.timestamp)
    RETURN max
  `;
  return cursor.toArray()[0];
}

/**
 * Return all events recorded after the timestamp.
 * @param {string} workflow
 * @param {number} timestamp - ms since epoch in UTC
 * @param {string} category
 * @param {number} limit
 * @return {Array}
 */
function getEventsAfterTimestamp(workflow, timestamp, category, limit) {
  const collection = config.getWorkflowCollection(workflow, 'events');

  if (category == null) {
    return query({count: true})`
      FOR event in ${collection}
        FILTER event.timestamp > ${timestamp}
        LIMIT ${limit}
        RETURN event
    `;
  } else {
    return query({count: true})`
      FOR event in ${collection}
        FILTER event.timestamp > ${timestamp} && event.category == ${category}
        LIMIT ${limit}
        RETURN event
    `;
  }
}

/**
 * Return all result documents connected to the job, sorted by completion time.
 * Return null if the job does not have a result.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Object}
 */
function listJobResults(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'returned');
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN p.vertices[1]
  `;
  const count = cursor.count();
  if (count == 0) {
    return null;
  }

  const results = cursor.toArray();
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
  const t1 = new Date(result1.completion_time).getTime();
  const t2 = new Date(result2.completion_time).getTime();
  return t1 - t2;
}

/**
 * Return the latest job result.
 * Return null if the job does not have a result.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Object}
 */
function getLatestJobResult(job, workflow) {
  const results = listJobResults(job, workflow);
  if (results == null) {
    return results;
  }

  return results.slice(-1)[0];
}

/**
 * Return job result for the given runId.
 * Return null if the job does not have a result for that runId.
 * @param {Object} job
 * @param {Object} workflow
 * @param {number} runId
 * @return {Object}
 */
function getJobResultByRunId(job, workflow, runId) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'returned');
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      FILTER p.vertices[1].run_id == ${runId}
      RETURN p.vertices[1]
  `;
  const count = cursor.count();
  if (count == 0) {
    return null;
  } else if (count > 1) {
    throw new Error(`Bug: cannot have more than one result with a run_id: ${JSON.stringify(job)}`);
  }
  return cursor.next();
}

/**
 * Return the user data consumed by the job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {ArangoQueryCursor}
 */
function listUserDataConsumedByJob(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'consumes');
  return query`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN p.vertices[1]
  `;
}

/**
 * Return the user data that is connected to the job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {ArangoQueryCursor}
 */
function listUserDataStoredByJob(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'stores');
  return query`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN p.vertices[1]
  `;
}

/**
 * Return the user data with content in its data field.
 * @param {Object} workflow
 * @return {ArangoQueryCursor}
 */
function listUserDataWithEphemeralData(workflow) {
  const collection = config.getWorkflowCollection(workflow, 'user_data');
  return query`
    FOR doc in ${collection}
      FILTER doc.is_ephemeral && doc.data != NULL && LENGTH(doc.data) > 0
      RETURN doc
  `;
}

/**
 * Clear all ephemeral user data.
 * @param {Object} workflow
 */
function clearEphemeralUserData(workflow) {
  const collection = config.getWorkflowCollection(workflow, 'user_data');
  // TODO: Clear the data inside the query; it would be faster.
  // But we probably won't ever have many of these.
  const cursor = query`
    FOR doc in ${collection}
      FILTER doc.is_ephemeral && doc.data != NULL && LENGTH(doc.data) > 0
      RETURN doc
  `;
  for (const doc of cursor) {
    const keys = Object.keys(doc.data);
    if (keys.length > 0) {
      for (const key of Object.keys(doc.data)) {
        delete doc.data[key];
      }
      collection.update(doc, doc, {mergeObjects: false});
    }
  }
}

/**
 * Return the workflow config.
 * @param {Object} workflow
 * @return {Object}
*/
function getWorkflowConfig(workflow) {
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${workflow._id}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'has_workflow_config' }
      RETURN p.vertices[1]
  `;
  if (cursor.count() != 1) {
    throw new Error(`workflow ${workflow._id} must only have one config: ${cursor.count()}`);
  }
  return cursor.next();
}

/**
 * Return the workflow status.
 * @param {Object} workflow
 * @return {Object}
*/
function getWorkflowStatus(workflow) {
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${workflow._id}
      GRAPH ${GRAPH_NAME}
      OPTIONS { edgeCollections: 'has_workflow_status' }
      RETURN p.vertices[1]
  `;
  if (cursor.count() != 1) {
    throw new Error(`workflow ${workflow._id} must only have one status: ${cursor.count()}`);
  }
  return cursor.next();
}

/**
 * Initialize job resource requirements.
 * @param {Object} workflow
 */
function initializeJobResourceRequirements(workflow) {
  const resourceRequirements = config.getWorkflowCollection(workflow, 'resource_requirements');
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'requires');
  const jobs = config.getWorkflowCollection(workflow, 'jobs');

  // Temporarily add the computed fields to each document to avoid the function calls in the
  // jobs query below.
  for (const rr of resourceRequirements.all()) {
    rr.runtime_seconds = utils.getTimeDurationInSeconds(rr.runtime);
    rr.memory_bytes = utils.getMemoryInBytes(rr.memory);
    resourceRequirements.update(rr, rr);
  }

  query`
    FOR job in ${jobs}
      FOR v, e, p
          IN 1
          OUTBOUND job._id
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          LET newInternal = MERGE(job.internal, {
              num_cpus: p.vertices[1].num_cpus,
              num_gpus: p.vertices[1].num_gpus,
              num_nodes: p.vertices[1].num_nodes,
              memory_bytes: p.vertices[1].memory_bytes,
              runtime_seconds: p.vertices[1].runtime_seconds,
            }
          )
          UPDATE job WITH { internal: newInternal } IN ${jobs}
    `;
  const rr = schemas.resourceRequirements.validate({name: 'default'}).value;
  rr.runtime_seconds = utils.getTimeDurationInSeconds(rr.runtime);
  rr.memory_bytes = utils.getMemoryInBytes(rr.memory);

  // Cover the jobs that do not have a requires edge.
  query`
    FOR job in ${jobs}
      FILTER job.internal.num_cpus == 0
      LET newInternal = MERGE(job.internal, {
          num_cpus: ${rr.num_cpus},
          num_gpus: ${rr.num_gpus},
          num_nodes: ${rr.num_nodes},
          memory_bytes: ${rr.memory_bytes},
          runtime_seconds: ${rr.runtime_seconds},
        }
      )
      UPDATE job WITH { internal: newInternal } IN ${jobs}
  `;

  for (const rr of resourceRequirements.all()) {
    delete rr.memory_bytes;
    delete rr.runtime_seconds;
    resourceRequirements.update(rr, rr);
  }
}

/**
 * Initialize job scheduler.
 * @param {Object} workflow
 */
function initializeJobScheduler(workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'scheduled_bys');
  const jobs = config.getWorkflowCollection(workflow, 'jobs');

  query`
    FOR job in ${jobs}
      FOR v, e, p
          IN 1
          OUTBOUND job._id
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          LET newInternal = MERGE(job.internal, {
              scheduler_config_id: IS_NULL(p.vertices[1]._id) ? '' : p.vertices[1]._id,
            }
          )
          UPDATE job WITH { internal: newInternal } IN ${jobs}
    `;
}

/** Set initial job statuses to blocked or ready. The default behavior changes all existing
 * statuses except JobStatus.Disabled.
 * @param {Object} workflow
 * @param {Boolean} onlyUninitialized
 */
function initializeJobStatus(workflow, onlyUninitialized) {
  initializeJobResourceRequirements(workflow);
  initializeJobScheduler(workflow);

  const graphName = config.getWorkflowGraphName(workflow);
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');

  // This is not strictly necessary but is a good safety net against bugs elsewhere.
  uninitializeBlockedJobs(workflow);

  query`
    FOR job in ${jobs}
      FILTER job.status != ${JobStatus.Disabled}
      FOR v
          IN 1
          INBOUND job._id
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          FILTER v.status != ${JobStatus.Done}
            && (!${onlyUninitialized} || job.status == ${JobStatus.Uninitialized})
          UPDATE job WITH { status: ${JobStatus.Blocked} } IN ${jobs}
  `;
  // Initialize all unblocked jobs.
  query`
    FOR job in ${jobs}
        FILTER job.status != ${JobStatus.Disabled}
          && job.status != ${JobStatus.Blocked}
          && job.status != ${JobStatus.Done}
          && job.status != ${JobStatus.Canceled}
        UPDATE job WITH { status: ${JobStatus.Ready} } IN ${jobs}
  `;
  console.debug(
      `Initialized all incomplete job status to ${JobStatus.Ready} or ${JobStatus.Blocked}`,
  );
}

/**
 * Return an iterator over all documents of the given type connected to the workflow.
 * @param {Object} workflow
 * @param {string} collectionName
 * @return {Object}
 */
function iterWorkflowDocuments(workflow, collectionName) {
  const collection = config.getWorkflowCollection(workflow, collectionName);
  return collection.all();
}

/**
 * Return true if the job is blocked by another job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {bool}
 *
 **/
function isJobBlocked(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const cursor = query`
    FOR v
        IN 1
        INBOUND ${job._id}
        GRAPH ${graphName}
        OPTIONS { edgeCollections: ${edgeName} }
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
 * @param {Object} job
 * @param {Object} workflow
 * @return {bool}
 *
 **/
function isJobInitiallyBlocked(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const cursor = query({count: true})`
    FOR v
        IN 1
        INBOUND ${job._id}
        GRAPH ${graphName}
        OPTIONS { edgeCollections: ${edgeName} }
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
  return status == JobStatus.Done || status == JobStatus.Canceled ||
    status == JobStatus.Terminated;
}

/**
 * Return true if the workflow is complete.
 * @param {Object} workflow
 * @return {bool}
 */
function isWorkflowComplete(workflow) {
  // TODO: This function will be called a lot - by every compute node on some interval.
  // Track how much time is spent here.
  const collection = config.getWorkflowCollection(workflow, 'jobs');
  const cursor = query({count: true})`
    FOR job in ${collection}
      FILTER !(
        job.status == ${JobStatus.Done}
        OR job.status == ${JobStatus.Canceled}
        OR job.status == ${JobStatus.Terminated}
        OR job.status == ${JobStatus.Disabled}
      )
      LIMIT 1
      RETURN job._key
  `;
  return cursor.count() == 0;
}

/**
* Return true if this is the first time that workflow completion has been detected
* and a completion script is defined.
* It is assumed that the caller has already checked that the workflow is complete.
* @param {Object} workflow
* @return {bool}
*/
function needsToRunCompletionScript(workflow) {
  const config = getWorkflowConfig(workflow);
  if (config.workflow_completion_script == null) {
    return false;
  }
  const collection = db._collection('workflow_statuses');
  const status = getWorkflowStatus(workflow);
  const needsRun = !status.has_detected_need_to_run_completion_script;
  if (needsRun) {
    status.has_detected_need_to_run_completion_script = true;
    try {
      collection.update(status, status, {mergeObjects: false});
      console.debug(`Workflow ${workflow._key} has been detected as complete.`);
    } catch (err) {
      if (e.errorNum === CONFLICTING_REV) {
        return false; // Another process has already set this.
      }
      throw err;
    }
  }
  return needsRun;
}

/**
 * Return the job's process stats.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Array} Array of jobProcessStats
 */
function listJobProcessStats(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'process_used');
  const cursor = query({count: true})`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName} }
      RETURN p.vertices[1]
  `;
  const results = cursor.toArray();
  if (results.length > 1) {
    results.sort((x, y) => x.run_id - y.run_id);
  }
  return results;
}

/**
 * Join two collections by an inbound edge.
 * @param {Object} workflow
 * @param {string} fromCollectionBase
 * @param {string} edgeBase
 * @param {Object} filters
 * @param {number} skip
 * @param {number} limit
 * @return {Object}
 */
function joinCollectionsByInboundEdge(
    workflow,
    fromCollectionBase,
    edgeBase,
    filters,
    skip,
    limit,
) {
  const graphName = config.getWorkflowGraphName(workflow);
  let fromCollection = config.getWorkflowCollection(workflow, fromCollectionBase);
  if (filters != null && Object.keys(filters).length > 0) {
    fromCollection = fromCollection.byExample(filters);
  } else {
    fromCollection = fromCollection.all();
  }
  fromCollection = fromCollection.skip(skip)
      .limit(limit)
      .toArray();
  const edgeName = config.getWorkflowCollectionName(workflow, edgeBase);
  // TODO: It would be better to allow dynamic filtering of fields on either
  // side of the edge in this query.
  // Note that there can be multiple edges between two vertexes because the same
  // compute node can run the same job multiple times on workflow restarts.
  const cursor = query({count: true})`
    FOR x in ${fromCollection}
      FOR v, e, p
          IN 1
          INBOUND x._id
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          RETURN {from: p.vertices[1], to: x, edge: e}
  `;
  return cursor;
}

/**
 * Join two collections by an outbound edge.
 * @param {Object} workflow
 * @param {string} fromCollectionBase
 * @param {string} edgeBase
 * @param {Object} filters
 * @param {number} skip
 * @param {number} limit
 * @return {Object}
 */
function joinCollectionsByOutboundEdge(
    workflow,
    fromCollectionBase,
    edgeBase,
    filters,
    skip,
    limit,
) {
  const graphName = config.getWorkflowGraphName(workflow);
  let fromCollection = config.getWorkflowCollection(workflow, fromCollectionBase);
  if (filters != null && Object.keys(filters).length > 0) {
    fromCollection = fromCollection.byExample(filters);
  } else {
    fromCollection = fromCollection.all();
  }
  fromCollection = fromCollection.skip(skip)
      .limit(limit)
      .toArray();
  const edgeName = config.getWorkflowCollectionName(workflow, edgeBase);

  // Note that there can be multiple edges between two vertexes because the same
  // compute node can run the same job multiple times on workflow restarts.
  const cursor = query({count: true})`
    FOR x in ${fromCollection}
      FOR v, e, p
          IN 1
          OUTBOUND x._id
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName} }
          RETURN {from: x, to: p.vertices[1], edge: e}
  `;
  return cursor;
}

/**
 * Return an array of file keys and revisions needed by the job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Array}
 */
function listNeedsFileRevisions(job, workflow) {
  const items = [];
  for (const item of listFilesNeededByJob(job, workflow)) {
    items.push({key: item._key, rev: item._rev});
  }
  items.sort((x, y) => x.key - y.key);
  return items;
}

/**
 * Return an array of user data keys and revisions consumed by the job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Array}
 */
function listConsumesUserDataRevisions(job, workflow) {
  const items = [];
  for (const item of listUserDataConsumedByJob(job, workflow)) {
    items.push({key: item._key, rev: item._rev});
  }
  items.sort((x, y) => x.key - y.key);
  return items;
}

/**
 * Return an array of user data keys and revisions stored by the job.
 * @param {Object} job
 * @param {Object} workflow
 * @return {Array}
 */
function listStoresUserDataRevisions(job, workflow) {
  const items = [];
  for (const item of listUserDataStoredByJob(job, workflow)) {
    items.push({key: item._key, rev: item._rev});
  }
  items.sort((x, y) => x.key - y.key);
  return items;
}

/**
 * Return an array of user_data keys whose data should exist but doesn't.
 * @param {Object} workflow
 * @return {Array}
 */
function listMissingUserData(workflow) {
  const expectedUserData = [];
  const missingUserData = [];
  const consumesCollection = config.getWorkflowCollection(workflow, 'consumes');
  const jobsCollection = config.getWorkflowCollection(workflow, 'jobs');
  const storesCollection = config.getWorkflowCollection(workflow, 'stores');
  const userDataCollection = config.getWorkflowCollection(workflow, 'user_data');

  for (const edge of consumesCollection.all()) {
    const udId = edge._to;
    const storesEdge = storesCollection.byExample({_to: udId}).toArray();
    if (storesEdge.length == 0) {
      // This user data should have been added by the user.
      expectedUserData.push(udId);
    } else if (storesEdge.length == 1) {
      const jobId = storesEdge[0]._from;
      const job = jobsCollection.document(jobId);
      if (job.status == JobStatus.Done) {
        // This user data should have been added by the job.
        expectedUserData.push(udId);
      }
    } else {
      throw new Error(`A user_data document can never have more than 1 stores edge: ` +
        `${JSON.stringify(storesEdge)}`);
    }
  }

  for (const udId of expectedUserData) {
    const ud = userDataCollection.document(udId);
    if (ud.data != null && Object.keys(ud.data).length == 0) {
      missingUserData.push(ud._key);
    }
  }
  return missingUserData;
}

/**
 * Return an array of file keys whose path must exist.
 * @param {Object} workflow
 * @return {Array}
 */
function listRequiredExistingFiles(workflow) {
  const requiredFiles = [];
  const needsCollection = config.getWorkflowCollection(workflow, 'needs');
  const jobsCollection = config.getWorkflowCollection(workflow, 'jobs');
  const producesCollection = config.getWorkflowCollection(workflow, 'produces');
  const workflowStatus = getWorkflowStatus(workflow);

  // TODO: use chunked return

  for (const edge of needsCollection.all()) {
    const fileId = edge._to;
    const producesEdge = producesCollection.byExample({_to: fileId}).toArray();
    if (producesEdge.length == 0) {
      // This file should have been created by the user.
      requiredFiles.push(fileId);
    } else if (producesEdge.length == 1) {
      const jobId = producesEdge[0]._from;
      const job = jobsCollection.document(jobId);
      if (job.status == JobStatus.Done &&
        getJobResultByRunId(job, workflow, workflowStatus.run_id) == 0) {
        // This user data should have been added by the job.
        requiredFiles.push(fileId);
      }
    } else {
      throw new Error(`A file document can never have more than 1 produces edge: ` +
        `${JSON.stringify(producesEdge)}`);
    }
  }

  return requiredFiles;
}

/**
 * Update a job status and manage all downstream consequences.
 * @param {Object} job
 * @param {Object} workflow
 * @param {number} runId
 * @return {Object}
 */
function manageJobStatusChange(job, workflow, runId) {
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const oldStatus = jobs.document(job._key).status;
  if (job.status == oldStatus) {
    return job;
  }
  const meta = jobs.update(job, job, {mergeObjects: false});
  Object.assign(job, meta);

  const workflowStatus = getWorkflowStatus(workflow);
  const workflowRunId = workflowStatus.run_id;

  if (runId != workflowRunId) {
    throw new Error(
        `Invalid job status change request. run_id=${runId}. Workflow run_id=${workflowRunId}`,
    );
  }
  if (!isJobStatusComplete(oldStatus) && isJobStatusComplete(job.status)) {
    const result = getJobResultByRunId(job, workflow, workflowStatus.run_id);
    if (result == null) {
      throw new Error(`Job ${job._key} does not have a result for run_id=${workflowRunId}.`);
    }
    updateBlockedJobsFromCompletion(job, workflow);
  } else if (isJobStatusComplete(oldStatus) && job.status == JobStatus.Uninitialized) {
    updateJobsFromCompletionReversal(job, workflow);
  }

  return job;
}

/**
 * Prepare a list of jobs for submission that meet the worker resource availability.
 * @param {Object} workflow
 * @param {Object} workerResources
 * @param {string} sortMethod
 * @param {Number} limit
 * @param {Object} reason
 * @return {Array}
 */
function prepareJobsForSubmission(workflow, workerResources, sortMethod, limit, reason) {
  const jobs = [];
  const collection = config.getWorkflowCollection(workflow, 'jobs');
  const collectionName = config.getWorkflowCollectionName(workflow, 'jobs');
  let availableCpus = workerResources.num_cpus;
  let availableGpus = workerResources.num_gpus;
  let availableMemory = workerResources.memory_gb * GiB;
  const queryLimit = limit == null ? availableCpus : limit;
  const workerTimeLimit =
    workerResources.time_limit == null ?
      Number.MAX_SAFE_INTEGER : utils.getTimeDurationInSeconds(workerResources.time_limit);
  const schedulerConfigId = workerResources.scheduler_config_id == null ? '' :
    workerResources.scheduler_config_id;
  const sortCommand = makeSortCommand(sortMethod);

  db._executeTransaction({
    collections: {
      exclusive: collectionName,
      allowImplicit: false,
    },
    action: function() {
      const cursor = query`
        FOR job IN ${collection}
          FILTER (job.status == ${JobStatus.Ready} || job.status == ${JobStatus.Scheduled})
            && job.internal.memory_bytes <= ${availableMemory}
            && job.internal.num_cpus <= ${availableCpus}
            && job.internal.num_gpus <= ${availableGpus}
            && job.internal.runtime_seconds <= ${workerTimeLimit}
            && job.internal.num_nodes <= ${workerResources.num_nodes}
            && (job.internal.scheduler_config_id == ''
                || job.internal.scheduler_config_id == ${schedulerConfigId})
          ${sortCommand}
          LIMIT ${queryLimit}
          RETURN job
      `;

      // This implementation stores the job resource information in the internal object
      // so that it doesn't have to run a graph query while holding an exclusive lock.
      for (const job of cursor) {
        if (
          job.internal.num_cpus <= availableCpus &&
          job.internal.num_gpus <= availableGpus &&
          job.internal.memory_bytes <= availableMemory
        ) {
          job.status = JobStatus.SubmittedPending;
          const meta = collection.update(job, job, {mergeObjects: false});
          Object.assign(job, meta);
          jobs.push(job);
          availableCpus -= job.internal.num_cpus;
          availableGpus -= job.internal.num_gpus;
          availableMemory -= job.internal.memory_bytes;
          if (availableCpus == 0 || availableMemory == 0) {
            break;
          }
        }
      }
    },
  });

  if (jobs.length == 0) {
    reason.message = `No jobs matched status='ready', memory_bytes <= ${availableMemory}, ` +
      `num_cpus <= ${availableCpus}, num_gpus <= ${availableGpus}, ` +
      `runtime_seconds <= ${workerTimeLimit}, ` +
      `num_nodes == ${workerResources.num_nodes}, scheduler_config_id == ${schedulerConfigId}`;
  }
  console.debug(`Prepared ${jobs.length} jobs for submission.`);
  return jobs;
}

/**
 * Return an aql.literal string for a sort command.
 * @param {string} sortMethod
 * @return {Object}
 */
function makeSortCommand(sortMethod) {
  let sortStr = null;
  const memStr = 'job.internal.memory_bytes DESC';
  const gpuStr = 'SORT job.internal.num_gpus DESC';
  const runtimeStr = 'job.internal.runtime_seconds DESC';
  if (sortMethod == 'gpus_runtime_memory') {
    sortStr = `${gpuStr}, ${runtimeStr}, ${memStr}`;
  } else if (sortMethod == 'gpus_memory_runtime') {
    sortStr = `${gpuStr}, ${memStr}, ${runtimeStr}`;
  } else if (sortMethod == 'none') {
    sortStr = '';
  } else {
    throw new Error(`Unsupported sort_method=${sortMethod}`);
  }
  return aql.literal(sortStr);
}

/**
 * Prepare a list of jobs for submission with no resource requirement considerations.
 * @param {Object} workflow
 * @param {Number} limit
 * @return {Array}
 */
function prepareJobsForSubmissionNoResourceChecks(workflow, limit) {
  const jobs = [];
  const collection = config.getWorkflowCollection(workflow, 'jobs');
  const collectionName = config.getWorkflowCollectionName(workflow, 'jobs');

  db._executeTransaction({
    collections: {
      exclusive: collectionName,
      allowImplicit: false,
    },
    action: function() {
      const cursor = query({count: true})`
        FOR job IN ${collection}
          FILTER job.status == ${JobStatus.Ready} || job.status == ${JobStatus.Scheduled}
          LIMIT ${limit}
          RETURN job
      `;

      // This implementation stores the job resource information in the internal object
      // so that it doesn't have to run a graph query while holding an exclusive lock.
      for (const job of cursor) {
        job.status = JobStatus.SubmittedPending;
        const meta = collection.update(job, job, {mergeObjects: false});
        Object.assign(job, meta);
        jobs.push(job);
      }
    },
  });

  return jobs;
}

/**
 * Return an array of schedulers that need to be scheduled. Changes job status to scheduled.
 * @param {Object} workflow
 * @return {Array}
 */
function prepareJobsForScheduling(workflow) {
  const schedulers = [];
  const collection = config.getWorkflowCollection(workflow, 'jobs');
  const collectionName = config.getWorkflowCollectionName(workflow, 'jobs');

  db._executeTransaction({
    collections: {
      exclusive: collectionName,
      allowImplicit: false,
    },
    action: function() {
      const cursor = query({count: true})`
        FOR job IN ${collection}
          FILTER job.status == ${JobStatus.Ready} && NOT_NULL(job.schedule_compute_nodes)
          UPDATE job WITH { status: ${JobStatus.Scheduled} } IN ${collection}
          RETURN job.schedule_compute_nodes
      `;

      for (const params of cursor) {
        schedulers.push(params);
      }
    },
  });

  return schedulers;
}

/**
 * Process user data that was consumed by jobs and later changed, and reinitialize job status.
 * There is no protection for concurrent requests.
 * @param {Object} workflow
 * @return {Array}
 */
function processConsumedUserData(workflow) {
  const consumesCollection = config.getWorkflowCollection(workflow, 'consumes');
  const jobsCollection = config.getWorkflowCollection(workflow, 'jobs');
  const userDataCollection = config.getWorkflowCollection(workflow, 'user_data');
  const reinitializedJobs = [];

  for (const edge of consumesCollection.all()) {
    const ud = userDataCollection.document(edge._to);
    if (ud._rev != edge.consumed_revision) {
      const job = jobsCollection.document(edge._from);
      if (job.status == JobStatus.Done) {
        job.status = JobStatus.Uninitialized;
        jobsCollection.update(job, job, {mergeObjects: false});
        reinitializedJobs.push(job._key);
      }
    }
  }
  return reinitializedJobs;
}

/** Reset failed job status to uninitialized.
 * @param {Object} workflow
 */
function resetFailedJobStatus(workflow) {
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'returned');
  const runId = getWorkflowStatus(workflow).run_id;

  const cursor = query`
    FOR job in ${jobs}
      FOR v, e, p
        IN 1
        OUTBOUND job._id
        GRAPH ${graphName}
        OPTIONS { edgeCollections: ${edgeName} }
        FILTER p.vertices[1].run_id == ${runId} && p.vertices[1].return_code != 0
        UPDATE job WITH { status: ${JobStatus.Uninitialized} } IN ${jobs}
        RETURN job
  `;
  console.debug(`Reset failed job status to ${JobStatus.Uninitialized}`);

  // Would it be faster to call uninitializeBlockedJobs?
  for (const job of cursor) {
    updateJobsFromCompletionReversal(job, workflow);
  }
}

/** Reset all job status to uninitialized.
 * @param {Object} workflow
 */
function resetJobStatus(workflow) {
  const jobs = config.getWorkflowCollection(workflow, 'jobs');

  query`
    FOR job in ${jobs}
      FILTER job.status != ${JobStatus.Uninitialized}
      UPDATE job WITH ({ status: ${JobStatus.Uninitialized} }) in ${jobs}
  `;
  console.debug(`Reset job status to ${JobStatus.Uninitialized}`);
}

/** Reset workflow config.
 * @param {Object} workflow
 */
function resetWorkflowConfig(workflow) {
  const config = {
    compute_node_resource_stats: schemas.computeNodeResourceStatConfig.validate({}).value,
  };

  const doc = getWorkflowConfig(workflow);
  if (doc == null) {
    db.workflow_config.save(config);
  } else {
    Object.assign(doc, config);
    db.workflow_config.update(doc, doc, {mergeObjects: false});
  }
}

/** Reset workflow status.
 * @param {Object} workflow
 */
function resetWorkflowStatus(workflow) {
  const status = {
    is_canceled: false,
    scheduled_compute_node_ids: [],
    auto_tune_status: schemas.autoTuneStatus.validate({}).value,
    has_detected_need_to_run_completion_script: false,
  };
  const doc = getWorkflowStatus(workflow);
  Object.assign(doc, status);
  db.workflow_statuses.update(doc, doc, {mergeObjects: false});
  console.debug(`Reset workflow status`);
}

/**
 * Setup the jobs to auto-tune resource requirements.
 * Enable one job from each resource requirement group and disable the rest.
 * @param {Object} workflow
 */
function setupAutoTuneResourceRequirements(workflow) {
  const groups = new Set();
  const status = getWorkflowStatus(workflow);
  status.auto_tune_status.enabled = true;

  const workflowConfig = getWorkflowConfig(workflow);
  if (!workflowConfig.compute_node_resource_stats.process) {
    throw new Error('The auto-tune feature requires collection of job process stats.');
  }

  // PERF: make one query
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  for (const job of jobs.all()) {
    if (job.status == JobStatus.Blocked) {
      continue;
    }
    const rr = getJobResourceRequirements(job, workflow);
    if (groups.has(rr.name)) {
      if (job.status == JobStatus.Disabled) {
        // TODO: should we track these instead?
        res.throw(400, `Job ${job._key} is already disabled`);
      }
      // This isn't atomic, but the user shouldn't call this in parallel.
      // Let Arango fail the operation if they do that.
      job.status = JobStatus.Disabled;
      jobs.update(job, job, {mergeObjects: false});
    } else {
      status.auto_tune_status.job_keys.push(job._key);
      groups.add(rr.name);
    }
  }
  db.workflow_statuses.update(status, status, {mergeObjects: false});
}

/**
 * Process the results of setupAutoTuneResourceRequirements.
 * 1. Update the resource requirements groups based on the utilization stats from
 * the selected jobs that ran.
 * 2. Update all non-auto-tune job status from disabled to uninitialized.
 * @param {Object} workflow
 */
function processAutoTuneResourceRequirementsResults(workflow) {
  const workflowStatus = getWorkflowStatus(workflow);
  workflowStatus.auto_tune_status.disabled = true;
  const groupsUpdated = new Set();
  const autoTuneJobs = new Set();
  const jobs = config.getWorkflowCollection(workflow, 'jobs');

  // PERF: This will be slow with huge numbers of jobs.
  // FUTURE: consider whether all changes can be made atomically.
  for (const key of workflowStatus.auto_tune_status.job_keys) {
    const job = jobs.document(key);
    const jobStats = listJobProcessStats(job, workflow);
    if (jobStats.length == 0) {
      throw new Error(`job ${job._key} does not have any process stats`);
    }
    const stats = jobStats.slice(-1)[0];
    const maxMemoryGb = Math.ceil(stats.max_rss / GiB);
    const maxMemory = `${maxMemoryGb}g`;
    const maxCpusUsed = stats.max_cpu_percent == 0 ? 1 : Math.ceil(stats.max_cpu_percent / 100);
    const rr = getJobResourceRequirements(job, workflow);
    const result = getJobResultByRunId(job, workflow, workflowStatus.run_id);
    if (result == null) {
      throw new Error(`No job result for ${job._key} - ${job.status}. Cannot complete auto-tune.`);
    }
    const oldRr = JSON.parse(JSON.stringify(rr));
    rr.num_cpus = maxCpusUsed;
    rr.memory = maxMemory;
    const minutes = Math.ceil(result.exec_time_minutes);
    rr.runtime = `P0DT0H${minutes}M`;
    if (groupsUpdated.has(rr.name)) {
      throw new Error(`resource requirements ${rr.name} was already updated`);
    }
    groupsUpdated.add(rr.name);
    const rrCollection = config.getWorkflowCollection(workflow, 'resource_requirements');
    rrCollection.update(rr, rr, {mergeObjects: false});
    const event = {
      timestamp: Date.now(),
      category: 'resource_requirements',
      type: 'update',
      name: rr.name,
      old: oldRr,
      new: rr,
      message: `Updated resource requirements for name = ${rr.name}`,
    };
    const eventsCollection = config.getWorkflowCollection(workflow, 'events');
    eventsCollection.save(event);
    autoTuneJobs.add(job._key);
  }

  const jobsCollection = config.getWorkflowCollection(workflow, 'jobs');
  for (const job of jobsCollection.all()) {
    if (!autoTuneJobs.has(job._key)) {
      if (job.status != JobStatus.Disabled) {
        throw new Error(`Expected status disabled instead of ${job.status} for job ${job._key}`);
      }
      job.status = JobStatus.Uninitialized;
      jobsCollection.update(job, job, {mergeObjects: false});
    }
  }
  db.workflow_statuses.update(workflowStatus, workflowStatus, {mergeObjects: false});
}

/**
 * Update blocked jobs after a job completion.
 * @param {Object} job
 * @param {Object} workflow
 */
function updateBlockedJobsFromCompletion(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const cursor = query`
    FOR v, e, p
      IN 1
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName}, uniqueVertices: 'global', order: 'bfs' }
      FILTER v.status == ${JobStatus.Blocked}
      RETURN p.vertices[1]
  `;
  const workflowStatus = getWorkflowStatus(workflow);
  const result = getJobResultByRunId(job, workflow, workflowStatus.run_id);
  // TODO: should other queries use bfs?
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const canceledJobs = [];
  for (const blockedJob of cursor) {
    if (result.return_code != 0 && blockedJob.cancel_on_blocking_job_failure) {
      blockedJob.status = JobStatus.Canceled;
      // Need to cancel all other jobs that also block this job.
      // They might not have started yet and it would be pointless to run them.
      canceledJobs.push(blockedJob._id);
    } else if (!isJobBlocked(blockedJob, workflow)) {
      blockedJob.status = JobStatus.Ready;
    }
    if (job.status != JobStatus.Blocked) {
      jobs.update(blockedJob, blockedJob, {mergeObjects: false});
    }
  }
  if (canceledJobs.length > 0) {
    for (const jobId of canceledJobs) {
      // TODO: consider canceling running jobs.
      query`
        FOR v, e, p
          IN 1
          INBOUND ${jobId}
          GRAPH ${graphName}
          OPTIONS { edgeCollections: ${edgeName}, uniqueVertices: 'global', order: 'bfs' }
          FILTER v.status == ${JobStatus.Ready}
          UPDATE v WITH { status: ${JobStatus.Canceled} } IN ${jobs}
          RETURN p.vertices[1]
      `;
    }
  }
}

/**
 * Update jobs after a job completion reversal.
 * @param {Object} job
 * @param {Object} workflow
 */
function updateJobsFromCompletionReversal(job, workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const numJobs = jobs.count();
  query`
    FOR v, e, p
      IN 1..${numJobs}
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName}, uniqueVertices: 'global', order: 'bfs' }
      FILTER v.status != ${JobStatus.Uninitialized}
      UPDATE v WITH { status: ${JobStatus.Uninitialized} } IN ${jobs}
    `;
}

/**
 * Ensure that all jobs downstream of an uninitialized job are also uninitialized.
 * @param {Object} workflow
 */
function uninitializeBlockedJobs(workflow) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const numJobs = jobs.count();
  query`
    FOR job in ${jobs}
      FILTER job.status == ${JobStatus.Uninitialized}
      FOR v, e, p
        IN 1..${numJobs}
        OUTBOUND job._id
        GRAPH ${graphName}
        OPTIONS { edgeCollections: ${edgeName}, uniqueVertices: 'global', order: 'bfs' }
        FILTER v.status != ${JobStatus.Uninitialized}
        UPDATE v WITH { status: ${JobStatus.Uninitialized} } IN ${jobs}
  `;
}

/**
 * Return a cursor of of jobs downstream from this job.
 * @param {Object} job
 * @param {Object} workflow
 * @param {skip} skip
 * @param {number} limit
 * @return {ArangoQueryCursor}
 */
function listDownstreamJobs(job, workflow, skip, limit) {
  const graphName = config.getWorkflowGraphName(workflow);
  const edgeName = config.getWorkflowCollectionName(workflow, 'blocks');
  const jobs = config.getWorkflowCollection(workflow, 'jobs');
  const numJobs = jobs.count();
  return query({count: true})`
    FOR v, e, p
      IN 1..${numJobs}
      OUTBOUND ${job._id}
      GRAPH ${graphName}
      OPTIONS { edgeCollections: ${edgeName}, uniqueVertices: 'global', order: 'bfs' }
      LIMIT ${skip}, ${limit}
      RETURN p.vertices[1]
  `;
}

/**
 * Update workflow config.
 * @param {Object} workflow
 * @param {Object} config
 * @return {Object}
 **/
function updateWorkflowConfig(workflow, config) {
  const doc = getWorkflowConfig(workflow);
  Object.assign(doc, config);
  Object.assign(doc.compute_node_resource_stats, config.compute_node_resource_stats);
  const meta = db.workflow_configs.update(doc, doc, {mergeObjects: false});
  Object.assign(doc, meta);
  return doc;
}

module.exports = {
  addBlocksEdgesFromFiles,
  addBlocksEdgesFromUserData,
  cancelWorkflowJobs,
  getBlockingJobs,
  getJobResourceRequirements,
  getJobResultByRunId,
  getJobScheduler,
  getJobsThatNeedFile,
  getLatestJobResult,
  getReadyJobRequirements,
  getWorkflowConfig,
  getWorkflowStatus,
  getJobSpecification,
  getLatestEventTimestamp,
  getEventsAfterTimestamp,
  initializeJobStatus,
  isJobBlocked,
  isJobInitiallyBlocked,
  isJobStatusComplete,
  isWorkflowComplete,
  needsToRunCompletionScript,
  iterWorkflowDocuments,
  joinCollectionsByInboundEdge,
  joinCollectionsByOutboundEdge,
  listConsumesUserDataRevisions,
  listDownstreamJobs,
  listFilesNeededByJob,
  listFilesProducedByJob,
  listJobProcessStats,
  listJobResults,
  listMissingUserData,
  listNeedsFileRevisions,
  listRequiredExistingFiles,
  listStoresUserDataRevisions,
  listUserDataConsumedByJob,
  listUserDataStoredByJob,
  listUserDataWithEphemeralData,
  clearEphemeralUserData,
  manageJobStatusChange,
  prepareJobsForSubmission,
  prepareJobsForSubmissionNoResourceChecks,
  prepareJobsForScheduling,
  processAutoTuneResourceRequirementsResults,
  processConsumedUserData,
  resetFailedJobStatus,
  resetJobStatus,
  resetWorkflowConfig,
  resetWorkflowStatus,
  setOrReplaceJobResourceRequirements,
  setupAutoTuneResourceRequirements,
  updateBlockedJobsFromCompletion,
  updateJobsFromCompletionReversal,
  updateWorkflowConfig,
};
