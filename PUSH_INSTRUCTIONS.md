# Push the full DP Adventure to GitHub (53 interactive levels)

> The Cowork sandbox can't reach github.com — these are normal git commands you
> can paste into Git Bash. All files are in
> `C:\Users\Owner\Documents\Claude\Projects\Learn algos`.

## 1) Clone the repo (skip if you already have it)

```bash
cd ~/Documents/Claude/Projects
git clone https://github.com/tools-maker-art/algos.git algos-repo
cd algos-repo
git checkout main
git pull
```

## 2) Create a fresh branch

```bash
git checkout -b feat/dp-adventure-interactive-53
```

## 3) Replace site files

```bash
SRC="/c/Users/Owner/Documents/Claude/Projects/Learn algos"
rm -rf ./levels ./_build_levels.py ./_gen.py ./level-runtime.js
cp "$SRC/index.html"          .
cp "$SRC/dp-roadmap.html"     .
cp "$SRC/styles.css"          .
cp "$SRC/script.js"           .
cp "$SRC/level-runtime.js"    .
cp "$SRC/_gen.py"             .   # optional — regenerator
mkdir -p ./levels
cp "$SRC/levels/"*.html ./levels/
```

## 4) Commit & push

```bash
git add .
git commit -m "Make all 53 DP Adventure levels playable + interactive"
git push -u origin feat/dp-adventure-interactive-53
```

## 5) Open the PR

```
https://github.com/tools-maker-art/algos/compare/main...feat/dp-adventure-interactive-53?expand=1
```

**PR title**
```
Make all 53 DP Adventure levels playable + interactive
```

**PR description**
```
- Every level (2..53) now loads level-runtime.js and mounts interactive widgets
  from a per-level JSON block:
    - data-viz   → scene 1 visual (bars / coins / grid / strings / stick / balloons)
    - data-tree  → expanding recursion tree (where applicable)
    - data-memo  → backpack stepper that fills with sticky notes
    - data-tab   → DP table that fills cell-by-cell on Next
    - data-space → space-saver boxes that update on Next
    - compare    → before-vs-after bars
- Level 1 remains hand-crafted with its own bunny + tree logic.
- 4 Java code blocks per level (212 total) — brute → memo → tab → space.
- Roadmap unlocked: 53 clickable cards grouped into 8 worlds.
- Static HTML/CSS/JS only — works on GitHub Pages with no build step.
```

---

## What changed in this pass

A new shared file: **level-runtime.js** (~220 lines, vanilla JS).
It reads `<script type="application/json" id="level-data">` from each level page,
then mounts:
1. The **scene 1 visual** (kind: `bars`, `coins`, `grid`, `strings`, `string`, `stick`, `balloons`).
2. An **expanding recursion tree** (`data-tree`) where the level supplies node data.
3. The **memo backpack stepper** that reveals stickies one at a time on click.
4. The **tab table stepper** with formula text per step.
5. The **space-saver boxes** that update prev/curr/next via stepper.
6. The **before-vs-after** bars in scene 6.

Every page declares its own data, so each level animates the right visuals.
GitHub Pages: enable Pages → branch `main` → folder `/`. No build step needed.
