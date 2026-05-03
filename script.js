(function () {
  "use strict";

  var scene = 0;
  var stairs = 5;
  var timers = [];

  var copy = [
    {
      kicker: "Scene 1 of 4",
      title: "Try every path",
      text: "Pick a stair count. Then let the computer try every 1-step and 2-step choice. This is brute force: simple, but it grows fast.",
      label: "Brute force",
      badge: "Try everything",
      button: "Run brute force"
    },
    {
      kicker: "Scene 2 of 4",
      title: "The repeats are the problem",
      text: "The red bubbles are questions we already asked. Brute force forgets, so it keeps paying for the same answer.",
      label: "Repeated work",
      badge: "Same question again",
      button: "Highlight repeats"
    },
    {
      kicker: "Scene 3 of 4",
      title: "Remember tiny answers",
      text: "Dynamic Programming means: solve a small question once, save it, and reuse it when the same question comes back.",
      label: "Memory table",
      badge: "Save and reuse",
      button: "Use memory"
    },
    {
      kicker: "Scene 4 of 4",
      title: "Keep only what you need",
      text: "For this stair game, the next answer only needs the last two answers. Less memory means less space.",
      label: "Space saver",
      badge: "Two boxes",
      button: "Save space"
    }
  ];

  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function clearTimers() {
    timers.forEach(function (timer) {
      window.clearTimeout(timer);
    });
    timers = [];
  }

  function wait(fn, delay) {
    timers.push(window.setTimeout(fn, delay));
  }

  function ways(n) {
    var a = 1;
    var b = 1;
    for (var i = 2; i <= n; i += 1) {
      var next = a + b;
      a = b;
      b = next;
    }
    return b;
  }

  function bruteCalls(n) {
    if (n <= 1) return 1;
    return 1 + bruteCalls(n - 1) + bruteCalls(n - 2);
  }

  function buildStairs() {
    var board = $("#stairs-board");
    if (!board) return;

    board.innerHTML = "";
    for (var i = 1; i <= stairs; i += 1) {
      var stair = document.createElement("span");
      stair.className = "stair";
      stair.dataset.step = i;
      stair.style.setProperty("--h", 42 + i * 22 + "px");
      board.appendChild(stair);
    }

    var dot = document.createElement("div");
    dot.className = "dot";
    dot.id = "dot";
    board.appendChild(dot);

    var ribbon = document.createElement("div");
    ribbon.className = "path-ribbon";
    ribbon.id = "path-ribbon";
    ribbon.textContent = "Press run to watch choices appear.";
    board.appendChild(ribbon);

    updateDot(0);
  }

  function updateDot(step) {
    var board = $("#stairs-board");
    var dot = $("#dot");
    if (!board || !dot) return;

    var items = $$(".stair", board);
    if (!items.length) return;

    if (step <= 0) {
      dot.style.left = "18px";
      dot.style.bottom = "54px";
      return;
    }

    var target = items[Math.min(step, items.length) - 1];
    var boardBox = board.getBoundingClientRect();
    var targetBox = target.getBoundingClientRect();
    dot.style.left = targetBox.left - boardBox.left + targetBox.width / 2 - dot.offsetWidth / 2 + "px";
    dot.style.bottom = targetBox.height + 14 + "px";
  }

  function setRibbon(path) {
    var ribbon = $("#path-ribbon");
    if (!ribbon) return;

    ribbon.innerHTML = "";
    if (!path.length) {
      ribbon.textContent = "Try paths made from 1-hop and 2-hop moves.";
      return;
    }
    path.forEach(function (hop) {
      var chip = document.createElement("span");
      chip.textContent = hop;
      ribbon.appendChild(chip);
    });
  }

  function makeLevels(n) {
    var rows = [];
    var seen = Object.create(null);

    function visit(left, depth) {
      rows[depth] = rows[depth] || [];
      var repeated = seen[left] === true;
      rows[depth].push({ left: left, repeated: repeated });
      seen[left] = true;
      if (left > 1 && depth < 4) {
        visit(left - 1, depth + 1);
        visit(left - 2, depth + 1);
      }
    }

    visit(n, 0);
    return rows;
  }

  function renderTree(mode) {
    var tree = $("#choice-tree");
    if (!tree) return;

    tree.innerHTML = "";

    if (mode === "memory") {
      var intro = document.createElement("p");
      intro.textContent = "Saved answers";
      intro.style.fontWeight = "900";
      tree.appendChild(intro);

      var shelf = document.createElement("div");
      shelf.className = "memory-shelf";
      for (var i = 0; i <= stairs; i += 1) {
        var box = document.createElement("div");
        box.className = "memory-box";
        box.textContent = "step " + i + " = " + ways(i);
        shelf.appendChild(box);
      }
      tree.appendChild(shelf);
      return;
    }

    if (mode === "space") {
      var wrap = document.createElement("div");
      wrap.className = "space-demo";
      var a = document.createElement("div");
      var plus = document.createElement("div");
      var b = document.createElement("div");
      a.className = "space-box";
      b.className = "space-box";
      plus.className = "space-plus";
      a.textContent = "prev";
      b.textContent = "curr";
      plus.textContent = "+";
      wrap.appendChild(a);
      wrap.appendChild(plus);
      wrap.appendChild(b);
      tree.appendChild(wrap);
      return;
    }

    makeLevels(stairs).forEach(function (row, depth) {
      var rowEl = document.createElement("div");
      rowEl.className = "tree-row";
      row.slice(0, 12).forEach(function (item, index) {
        var node = document.createElement("span");
        node.className = "tree-node";
        node.textContent = "f(" + item.left + ")";
        node.style.animationDelay = depth * 80 + index * 18 + "ms";
        if (mode === "repeats" && item.repeated) node.classList.add("repeat");
        rowEl.appendChild(node);
      });
      tree.appendChild(rowEl);
    });
  }

  function animateBrute() {
    var paths = [];

    function walk(left, path) {
      if (left === 0) {
        paths.push(path.slice());
        return;
      }
      if (left < 0) return;
      path.push(1);
      walk(left - 1, path);
      path.pop();
      path.push(2);
      walk(left - 2, path);
      path.pop();
    }

    walk(stairs, []);
    updateDot(0);
    setRibbon([]);
    paths.slice(0, 8).forEach(function (path, pathIndex) {
      wait(function () {
        var total = 0;
        setRibbon(path);
        updateDot(0);
        path.forEach(function (hop, hopIndex) {
          wait(function () {
            total += hop;
            updateDot(total);
          }, hopIndex * 280);
        });
      }, pathIndex * 980);
    });
  }

  function animateMemory() {
    var values = [];
    for (var i = 0; i <= stairs; i += 1) values.push(ways(i));

    var tree = $("#choice-tree");
    if (!tree) return;
    tree.innerHTML = "";

    var label = document.createElement("p");
    label.textContent = "Filling the memory table, one answer at a time.";
    label.style.fontWeight = "900";
    tree.appendChild(label);

    var shelf = document.createElement("div");
    shelf.className = "memory-shelf";
    tree.appendChild(shelf);

    values.forEach(function (value, index) {
      wait(function () {
        var box = document.createElement("div");
        box.className = "memory-box";
        box.textContent = "step " + index + " = " + value;
        shelf.appendChild(box);
        updateDot(index);
      }, index * 360);
    });
  }

  function animateSpace() {
    var tree = $("#choice-tree");
    if (!tree) return;

    var prev = 1;
    var curr = 1;
    tree.innerHTML = "";
    var wrap = document.createElement("div");
    wrap.className = "space-demo";
    var left = document.createElement("div");
    var plus = document.createElement("div");
    var right = document.createElement("div");
    left.className = "space-box";
    right.className = "space-box";
    plus.className = "space-plus";
    plus.textContent = "+";
    wrap.appendChild(left);
    wrap.appendChild(plus);
    wrap.appendChild(right);
    tree.appendChild(wrap);

    function paint(step) {
      left.textContent = prev;
      right.textContent = curr;
      updateDot(step);
    }

    paint(1);
    for (var i = 2; i <= stairs; i += 1) {
      wait((function (step) {
        return function () {
          var next = prev + curr;
          prev = curr;
          curr = next;
          paint(step);
        };
      }(i)), i * 420);
    }
  }

  function updateStats() {
    var brute = bruteCalls(stairs);
    var memo = stairs + 1;
    var answer = ways(stairs);
    $("#brute-count").textContent = brute;
    $("#memo-count").textContent = memo;
    $("#answer-count").textContent = answer;
  }

  function paintScene() {
    var data = copy[scene];
    $("#lesson-kicker").textContent = data.kicker;
    $("#lesson-title").textContent = data.title;
    $("#lesson-text").textContent = data.text;
    $("#mode-label").textContent = data.label;
    $("#mode-badge").textContent = data.badge;
    $("#run-action").textContent = data.button;

    $$(".step-tab").forEach(function (tab, index) {
      tab.classList.toggle("active", index === scene);
    });

    if (scene === 0) renderTree("normal");
    if (scene === 1) renderTree("repeats");
    if (scene === 2) renderTree("memory");
    if (scene === 3) renderTree("space");
  }

  function runAction() {
    clearTimers();
    if (scene === 0) {
      renderTree("normal");
      animateBrute();
    }
    if (scene === 1) {
      renderTree("repeats");
      setRibbon([]);
    }
    if (scene === 2) animateMemory();
    if (scene === 3) animateSpace();
  }

  function bind() {
    $$(".difficulty-picker button").forEach(function (button) {
      button.addEventListener("click", function () {
        stairs = parseInt(button.dataset.stairs, 10);
        $$(".difficulty-picker button").forEach(function (item) {
          item.classList.toggle("active", item === button);
        });
        clearTimers();
        buildStairs();
        updateStats();
        paintScene();
      });
    });

    $$(".step-tab").forEach(function (button) {
      button.addEventListener("click", function () {
        scene = parseInt(button.dataset.jumpStep, 10);
        clearTimers();
        setRibbon([]);
        paintScene();
      });
    });

    $("#next-step").addEventListener("click", function () {
      scene = (scene + 1) % copy.length;
      clearTimers();
      setRibbon([]);
      paintScene();
    });

    $("#run-action").addEventListener("click", runAction);
  }

  if ($("#game")) {
    buildStairs();
    updateStats();
    paintScene();
    bind();
  }
}());
