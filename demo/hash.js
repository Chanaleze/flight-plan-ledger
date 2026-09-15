/* Flight Plan Integrity Ledger — demo-only browser mirror of canonical hashing.
 *
 * Byte-exact mirror of FlightPlanCanonicalV1.canonical_bytes() for the inputs
 * the demo accepts (flat JSON objects with string/date fields). The server
 * always re-validates and its hash is authoritative; this mirror exists so
 * visitors can see the *same* hash computed locally in their browser.
 *
 * Rules mirrored from src/flight_plan_ledger/models/canonical.py:
 * - unknown fields dropped; missing required fields rejected
 * - callsign/aircraft_id/origin/destination: trimmed + upper-cased
 * - dof: strict YYYY-MM-DD, must be a real date
 * - departure_time_utc (optional): any ISO offset accepted, naive = UTC,
 *   emitted as UTC with 'Z'; fractional seconds as microseconds (6 digits,
 *   omitted when zero); extra digits truncated to 6
 * - schema_version defaults to "FlightPlanCanonicalV1"
 * - keys sorted, no whitespace (separators ',', ':'), UTF-8
 *
 * No DOM dependencies: safe to load in Node for parity checks.
 */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  } else {
    root.fplHash = api;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var SCHEMA_VERSION = 'FlightPlanCanonicalV1';
  var ID_FIELDS = ['callsign', 'aircraft_id', 'origin', 'destination'];

  function fail(message) {
    throw new Error(message);
  }

  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function pad4(n) {
    return ('000' + n).slice(-4);
  }

  function cmp(a, b) {
    return a < b ? -1 : a > b ? 1 : 0;
  }

  function normId(value, name) {
    if (typeof value !== 'string') fail(name + ' must be a string');
    return value.trim().toUpperCase();
  }

  function normDate(value) {
    if (typeof value !== 'string') fail('dof must be a string like YYYY-MM-DD');
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value.trim());
    if (!m) fail('dof must look like YYYY-MM-DD');
    var y = +m[1], mo = +m[2], d = +m[3];
    if (mo < 1 || mo > 12) fail('dof month out of range');
    var probe = new Date(Date.UTC(y, mo - 1, d));
    if (probe.getUTCFullYear() !== y || probe.getUTCMonth() !== mo - 1 || probe.getUTCDate() !== d) {
      fail('dof is not a real calendar date');
    }
    return pad4(y) + '-' + pad2(mo) + '-' + pad2(d);
  }

  var DT_RE = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?\s*(Z|[+-]\d{2}:?\d{2})?$/i;

  function normDateTime(value) {
    if (typeof value !== 'string') fail('departure_time_utc must be a string');
    var m = DT_RE.exec(value.trim());
    if (!m) fail('departure_time_utc must be ISO-8601');
    var y = +m[1], mo = +m[2], d = +m[3], h = +m[4], mi = +m[5], s = m[6] === undefined ? 0 : +m[6];
    var frac = m[7] || '';
    if (mo < 1 || mo > 12 || d < 1 || d > 31 || h > 23 || mi > 59 || s > 59) {
      fail('departure_time_utc has out-of-range components');
    }
    var probe = new Date(Date.UTC(y, mo - 1, d));
    if (probe.getUTCFullYear() !== y || probe.getUTCMonth() !== mo - 1 || probe.getUTCDate() !== d) {
      fail('departure_time_utc is not a real calendar date');
    }
    if (frac.length > 9) fail('departure_time_utc has too many fractional digits');
    var micro = (frac + '000000').slice(0, 6); // truncate to 6, pad right
    var offsetMs = 0;
    if (m[8] && m[8].toUpperCase() !== 'Z') {
      var sign = m[8][0] === '+' ? 1 : -1;
      var digits = m[8].slice(1).replace(':', '');
      var oh = +digits.slice(0, 2), om = +digits.slice(2, 4);
      if (oh > 23 || om > 59) fail('departure_time_utc has a bad UTC offset');
      offsetMs = sign * (oh * 60 + om) * 60000;
    }
    var t = new Date(Date.UTC(y, mo - 1, d, h, mi, s) - offsetMs);
    var out = pad4(t.getUTCFullYear()) + '-' + pad2(t.getUTCMonth() + 1) + '-' + pad2(t.getUTCDate()) +
      'T' + pad2(t.getUTCHours()) + ':' + pad2(t.getUTCMinutes()) + ':' + pad2(t.getUTCSeconds());
    if (!/^0+$/.test(micro)) out += '.' + micro;
    return out + 'Z';
  }

  function canonicalJson(plan) {
    if (plan === null || typeof plan !== 'object' || Array.isArray(plan)) {
      fail('plan must be a JSON object');
    }
    var out = {};
    ID_FIELDS.forEach(function (name) {
      if (plan[name] === undefined || plan[name] === null) fail(name + ' is required');
      out[name] = normId(plan[name], name);
    });
    if (plan.dof === undefined || plan.dof === null) fail('dof is required');
    out.dof = normDate(plan.dof);
    if (plan.departure_time_utc !== undefined && plan.departure_time_utc !== null) {
      out.departure_time_utc = normDateTime(plan.departure_time_utc);
    }
    if (plan.route !== undefined && plan.route !== null) {
      if (typeof plan.route !== 'string') fail('route must be a string');
      out.route = plan.route;
    }
    var sv = plan.schema_version;
    if (sv === undefined) {
      out.schema_version = SCHEMA_VERSION;
    } else if (typeof sv !== 'string') {
      fail('schema_version must be a string');
    } else {
      out.schema_version = sv;
    }
    return JSON.stringify(out, Object.keys(out).sort(cmp));
  }

  function sha256Hex(text) {
    var subtle = (typeof crypto !== 'undefined' && crypto.subtle) ||
      (typeof require === 'function' ? require('crypto').webcrypto.subtle : null);
    if (!subtle) return Promise.reject(new Error('WebCrypto SHA-256 is unavailable here; serve over http(s).'));
    var bytes = new TextEncoder().encode(text);
    return subtle.digest('SHA-256', bytes).then(function (digest) {
      return Array.prototype.map.call(new Uint8Array(digest), function (b) {
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    });
  }

  return { canonicalJson: canonicalJson, sha256Hex: sha256Hex };
});
