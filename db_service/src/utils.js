'use strict';
const parse = require('tinyduration').parse;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const CONFLICTING_REV = errors.ERROR_ARANGO_CONFLICT.code;
const {KiB, MiB, GiB, TiB, MAX_TRANSFER_RECORDS} = require('./defs');
const product = (...a) => a.reduce((a, b) => a.flatMap((d) => b.map((e) => [d, e].flat())));


/**
 * Return the size in bytes of the memory expressed as a string.
 * @param {string} memoryString - Memory size such as '30g', '30 G', '3000M'
 * @return {integer}
 */
function getMemoryInBytes(memoryString) {
  let result = memoryString.match(/^\s*([0-9]+)\s*$/);
  if (result != null) {
    return parseInt(result[1]);
  }

  result = memoryString.match(/([0-9]+)\s*([kmgtKMGT])/);
  if (result == null) {
    throw new Error(`${memoryString} is an invalid memory value`);
  }
  let size = parseInt(result[1]);
  const units = result[2].toLowerCase();
  if (units == 'k') {
    size *= KiB;
  } else if (units == 'm') {
    size *= MiB;
  } else if (units == 'g') {
    size *= GiB;
  } else if (units == 't') {
    size *= TiB;
  } else {
    throw new Error(`${units} is an invalid memory unit`);
  }

  return size;
}

/**
 * Return the duration in seconds.
 * @param {string} duration - Duration in ISO-8601 format
 * @return {number} - Duration in seconds
 */
function getTimeDurationInSeconds(duration) {
  const obj = parse(duration);
  if (obj.years != undefined || obj.months != undefined) {
    throw new Error('duration=${duration} contains inexact time periods');
  }

  let durationSeconds = 0;
  if (obj.days != undefined) {
    durationSeconds += obj.days * 24 * 60 * 60;
  }
  if (obj.hours != undefined) {
    durationSeconds += obj.hours * 60 * 60;
  }
  if (obj.minutes != undefined) {
    durationSeconds += obj.minutes * 60;
  }
  if (obj.seconds != undefined) {
    durationSeconds += obj.seconds;
  }

  return durationSeconds;
}

/**
 * Return the walltime in seconds.
 * @param {string} duration - Duration in HH:MM:SS or variants
 * @return {number} - Duration in seconds
 */
function getWalltimeInSeconds(duration) {
  // From Slurm docs:
  // Acceptable time formats include "minutes", "minutes:seconds", "hours:minutes:seconds",
  // "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds".

  // hours:minutes:seconds
  let result = duration.match(/^([0-9]+):([0-9]+):([0-9]+)$/);
  if (result != null) {
    return result[1] * 3600 + result[2] * 60 + result[3];
  }
  // days-hours:minutes:seconds
  result = duration.match(/^([0-9]+)-([0-9]+):([0-9]+):([0-9]+)$/);
  if (result != null) {
    return result[1] * 3600 * 24 + result[2] * 3600 + result[3] * 60 + result[4];
  }
  // days-hours:minutes
  result = duration.match(/^([0-9]+)-([0-9]+):([0-9]+)$/);
  if (result != null) {
    return result[1] * 3600 * 24 + result[2] * 3600 + result[3] * 60;
  }
  // minutes
  result = duration.match(/^([0-9]+)$/);
  if (result != null) {
    return result[1] * 60;
  }
  // minutes:seconds
  result = duration.match(/^([0-9]+):([0-9]+)$/);
  if (result != null) {
    return result[1] * 60 + result[2];
  }
  // days-hours
  result = duration.match(/^([0-9]+)-([0-9]+)$/);
  if (result != null) {
    return result[1] * 3600 * 24 + result[2] * 3600;
  }

  throw new Error(`Walltime format ${duration} is not supported`);
}

/**
 * Return the number of records to send.
 * @param {string} limit
 * @return {number}
 */
function getItemsLimit(limit) {
  return limit <= MAX_TRANSFER_RECORDS ? limit : MAX_TRANSFER_RECORDS;
}

/**
 * Return the number of records to send.
 * @param {Object} items
 * @param {number} skip
 * @param {number} limit
 * @param {number} totalCount
 * @return {Object}
 */
function makeCursorResult(items, skip, limit, totalCount) {
  return {
    items: items,
    skip: skip,
    limit: limit,
    max_limit: MAX_TRANSFER_RECORDS,
    count: items.length,
    total_count: totalCount,
    has_more: skip >= items.length || limit >= items.length ? false :
      skip + items.length < totalCount,
  };
}

/**
 * Make a cursor result by iterating over an ArangoQueryCursor. This is very inefficient
 * if it is called multiple times for multiple batches. Should only be used when there
 * isn't a way of using skip and limit in the Arango query.
 * @param {ArangoQueryCursor} cursor
 * @param {number} skip
 * @param {number} limit
 * @param {function} func
 * @return {Array}
 */
function makeCursorResultFromIteration(cursor, skip, limit, func) {
  const items = [];
  let i = 0;
  for (let item of cursor) {
    if (i > skip) {
      i++;
      continue;
    }
    if (func != null) {
      item = func(item);
    }
    items.push(item);
    if (items.length == limit) {
      break;
    }
  }
  return makeCursorResult(items, skip, limit, cursor.count());
}

/**
 * Convert the job for delivery to an API client.
 * @param {Object} job
 * @return {Object}
 */
function convertJobForApi(job) {
  delete job.internal;
  return job;
}

/**
 * Return Arango error messages in http responses.
 * @param {Object} e
 * @param {Object} res
 * @param {string} tag
 */
function handleArangoApiErrors(e, res, tag) {
  if (e.isArangoError) {
    if (e.errorNum === DOC_NOT_FOUND) {
      res.throw(404, `Error: Document not found. Operation: ${tag}`);
    } else if (e.errorNum === CONFLICTING_REV) {
      res.throw(409, `Error: Conflicting revision. Operation: ${tag}`);
    } else {
      res.throw(400, `Database error occurred: ${e}`, e);
    }
  }
  throw e;
}

module.exports = {
  convertJobForApi,
  getItemsLimit,
  getTimeDurationInSeconds,
  getWalltimeInSeconds,
  getMemoryInBytes,
  handleArangoApiErrors,
  makeCursorResult,
  makeCursorResultFromIteration,
  product,
};
