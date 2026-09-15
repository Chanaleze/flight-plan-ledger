/* Flight Plan Integrity Ledger — demo frontend (no build step, no dependencies).
 * The server is stateless: the session chain lives only in this page's memory.
 * All rendering uses textContent — user-supplied plan data never becomes HTML.
 */
(function () {
  'use strict';

  function $(id) { return document.getElementById(id); }

  function textEl(tag, cls, str) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    e.textContent = str;
    return e;
  }

  function short(s, n) {
    s = String(s);
    return s.length > (n || 18) ? s.slice(0, n || 18) + '…' : s;
  }

  var params = new URLSearchParams(window.location.search);
  var API_BASE = params.get('api') || (window.location.origin + '/api/demo');
  var SAMPLES_BASE = new URL('../examples/sample-flight-plans/', window.location.href).href;

  var state = {
    plan: null,
    planHash: null,
    entry: null,
    keyId: null,
    chain: [], // {entry, publicKeyPem, keyId}
    keys: {},  // keyId -> PEM
    lastSig: {} // sequence -> true/false (from last chain verification)
  };

  /* ---------- API ---------- */

  function apiError(action, err) {
    return new Error(
      'API ' + action + ' failed: ' + err.message +
      ' — is the demo backend deployed? See “Demo architecture & deployment”. ' +
      'You can point this page at it with ?api=https://<your-app>.vercel.app/api/demo'
    );
  }

  function api(action, payload) {
    payload = payload || {};
    payload.action = action;
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, 20000);
    return fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: ctrl.signal
    }).then(function (res) {
      clearTimeout(timer);
      return res.json().then(function (body) {
        if (!res.ok) throw new Error((body && body.error) || ('HTTP ' + res.status));
        return body;
      });
    }).catch(function (err) {
      clearTimeout(timer);
      throw apiError(action, err);
    });
  }

  function withBusy(btn, fn) {
    btn.disabled = true;
    return Promise.resolve().then(fn).catch(function (err) {
      showResult($('chainResult'), false, err.message);
    }).then(function () { btn.disabled = false; });
  }

  /* ---------- rendering ---------- */

  function badge(el, kind, msg) {
    el.hidden = false;
    el.className = 'badge ' + kind;
    el.textContent = msg;
  }

  function showResult(el, ok, title, detailObj) {
    el.hidden = false;
    el.className = 'result ' + (ok ? 'ok' : 'bad');
    el.innerHTML = '';
    el.appendChild(textEl('strong', null, (ok ? '✓ ' : '✗ ') + title));
    if (detailObj !== undefined) {
      el.appendChild(textEl('pre', null, JSON.stringify(detailObj, null, 2)));
    }
  }

  function currentPlan() {
    var raw = $('planInput').value.trim();
    if (!raw) throw new Error('Paste or load a flight plan first.');
    try {
      var obj = JSON.parse(raw);
    } catch (e) {
      throw new Error('Plan is not valid JSON: ' + e.message);
    }
    if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) {
      throw new Error('Plan must be a JSON object.');
    }
    return obj;
  }

  /* entry_hash is returned by the API; we keep it alongside each chain item
     as the link for the next entry (it is not part of the ledger model). */
  function tipHash() {
    if (!state.chain.length) return null;
    var last = state.chain[state.chain.length - 1];
    return last.entryHash;
  }

  function renderEntry(body) {
    var box = $('entryOut');
    box.hidden = false;
    box.innerHTML = '';
    var e = body.entry;
    box.appendChild(textEl('strong', null, 'Entry #' + e.sequence + ' · ' + e.status));
    var dl = document.createElement('dl');
    [['entry_id', e.entry_id], ['plan_hash', e.plan_hash], ['entry_hash', body.entry_hash],
     ['key_id', body.key_id], ['submitter', e.submitter_id], ['demo', String(e.metadata.demo)],
     ['recorded', e.timestamp]].forEach(function (pair) {
      dl.appendChild(textEl('dt', null, pair[0]));
      dl.appendChild(textEl('dd', null, pair[1]));
    });
    box.appendChild(dl);
    var det = document.createElement('details');
    det.appendChild(textEl('summary', null, 'signature + demo public key'));
    det.appendChild(textEl('pre', null, 'signature (base64):\n' + e.signature.value + '\n\npublic key (PEM):\n' + body.public_key_pem));
    box.appendChild(det);
    box.appendChild(textEl('p', 'muted small', body.warning));
  }

  function renderChain() {
    var box = $('chainOut');
    box.innerHTML = '';
    if (!state.chain.length) {
      box.appendChild(textEl('p', 'muted', 'Chain is empty — record an entry above.'));
      return;
    }
    var table = document.createElement('table');
    var head = document.createElement('thead');
    var hr = document.createElement('tr');
    ['Seq', 'Callsign', 'Status', 'Plan hash', 'Key', 'Sig'].forEach(function (h) {
      hr.appendChild(textEl('th', null, h));
    });
    head.appendChild(hr);
    table.appendChild(head);
    var tb = document.createElement('tbody');
    state.chain.forEach(function (item) {
      var e = item.entry;
      var tr = document.createElement('tr');
      tr.appendChild(textEl('td', null, String(e.sequence)));
      tr.appendChild(textEl('td', null, e.metadata.callsign || '?'));
      tr.appendChild(textEl('td', null, e.status));
      tr.appendChild(textEl('td', 'mono', short(e.plan_hash, 16)));
      tr.appendChild(textEl('td', 'mono', short(item.keyId.replace('demo-ephemeral-', 'demo:'), 14)));
      var sig = state.lastSig[e.sequence];
      tr.appendChild(textEl('td', null, sig === undefined ? '—' : (sig ? '✓' : '✗')));
      tb.appendChild(tr);
    });
    table.appendChild(tb);
    box.appendChild(table);
  }

  function renderRecovery(report) {
    $('recoverOut').hidden = false;
    $('recoverSummary').textContent =
      'Last known good set — ' + report.accepted_plan_count + ' accepted plan(s), ' +
      'replayed from ' + state.chain.length + ' ledger entr' +
      (state.chain.length === 1 ? 'y' : 'ies') + ' (generated ' + report.generated_at + ').';
    var tb = $('recoverTable').querySelector('tbody');
    tb.innerHTML = '';
    report.plans.forEach(function (p) {
      var tr = document.createElement('tr');
      tr.appendChild(textEl('td', null, String(p.sequence)));
      tr.appendChild(textEl('td', null, p.callsign || '?'));
      tr.appendChild(textEl('td', null, (p.origin || '?') + ' → ' + (p.destination || '?')));
      tr.appendChild(textEl('td', null, p.aircraft_id || '?'));
      tr.appendChild(textEl('td', null, p.dof || '?'));
      tr.appendChild(textEl('td', 'mono', short(p.plan_hash, 16)));
      tb.appendChild(tr);
    });
  }

  /* ---------- step 1: hash ---------- */

  function doHash(fromAuto) {
    var plan;
    try {
      plan = currentPlan();
    } catch (err) {
      if (!fromAuto) {
        $('canonicalOut').textContent = '—';
        showResult($('chainResult'), false, err.message);
      }
      return Promise.resolve();
    }
    var canon, hex;
    try {
      canon = window.fplHash.canonicalJson(plan);
    } catch (err) {
      $('canonicalOut').textContent = '—';
      badge($('parityBadge'), 'bad', 'Invalid plan: ' + err.message);
      state.plan = null;
      return Promise.resolve();
    }
    return window.fplHash.sha256Hex(canon).then(function (h) {
      hex = h;
      state.plan = plan;
      state.planHash = 'sha256:' + hex;
      $('canonicalOut').textContent = canon;
      $('planHashOut').textContent = state.planHash;
      return api('hash', { plan: plan }).then(function (server) {
        var match = server.plan_hash === state.planHash && server.canonical_json === canon;
        badge($('parityBadge'), match ? 'ok' : 'bad',
          match ? '✓ browser hash = server hash' : '✗ hash mismatch — please report this');
      }).catch(function () {
        badge($('parityBadge'), 'muted', 'server unreachable — browser hash shown only');
      });
    }).catch(function (err) {
      badge($('parityBadge'), 'bad', err.message);
    });
  }

  /* ---------- step 2: sign ---------- */

  function doSign() {
    var plan;
    try {
      plan = currentPlan();
    } catch (err) {
      showResult($('chainResult'), false, err.message);
      return Promise.resolve();
    }
    var next = state.chain.length + 1;
    var payload = { plan: plan, status: $('statusSelect').value, sequence: next };
    var tip = tipHash();
    if (tip) payload.previous_entry_hash = tip;
    return api('sign', payload).then(function (body) {
      state.entry = body.entry;
      state.keyId = body.key_id;
      state.chain.push({ entry: body.entry, entryHash: body.entry_hash, publicKeyPem: body.public_key_pem, keyId: body.key_id });
      state.keys[body.key_id] = body.public_key_pem;
      state.lastSig = {};
      renderEntry(body);
      renderChain();
      // refresh the local hash view so step 1 stays in sync with what was signed
      state.plan = plan;
      return doHash(true);
    });
  }

  /* ---------- step 3: verify ---------- */

  function doVerify() {
    if (!state.entry) {
      showResult($('verifyOut'), false, 'Nothing to verify yet — sign an entry first (step 2).');
      return Promise.resolve();
    }
    var plan;
    try {
      plan = currentPlan();
    } catch (err) {
      showResult($('verifyOut'), false, err.message);
      return Promise.resolve();
    }
    return api('verify', { plan: plan, entry: state.entry, public_keys: state.keys })
      .then(function (res) {
        showResult($('verifyOut'), res.valid, res.message, {
          plan_hash_match: res.plan_hash_match,
          signature_valid: res.signature_valid,
          sequence: res.sequence,
          status: res.status
        });
      });
  }

  function doTamper() {
    var plan;
    try {
      plan = currentPlan();
    } catch (err) {
      showResult($('verifyOut'), false, err.message);
      return Promise.resolve();
    }
    var copy = JSON.parse(JSON.stringify(plan));
    copy.callsign = String(copy.callsign || 'X') + 'X';
    $('planInput').value = JSON.stringify(copy, null, 2);
    showResult($('verifyOut'), true, 'Tampered copy loaded into the editor (callsign + “X”). Verifying…');
    return doVerify();
  }

  /* ---------- step 4: chain + recovery ---------- */

  function chainPayload() {
    return {
      entries: state.chain.map(function (item) {
        var e = JSON.parse(JSON.stringify(item.entry));
        delete e.entry_hash; // client-side tip bookkeeping, not part of the model
        return e;
      }),
      public_keys: state.keys
    };
  }

  function doChain() {
    if (!state.chain.length) {
      showResult($('chainResult'), false, 'Chain is empty — record an entry first (step 2).');
      return Promise.resolve();
    }
    return api('verify_chain', chainPayload()).then(function (res) {
      state.lastSig = {};
      res.chain.forEach(function (c) {
        if (c.signature_valid !== null) state.lastSig[c.sequence] = c.signature_valid;
      });
      renderChain();
      showResult($('chainResult'), res.valid, res.message, { entries_checked: res.entries_checked });
    });
  }

  function doRecover() {
    if (!state.chain.length) {
      showResult($('chainResult'), false, 'Chain is empty — record an entry first (step 2).');
      return Promise.resolve();
    }
    return api('recover', { entries: chainPayload().entries }).then(function (report) {
      renderRecovery(report);
      showResult($('chainResult'), true,
        'Outage simulated: primary system “down”, ledger replayed — ' +
        report.accepted_plan_count + ' accepted plan(s) recovered.');
    });
  }

  function doReset() {
    state.plan = null;
    state.planHash = null;
    state.entry = null;
    state.keyId = null;
    state.chain = [];
    state.keys = {};
    state.lastSig = {};
    $('entryOut').hidden = true;
    $('verifyOut').hidden = true;
    $('chainResult').hidden = true;
    $('recoverOut').hidden = true;
    $('canonicalOut').textContent = '—';
    $('planHashOut').textContent = '—';
    $('parityBadge').hidden = true;
    renderChain();
  }

  /* ---------- loading samples / files ---------- */

  function loadSample() {
    var name = $('sampleSelect').value;
    return fetch(SAMPLES_BASE + name).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.text();
    }).then(function (txt) {
      $('planInput').value = txt;
      return doHash(true);
    }).catch(function (err) {
      showResult($('chainResult'), false, 'Could not load sample (' + err.message + '). Paste plan JSON manually.');
    });
  }

  /* ---------- wiring ---------- */

  $('hashBtn').addEventListener('click', function () { doHash(false); });
  $('signBtn').addEventListener('click', function () { withBusy(this, doSign); });
  $('verifyBtn').addEventListener('click', function () { withBusy(this, doVerify); });
  $('tamperBtn').addEventListener('click', function () { withBusy(this, doTamper); });
  $('chainBtn').addEventListener('click', function () { withBusy(this, doChain); });
  $('recoverBtn').addEventListener('click', function () { withBusy(this, doRecover); });
  $('resetBtn').addEventListener('click', doReset);
  $('loadSampleBtn').addEventListener('click', function () { withBusy(this, loadSample); });
  $('fileInput').addEventListener('change', function () {
    var f = this.files && this.files[0];
    if (!f) return;
    var rd = new FileReader();
    rd.onload = function () {
      $('planInput').value = String(rd.result || '');
      doHash(true);
    };
    rd.readAsText(f);
  });

  $('apiBase').textContent = API_BASE;
  fetch(API_BASE, { method: 'GET' }).then(function (res) {
    return res.json();
  }).then(function (info) {
    $('apiStatus').textContent = 'connected (' + info.service + ' ' + info.version + ', demo_only=' + info.demo_only + ')';
  }).catch(function () {
    $('apiStatus').textContent = 'unreachable — hashing still works locally; deploy the backend (see docs/demo.md)';
  });

  renderChain();
  loadSample();
})();
