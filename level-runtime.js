/* DP Adventure — universal interactive runtime for levels 2..53.
 * Reads <script type="application/json" id="level-data"> and mounts widgets:
 *  - data-viz="row|grid|chart|stick|string|bars|items"  → scene 1 visual
 *  - data-tree                                        → expanding recursion tree
 *  - data-memo                                        → memo backpack stepper
 *  - data-tab                                         → tab table stepper
 *  - data-space                                       → space-saver stepper
 *  - data-compare                                     → before-vs-after bars
 */
(function () {
  'use strict';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  var dataEl = document.getElementById('level-data');
  if (!dataEl) return;
  var L;
  try { L = JSON.parse(dataEl.textContent); } catch (e) { console.error('bad level data', e); return; }

  /* ---------- Scene 1: visual ---------- */
  function mountViz(host) {
    var v = L.viz || {};
    if (v.kind === 'row' || v.kind === 'coins') {
      host.innerHTML = '<p class="muted center" style="margin:0 0 8px">' + (v.label || '') + '</p>' +
        '<div class="coins">' + v.items.map(function (x) { return '<div class="coin">' + x + '</div>'; }).join('') + '</div>';
    } else if (v.kind === 'bars') {
      var mx = Math.max.apply(null, v.items);
      host.innerHTML = '<p class="muted center" style="margin:0 0 8px">' + (v.label || '') + '</p>' +
        '<div class="stairs" style="height:140px">' + v.items.map(function (x) {
          return '<div class="step" style="height:' + (20 + Math.round(110 * x / mx)) + 'px">' + x + '</div>';
        }).join('') + '</div>';
    } else if (v.kind === 'grid') {
      var rows = v.rows, cols = v.cols, blocks = (v.blocks || []);
      var cells = '';
      for (var r = 0; r < rows; r++) for (var c = 0; c < cols; c++) {
        var cls = 'cell';
        var txt = '';
        if (r === 0 && c === 0) { cls += ' start'; txt = 'S'; }
        else if (r === rows - 1 && c === cols - 1) { cls += ' end'; txt = '🍓'; }
        else if (blocks.some(function (b) { return b[0] === r && b[1] === c; })) { cls += ' block'; txt = '🪨'; }
        else if (v.values) { txt = v.values[r * cols + c]; }
        cells += '<div class="' + cls + '">' + txt + '</div>';
      }
      host.innerHTML = '<div class="grid-viz" style="grid-template-columns:repeat(' + cols + ',1fr);max-width:' + (cols * 64) + 'px;margin:0 auto;gap:6px">' + cells + '</div>';
    } else if (v.kind === 'string') {
      host.innerHTML = '<p class="muted center" style="margin:0 0 8px">' + (v.label || '') + '</p>' +
        '<div style="text-align:center;font-family:var(--mono);font-size:22px;font-weight:800;color:var(--primary)">"' + v.s + '"</div>';
    } else if (v.kind === 'strings') {
      host.innerHTML = '<p class="muted center" style="margin:0 0 8px">two strings</p>' +
        '<div style="text-align:center;font-family:var(--mono);font-size:18px;font-weight:800">' +
        '<div style="margin:6px"><span style="color:var(--primary)">A:</span> ' + v.a + '</div>' +
        '<div style="margin:6px"><span style="color:var(--accent)">B:</span> ' + v.b + '</div></div>';
    } else if (v.kind === 'stick') {
      var pieces = '';
      for (var i = 0; i < v.length; i++) pieces += '[' + (i + 1) + ']';
      host.innerHTML = '<p class="muted center" style="margin:0 0 8px">stick of length ' + v.length + (v.cuts ? ' · cuts at ' + v.cuts.join(',') : '') + '</p>' +
        '<pre class="code" style="background:#fff;color:var(--ink);text-align:center;font-family:var(--mono)">' + pieces + '</pre>';
    } else if (v.kind === 'balloons') {
      host.innerHTML = '<p class="muted center" style="margin:0 0 8px">' + (v.label || 'balloons') + '</p>' +
        '<div class="coins">' + v.items.map(function (x) { return '<div class="coin">🎈' + x + '</div>'; }).join('') + '</div>';
    } else {
      host.innerHTML = '';
    }
  }

  /* ---------- Recursion tree (Scene 2) ---------- */
  function mountTree(host) {
    var t = L.tree;
    if (!t) { host.innerHTML = '<p class="muted center">recursion tree shown via the recurrence above</p>'; return; }
    var revealed = 1, maxDepth = t.maxDepth || 4;
    var nodes = t.nodes || [];
    function render() {
      var visible = nodes.filter(function (n) { return n.d <= revealed; });
      var byD = {}; visible.forEach(function (n) { (byD[n.d] = byD[n.d] || []).push(n); });
      var ds = Object.keys(byD).map(Number).sort(function (a, b) { return a - b; });
      var deepest = byD[ds[ds.length - 1]] || [];
      var nodeW = 78, rowH = 70, padX = 14;
      var width = Math.max(360, padX * 2 + deepest.length * (nodeW + 8));
      var height = ds.length * rowH + 20;
      var xs = {};
      if (deepest.length === 1) xs[deepest[0].id] = width / 2;
      else deepest.forEach(function (n, i) { xs[n.id] = padX + nodeW / 2 + i * ((width - padX * 2 - nodeW) / (deepest.length - 1)); });
      var childMap = {}; visible.forEach(function (n) { if (n.p != null) (childMap[n.p] = childMap[n.p] || []).push(n.id); });
      for (var di = ds.length - 2; di >= 0; di--) {
        (byD[ds[di]] || []).forEach(function (n) {
          var kids = childMap[n.id] || [];
          if (kids.length) { var s = 0; kids.forEach(function (k) { s += xs[k]; }); xs[n.id] = s / kids.length; }
          else xs[n.id] = width / 2;
        });
      }
      var svg = '<svg class="tree" width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + ' ' + height + '">';
      visible.forEach(function (n) {
        if (n.p == null) return;
        var pn = visible.find(function (q) { return q.id === n.p; }); if (!pn) return;
        svg += '<line x1="' + xs[pn.id] + '" y1="' + (pn.d * rowH + 15 + 36) + '" x2="' + xs[n.id] + '" y2="' + (n.d * rowH + 15) + '" class="edge' + (n.dup ? ' dim' : '') + '"/>';
      });
      visible.forEach(function (n) {
        var x = xs[n.id], y = n.d * rowH + 15;
        var cls = 'node-bg' + (n.dup ? ' dup' : '') + (n.base ? ' base' : '');
        svg += '<rect x="' + (x - nodeW / 2) + '" y="' + y + '" width="' + nodeW + '" height="36" rx="10" class="' + cls + '"/>';
        svg += '<text x="' + x + '" y="' + (y + 22) + '" class="' + (n.dup ? 'dup' : (n.base ? 'base' : '')) + '">' + n.lbl + '</text>';
      });
      svg += '</svg>';
      host.innerHTML = svg;
      var calls = visible.length, dups = visible.filter(function (n) { return n.dup; }).length;
      var c = $('#tree-calls'); if (c) c.textContent = calls;
      var d = $('#tree-dups'); if (d) d.textContent = dups;
    }
    render();
    var scope = host.parentElement;
    var btn1 = scope.querySelector('[data-tree="expand"]');
    if (btn1) btn1.addEventListener('click', function () { revealed = Math.min(maxDepth, revealed + 1); render(); });
    var btn2 = scope.querySelector('[data-tree="all"]');
    if (btn2) btn2.addEventListener('click', function () { revealed = maxDepth; render(); });
    var btn3 = scope.querySelector('[data-tree="reset"]');
    if (btn3) btn3.addEventListener('click', function () { revealed = 1; render(); });
  }

  /* ---------- Memo backpack stepper ---------- */
  function mountMemo(host) {
    var m = L.memo;
    if (!m || !m.entries) return;
    var i = -1;
    function render() {
      host.innerHTML = '';
      for (var k = 0; k <= i; k++) {
        var e = m.entries[k];
        var slot = document.createElement('div');
        slot.className = 'memo-slot';
        slot.innerHTML = '<div class="k">' + e.k + '</div><div class="v">= ' + e.v + '</div>';
        host.appendChild(slot);
      }
      var saved = $('#memo-saved'); if (saved) saved.textContent = Math.max(0, i + 1);
      var skipped = $('#memo-skipped'); if (skipped) skipped.textContent = Math.max(0, i + 1) > 0 ? Math.floor((i + 1) * 0.7) : 0;
      var lbl = $('#memo-step-lbl'); if (lbl) lbl.textContent = (i + 1) + ' / ' + m.entries.length;
    }
    render();
    var scope = host.closest('.scene');
    scope.querySelector('[data-memo="next"]').addEventListener('click', function () { i = Math.min(m.entries.length - 1, i + 1); render(); });
    scope.querySelector('[data-memo="all"]').addEventListener('click', function () { i = m.entries.length - 1; render(); });
    scope.querySelector('[data-memo="reset"]').addEventListener('click', function () { i = -1; render(); });
  }

  /* ---------- Tab table stepper ---------- */
  function mountTab(host) {
    var t = L.tab;
    if (!t || !t.values) return;
    var i = -1;
    function render() {
      host.innerHTML = '';
      t.values.forEach(function (v, k) {
        var c = document.createElement('div');
        c.className = 'tab-cell' + (k <= i ? ' filled' : '') + (k === i ? ' current' : '');
        var lbl = (t.labels && t.labels[k]) || ('dp[' + k + ']');
        c.innerHTML = '<span class="idx">' + lbl + '</span>' + (k <= i ? v : '?');
        host.appendChild(c);
      });
      var f = $('#tab-formula');
      if (f) {
        if (i < 0) f.innerHTML = 'Click <b>Next</b> to fill the next box →';
        else if (t.formulas && t.formulas[i]) f.innerHTML = t.formulas[i];
        else f.innerHTML = '<b>' + (t.labels ? t.labels[i] : 'dp[' + i + ']') + '</b> = <b>' + t.values[i] + '</b>';
      }
      var lbl = $('#tab-step-lbl'); if (lbl) lbl.textContent = (Math.max(0, i) + (i >= 0 ? 1 : 0)) + ' / ' + t.values.length;
    }
    render();
    var scope = host.closest('.scene');
    scope.querySelector('[data-tab="next"]').addEventListener('click', function () { i = Math.min(t.values.length - 1, i + 1); render(); });
    scope.querySelector('[data-tab="all"]').addEventListener('click', function () { i = t.values.length - 1; render(); });
    scope.querySelector('[data-tab="reset"]').addEventListener('click', function () { i = -1; render(); });
  }

  /* ---------- Space saver stepper ---------- */
  function mountSpace(host) {
    var s = L.space;
    if (!s || !s.frames) {
      host.innerHTML = '<p class="muted center">N/A — full table required for this problem.</p>';
      return;
    }
    var i = 0, frames = s.frames, labels = s.labels || ['prev', 'curr', 'next'];
    function render() {
      var f = frames[i];
      var html = '<div class="space-stage">';
      f.forEach(function (val, k) {
        var cls = 'space-box' + (k === f.length - 1 ? ' curr' : '');
        html += '<div><div class="' + cls + '">' + val + '</div><div class="muted center" style="margin-top:6px;font-size:12px;font-weight:800;letter-spacing:.5px;text-transform:uppercase">' + (labels[k] || '') + '</div></div>';
        if (k < f.length - 1) html += '<div class="arrow">+</div>';
      });
      html += '</div>';
      host.innerHTML = html;
      var lbl = $('#space-step-lbl'); if (lbl) lbl.textContent = 'step ' + (i + 1) + ' of ' + frames.length;
    }
    render();
    var scope = host.closest('.scene');
    scope.querySelector('[data-space="next"]').addEventListener('click', function () { i = Math.min(frames.length - 1, i + 1); render(); });
    scope.querySelector('[data-space="all"]').addEventListener('click', function () { i = frames.length - 1; render(); });
    scope.querySelector('[data-space="reset"]').addEventListener('click', function () { i = 0; render(); });
  }

  /* ---------- Compare bars ---------- */
  function mountCompare() {
    var c = L.compare; if (!c) return;
    var bn = $('#cmp-brute-num'); if (bn) bn.innerHTML = c.brute + ' <small>tries</small>';
    var dn = $('#cmp-dp-num'); if (dn) dn.innerHTML = c.dp + ' <small>steps</small>';
    var db = $('#cmp-dp-bar'); if (db) db.style.width = Math.max(4, Math.min(100, (c.dpRatio || 25))) + '%';
  }

  /* ---------- mount everything ---------- */
  function mount() {
    var v = $('[data-viz]'); if (v) mountViz(v);
    var t = $('[data-tree]'); if (t) mountTree(t);
    var m = $('[data-memo]'); if (m) mountMemo(m);
    var tab = $('[data-tab]'); if (tab) mountTab(tab);
    var sp = $('[data-space]'); if (sp) mountSpace(sp);
    mountCompare();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
