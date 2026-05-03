/* =========================================================
   DP Adventure — Shared JavaScript helpers
   No frameworks. Vanilla ES5/ES6, GitHub-Pages friendly.
   ========================================================= */

(function () {
  'use strict';

  /* ---------------- Toggle sections ----------------
     Use: <button data-toggle="#myId">Toggle</button>
  */
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-toggle]');
    if (!t) return;
    var sel = t.getAttribute('data-toggle');
    var node = document.querySelector(sel);
    if (!node) return;
    node.classList.toggle('hidden');
  });

  /* ---------------- Step-by-step reveal ----------------
     Each container [data-stepper] holds .dryrun-step children.
     Buttons inside: [data-step="prev|next|reset|all"].
  */
  function initStepper(container) {
    var steps = container.querySelectorAll('.dryrun-step');
    var idx = 0;

    function render() {
      steps.forEach(function (s, i) {
        s.classList.toggle('hidden', i > idx);
        s.classList.toggle('current', i === idx);
      });
      var pct = steps.length > 1 ? Math.round((idx / (steps.length - 1)) * 100) : 100;
      var bar = container.querySelector('.progress > span');
      if (bar) bar.style.width = pct + '%';
      var label = container.querySelector('.stepper .label');
      if (label) label.textContent = 'Step ' + (idx + 1) + ' / ' + steps.length;
    }

    container.addEventListener('click', function (e) {
      var b = e.target.closest('[data-step]');
      if (!b) return;
      var act = b.getAttribute('data-step');
      if (act === 'next') idx = Math.min(steps.length - 1, idx + 1);
      else if (act === 'prev') idx = Math.max(0, idx - 1);
      else if (act === 'reset') idx = 0;
      else if (act === 'all') idx = steps.length - 1;
      render();
    });

    render();
  }

  document.querySelectorAll('[data-stepper]').forEach(initStepper);

  /* ---------------- Visual highlights ----------------
     Stairs / coins / grids: clicking a cell toggles .active on it.
  */
  document.querySelectorAll('.viz').forEach(function (viz) {
    viz.addEventListener('click', function (e) {
      var item = e.target.closest('.step,.coin,.cell,.node');
      if (!item) return;
      item.classList.toggle('active');
      if (item.classList.contains('node')) item.classList.toggle('cached');
    });
  });

  /* ---------------- Confetti-like sparkle on Mini Challenge ----------- */
  document.querySelectorAll('[data-celebrate]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.textContent = '🎉 Yay! Try the next level!';
      btn.disabled = true;
      btn.style.background = 'linear-gradient(135deg,#36c39c,#7c5cff)';
    });
  });

  /* ---------------- Smooth scroll for in-page links ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href');
    if (id.length < 2) return;
    var target = document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* ---------------- Mark visited levels (localStorage) ---------- */
  try {
    var path = location.pathname.split('/').pop();
    if (path && path.indexOf('level-') === 0) {
      var visited = JSON.parse(localStorage.getItem('dp_visited') || '{}');
      visited[path] = Date.now();
      localStorage.setItem('dp_visited', JSON.stringify(visited));
    }
    // On the roadmap, add a small green dot for visited
    document.querySelectorAll('.level-card[data-href]').forEach(function (card) {
      var v = JSON.parse(localStorage.getItem('dp_visited') || '{}');
      var name = card.getAttribute('data-href').split('/').pop();
      if (v[name]) {
        var dot = document.createElement('span');
        dot.textContent = '✓';
        dot.style.cssText = 'position:absolute;top:8px;right:10px;color:#36c39c;font-weight:900;';
        card.appendChild(dot);
      }
    });
  } catch (err) { /* localStorage may be blocked */ }
})();
