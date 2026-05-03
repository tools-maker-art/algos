/* DP Adventure — interactive helpers (vanilla JS) */
(function () {
  'use strict';
  function $$(s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); }
  function $(s, root) { return (root || document).querySelector(s); }
  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (html != null) n.innerHTML = html;
    return n;
  }
  function svgEl(tag, attrs) {
    var n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    if (attrs) for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  /* ===== STORY: bunny starts on the GROUND (position -1) ===== */
  var storyState = { n: 5, pos: -1 }; // pos = -1 means ground; 0..n-1 means step
  function ways(n) {
    if (n <= 1) return 1;
    var a = 1, b = 1;
    for (var i = 2; i <= n; i++) { var c = a + b; a = b; b = c; }
    return b;
  }
  function buildStairs() {
    var stage = $('#stairs-stage'); if (!stage) return;
    stage.innerHTML = '';
    var n = storyState.n;
    // Ground tile
    var ground = el('div', { 'class': 'ground' });
    ground.innerHTML = '<span class="ground-label">START</span>';
    stage.appendChild(ground);
    var maxH = 170, baseH = 30;
    for (var i = 1; i <= n; i++) {
      var h = baseH + (i / n) * (maxH - baseH);
      var s = el('div', { 'class': 'step', 'data-i': i });
      s.style.height = h + 'px';
      stage.appendChild(s);
    }
    var bunny = el('div', { 'class': 'bunny', id: 'bunny' });
    bunny.textContent = '🐰';
    stage.appendChild(bunny);
    storyState.pos = -1;
    setTimeout(function () { placeBunny(); }, 30);
    var t = $('#story-ways'); if (t) t.textContent = ways(n);
    renderAllPaths();
  }
  function placeBunny() {
    var bunny = $('#bunny'); if (!bunny) return;
    var stage = $('#stairs-stage');
    var ground = $('.ground', stage);
    var prect = stage.getBoundingClientRect();
    if (storyState.pos === -1 && ground) {
      var gr = ground.getBoundingClientRect();
      bunny.style.left = (gr.left - prect.left + gr.width / 2 - 17) + 'px';
      bunny.style.bottom = '6px';
      return;
    }
    var steps = $$('.step', stage);
    if (storyState.pos >= steps.length) storyState.pos = steps.length - 1;
    var s = steps[storyState.pos];
    var rect = s.getBoundingClientRect();
    bunny.style.left = (rect.left - prect.left + rect.width / 2 - 17) + 'px';
    bunny.style.bottom = (rect.height - 4) + 'px';
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-hop]');
    if (btn) {
      var dir = btn.getAttribute('data-hop');
      if (dir === '1') storyState.pos = Math.min(storyState.n - 1, storyState.pos + 1);
      if (dir === '2') storyState.pos = Math.min(storyState.n - 1, storyState.pos + 2);
      if (dir === 'r') storyState.pos = -1;
      placeBunny();
    }
    var nb = e.target.closest('[data-set-n]');
    if (nb) {
      storyState.n = parseInt(nb.getAttribute('data-set-n'), 10);
      $$('[data-set-n]').forEach(function (b) { b.classList.toggle('active', b === nb); });
      buildStairs();
      resetTree(); resetMemo(); resetTab(); resetSpace(); updateCompare();
    }
  });

  /* ===== ALL PATHS: enumerate every way to climb N stairs ===== */
  function allPaths(n) {
    if (n === 0) return [[]];
    if (n < 0) return [];
    var out = [];
    allPaths(n - 1).forEach(function (p) { out.push([1].concat(p)); });
    allPaths(n - 2).forEach(function (p) { out.push([2].concat(p)); });
    return out;
  }
  function renderAllPaths() {
    var box = $('#all-paths'); if (!box) return;
    box.innerHTML = '';
    var paths = allPaths(storyState.n);
    paths.forEach(function (p, i) {
      var row = el('div', { 'class': 'path-row' });
      var idx = el('span', { 'class': 'path-idx' });
      idx.textContent = (i + 1) + '.';
      row.appendChild(idx);
      p.forEach(function (h) {
        var hop = el('span', { 'class': 'hop hop-' + h });
        hop.textContent = h === 1 ? '⬆ 1' : '⏫ 2';
        row.appendChild(hop);
      });
      box.appendChild(row);
    });
    var c = $('#all-paths-count'); if (c) c.textContent = paths.length;
  }

  /* ===== BRUTE-FORCE TREE — labeled with stair counts, not f(n) ===== */
  var treeState = { revealed: 1 };
  function computeTree(n) {
    var nodes = []; var seen = {}; var idc = 0;
    function rec(val, depth, parent) {
      var id = idc++;
      var dup = !!seen[val];
      var base = (val <= 1);
      // Label: "🪜N" — N stairs left to climb.
      var lbl = '🪜 ' + val;
      if (val === 0) lbl = '🏁 0';
      if (val === 1) lbl = '🪜 1';
      var node = { id: id, label: lbl, val: val, depth: depth, parent: parent, isDup: dup, isBase: base };
      nodes.push(node);
      seen[val] = true;
      if (!base) {
        rec(val - 1, depth + 1, id);
        rec(val - 2, depth + 1, id);
      }
      return node;
    }
    rec(n, 0, -1);
    return nodes;
  }
  function renderTree() {
    var stage = $('#tree-svg-wrap'); if (!stage) return;
    stage.innerHTML = '';
    var n = Math.min(6, storyState.n);
    var all = computeTree(n);
    var maxAvail = 0; all.forEach(function (x) { if (x.depth > maxAvail) maxAvail = x.depth; });
    var maxDepth = Math.min(maxAvail, treeState.revealed);
    var visible = all.filter(function (x) { return x.depth <= maxDepth; });
    var byDepth = {};
    visible.forEach(function (x) { (byDepth[x.depth] = byDepth[x.depth] || []).push(x); });
    var rowH = 78, padX = 14, nodeW = 78, nodeH = 36;
    var deepest = byDepth[maxDepth] || [];
    var bottomCount = Math.max(1, deepest.length);
    var width = Math.max(360, padX * 2 + bottomCount * (nodeW + 8));
    var height = (maxDepth + 1) * rowH + 30;
    var svg = svgEl('svg', { width: width, height: height, viewBox: '0 0 ' + width + ' ' + height, 'class': 'tree' });
    var xs = {};
    if (bottomCount === 1) {
      xs[deepest[0].id] = width / 2;
    } else {
      deepest.forEach(function (x, i) {
        xs[x.id] = padX + nodeW / 2 + i * ((width - padX * 2 - nodeW) / (bottomCount - 1));
      });
    }
    var childMap = {};
    visible.forEach(function (x) { if (x.parent >= 0) (childMap[x.parent] = childMap[x.parent] || []).push(x.id); });
    for (var d = maxDepth - 1; d >= 0; d--) {
      (byDepth[d] || []).forEach(function (x) {
        var kids = childMap[x.id] || [];
        if (kids.length) {
          var s = 0; kids.forEach(function (k) { s += xs[k]; });
          xs[x.id] = s / kids.length;
        } else {
          xs[x.id] = width / 2;
        }
      });
    }
    visible.forEach(function (x) {
      if (x.parent < 0) return;
      var pNode = visible.filter(function (q) { return q.id === x.parent; })[0]; if (!pNode) return;
      var px = xs[pNode.id], py = pNode.depth * rowH + 15 + nodeH;
      var cx = xs[x.id], cy = x.depth * rowH + 15;
      var line = svgEl('line', { x1: px, y1: py, x2: cx, y2: cy, 'class': 'edge' + (x.isDup ? ' dim' : '') });
      svg.appendChild(line);
    });
    var liveCalls = 0, liveDups = 0;
    visible.forEach(function (x) {
      var cx = xs[x.id], y = x.depth * rowH + 15;
      var cls = 'node-bg' + (x.isDup ? ' dup' : '') + (x.isBase ? ' base' : '');
      svg.appendChild(svgEl('rect', { x: cx - nodeW / 2, y: y, width: nodeW, height: nodeH, rx: 10, 'class': cls }));
      var t = svgEl('text', { x: cx, y: y + 22, 'class': (x.isDup ? 'dup' : (x.isBase ? 'base' : '')) });
      t.textContent = x.label;
      svg.appendChild(t);
      liveCalls++;
      if (x.isDup) liveDups++;
    });
    stage.appendChild(svg);
    var mc = $('#tree-calls'); if (mc) mc.textContent = liveCalls;
    var md = $('#tree-dups'); if (md) md.textContent = liveDups;
    var ws = $('#tree-ways'); if (ws) ws.textContent = ways(storyState.n);
  }
  function resetTree() { treeState.revealed = 1; renderTree(); }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-tree="expand"]')) { treeState.revealed = Math.min(8, treeState.revealed + 1); renderTree(); }
    else if (e.target.closest('[data-tree="all"]')) { treeState.revealed = 8; renderTree(); }
    else if (e.target.closest('[data-tree="reset"]')) { resetTree(); }
  });

  /* ===== MEMOIZATION ===== */
  var memoState = { i: -1, order: [] };
  function buildMemoOrder() {
    var n = storyState.n; var order = []; var stored = {};
    function rec(k) {
      if (k <= 1) {
        order.push({ k: k, action: 'store', val: 1 }); stored[k] = 1; return 1;
      }
      if (stored.hasOwnProperty(k)) {
        order.push({ k: k, action: 'hit', val: stored[k] }); return stored[k];
      }
      var a = rec(k - 1), b = rec(k - 2);
      var v = a + b; stored[k] = v;
      order.push({ k: k, action: 'store', val: v }); return v;
    }
    rec(n); return order;
  }
  function renderMemo() {
    var slots = $('#memo-slots'); if (!slots) return;
    slots.innerHTML = '';
    var hits = 0, stores = 0; var added = {};
    for (var idx = 0; idx <= memoState.i && idx < memoState.order.length; idx++) {
      var step = memoState.order[idx];
      if (step.action === 'store' && !added[step.k]) {
        var slot = document.createElement('div');
        slot.className = 'memo-slot';
        slot.innerHTML = '<div class="k">🪜 ' + step.k + ' stairs</div><div class="v">= ' + step.val + ' way' + (step.val === 1 ? '' : 's') + '</div>';
        slots.appendChild(slot); added[step.k] = true; stores++;
      } else if (step.action === 'hit') { hits++; }
    }
    var ms = $('#memo-saved'); if (ms) ms.textContent = stores;
    var mh = $('#memo-skipped'); if (mh) mh.textContent = hits;
    var lbl = $('#memo-step-lbl'); if (lbl) lbl.textContent = (memoState.i + 1) + ' / ' + memoState.order.length;
  }
  function resetMemo() { memoState.order = buildMemoOrder(); memoState.i = -1; renderMemo(); }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-memo="next"]')) { memoState.i = Math.min(memoState.order.length - 1, memoState.i + 1); renderMemo(); }
    else if (e.target.closest('[data-memo="all"]')) { memoState.i = memoState.order.length - 1; renderMemo(); }
    else if (e.target.closest('[data-memo="reset"]')) { resetMemo(); }
  });

  /* ===== TABULATION ===== */
  var tabState = { i: -1 };
  function renderTab() {
    var row = $('#tab-row'); if (!row) return;
    row.innerHTML = '';
    var n = storyState.n;
    var vals = []; vals[0] = 1; vals[1] = 1;
    for (var i = 2; i <= n; i++) vals[i] = vals[i - 1] + vals[i - 2];
    for (var k = 0; k <= n; k++) {
      var c = document.createElement('div');
      c.className = 'tab-cell';
      if (k <= tabState.i) c.classList.add('filled');
      if (k === tabState.i) c.classList.add('current');
      c.innerHTML = '<span class="idx">' + k + ' stairs</span>' + (k <= tabState.i ? vals[k] : '?');
      row.appendChild(c);
    }
    var f = $('#tab-formula');
    if (f) {
      if (tabState.i === 0 || tabState.i === 1) f.innerHTML = '<b>' + tabState.i + ' stairs</b> → <b>1 way</b> (easy starter)';
      else if (tabState.i >= 2) f.innerHTML = '<b>' + tabState.i + ' stairs</b> = ways for <b>' + (tabState.i - 1) + '</b> + ways for <b>' + (tabState.i - 2) + '</b> = <b>' + vals[tabState.i] + '</b>';
      else f.innerHTML = 'Click <b>Next</b> to fill the next box →';
    }
    var lbl = $('#tab-step-lbl'); if (lbl) lbl.textContent = (Math.max(0, tabState.i) + 1) + ' / ' + (n + 1);
  }
  function resetTab() { tabState.i = -1; renderTab(); }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-tab="next"]')) { tabState.i = Math.min(storyState.n, tabState.i + 1); renderTab(); }
    else if (e.target.closest('[data-tab="all"]')) { tabState.i = storyState.n; renderTab(); }
    else if (e.target.closest('[data-tab="reset"]')) { resetTab(); }
  });

  /* ===== SPACE OPTIMIZATION ===== */
  var spaceState = { step: 1, prev: 1, curr: 1 };
  function renderSpace() {
    var p = $('#space-prev'), c = $('#space-curr'), nx = $('#space-next'); if (!p || !c) return;
    p.textContent = spaceState.prev;
    c.textContent = spaceState.curr;
    if (nx) nx.textContent = (spaceState.step >= storyState.n) ? '✓' : '?';
    var lbl = $('#space-step-lbl'); if (lbl) lbl.textContent = 'we are at stair ' + spaceState.step + ' · current answer = ' + spaceState.curr;
  }
  function resetSpace() { spaceState = { step: 1, prev: 1, curr: 1 }; renderSpace(); }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-space="next"]')) {
      if (spaceState.step >= storyState.n) return;
      var nxt = spaceState.prev + spaceState.curr;
      var nbox = $('#space-next');
      if (nbox) { nbox.textContent = nxt; nbox.classList.add('curr'); setTimeout(function () { nbox.classList.remove('curr'); }, 350); }
      spaceState.prev = spaceState.curr;
      spaceState.curr = nxt;
      spaceState.step++;
      setTimeout(renderSpace, 280);
    } else if (e.target.closest('[data-space="reset"]')) {
      resetSpace();
    } else if (e.target.closest('[data-space="all"]')) {
      var a = 1, b = 1;
      for (var i = 2; i <= storyState.n; i++) { var t = a + b; a = b; b = t; }
      spaceState.prev = a; spaceState.curr = b; spaceState.step = storyState.n; renderSpace();
    }
  });

  /* ===== COMPARE ===== */
  function bruteCalls(n) {
    var a = 1, b = 1;
    for (var i = 2; i <= n + 1; i++) { var c = a + b; a = b; b = c; }
    return 2 * b - 1;
  }
  function updateCompare() {
    var n = storyState.n;
    var bc = bruteCalls(n);
    var dpSteps = n + 1;
    var bn = $('#cmp-brute-num'); if (bn) bn.innerHTML = bc + ' <small>tries</small>';
    var dn = $('#cmp-dp-num'); if (dn) dn.innerHTML = dpSteps + ' <small>steps</small>';
    var bb = $('#cmp-brute-bar'); if (bb) bb.style.width = '100%';
    var db = $('#cmp-dp-bar'); if (db) db.style.width = Math.max(4, Math.min(100, (dpSteps / bc) * 100)) + '%';
  }

  /* ===== INIT ===== */
  buildStairs();
  renderTree();
  resetMemo();
  renderTab();
  renderSpace();
  updateCompare();
})();
