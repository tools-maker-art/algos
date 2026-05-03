/* DP Adventure - universal interactive runtime for generated levels. */
(function () {
  'use strict';

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(x) {
    return String(x == null ? '' : x)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  var dataEl = document.getElementById('level-data');
  if (!dataEl) return;

  var L;
  try {
    L = JSON.parse(dataEl.textContent);
  } catch (e) {
    console.error('bad level data', e);
    return;
  }

  function mountViz(host) {
    var v = L.viz || {};
    var kind = v.kind || 'items';
    var label = v.label || 'play with the tiny problem';
    var mission = {
      bars: 'Move across the steps. Tap blocks to mark the path you would try.',
      row: 'Tap cards to choose or skip. This is the little decision DP remembers.',
      coins: 'Tap treasure cards to choose or skip. Watch the score grow.',
      grid: 'Tap cells to draw a path. DP counts paths without walking them all.',
      string: 'Tap letters to build a prefix. DP remembers which prefixes work.',
      strings: 'Tap matching letters. String DP is a matching game.',
      stick: 'Tap cut marks to split the stick. Interval DP tries cut orders.',
      balloons: 'Tap balloons to pop them. Interval DP chooses the best last pop.'
    }[kind] || 'Tap pieces, then run the demo. This turns the recurrence into a small game.';

    function renderPieces() {
      if (kind === 'grid') {
        var rows = v.rows || 3;
        var cols = v.cols || 3;
        var blocks = v.blocks || [];
        var cells = '';
        for (var r = 0; r < rows; r++) {
          for (var c = 0; c < cols; c++) {
            var blocked = blocks.some(function (b) { return b[0] === r && b[1] === c; });
            var cls = 'game-cell' + (blocked ? ' blocked' : '') + (r === 0 && c === 0 ? ' start' : '') + (r === rows - 1 && c === cols - 1 ? ' end' : '');
            var txt = blocked ? 'rock' : (r === 0 && c === 0 ? 'START' : (r === rows - 1 && c === cols - 1 ? 'GOAL' : (v.values ? v.values[r * cols + c] : '')));
            cells += '<button type="button" class="' + cls + '" data-game-piece="' + (r * cols + c) + '"' + (blocked ? ' disabled' : '') + '>' + esc(txt) + '</button>';
          }
        }
        return '<div class="game-grid" style="grid-template-columns:repeat(' + cols + ',1fr)">' + cells + '</div>';
      }

      if (kind === 'string') {
        return '<div class="letter-track">' + String(v.s || '').split('').map(function (ch, i) {
          return '<button type="button" class="letter-tile" data-game-piece="' + i + '">' + esc(ch) + '</button>';
        }).join('') + '</div>';
      }

      if (kind === 'strings') {
        return '<div class="string-match"><div>' + String(v.a || '').split('').map(function (ch, i) {
          return '<button type="button" class="letter-tile" data-game-piece="' + i + '">A:' + esc(ch) + '</button>';
        }).join('') + '</div><div>' + String(v.b || '').split('').map(function (ch, i) {
          return '<button type="button" class="letter-tile alt" data-game-piece="' + (100 + i) + '">B:' + esc(ch) + '</button>';
        }).join('') + '</div></div>';
      }

      if (kind === 'stick') {
        var parts = [];
        for (var i = 0; i < (v.length || 5); i++) parts.push(i + 1);
        return '<div class="stick-track">' + parts.map(function (x, i) {
          return '<button type="button" class="stick-piece" data-game-piece="' + i + '">' + esc(x) + '</button>';
        }).join('') + '</div>';
      }

      var items = v.items || [1, 2, 3, 4];
      var max = Math.max.apply(null, items.map(function (x) { return Number(x) || 1; }));
      var cls = kind === 'bars' ? 'step-card' : (kind === 'balloons' ? 'balloon-card' : 'loot-card');
      return '<div class="game-track">' + items.map(function (x, i) {
        var style = kind === 'bars' ? ' style="--piece-h:' + (36 + Math.round(82 * (Number(x) || 1) / max)) + 'px"' : '';
        var prefix = kind === 'balloons' ? 'pop ' : '';
        return '<button type="button" class="' + cls + '" data-game-piece="' + i + '"' + style + '>' + prefix + esc(x) + '</button>';
      }).join('') + '</div>';
    }

    host.classList.add('game-viz');
    host.innerHTML =
      '<div class="game-card">' +
        '<div class="game-copy">' +
          '<span class="game-badge">mini game</span>' +
          '<h3>' + esc(label) + '</h3>' +
          '<p>' + esc(mission) + '</p>' +
          '<div class="game-controls">' +
            '<button type="button" class="btn small" data-game-run>Run demo</button>' +
            '<button type="button" class="btn ghost small" data-game-reset>Reset</button>' +
            '<span class="game-score" aria-live="polite">Score 0</span>' +
          '</div>' +
        '</div>' +
        '<div class="game-playfield">' +
          '<div class="game-hero" aria-hidden="true"></div>' +
          renderPieces() +
        '</div>' +
      '</div>';

    var pieces = $$('[data-game-piece]', host);
    var scoreEl = $('.game-score', host);
    function setScore() {
      if (scoreEl) scoreEl.textContent = 'Score ' + $$('.active', host).length;
    }
    function reset() {
      pieces.forEach(function (p) { p.classList.remove('active', 'demo'); });
      setScore();
    }
    pieces.forEach(function (piece) {
      piece.addEventListener('click', function () {
        piece.classList.toggle('active');
        setScore();
      });
    });
    var resetBtn = $('[data-game-reset]', host);
    if (resetBtn) resetBtn.addEventListener('click', reset);
    var runBtn = $('[data-game-run]', host);
    if (runBtn) {
      runBtn.addEventListener('click', function () {
        reset();
        pieces.filter(function (p) { return !p.disabled; }).slice(0, Math.min(6, pieces.length)).forEach(function (piece, i) {
          window.setTimeout(function () {
            piece.classList.add('demo', 'active');
            setScore();
          }, i * 260);
        });
      });
    }
  }

  function mountTree(host) {
    var t = L.tree;
    if (!t) {
      host.innerHTML = '<p class="muted center">The recurrence above is the tiny choice tree for this level.</p>';
      return;
    }
    var revealed = 1;
    var maxDepth = t.maxDepth || 4;
    var nodes = t.nodes || [];

    function render() {
      var visible = nodes.filter(function (n) { return n.d <= revealed; });
      var byDepth = {};
      visible.forEach(function (n) { (byDepth[n.d] = byDepth[n.d] || []).push(n); });
      var depths = Object.keys(byDepth).map(Number).sort(function (a, b) { return a - b; });
      var deepest = byDepth[depths[depths.length - 1]] || [];
      var nodeW = 86;
      var rowH = 70;
      var padX = 14;
      var width = Math.max(360, padX * 2 + deepest.length * (nodeW + 8));
      var height = depths.length * rowH + 20;
      var xs = {};
      if (deepest.length === 1) xs[deepest[0].id] = width / 2;
      else deepest.forEach(function (n, i) { xs[n.id] = padX + nodeW / 2 + i * ((width - padX * 2 - nodeW) / (deepest.length - 1)); });

      var childMap = {};
      visible.forEach(function (n) { if (n.p != null) (childMap[n.p] = childMap[n.p] || []).push(n.id); });
      for (var di = depths.length - 2; di >= 0; di--) {
        (byDepth[depths[di]] || []).forEach(function (n) {
          var kids = childMap[n.id] || [];
          if (kids.length) {
            var sum = 0;
            kids.forEach(function (k) { sum += xs[k]; });
            xs[n.id] = sum / kids.length;
          } else {
            xs[n.id] = width / 2;
          }
        });
      }

      var svg = '<svg class="tree" width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + ' ' + height + '">';
      visible.forEach(function (n) {
        if (n.p == null) return;
        var parent = visible.find(function (q) { return q.id === n.p; });
        if (!parent) return;
        svg += '<line x1="' + xs[parent.id] + '" y1="' + (parent.d * rowH + 51) + '" x2="' + xs[n.id] + '" y2="' + (n.d * rowH + 15) + '" class="edge' + (n.dup ? ' dim' : '') + '"/>';
      });
      visible.forEach(function (n) {
        var x = xs[n.id];
        var y = n.d * rowH + 15;
        var cls = 'node-bg' + (n.dup ? ' dup' : '') + (n.base ? ' base' : '');
        svg += '<rect x="' + (x - nodeW / 2) + '" y="' + y + '" width="' + nodeW + '" height="36" rx="10" class="' + cls + '"/>';
        svg += '<text x="' + x + '" y="' + (y + 22) + '" class="' + (n.dup ? 'dup' : (n.base ? 'base' : '')) + '">' + esc(n.lbl) + '</text>';
      });
      svg += '</svg>';
      host.innerHTML = svg;
      var calls = $('#tree-calls');
      if (calls) calls.textContent = visible.length;
      var dups = $('#tree-dups');
      if (dups) dups.textContent = visible.filter(function (n) { return n.dup; }).length;
    }

    render();
    var scope = host.closest('.scene') || host.parentElement;
    var expand = scope.querySelector('[data-tree="expand"]');
    if (expand) expand.addEventListener('click', function () { revealed = Math.min(maxDepth, revealed + 1); render(); });
    var all = scope.querySelector('[data-tree="all"]');
    if (all) all.addEventListener('click', function () { revealed = maxDepth; render(); });
    var reset = scope.querySelector('[data-tree="reset"]');
    if (reset) reset.addEventListener('click', function () { revealed = 1; render(); });
  }

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
        slot.innerHTML = '<div class="k">' + esc(e.k) + '</div><div class="v">= ' + esc(e.v) + '</div>';
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
        c.innerHTML = '<span class="idx">' + esc(lbl) + '</span>' + (k <= i ? esc(v) : '?');
        host.appendChild(c);
      });
      var f = $('#tab-formula');
      if (f) {
        if (i < 0) f.innerHTML = 'Click <b>Next</b> to fill the next box.';
        else if (t.formulas && t.formulas[i]) f.innerHTML = t.formulas[i];
        else f.innerHTML = '<b>' + esc(t.labels ? t.labels[i] : 'dp[' + i + ']') + '</b> = <b>' + esc(t.values[i]) + '</b>';
      }
      var lbl = $('#tab-step-lbl'); if (lbl) lbl.textContent = (i >= 0 ? i + 1 : 0) + ' / ' + t.values.length;
    }
    render();
    var scope = host.closest('.scene');
    scope.querySelector('[data-tab="next"]').addEventListener('click', function () { i = Math.min(t.values.length - 1, i + 1); render(); });
    scope.querySelector('[data-tab="all"]').addEventListener('click', function () { i = t.values.length - 1; render(); });
    scope.querySelector('[data-tab="reset"]').addEventListener('click', function () { i = -1; render(); });
  }

  function mountSpace(host) {
    var s = L.space;
    if (!s || !s.frames) {
      host.innerHTML = '<p class="muted center">This level needs the table, so there is no smaller space trick yet.</p>';
      return;
    }
    var i = 0;
    var frames = s.frames;
    var labels = s.labels || ['prev', 'curr', 'next'];
    function render() {
      var frame = frames[i];
      var html = '<div class="space-stage">';
      frame.forEach(function (val, k) {
        var cls = 'space-box' + (k === frame.length - 1 ? ' curr' : '');
        html += '<div><div class="' + cls + '">' + esc(val) + '</div><div class="muted center" style="margin-top:6px;font-size:12px;font-weight:800;letter-spacing:.5px;text-transform:uppercase">' + esc(labels[k] || '') + '</div></div>';
        if (k < frame.length - 1) html += '<div class="arrow">+</div>';
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

  function mountCompare() {
    var c = L.compare;
    if (!c) return;
    var brute = $('#cmp-brute-num'); if (brute) brute.innerHTML = esc(c.brute) + ' <small>tries</small>';
    var dp = $('#cmp-dp-num'); if (dp) dp.innerHTML = esc(c.dp) + ' <small>steps</small>';
    var bar = $('#cmp-dp-bar'); if (bar) bar.style.width = Math.max(4, Math.min(100, c.dpRatio || 25)) + '%';
  }

  function mount() {
    var v = $('[data-viz]'); if (v) mountViz(v);
    var t = $('[data-tree]'); if (t) mountTree(t);
    var m = $('.slots[data-memo]'); if (m) mountMemo(m);
    var tab = $('[data-tab]'); if (tab) mountTab(tab);
    var sp = $('[data-space]'); if (sp) mountSpace(sp);
    mountCompare();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
}());
