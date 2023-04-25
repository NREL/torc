'use strict';
const GRAPH_NAME = 'workflow_graph';
const KiB = 1024;
const MiB = KiB * KiB;
const GiB = MiB * KiB;
const TiB = GiB * KiB;
const MAX_TRANSFER_RECORDS = 1000;

const JobStatus = {
  // Initial state. Not yet known if it is blocked or ready.
  Uninitialized: 'uninitialized',
  // The job cannot start because of dependencies.
  Blocked: 'blocked',
  // A blocking job failed and so the job never ran.
  Canceled: 'canceled',
  // Compute node timeout occurred and the job was notified to checkpoint and shut down.
  Terminated: 'terminated',
  // The job finished. It may or may not have completed successfully.
  Done: 'done',
  // The job can be submitted.
  Ready: 'ready',
  // The job is running on a compute node.
  Submitted: 'submitted',
  // The job was given to a compute node but is not yet running.
  SubmittedPending: 'submitted_pending',
  // The job cannot be run.
  Disabled: 'disabled',
};

module.exports = {
  GRAPH_NAME,
  MAX_TRANSFER_RECORDS,
  KiB,
  MiB,
  GiB,
  TiB,
  JobStatus,
};
