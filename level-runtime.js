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
    var story = {
      bars: 'The climber wants to reach the top. Try small jumps, then see every route.',
      row: 'The explorer walks past choices one by one. Pick or skip each spot.',
      coins: 'The collector walks along treasure piles. Pick some, skip others.',
      grid: 'The explorer starts at START and wants GOAL. Walk right or down.',
      string: 'The word builder moves across letters and tries prefixes.',
      strings: 'Two word builders look for matching letters.',
      stick: 'The cutter chooses cut marks and tries different orders.',
      balloons: 'The popper chooses balloons and tries different pop orders.'
    }[kind] || 'Move through the tiny puzzle and watch the choices become visible.';

    function buildWays() {
      var ways = [];
      if (kind === 'bars') {
        var n = (v.items || []).length;
        function hop(left, path) {
          if (left === 0) { ways.push(path.slice()); return; }
          if (left < 0 || ways.length >= 24) return;
          path.push('hop 1'); hop(left - 1, path); path.pop();
          path.push('hop 2'); hop(left - 2, path); path.pop();
        }
        hop(n, []);
      } else if (kind === 'grid') {
        var rows = v.rows || 3, cols = v.cols || 3, blocks = v.blocks || [];
        function blocked(r, c) { return blocks.some(function (b) { return b[0] === r && b[1] === c; }); }
        function walk(r, c, path) {
          if (r === rows - 1 && c === cols - 1) { ways.push(path.slice()); return; }
          if (ways.length >= 24) return;
          if (c + 1 < cols && !blocked(r, c + 1)) { path.push('right'); walk(r, c + 1, path); path.pop(); }
          if (r + 1 < rows && !blocked(r + 1, c)) { path.push('down'); walk(r + 1, c, path); path.pop(); }
        }
        walk(0, 0, []);
      } else if (kind === 'string') {
        String(v.s || '').split('').forEach(function (ch, i) {
          ways.push(['prefix ' + (i + 1), String(v.s || '').slice(0, i + 1)]);
        });
      } else if (kind === 'strings') {
        var a = String(v.a || ''), b = String(v.b || '');
        for (var i = 0; i < a.length; i++) {
          for (var j = 0; j < b.length; j++) {
            if (a[i] === b[j] && ways.length < 24) ways.push(['match ' + a[i], 'A' + i, 'B' + j]);
          }
        }
      } else if (kind === 'stick') {
        var length = v.length || 5;
        for (var cut = 1; cut < length && ways.length < 18; cut++) ways.push(['cut at ' + cut, 'left ' + cut, 'right ' + (length - cut)]);
      } else if (kind === 'balloons') {
        (v.items || []).slice(0, 6).forEach(function (x, i) {
          ways.push(['pop balloon ' + (i + 1), 'score x' + x]);
        });
      } else {
        var items = v.items || [1, 2, 3, 4];
        function choose(i, path) {
          if (i >= items.length) { ways.push(path.slice()); return; }
          if (ways.length >= 24) return;
          path.push('take ' + items[i]); choose(i + 1, path); path.pop();
          path.push('skip ' + items[i]); choose(i + 1, path); path.pop();
        }
        choose(0, []);
      }
      return ways.length ? ways : [['try choice A'], ['try choice B']];
    }

    function chip(text) {
      var cls = /2|down|skip|right|cut|pop/.test(String(text)) ? 'way-chip alt' : 'way-chip';
      return '<span class="' + cls + '">' + esc(text) + '</span>';
    }

    function renderWays(ways) {
      return ways.map(function (way, i) {
        return '<div class="way-row"><span class="way-idx">' + (i + 1) + '.</span>' + way.map(chip).join('') + '</div>';
      }).join('');
    }

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
        return '<div class="game-grid journey-grid" style="grid-template-columns:repeat(' + cols + ',1fr)">' + cells + '</div>';
      }

      if (kind === 'string') {
        return '<div class="letter-track journey-track">' + String(v.s || '').split('').map(function (ch, i) {
          return '<button type="button" class="letter-tile" data-game-piece="' + i + '">' + esc(ch) + '</button>';
        }).join('') + '</div>';
      }

      if (kind === 'strings') {
        return '<div class="string-match journey-track"><div>' + String(v.a || '').split('').map(function (ch, i) {
          return '<button type="button" class="letter-tile" data-game-piece="' + i + '">A:' + esc(ch) + '</button>';
        }).join('') + '</div><div>' + String(v.b || '').split('').map(function (ch, i) {
          return '<button type="button" class="letter-tile alt" data-game-piece="' + (100 + i) + '">B:' + esc(ch) + '</button>';
        }).join('') + '</div></div>';
      }

      if (kind === 'stick') {
        var parts = [];
        for (var i = 0; i < (v.length || 5); i++) parts.push(i + 1);
        return '<div class="stick-track journey-track">' + parts.map(function (x, i) {
          return '<button type="button" class="stick-piece" data-game-piece="' + i + '">' + esc(x) + '</button>';
        }).join('') + '</div>';
      }

      var items = v.items || [1, 2, 3, 4];
      var max = Math.max.apply(null, items.map(function (x) { return Number(x) || 1; }));
      var cls = kind === 'bars' ? 'step-card' : (kind === 'balloons' ? 'balloon-card' : 'loot-card');
      return '<div class="game-track journey-track">' + items.map(function (x, i) {
        var style = kind === 'bars' ? ' style="--piece-h:' + (36 + Math.round(82 * (Number(x) || 1) / max)) + 'px"' : '';
        var prefix = kind === 'balloons' ? 'pop ' : '';
        return '<button type="button" class="' + cls + '" data-game-piece="' + i + '"' + style + '>' + prefix + esc(x) + '</button>';
      }).join('') + '</div>';
    }

    var ways = buildWays();
    host.classList.add('game-viz');
    host.innerHTML =
      '<div class="journey-card">' +
        '<div class="journey-head">' +
          '<span class="game-badge">story game</span>' +
          '<h3>' + esc(label) + '</h3>' +
          '<p>' + esc(story) + '</p>' +
          '<div class="game-controls">' +
            '<button type="button" class="btn small" data-game-run>Show one try</button>' +
            '<button type="button" class="btn ghost small" data-game-reset>Back to start</button>' +
            '<span class="game-score" aria-live="polite">0 choices tried</span>' +
          '</div>' +
        '</div>' +
        '<div class="journey-stage">' +
          '<div class="game-hero journey-hero" aria-hidden="true"></div>' +
          renderPieces() +
        '</div>' +
        '<details class="ways-panel">' +
          '<summary>show me all ' + ways.length + ' ways to try it</summary>' +
          '<p>' + esc(missionForWays(kind)) + '</p>' +
          '<div class="ways-list">' + renderWays(ways) + '</div>' +
        '</details>' +
      '</div>';

    var pieces = $$('[data-game-piece]', host);
    var scoreEl = $('.game-score', host);
    var hero = $('.journey-hero', host);
    function setScore() {
      if (scoreEl) scoreEl.textContent = $$('.active', host).length + ' choices tried';
    }
    function moveHeroTo(piece) {
      if (!hero || !piece) return;
      var stage = $('.journey-stage', host).getBoundingClientRect();
      var box = piece.getBoundingClientRect();
      hero.style.left = (box.left - stage.left + box.width / 2 - 17) + 'px';
      hero.style.top = (box.top - stage.top - 36) + 'px';
      hero.style.bottom = 'auto';
    }
    function reset() {
      pieces.forEach(function (p) { p.classList.remove('active', 'demo'); });
      if (hero) {
        hero.style.left = '18px';
        hero.style.top = 'auto';
        hero.style.bottom = '42px';
      }
      setScore();
    }
    pieces.forEach(function (piece) {
      piece.addEventListener('click', function () {
        piece.classList.toggle('active');
        moveHeroTo(piece);
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
            moveHeroTo(piece);
            setScore();
          }, i * 260);
        });
      });
    }
  }

  function missionForWays(kind) {
    return {
      bars: 'Each row is one route made from 1-step and 2-step hops.',
      grid: 'Each row is one route from START to GOAL.',
      row: 'Each row is one take-or-skip plan.',
      coins: 'Each row is one treasure plan.',
      string: 'Each row is one prefix the word builder can test.',
      strings: 'Each row is one possible letter match.',
      stick: 'Each row is one cut choice to try first.',
      balloons: 'Each row is one pop choice to try.'
    }[kind] || 'Each row is one possible way to try the tiny puzzle.';
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
      var skipped = $('#memo-skipped');
      if (skipped) {
        var cmp = L.compare;
        var totalSaved = (cmp && cmp.brute && cmp.dp) ? Math.max(0, cmp.brute - cmp.dp) : 0;
        skipped.textContent = (i >= 0 && totalSaved)
          ? Math.round((i + 1) / m.entries.length * totalSaved)
          : Math.max(0, i);
      }
      var lbl = $('#memo-step-lbl'); if (lbl) lbl.textContent = (i + 1) + ' / ' + m.entries.length;
    }
    render();
    var scope = host.closest('.scene');
    if (!scope) return;
    var nBtn = scope.querySelector('[data-memo="next"]');
    var aBtn = scope.querySelector('[data-memo="all"]');
    var rBtn = scope.querySelector('[data-memo="reset"]');
    if (nBtn) nBtn.addEventListener('click', function () { i = Math.min(m.entries.length - 1, i + 1); render(); });
    if (aBtn) aBtn.addEventListener('click', function () { i = m.entries.length - 1; render(); });
    if (rBtn) rBtn.addEventListener('click', function () { i = -1; render(); });
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
    if (!scope) return;
    var nBtn = scope.querySelector('[data-tab="next"]');
    var aBtn = scope.querySelector('[data-tab="all"]');
    var rBtn = scope.querySelector('[data-tab="reset"]');
    if (nBtn) nBtn.addEventListener('click', function () { i = Math.min(t.values.length - 1, i + 1); render(); });
    if (aBtn) aBtn.addEventListener('click', function () { i = t.values.length - 1; render(); });
    if (rBtn) rBtn.addEventListener('click', function () { i = -1; render(); });
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
    if (!scope) return;
    var nBtn = scope.querySelector('[data-space="next"]');
    var aBtn = scope.querySelector('[data-space="all"]');
    var rBtn = scope.querySelector('[data-space="reset"]');
    if (nBtn) nBtn.addEventListener('click', function () { i = Math.min(frames.length - 1, i + 1); render(); });
    if (aBtn) aBtn.addEventListener('click', function () { i = frames.length - 1; render(); });
    if (rBtn) rBtn.addEventListener('click', function () { i = 0; render(); });
  }

  function mountCompare() {
    var c = L.compare;
    if (!c) return;
    var brute = $('#cmp-brute-num'); if (brute) brute.innerHTML = esc(c.brute) + ' <small>tries</small>';
    var dp = $('#cmp-dp-num'); if (dp) dp.innerHTML = esc(c.dp) + ' <small>steps</small>';
    var bar = $('#cmp-dp-bar'); if (bar) bar.style.width = Math.max(4, Math.min(100, c.dpRatio || 25)) + '%';
  }

  function makeLevelFile(num) {
    var files = {
      1: 'level-01-fibonacci.html', 2: 'level-02-climbing-stairs.html',
      3: 'level-03-frog-jump.html', 4: 'level-04-frog-jump-k.html',
      5: 'level-05-non-adjacent-sum.html', 6: 'level-06-house-robber.html',
      7: 'level-07-house-robber-2.html', 8: 'level-08-unique-paths.html',
      9: 'level-09-unique-paths-2.html', 10: 'level-10-min-path-sum.html',
      11: 'level-11-triangle.html', 12: 'level-12-falling-path-sum.html',
      13: 'level-13-cherry-pickup.html', 14: 'level-14-subset-sum.html',
      15: 'level-15-partition-equal-subset.html', 16: 'level-16-count-subsets-sum-k.html',
      17: 'level-17-min-subset-diff.html', 18: 'level-18-target-sum.html',
      19: 'level-19-01-knapsack.html', 20: 'level-20-unbounded-knapsack.html',
      21: 'level-21-coin-change-min.html', 22: 'level-22-coin-change-2.html',
      23: 'level-23-rod-cutting.html', 24: 'level-24-lcs.html',
      25: 'level-25-print-lcs.html', 26: 'level-26-longest-common-substring.html',
      27: 'level-27-scs.html', 28: 'level-28-min-insertions-palindrome.html',
      29: 'level-29-min-deletions-equal.html', 30: 'level-30-edit-distance.html',
      31: 'level-31-wildcard-matching.html', 32: 'level-32-distinct-subsequences.html',
      33: 'level-33-lis-n2.html', 34: 'level-34-lis-bsearch.html',
      35: 'level-35-number-of-lis.html', 36: 'level-36-bitonic.html',
      37: 'level-37-largest-divisible-subset.html', 38: 'level-38-longest-string-chain.html',
      39: 'level-39-stock-1.html', 40: 'level-40-stock-2.html',
      41: 'level-41-stock-3.html', 42: 'level-42-stock-4.html',
      43: 'level-43-stock-cooldown.html', 44: 'level-44-stock-fee.html',
      45: 'level-45-mcm.html', 46: 'level-46-cut-stick.html',
      47: 'level-47-burst-balloons.html', 48: 'level-48-palindrome-partition-2.html',
      49: 'level-49-partition-max-sum.html', 50: 'level-50-largest-rect-histogram.html',
      51: 'level-51-maximum-rectangle.html', 52: 'level-52-word-break.html',
      53: 'level-53-word-break-2.html'
    };
    return files[num] || '';
  }

  function addContractNav() {
    var nav = $('.topbar nav');
    if (!nav) return;
    var title = $('.level-top h1');
    var match = title && title.textContent.match(/Level\s+(\d+)/i);
    var n = match ? Number(match[1]) : 0;
    var prev = n > 1 ? makeLevelFile(n - 1) : '../dp-roadmap.html';
    var next = n < 53 ? makeLevelFile(n + 1) : '../dp-roadmap.html';
    nav.innerHTML =
      '<a href="../dp-roadmap.html">Map</a>' +
      '<a href="' + esc(prev) + '">&#8592; Prev</a>' +
      '<span class="level-pill">Level ' + esc(n || '?') + '</span>' +
      '<a href="' + esc(next) + '">Next &#8594;</a>';
  }

  function addContractTabs() {
    var main = $('.container-narrow');
    if (!main || $('.contract-tabs')) return;
    var scenes = $$('.scene', main).slice(0, 6);
    if (scenes.length < 6) return;
    var labels = [
      ['01', '&#128214;', 'The Story'],
      ['02', '&#127795;', 'Brute Force'],
      ['03', '&#127890;', 'Memoization'],
      ['04', '&#129521;', 'Tabulation'],
      ['05', '&#129718;', 'Space Saver'],
      ['06', '&#9889;', 'Before vs After']
    ];
    var tabbar = document.createElement('div');
    tabbar.className = 'contract-tabs lesson-steps';
    tabbar.setAttribute('role', 'tablist');
    tabbar.setAttribute('aria-label', 'Level stages');
    tabbar.innerHTML = labels.map(function (x, i) {
      return '<button class="lesson-step' + (i === 0 ? ' active' : '') + '" type="button" role="tab" aria-selected="' + (i === 0 ? 'true' : 'false') + '" data-contract-tab="' + i + '">' +
        '<span class="step-bubble">' + x[0] + '</span><span class="step-icon">' + x[1] + '</span><span><b>' + x[2] + '</b><small>Step-by-step</small></span></button>';
    }).join('');
    main.insertBefore(tabbar, scenes[0]);
    scenes.forEach(function (scene, i) {
      scene.classList.add('contract-panel');
      scene.setAttribute('role', 'tabpanel');
      if (i > 0) scene.hidden = true;
    });
    $$('[data-contract-tab]', tabbar).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var idx = Number(btn.getAttribute('data-contract-tab'));
        $$('[data-contract-tab]', tabbar).forEach(function (b, j) {
          b.classList.toggle('active', j === idx);
          b.setAttribute('aria-selected', j === idx ? 'true' : 'false');
        });
        scenes.forEach(function (scene, j) { scene.hidden = j !== idx; });
      });
    });
  }

  function addWhyLines() {
    var lines = [
      'Why this matters: the concrete moves make the recurrence feel like the story, not a formula.',
      'Why this matters: brute force is honest, but it exposes repeated questions.',
      'Why this matters: memoization keeps the same story and skips wasted work.',
      'Why this matters: tabulation turns recursion into a predictable left-to-right build.',
      'Why this matters: the space saver keeps only the values the next step can actually use.',
      'Why this matters: the counter shows why the DP version scales.'
    ];
    $$('.scene').slice(0, 6).forEach(function (scene, i) {
      if ($('.why-line', scene)) return;
      var p = document.createElement('p');
      p.className = 'why-line';
      p.textContent = lines[i];
      scene.appendChild(p);
    });
  }

  function labelStepCounters() {
    var treeScene = $('[data-tree]') && $('[data-tree]').closest('.scene');
    if (treeScene && !$('#tree-step-lbl')) {
      var p = document.createElement('p');
      p.className = 'muted center contract-step-count';
      p.innerHTML = 'Step <span id="tree-step-lbl">1 / ' + esc(((L.tree && L.tree.maxDepth) || 4) + 1) + '</span>';
      var row = $('.btn-row', treeScene);
      if (row) row.insertAdjacentElement('afterend', p);
    }
    function syncTreeLabel() {
      var lbl = $('#tree-step-lbl');
      if (!lbl || !L.tree) return;
      var visible = $$('svg.tree .node-bg').length;
      var total = (L.tree.nodes || []).length || visible;
      lbl.textContent = visible + ' / ' + total;
    }
    $$('[data-tree="expand"],[data-tree="all"],[data-tree="reset"]').forEach(function (b) {
      b.addEventListener('click', function () { window.setTimeout(syncTreeLabel, 0); });
    });
    syncTreeLabel();
  }

  function addAutoControls() {
    var configs = [
      { scene: $('[data-tree]') && $('[data-tree]').closest('.scene'), step: '[data-tree="expand"]', reset: '[data-tree="reset"]' },
      { scene: $('.slots[data-memo]') && $('.slots[data-memo]').closest('.scene'), step: '[data-memo="next"]', reset: '[data-memo="reset"]' },
      { scene: $('[data-tab]') && $('[data-tab]').closest('.scene'), step: '[data-tab="next"]', reset: '[data-tab="reset"]' },
      { scene: $('[data-space]') && $('[data-space]').closest('.scene'), step: '[data-space="next"]', reset: '[data-space="reset"]' }
    ];
    configs.forEach(function (cfg) {
      if (!cfg.scene || cfg.scene.querySelector('[data-contract-auto]')) return;
      var row = $('.btn-row', cfg.scene);
      var step = cfg.scene.querySelector(cfg.step);
      var reset = cfg.scene.querySelector(cfg.reset);
      if (!row || !step || !reset) return;
      step.textContent = '\u25b6 Step';
      reset.textContent = '\u21ba Reset';
      var fill = row.querySelector('[data-tree="all"],[data-memo="all"],[data-tab="all"],[data-space="all"]');
      if (fill) fill.style.display = 'none';
      var auto = document.createElement('button');
      auto.type = 'button';
      auto.className = 'btn ghost';
      auto.setAttribute('data-contract-auto', '');
      auto.textContent = '\u23e9 Auto';
      row.insertBefore(auto, reset);
      var timer = null;
      function stop(done) {
        if (timer) window.clearInterval(timer);
        timer = null;
        auto.textContent = done ? '\u2705 Done' : '\u23e9 Auto';
      }
      reset.addEventListener('click', function () { stop(false); });
      auto.addEventListener('click', function () {
        if (timer) { stop(false); return; }
        auto.textContent = '\u23f8 Pause';
        timer = window.setInterval(function () {
          var before = cfg.scene.textContent;
          step.click();
          window.setTimeout(function () {
            var after = cfg.scene.textContent;
            if (before === after) stop(true);
          }, 0);
        }, 600);
      });
    });
  }

  function addCompareSlider() {
    var scene = $('#cmp-brute-num') && $('#cmp-brute-num').closest('.scene');
    if (!scene || scene.querySelector('[data-compare-slider]')) return;
    var c = L.compare || {};
    var wrap = document.createElement('div');
    wrap.className = 'compare-slider';
    wrap.innerHTML =
      '<label>n grows: <span data-compare-n>1</span></label>' +
      '<input data-compare-slider type="range" min="1" max="12" value="1">' +
      '<div class="complexity-row"><span class="bad">O(2^n)</span><span class="good">O(n)</span></div>';
    scene.insertBefore(wrap, $('.compare', scene));
    var slider = $('[data-compare-slider]', wrap);
    var nLbl = $('[data-compare-n]', wrap);
    var brute = $('#cmp-brute-num');
    var dp = $('#cmp-dp-num');
    slider.addEventListener('input', function () {
      var n = Number(slider.value);
      nLbl.textContent = n;
      if (brute) brute.innerHTML = esc(Math.min(999999, Math.pow(2, n) - 1)) + ' <small>calls</small>';
      if (dp) dp.innerHTML = esc(n + 1) + ' <small>DP steps</small>';
    });
    if (c.brute && brute) brute.innerHTML = esc(c.brute) + ' <small>calls</small>';
    if (c.dp && dp) dp.innerHTML = esc(c.dp) + ' <small>DP steps</small>';
  }

  function mount() {
    addContractNav();
    addContractTabs();
    var v = $('[data-viz]'); if (v) mountViz(v);
    var t = $('[data-tree]'); if (t) mountTree(t);
    var m = $('.slots[data-memo]'); if (m) mountMemo(m);
    var tab = $('[data-tab]'); if (tab) mountTab(tab);
    var sp = $('[data-space]'); if (sp) mountSpace(sp);
    mountCompare();
    labelStepCounters();
    addAutoControls();
    addCompareSlider();
    addWhyLines();

    // Inject keyboard hint into each interactive scene's btn-row
    $$('[data-tree="expand"],[data-memo="next"],[data-tab="next"],[data-space="next"]').forEach(function (btn) {
      var row = btn.closest('.btn-row');
      if (row && !row.querySelector('.kbd-hint')) {
        var hint = document.createElement('span');
        hint.className = 'kbd-hint';
        hint.setAttribute('aria-hidden', 'true');
        hint.innerHTML = '<kbd>&#8592;</kbd><kbd>&#8594;</kbd>';
        row.appendChild(hint);
      }
    });

    // Keyboard shortcuts: → next/expand, ← reset, End = fill all (active when focus is inside a scene)
    document.addEventListener('keydown', function (e) {
      var el = document.activeElement;
      if (!el || el === document.body || !el.closest) return;
      var scene = el.closest('.scene');
      if (!scene) return;
      if (e.key === 'ArrowRight') {
        var btn = scene.querySelector('[data-tree="expand"],[data-memo="next"],[data-tab="next"],[data-space="next"]');
        if (btn) { e.preventDefault(); btn.click(); }
      } else if (e.key === 'ArrowLeft') {
        var rst = scene.querySelector('[data-tree="reset"],[data-memo="reset"],[data-tab="reset"],[data-space="reset"]');
        if (rst) { e.preventDefault(); rst.click(); }
      } else if (e.key === 'End') {
        var all = scene.querySelector('[data-tree="all"],[data-memo="all"],[data-tab="all"],[data-space="all"]');
        if (all) { e.preventDefault(); all.click(); }
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
}());
