const parse = require('tinyduration').parse;

const {KiB, MiB, GiB, TiB} = require('./defs');
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
  obj = parse(duration);
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

module.exports = {getTimeDurationInSeconds, getMemoryInBytes, product};
