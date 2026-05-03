# Push the redesigned DP Adventure to GitHub

> **No special permission needed from me** — you have Git Bash, and these are
> just normal git commands. The Cowork sandbox itself can't reach github.com,
> so I built every file locally in
> `C:\Users\Owner\Documents\Claude\Projects\Learn algos`.
> Open Git Bash and paste these commands.

## 1) Clone the repo (skip if you already have it)

```bash
cd ~/Documents/Claude/Projects
git clone https://github.com/tools-maker-art/algos.git algos-repo
cd algos-repo
git checkout main
git pull
```

## 2) Create a fresh branch off `main`

```bash
git checkout main
git pull
git checkout -b feat/dp-adventure-visual-redesign
```

## 3) Replace the old files with the new visual redesign

In Git Bash, the Windows path becomes `/c/Users/Owner/...`:

```bash
SRC="/c/Users/Owner/Documents/Claude/Projects/Learn algos"

# Wipe any old generated files
rm -rf ./levels ./_build_levels.py

# Copy the new design over
cp "$SRC/index.html"        .
cp "$SRC/dp-roadmap.html"   .
cp "$SRC/styles.css"        .
cp "$SRC/script.js"         .
mkdir -p ./levels
cp "$SRC/levels/level-01-fibonacci.html" ./levels/
```

## 4) Commit & push

```bash
git add .
git commit -m "Redesign DP Adventure as visual interactive game"
git push -u origin feat/dp-adventure-visual-redesign
```

## 5) Open the PR

Go to:
```
https://github.com/tools-maker-art/algos/compare/main...feat/dp-adventure-visual-redesign?expand=1
```

**PR title**
```
Redesign DP Adventure as visual interactive game
```

**PR description**
```
- Reworked roadmap into game-map style
- Added visual interactive Fibonacci level
- Added recursion tree visualization
- Added memoization, tabulation, and space optimization demos
- Reduced text-heavy content
- Improved mobile-friendly playful design
- Bunny now starts on the ground (step 0)
- All 8 ways for N=5 listed visually inside an expandable panel
- Brute-force tree no longer uses scary f(N) — labels read "🪜 N stairs"
- Added "What does this mean?" explainers under every concept
```

---

## What's in this redesign (latest pass)

**index.html** — minimal landing page. One headline, subtitle, and a big
**▶ Start Adventure** button.

**dp-roadmap.html** — game-map style. A wandering dashed path under the level
cards. **Level 1 is glowing & playable**; the others are locked with `🔒 soon`
pills as placeholders.

**levels/level-01-fibonacci.html** — six visual scenes, each with a "?"
expandable explainer:

1. **Story** — bunny stands on the **ground** (a brown START tile), then hops
   up using **hop 1** / **hop 2** buttons. Below: a panel that lists **all 8
   ways** for N=5 as little hop-sequences.
2. **Brute force** — SVG tree where each node reads `🪜 N stairs` (no scary
   `f(N)` math). Duplicates highlight in **red**, base cases in yellow.
   Counter labels say "Bunny questions asked" and "Same question repeated".
3. **Memoization** — backpack fills with **stickies** like "🪜 3 stairs = 3
   ways". Counter calls them "Stickies in backpack" and "Wasted work skipped".
4. **Tabulation** — boxes labeled "0 stairs / 1 stair / 2 stairs…" fill left
   to right with each click. Formula reads in plain words: "**3 stairs** =
   ways for **2** + ways for **1** = **3**".
5. **Space saver** — three boxes (**prev / curr / next**) animate as you slide
   forward. Status: "we are at stair 4 · current answer = 5".
6. **Before vs After** — bars show "tries" vs "steps".

The **N picker (3 / 4 / 5 / 6)** at the top resets every scene so the bunny,
tree, backpack, table, and comparison all stay in sync.

**styles.css** + **script.js** — vanilla theme, no frameworks, mobile responsive.

GitHub Pages: enable Pages → branch `main` → folder `/`. No build step needed.
