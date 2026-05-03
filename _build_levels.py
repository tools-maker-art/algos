#!/usr/bin/env python3
"""
DP Adventure — generator for the 53 level pages and the roadmap.
Run from the repo root:
    python3 _build_levels.py
Outputs:
    levels/level-XX-<slug>.html  (53 files)
    dp-roadmap.html
"""
import os, html, re, pathlib, json

ROOT = pathlib.Path(__file__).parent
LEVELS_DIR = ROOT / "levels"
LEVELS_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def slugify(s):
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s

def section(emoji, title, body, extra_id=None):
    """Render one of the 13 sections as a card."""
    idattr = f' id="{extra_id}"' if extra_id else ''
    return f"""
  <div class="section-card"{idattr}>
    <h2><span class="emoji">{emoji}</span> {title}</h2>
    {body}
  </div>"""

def code_block(code):
    return f'<pre class="code">{html.escape(code)}</pre>'

def details(summary, body):
    return f"<details><summary>{summary}</summary>{body}</details>"

# --------------------------------------------------------------------------
# 53 LEVELS — full content
# Each level dict provides every section the template requires.
# Keys are short to keep this file readable; the renderer expands them.
# --------------------------------------------------------------------------

LEVELS = []

def L(**kw):
    LEVELS.append(kw)

# =========================================================================
# WORLD A — BASICS (1D DP)  -----------------------------------------------
# =========================================================================
L(
  num=1, world="A", world_name="Basics", slug="fibonacci", fun="🐣 The Bunny Family Tree",
  ttl="Fibonacci Number",
  obj="Find the N-th number in the famous Fibonacci sequence — without falling asleep counting.",
  prob="Fibonacci is a list where each number is the sum of the two before it: 0, 1, 1, 2, 3, 5, 8, 13… We want the N-th one.",
  story=("Two bunnies appear. Every month, every pair makes a new pair. How many pairs after N months? "
         "That count <em>is</em> the Fibonacci sequence. Cute and sneaky."),
  brute=("Write fib(n) = fib(n-1) + fib(n-2). Looks tiny — but fib(40) recomputes the same little numbers "
         "<strong>billions</strong> of times. Your laptop sweats."),
  trans=("We notice the same fib(k) is asked over and over. So… write the answer down the first time, then reuse it. "
         "That&rsquo;s the leap from recursion to <em>memoization</em>."),
  rec="fib(n) = fib(n-1) + fib(n-2), base: fib(0)=0, fib(1)=1.",
  memo="Keep an array memo[]. Before computing fib(n), check memo[n]. If known, return it. Else compute, store, return.",
  tab="Build dp[0..n] left to right: dp[0]=0, dp[1]=1, dp[i]=dp[i-1]+dp[i-2].",
  space="Only the last two values matter. Keep two variables: prev2, prev1. O(1) memory.",
  dry=[
    ("Start", "We want fib(5). prev2=0, prev1=1."),
    ("i=2", "curr = 0+1 = 1. Now prev2=1, prev1=1."),
    ("i=3", "curr = 1+1 = 2. prev2=1, prev1=2."),
    ("i=4", "curr = 1+2 = 3. prev2=2, prev1=3."),
    ("i=5", "curr = 2+3 = 5. ✅ Answer: <code class='inline'>5</code>."),
  ],
  comp="Brute recursion: O(2ⁿ) — explosive. Memo / Tab / Space-optimized: O(n) time, O(1) memory after optimisation.",
  take="If you ever recompute the same thing twice, you&rsquo;re ready for DP.",
  challenge="Find fib(20) using only two variables. (Answer: 6765.)",
  uiidea="Recursion tree: tap a node to mark it &lsquo;cached&rsquo;. Watch how memoization prunes giant duplicate subtrees.",
  viz="""
  <div class="viz">
    <p class="muted center">A tiny recursion tree for <code class="inline">fib(4)</code>. Tap nodes to &ldquo;cache&rdquo; them.</p>
    <div class="tree-viz">
      <div class="tree-row"><span class="node">fib(4)</span></div>
      <div class="tree-row"><span class="node">fib(3)</span><span class="node">fib(2)</span></div>
      <div class="tree-row"><span class="node">fib(2)</span><span class="node">fib(1)</span><span class="node">fib(1)</span><span class="node">fib(0)</span></div>
      <div class="tree-row"><span class="node">fib(1)</span><span class="node">fib(0)</span></div>
    </div>
  </div>"""
)

L(
  num=2, world="A", world_name="Basics", slug="climbing-stairs", fun="🪜 Stair Sprint",
  ttl="Climbing Stairs",
  obj="Count the number of unique ways to reach the top of a staircase taking 1 or 2 steps at a time.",
  prob="You&rsquo;re at step 0. The top is step N. From any step you may jump 1 or 2 stairs. How many distinct paths exist?",
  story=("Imagine a tiny cat hopping up stairs. Sometimes it leaps two, sometimes one. "
         "How many different hop-stories can it tell after reaching the top?"),
  brute="Try every choice: at each stair branch into &lsquo;+1&rsquo; and &lsquo;+2&rsquo;. Lots of repeated subproblems.",
  trans="Ways(n) only depends on Ways(n-1) and Ways(n-2). Sound familiar? Yep — this is Fibonacci wearing a hat.",
  rec="ways(n) = ways(n-1) + ways(n-2). Base: ways(0)=1, ways(1)=1.",
  memo="Cache ways(n) once computed.",
  tab="dp[0]=1, dp[1]=1, dp[i]=dp[i-1]+dp[i-2].",
  space="Two variables prev2, prev1.",
  dry=[
    ("n=1","ways = 1 (just step up)."),
    ("n=2","Either 1+1 or 2. ways = 2."),
    ("n=3","From step 2 (2 ways) or step 1 (1 way). ways = 3."),
    ("n=4","From step 3 (3) or step 2 (2). ways = 5."),
    ("n=5","From step 4 (5) or step 3 (3). ways = 8."),
  ],
  comp="O(n) time, O(1) space.",
  take="Many problems with two choices reduce to ways(n-1)+ways(n-2)-style recurrences.",
  challenge="Modify it so the cat can hop 1, 2, or 3 stairs. (Hint: add ways(n-3).)",
  uiidea="Stairs visual: tap stairs to highlight the path. Counter at top updates the number of unique paths.",
  viz="""
  <div class="viz">
    <p class="muted center">5 stairs · tap to walk a path</p>
    <div class="stairs">
      <div class="step" style="height:30px">1</div>
      <div class="step" style="height:50px">2</div>
      <div class="step" style="height:70px">3</div>
      <div class="step" style="height:100px">4</div>
      <div class="step" style="height:130px">5</div>
    </div>
  </div>"""
)

L(
  num=3, world="A", world_name="Basics", slug="frog-jump", fun="🐸 Frog & The Stones",
  ttl="Frog Jump",
  obj="Help the frog reach the last stone with the minimum total jump-energy.",
  prob="Heights[i] is the height of stone i. From stone i the frog can jump to i+1 or i+2. Energy = |height diff|. Reach stone n-1 with minimum total energy.",
  story=("A frog is on stone 1. The pond has N stones each with a height. Each jump costs effort equal to the height "
         "difference. Saving lily-pads is life — minimise total tiredness."),
  brute="Try both jumps from every stone recursively. Same subproblems show up everywhere.",
  trans="cost(i) only needs cost(i-1) and cost(i-2). Pure 1D DP.",
  rec="cost(i) = min( cost(i-1)+|h[i]-h[i-1]|, cost(i-2)+|h[i]-h[i-2]| ).",
  memo="Cache cost(i).",
  tab="dp[0]=0; dp[1]=|h[1]-h[0]|; for i≥2 use the recurrence.",
  space="Two variables: prev2, prev1.",
  dry=[
    ("Heights","[10, 30, 40, 20]"),
    ("dp[0]","0 (start)"),
    ("dp[1]","|30-10|=20"),
    ("dp[2]","min( dp[1]+10, dp[0]+30 ) = min(30,30) = 30"),
    ("dp[3]","min( dp[2]+20, dp[1]+10 ) = min(50,30) = 30 ✅"),
  ],
  comp="O(n) time, O(1) space.",
  take="Two-choice transitions = small lookback DP.",
  challenge="What if the frog must visit stone 0 AND stone n-1 with min total energy? (Same recurrence.)",
  uiidea="Lily pads in a row, each labeled with height. Tap a path to see total energy update live.",
  viz="""
  <div class="viz">
    <p class="muted center">Tap stones to plan the frog&rsquo;s path</p>
    <div class="stairs">
      <div class="step" style="height:40px">10</div>
      <div class="step" style="height:90px">30</div>
      <div class="step" style="height:120px">40</div>
      <div class="step" style="height:60px">20</div>
    </div>
  </div>"""
)

L(
  num=4, world="A", world_name="Basics", slug="frog-jump-k", fun="🐸 Frog with Super Legs",
  ttl="Frog Jump with K distance",
  obj="Same frog — but now it can jump up to K stones in one go. Find min energy to reach the last stone.",
  prob="Jump distance is 1..K. Cost per jump = |height diff|. Min total energy to reach stone n-1.",
  story="The frog drank a tiny potion. It now leaps up to K stones. More options — but harder to choose.",
  brute="Try all K choices recursively from every stone. K^n in the worst case — yikes.",
  trans="cost(i) needs cost(i-1)…cost(i-K). Generalise the lookback.",
  rec="cost(i) = min over j=1..K of ( cost(i-j) + |h[i]-h[i-j]| ), if i-j ≥ 0.",
  memo="Cache cost(i).",
  tab="dp[0]=0; for i=1..n-1: dp[i]=min over j=1..K with valid i-j.",
  space="Need last K values; deque for O(n·log K) or just keep an array.",
  dry=[
    ("Heights, K=3","[10, 20, 30, 10], K=3"),
    ("dp[0]","0"),
    ("dp[1]","min via j=1 → 10"),
    ("dp[2]","min(dp[1]+10, dp[0]+20)=min(20,20)=20"),
    ("dp[3]","min(dp[2]+20, dp[1]+10, dp[0]+0)=min(40,20,0)=0 ✅"),
  ],
  comp="O(n·K) time, O(n) space.",
  take="When &lsquo;just two choices&rsquo; becomes &lsquo;up to K&rsquo;, generalise the loop.",
  challenge="Find a K for which jumping straight to stone n-1 is best.",
  uiidea="Slider for K. Stones glow showing reachable jumps from current stone.",
  viz="""
  <div class="viz">
    <p class="muted center">Stones with heights 10, 20, 30, 10</p>
    <div class="stairs">
      <div class="step" style="height:40px">10</div>
      <div class="step" style="height:60px">20</div>
      <div class="step" style="height:90px">30</div>
      <div class="step" style="height:40px">10</div>
    </div>
  </div>"""
)

L(
  num=5, world="A", world_name="Basics", slug="non-adjacent-sum", fun="💰 Loot Without Touching",
  ttl="Maximum Sum of Non-Adjacent Elements",
  obj="Pick numbers from an array to maximise sum — but you can&rsquo;t pick two side-by-side.",
  prob="Given nums[], maximise sum of a chosen subset where no two chosen indices are adjacent.",
  story="A row of treasure piles. Picking pile i wakes up pile i+1&rsquo;s guard. Choose wisely!",
  brute="Try pick / skip at every index. 2ⁿ.",
  trans="At index i, two options: take nums[i] + best(i-2), or skip = best(i-1). Take the larger.",
  rec="best(i) = max( nums[i] + best(i-2), best(i-1) ).",
  memo="Cache best(i).",
  tab="dp[0]=nums[0]; dp[1]=max(nums[0],nums[1]); recurrence onward.",
  space="Two variables: prev2, prev1.",
  dry=[
    ("Nums","[2, 7, 9, 3, 1]"),
    ("dp[0]","2"),
    ("dp[1]","max(2,7)=7"),
    ("dp[2]","max(7, 9+2)=11"),
    ("dp[3]","max(11, 3+7)=11"),
    ("dp[4]","max(11, 1+11)=12 ✅"),
  ],
  comp="O(n) time, O(1) space.",
  take="The 'take or skip' pattern is a DP superpower.",
  challenge="Solve it if negative numbers are allowed (skip them all if needed).",
  uiidea="Coin row: tap to take. Adjacent coins fade. Total updates live.",
  viz="""
  <div class="viz">
    <p class="muted center">Tap coins to take them (adjacent become dim)</p>
    <div class="coins">
      <div class="coin">2</div><div class="coin">7</div><div class="coin">9</div>
      <div class="coin">3</div><div class="coin">1</div>
    </div>
  </div>"""
)

L(
  num=6, world="A", world_name="Basics", slug="house-robber", fun="🏠 The Polite Robber",
  ttl="House Robber",
  obj="Same as Level 5, told as a heist: maximise loot without robbing two adjacent houses.",
  prob="Houses in a line, value v[i]. Don&rsquo;t rob adjacent. Maximise total stolen.",
  story="A robber with manners — he avoids alarming neighbours. Adjacent houses share a wall (and an alarm).",
  brute="Pick/skip per house — 2ⁿ.",
  trans="Take v[i]+best(i-2) or skip best(i-1). Identical to non-adjacent sum, just dressed up.",
  rec="rob(i) = max( v[i]+rob(i-2), rob(i-1) ).",
  memo="Cache rob(i).",
  tab="Same as Level 5.",
  space="prev2, prev1.",
  dry=[
    ("Houses","[2, 7, 9, 3, 1]"),
    ("dp[0]","2"),
    ("dp[1]","max(2,7)=7"),
    ("dp[2]","max(7,11)=11"),
    ("dp[3]","11"),
    ("dp[4]","12 ✅ — rob houses 1, 3, 5 (values 2,9,1) → 12"),
  ],
  comp="O(n) time, O(1) space.",
  take="When two problems share a recurrence, they&rsquo;re actually the same problem.",
  challenge="Prove that you never want to skip 2 in a row. (Hint: you&rsquo;d be wasting a house.)",
  uiidea="Houses in a row. Tap to rob. Adjacent houses turn red (cannot rob).",
  viz="""
  <div class="viz">
    <p class="muted center">Tap houses to rob them — adjacent ones go locked</p>
    <div class="coins">
      <div class="coin">🏠2</div><div class="coin">🏠7</div><div class="coin">🏠9</div>
      <div class="coin">🏠3</div><div class="coin">🏠1</div>
    </div>
  </div>"""
)

L(
  num=7, world="A", world_name="Basics", slug="house-robber-2", fun="🏘️ Robber on a Roundabout",
  ttl="House Robber II",
  obj="Same robber — but the houses form a circle. The first and last are now neighbours.",
  prob="House Robber, but circular array. First and last are adjacent.",
  story="The houses now sit on a roundabout. Robbing both house 0 and house n-1 trips a single shared alarm.",
  brute="Try all subsets respecting the rule. Exponential.",
  trans="Split into two normal House Robber problems: (a) houses 0..n-2  (b) houses 1..n-1. Take the max.",
  rec="ans = max( robLine(v[0..n-2]), robLine(v[1..n-1]) )",
  memo="Memoise each linear sub-call as in Level 6.",
  tab="Run the linear DP twice on two slices.",
  space="O(1) per linear pass.",
  dry=[
    ("Houses","[2, 3, 2]"),
    ("Try slice [2,3]","max=3"),
    ("Try slice [3,2]","max=3"),
    ("Answer","3"),
  ],
  comp="O(n) time, O(1) space.",
  take="When a problem &lsquo;wraps around&rsquo;, split it into two non-wrapping cases.",
  challenge="Prove the answer is the same when nums has length 1.",
  uiidea="Circular layout of houses. Visualise both linear sub-problems side by side.",
  viz="""
  <div class="viz">
    <p class="muted center">Circular houses (first ↔ last are neighbours)</p>
    <div class="coins">
      <div class="coin">🏠2</div><div class="coin">🏠3</div><div class="coin">🏠2</div>
    </div>
  </div>"""
)

# =========================================================================
# WORLD B — GRID DP -------------------------------------------------------
# =========================================================================
L(
  num=8, world="B", world_name="Grid DP", slug="unique-paths", fun="🦊 Fox in the Forest",
  ttl="Unique Paths",
  obj="Count unique paths from the top-left to the bottom-right of an m×n grid moving only right or down.",
  prob="Grid m×n. From (0,0) you only move Right or Down. How many distinct paths reach (m-1,n-1)?",
  story="A fox lives at (0,0). Berries are at (m-1,n-1). It can only walk Right or Down. How many berry-routes exist?",
  brute="Try every path recursively. 2^(m+n).",
  trans="paths(i,j) = paths(i-1,j) + paths(i,j-1). Two choices reach a cell.",
  rec="paths(i,j) = paths(i-1,j) + paths(i,j-1). Base: paths(0,j)=paths(i,0)=1.",
  memo="Cache by (i,j).",
  tab="Fill 2D dp grid row by row.",
  space="Single row of size n. Update in place.",
  dry=[
    ("Grid 3×3","Goal at (2,2)"),
    ("Row 0","[1,1,1]"),
    ("Row 1","[1,2,3]"),
    ("Row 2","[1,3,6] ✅"),
  ],
  comp="O(m·n) time, O(n) space.",
  take="Grid DP = sum of ways from neighbours that lead here.",
  challenge="What is paths(7,3)?  (Answer: 28 — try it!)",
  uiidea="Grid of boxes. Tap to highlight a path. Live counter shows how many such paths exist.",
  viz="""
  <div class="viz">
    <p class="muted center">3×3 grid · click cells to walk Right/Down</p>
    <div class="grid-viz" style="grid-template-columns:repeat(3,1fr)">
      <div class="cell start">S</div><div class="cell"></div><div class="cell"></div>
      <div class="cell"></div><div class="cell"></div><div class="cell"></div>
      <div class="cell"></div><div class="cell"></div><div class="cell end">🍓</div>
    </div>
  </div>"""
)

L(
  num=9, world="B", world_name="Grid DP", slug="unique-paths-2", fun="🪨 Boulders in the Way",
  ttl="Unique Paths II",
  obj="Same grid — now some cells are blocked. Count paths that avoid the obstacles.",
  prob="Grid contains 0 (free) and 1 (obstacle). Count paths from (0,0) to (m-1,n-1) avoiding all 1s.",
  story="The fox now meets fallen boulders. Skip those cells entirely.",
  brute="Same recursion — but skip blocked cells.",
  trans="If grid[i][j]==1, paths(i,j)=0. Else paths(i,j)=paths(i-1,j)+paths(i,j-1).",
  rec="Conditional recurrence as above.",
  memo="Cache.",
  tab="2D dp; if obstacle, leave 0.",
  space="Single row, in place.",
  dry=[
    ("Grid","[[0,0,0],[0,1,0],[0,0,0]]"),
    ("Row 0","[1,1,1]"),
    ("Row 1","[1,0,1]   (block at (1,1))"),
    ("Row 2","[1,1,2] ✅"),
  ],
  comp="O(m·n) time, O(n) space.",
  take="Add &lsquo;walls&rsquo; by zeroing forbidden cells. The recurrence stays the same.",
  challenge="If the start or end cell is blocked, what&rsquo;s the answer?  (0.)",
  uiidea="Toggle cells to obstacles. Live recount of valid paths.",
  viz="""
  <div class="viz">
    <p class="muted center">3×3 with one boulder in the middle</p>
    <div class="grid-viz" style="grid-template-columns:repeat(3,1fr)">
      <div class="cell start">S</div><div class="cell"></div><div class="cell"></div>
      <div class="cell"></div><div class="cell block">🪨</div><div class="cell"></div>
      <div class="cell"></div><div class="cell"></div><div class="cell end">🍓</div>
    </div>
  </div>"""
)

L(
  num=10, world="B", world_name="Grid DP", slug="min-path-sum", fun="💎 Cheapest Treasure Trail",
  ttl="Minimum Path Sum",
  obj="Find a path from top-left to bottom-right that minimises the total of cell values.",
  prob="Each cell has a positive cost. Move Right/Down. Minimise sum of costs along path.",
  story="Each step costs gold. Find the cheapest trail to the treasure room.",
  brute="Try all paths.",
  trans="dp(i,j)=grid[i][j]+min(dp(i-1,j), dp(i,j-1)).",
  rec="As above. Base: dp(0,0)=grid[0][0].",
  memo="Cache.",
  tab="2D fill from top-left.",
  space="Single row.",
  dry=[
    ("Grid","[[1,3,1],[1,5,1],[4,2,1]]"),
    ("Row 0","[1,4,5]"),
    ("Row 1","[2,7,6]"),
    ("Row 2","[6,8,7] ✅ — cheapest path = 1→3→1→1→1 = 7"),
  ],
  comp="O(m·n) time, O(n) space.",
  take="Replace +1 with +cell to turn &lsquo;count&rsquo; DP into &lsquo;min-cost&rsquo; DP.",
  challenge="Trace the actual path, not just the cost. (Hint: store parent pointers.)",
  uiidea="Grid with cost labels. Tap path. Live total cost.",
  viz="""
  <div class="viz">
    <p class="muted center">3×3 cost grid</p>
    <div class="grid-viz" style="grid-template-columns:repeat(3,1fr)">
      <div class="cell">1</div><div class="cell">3</div><div class="cell">1</div>
      <div class="cell">1</div><div class="cell">5</div><div class="cell">1</div>
      <div class="cell">4</div><div class="cell">2</div><div class="cell">1</div>
    </div>
  </div>"""
)

L(
  num=11, world="B", world_name="Grid DP", slug="triangle", fun="⛰️ Triangle Trek",
  ttl="Triangle",
  obj="Walk top→bottom in a triangle of numbers, choosing the path with the smallest total sum.",
  prob="From triangle[i][j] you may move to triangle[i+1][j] or triangle[i+1][j+1]. Minimise total.",
  story="A pyramid path: each step you either keep going straight-down or step diagonally. Pick the cheapest descent.",
  brute="Recurse from top — exponential.",
  trans="dp(i,j) = triangle[i][j] + min( dp(i+1,j), dp(i+1,j+1) ).",
  rec="As above. Compute bottom-up to avoid overflow of recursion.",
  memo="Cache.",
  tab="Start from last row (dp = last row), fold upwards.",
  space="Single 1D array of length = bottom width.",
  dry=[
    ("Triangle","[[2],[3,4],[6,5,7],[4,1,8,3]]"),
    ("Bottom","[4,1,8,3]"),
    ("Row 2","[7,6,10] (e.g. 6+min(4,1)=7)"),
    ("Row 1","[9,10] (3+min(7,6)=9)"),
    ("Top","[11] ✅"),
  ],
  comp="O(n²) time, O(n) space.",
  take="Walk bottom-up to avoid awkward boundary checks.",
  challenge="What if you can also move diagonally to (i+1, j-1)? Add a third term in the min.",
  uiidea="Triangle of numbered cells. Tap a cell to expand allowed next steps.",
  viz="""
  <div class="viz center">
    <div class="muted">Triangle of choices</div>
    <pre class="code">      2
     3 4
    6 5 7
   4 1 8 3</pre>
  </div>"""
)

L(
  num=12, world="B", world_name="Grid DP", slug="falling-path-sum", fun="❄️ Falling Snow Path",
  ttl="Minimum/Maximum Falling Path Sum",
  obj="Drop a snowflake row-by-row down the grid. Minimise (or maximise) the total of cells you touch.",
  prob="From (i,j) you may go to (i+1,j-1), (i+1,j), or (i+1,j+1). Optimise sum.",
  story="A snowflake falls down a grid. Each row it shifts at most one column left or right. Find the cheapest descent.",
  brute="Recurse from each starting column.",
  trans="dp(i,j) = grid[i][j] + min( dp(i-1,j-1), dp(i-1,j), dp(i-1,j+1) ).",
  rec="Bottom-up usually clearer.",
  memo="Cache (i,j).",
  tab="Fill row-by-row.",
  space="Two rows (or one with care).",
  dry=[
    ("Grid","[[2,1,3],[6,5,4],[7,8,9]]"),
    ("Row 0","[2,1,3]"),
    ("Row 1","[7,6,5]   (e.g. 5+min(2,1,3)=6)"),
    ("Row 2","[12,13,14] → min=12 ✅"),
  ],
  comp="O(m·n) time, O(n) space.",
  take="Three-way grid moves are still 1D-row DP.",
  challenge="Switch the operator from min to max — does the structure change? (No.)",
  uiidea="Grid with a snowflake animation that 'falls' choosing each row's min.",
  viz="""
  <div class="viz">
    <p class="muted center">3×3 grid · snowflake falls top→bottom</p>
    <div class="grid-viz" style="grid-template-columns:repeat(3,1fr)">
      <div class="cell">2</div><div class="cell">1</div><div class="cell">3</div>
      <div class="cell">6</div><div class="cell">5</div><div class="cell">4</div>
      <div class="cell">7</div><div class="cell">8</div><div class="cell">9</div>
    </div>
  </div>"""
)

L(
  num=13, world="B", world_name="Grid DP", slug="cherry-pickup", fun="🍒 Two Friends, One Orchard",
  ttl="Cherry Pickup",
  obj="Two robots walk a grid simultaneously, picking cherries. Maximise the total they collect.",
  prob="Grid with cherries. Two paths from (0,0) to (m-1,n-1), each Right/Down. Cells visited by both count once.",
  story="Two friends start at the same gate. They each take a path. They&rsquo;re not allowed to take the same cherry twice.",
  brute="Try all pairs of paths — quadratic explosion.",
  trans=("Move both simultaneously by step count. State = (step, r1, r2). c1 = step-r1, c2 = step-r2. "
         "Pick max over the four (down/right × down/right) parents."),
  rec="dp(step, r1, r2) = grid[r1][c1] + (r1==r2 ? 0 : grid[r2][c2]) + max(four parents).",
  memo="3D cache.",
  tab="3D fill by step.",
  space="Two 2D layers (current step / previous).",
  dry=[
    ("Grid","[[0,1,-1],[1,0,-1],[1,1,1]]"),
    ("Walk both","Robot A: D,D,R,R · Robot B: R,R,D,D"),
    ("Cells used","Pairs are summed; shared cells count once."),
    ("Total","5 ✅"),
  ],
  comp="O(n³) time, O(n²) space (with optimisation).",
  take="When two agents move together, model state as (step, position1, position2).",
  challenge="What if a cell is a wall? (Make its value -∞ and skip those states.)",
  uiidea="Two coloured paths overlapping on a grid. Cherries glow when collected.",
  viz="""
  <div class="viz">
    <p class="muted center">Two friends walk → maximise cherries collected.</p>
    <div class="grid-viz" style="grid-template-columns:repeat(3,1fr)">
      <div class="cell">🍒</div><div class="cell">🍒</div><div class="cell"></div>
      <div class="cell">🍒</div><div class="cell"></div><div class="cell">🍒</div>
      <div class="cell">🍒</div><div class="cell">🍒</div><div class="cell">🍒</div>
    </div>
  </div>"""
)

# =========================================================================
# WORLD C — SUBSEQUENCES / KNAPSACK ---------------------------------------
# =========================================================================
L(
  num=14, world="C", world_name="Knapsack", slug="subset-sum", fun="🎒 Can the Bag Hit the Target?",
  ttl="Subset Sum",
  obj="Can a subset of numbers add up to exactly K?",
  prob="Given nums[] and target K, is there a subset whose sum equals K?",
  story=("You have a bag of pebbles, each weighing different grams. The shopkeeper asks: &ldquo;Can you give me exactly K grams?&rdquo;"),
  brute="Try every subset (2ⁿ).",
  trans="At each item: pick or skip. State = (i, current_sum). Two choices.",
  rec="canSum(i, target) = canSum(i-1, target) OR canSum(i-1, target - nums[i]).",
  memo="2D cache by (i, target).",
  tab="dp[i][k]: can we make k from first i? Fill row-by-row.",
  space="One row of size K+1, traverse target high→low.",
  dry=[
    ("Nums","[2,3,5], K=8"),
    ("k=0","Always true"),
    ("After 2","Reachable: 0,2"),
    ("After 3","0,2,3,5"),
    ("After 5","0,2,3,5,7,8 ✅"),
  ],
  comp="O(n·K) time, O(K) space.",
  take="Pick / Skip → boolean DP table.",
  challenge="What if we&rsquo;re not allowed to skip more than 1 item? (Add a &lsquo;skips&rsquo; dimension.)",
  uiidea="Pebbles with weights. Tap to put in the bag. Bag sum updates.",
  viz="""
  <div class="viz">
    <p class="muted center">Pebbles. Tap to drop in bag. Target = 8</p>
    <div class="coins">
      <div class="coin">2</div><div class="coin">3</div><div class="coin">5</div>
    </div>
  </div>"""
)

L(
  num=15, world="C", world_name="Knapsack", slug="partition-equal-subset", fun="⚖️ Fair-Share Day",
  ttl="Partition Equal Subset Sum",
  obj="Split the array into two groups with equal total.",
  prob="Can you partition nums[] into two subsets with equal sums?",
  story="Two siblings, one pile of candy. Can they split the pile <em>perfectly</em> evenly?",
  brute="Try every subset.",
  trans="If total is odd → impossible. Else target = total/2 → reduces to Subset Sum!",
  rec="canSum(i, target) — same as Level 14.",
  memo="2D cache.",
  tab="Boolean dp[K+1].",
  space="O(K).",
  dry=[
    ("Nums","[1,5,11,5]"),
    ("Total","22 → target 11"),
    ("Subset","{11} or {1,5,5} = 11 ✅"),
  ],
  comp="O(n·sum/2) time, O(sum/2) space.",
  take="Reduce a new problem to a known one — classic DP move.",
  challenge="What if the total is odd? Is partition possible? (No.)",
  uiidea="Candy pile splits into two side-by-side bowls; numbers compare.",
  viz="""
  <div class="viz">
    <p class="muted center">Candy: [1,5,11,5] · target 11</p>
    <div class="coins">
      <div class="coin">1</div><div class="coin">5</div><div class="coin">11</div><div class="coin">5</div>
    </div>
  </div>"""
)

L(
  num=16, world="C", world_name="Knapsack", slug="count-subsets-sum-k", fun="🔢 How Many Ways?",
  ttl="Count Subsets with Sum K",
  obj="Count how many subsets of nums[] add to exactly K.",
  prob="Return the number of subsets summing to K.",
  story="The treasure has weight K. How many distinct selections of pebbles sum exactly to K?",
  brute="Enumerate subsets.",
  trans="cnt(i,k) = cnt(i-1,k) + cnt(i-1,k-nums[i]). Replace OR with +.",
  rec="As above. Base cnt(0,0)=1.",
  memo="Cache (i,k).",
  tab="dp[k] += dp[k - nums[i]] for each item.",
  space="O(K).",
  dry=[
    ("Nums","[1,2,3,3], K=6"),
    ("Subsets","{3,3},{1,2,3},{1,2,3} → 3 ✅ (note the two 3s are distinct)"),
  ],
  comp="O(n·K) time, O(K) space.",
  take="Switch boolean OR to + and Subset Sum becomes Counting.",
  challenge="If nums has duplicates and you want unique-by-value subsets, how does it change?",
  uiidea="Pebbles tickle into the bag. Counter shows current ways.",
  viz="""
  <div class="viz">
    <p class="muted center">Counting subsets of [1,2,3,3] summing to 6</p>
    <div class="coins">
      <div class="coin">1</div><div class="coin">2</div><div class="coin">3</div><div class="coin">3</div>
    </div>
  </div>"""
)

L(
  num=17, world="C", world_name="Knapsack", slug="min-subset-diff", fun="⚖️ Smallest Sibling Quarrel",
  ttl="Minimum Subset Sum Difference",
  obj="Split the array into two groups so the difference of their sums is as small as possible.",
  prob="Find subset S1 such that |sum(S1) - sum(S2)| is minimised.",
  story="Two siblings split candy. They&rsquo;ll cry less if the split is closer to fair.",
  brute="All subsets.",
  trans="Find all reachable subset sums up to total/2; the closest one to total/2 minimises the gap.",
  rec="Boolean reach as in Subset Sum.",
  memo="2D cache.",
  tab="dp[k] = can we form k? Then ans = min total − 2k for reachable k.",
  space="O(sum).",
  dry=[
    ("Nums","[1,6,11,5]"),
    ("Total","23"),
    ("Reachable ≤ 11","0,1,5,6,7,11,12 (cap 11) → 11"),
    ("Diff","23 - 2·11 = 1 ✅"),
  ],
  comp="O(n·sum) time, O(sum) space.",
  take="Subset Sum table is reusable as a building block.",
  challenge="If all numbers are even, is the answer always even? (Yes.)",
  uiidea="Two bowls; their gap shrinks as you tweak choices.",
  viz="""
  <div class="viz">
    <p class="muted center">Try to balance the bowls</p>
    <div class="coins">
      <div class="coin">1</div><div class="coin">6</div><div class="coin">11</div><div class="coin">5</div>
    </div>
  </div>"""
)

L(
  num=18, world="C", world_name="Knapsack", slug="target-sum", fun="➕➖ Plus or Minus?",
  ttl="Target Sum",
  obj="Assign + or − to each number so the resulting expression equals target.",
  prob="Count ways to assign signs so the expression equals target.",
  story="A boss says: &ldquo;Use these numbers, each with + or −. Hit the magic number T. How many ways?&rdquo;",
  brute="2ⁿ sign combinations.",
  trans=("Let P = sum of +-nums, N = sum of −-nums. P-N=T, P+N=S → P=(S+T)/2. "
         "So count subsets with sum P. ⇒ Level 16."),
  rec="Reduces to Count Subsets with Sum K.",
  memo="2D cache.",
  tab="dp[k] += dp[k-num].",
  space="O(P).",
  dry=[
    ("Nums","[1,1,1,1,1], T=3"),
    ("S","5; P=(5+3)/2=4"),
    ("Subsets summing to 4","C(5,4)=5 ✅"),
  ],
  comp="O(n·P) time, O(P) space.",
  take="Algebra → reduction → known DP.",
  challenge="What if (S+T) is odd? (Answer is 0.)",
  uiidea="Each number has +/− toggle. Live expression value updates.",
  viz="""
  <div class="viz">
    <p class="muted center">Toggle + / − on each number to hit the target</p>
    <div class="coins">
      <div class="coin">±1</div><div class="coin">±1</div><div class="coin">±1</div><div class="coin">±1</div><div class="coin">±1</div>
    </div>
  </div>"""
)

L(
  num=19, world="C", world_name="Knapsack", slug="01-knapsack", fun="🎒 Pirate&rsquo;s Greedy Bag",
  ttl="0/1 Knapsack",
  obj="Pack a bag of capacity W with items (value, weight) to maximise total value. Each item once.",
  prob="Maximise value subject to total weight ≤ W. Each item picked at most once.",
  story="A pirate raids a treasury. Each item has value &amp; weight. Bag fits W kg. What&rsquo;s the best haul?",
  brute="Try all subsets (2ⁿ).",
  trans="State (i, w). Pick → val[i]+best(i-1,w-wt[i]); skip → best(i-1,w). Max of the two.",
  rec="As above. Base best(-1,*)=0.",
  memo="2D cache.",
  tab="dp[i][w]; row-by-row.",
  space="1D dp[w], iterate w high→low.",
  dry=[
    ("Items","wt=[1,3,4,5], val=[1,4,5,7], W=7"),
    ("Best","Pick items 2 and 3 (wt 3+4=7, val 4+5=9) ✅"),
  ],
  comp="O(n·W) time, O(W) space.",
  take="Pick/skip with weight bounds = textbook 0/1 Knapsack.",
  challenge="Print the chosen items, not just the value.",
  uiidea="Treasure chest items with weight tags. Drag into bag; bag value updates.",
  viz="""
  <div class="viz">
    <p class="muted center">Items (weight • value)</p>
    <div class="coins">
      <div class="coin">1•1</div><div class="coin">3•4</div><div class="coin">4•5</div><div class="coin">5•7</div>
    </div>
  </div>"""
)

L(
  num=20, world="C", world_name="Knapsack", slug="unbounded-knapsack", fun="🔁 Bottomless Coin Cup",
  ttl="Unbounded Knapsack",
  obj="Same knapsack — but each item can be picked any number of times.",
  prob="Maximise value with unlimited copies, weight ≤ W.",
  story="A magic shop: every item is restocked instantly. Pick the best mix.",
  brute="Recurse: pick or skip; on pick, stay on same i.",
  trans="best(i,w) = max( best(i-1,w), val[i]+best(i,w-wt[i]) ).",
  rec="As above.",
  memo="2D cache.",
  tab="dp[w] = max over items: dp[w]=max(dp[w], dp[w-wt[i]]+val[i]); iterate w low→high.",
  space="1D dp[w].",
  dry=[
    ("Items","wt=[1,3,4], val=[15,50,60], W=8"),
    ("Best","Use 2× item 3 (wt 8, val 120) ✅"),
  ],
  comp="O(n·W) time, O(W) space.",
  take="Iterate w low→high to allow re-use of same item.",
  challenge="With wt=[3,5] and W=7, what&rsquo;s the best with values [4,7]? (8)",
  uiidea="Same items but with infinity emojis. Drag multiple copies.",
  viz="""
  <div class="viz">
    <p class="muted center">Unlimited copies allowed!</p>
    <div class="coins">
      <div class="coin">1•15</div><div class="coin">3•50</div><div class="coin">4•60</div>
    </div>
  </div>"""
)

L(
  num=21, world="C", world_name="Knapsack", slug="coin-change-min", fun="🪙 Tiny Cashier",
  ttl="Coin Change (min coins)",
  obj="Make amount A using the fewest coins from given denominations (unlimited supply).",
  prob="Return min number of coins summing to A, or -1 if impossible.",
  story="A cashier with infinite coins of given denominations wants to give exact change with as few coins as possible.",
  brute="Try every coin at every step (exponential).",
  trans="min(A) = 1 + min over coins c with c≤A of min(A-c).",
  rec="As above. Base min(0)=0.",
  memo="1D cache.",
  tab="dp[A]; dp[0]=0; for a=1..A take min over coins.",
  space="O(A).",
  dry=[
    ("Coins","[1,2,5], A=11"),
    ("Greedy intuition","11 = 5+5+1 → 3 coins ✅"),
  ],
  comp="O(n·A) time, O(A) space.",
  take="When greedy fails (e.g. coins [1,3,4], A=6), DP saves you.",
  challenge="Coins [1,3,4] amount 6 — best is 2 (3+3), not 3 (4+1+1).",
  uiidea="Coin row; tap coins to drop; counter shows total + count.",
  viz="""
  <div class="viz">
    <p class="muted center">Coins = 1, 2, 5 · target 11</p>
    <div class="coins">
      <div class="coin">1</div><div class="coin">2</div><div class="coin">5</div>
    </div>
  </div>"""
)

L(
  num=22, world="C", world_name="Knapsack", slug="coin-change-2", fun="🪙 How Many Wallets?",
  ttl="Coin Change II",
  obj="Count the number of distinct ways to make amount A.",
  prob="Return number of combinations (order doesn&rsquo;t matter) that sum to A.",
  story="A coin collector wants to know in how many distinct ways can the amount be paid.",
  brute="Try all combinations.",
  trans="ways(A) = sum over coins of ways(A - c) — but iterate coins outer to avoid permutations.",
  rec="ways(i,A) = ways(i-1,A) + ways(i,A-c[i]).",
  memo="2D cache.",
  tab="dp[0]=1. For each coin c: for a=c..A: dp[a]+=dp[a-c].",
  space="O(A).",
  dry=[
    ("Coins","[1,2,5], A=5"),
    ("Combos","{5},{2,2,1},{2,1,1,1},{1,1,1,1,1} → 4 ✅"),
  ],
  comp="O(n·A) time, O(A) space.",
  take="Coin order matters? Loop coins outside to avoid permutations.",
  challenge="If coins=[2] and A=3, ways=0.",
  uiidea="Coin pouches that fill differently. Counter of unique fillings.",
  viz="""
  <div class="viz">
    <p class="muted center">Coins = [1,2,5], target = 5</p>
    <div class="coins">
      <div class="coin">1</div><div class="coin">2</div><div class="coin">5</div>
    </div>
  </div>"""
)

L(
  num=23, world="C", world_name="Knapsack", slug="rod-cutting", fun="🪵 The Lumberjack&rsquo;s Saw",
  ttl="Rod Cutting",
  obj="Cut a rod of length N into pieces to maximise total selling price.",
  prob="price[i] = price of a piece of length i+1. Cut rod of length N to max revenue.",
  story="A lumberjack&rsquo;s rod can be sold whole or chopped. Each length sells at a known price.",
  brute="Try every cut combination.",
  trans="best(N) = max over i in 1..N of price[i-1] + best(N-i). Same as Unbounded Knapsack.",
  rec="As above.",
  memo="1D cache.",
  tab="dp[N]; iterate length 1..N taking max over cuts.",
  space="O(N).",
  dry=[
    ("Prices","[1,5,8,9,10,17,17,20], N=8"),
    ("Best","2+6 → 5+17 = 22 ✅"),
  ],
  comp="O(N²) time, O(N) space.",
  take="Rod Cutting ≡ Unbounded Knapsack with weight = length.",
  challenge="If price=[3,5] and N=4, best is 4·3=12.",
  uiidea="Drag a knife to cut a rod. Live total price updates.",
  viz="""
  <div class="viz">
    <p class="muted center">Rod of length 8 → cut for max revenue</p>
    <pre class="code">[ 1 ][ 2 ][ 3 ][ 4 ][ 5 ][ 6 ][ 7 ][ 8 ]</pre>
  </div>"""
)

# =========================================================================
# WORLD D — STRINGS -------------------------------------------------------
# =========================================================================
L(
  num=24, world="D", world_name="Strings", slug="lcs", fun="🧬 Twin Spy Notes",
  ttl="Longest Common Subsequence",
  obj="Find the length of the longest sequence of letters appearing in order in both strings.",
  prob="Given strings A,B return length of longest common subsequence.",
  story="Two spies wrote two notes. Find the longest secret phrase whose letters appear (in order) in both.",
  brute="Try all subsequences of A and check.",
  trans="If A[i]==B[j]: 1+LCS(i-1,j-1). Else max(LCS(i-1,j), LCS(i,j-1)).",
  rec="As above.",
  memo="2D cache.",
  tab="dp[i][j] table.",
  space="2 rows.",
  dry=[
    ("A,B","'abcde','ace'"),
    ("Match","a✓ c✓ e✓ → length 3 ✅"),
  ],
  comp="O(n·m) time, O(n·m) or O(min(n,m)) space.",
  take="Match? +1 diagonal. Else max of left/up. The classic 2D string DP.",
  challenge="What if equal letters cost 2 instead of 1? Same recurrence.",
  uiidea="Two strings as ribbon. Highlight matched letters along a diagonal.",
  viz="""
  <div class="viz">
    <p class="muted center">a-b-c-d-e &nbsp; vs &nbsp; a-c-e</p>
    <pre class="code">  ' ' a c e
' ' 0 0 0 0
 a  0 1 1 1
 b  0 1 1 1
 c  0 1 2 2
 d  0 1 2 2
 e  0 1 2 3 ✅</pre>
  </div>"""
)

L(
  num=25, world="D", world_name="Strings", slug="print-lcs", fun="🖨️ Print the Hidden Phrase",
  ttl="Print LCS",
  obj="Reconstruct the actual longest common subsequence (not just its length).",
  prob="After computing the LCS table, walk back to print one valid LCS string.",
  story="Now print the secret. Trace from dp[n][m] back to dp[0][0] following the choices that made the table grow.",
  brute="Recompute via brute LCS — slow.",
  trans="Walk backward: if A[i-1]==B[j-1] take that letter; else move to the larger neighbour.",
  rec="Trace function on memo table.",
  memo="Reuse LCS table from Level 24.",
  tab="Same.",
  space="Same.",
  dry=[
    ("A,B","'abcde','ace'"),
    ("Trace","From dp[5][3]=3 backwards → 'ace' ✅"),
  ],
  comp="O(n·m) time, O(n·m) space.",
  take="DP tables don&rsquo;t just give numbers — you can rebuild the answer.",
  challenge="Print all distinct LCSs (warning: can be exponential).",
  uiidea="Walk back arrows on the LCS grid; pick up letters as you go.",
  viz="""
  <div class="viz">
    <p class="muted center">Trace dp table backwards</p>
    <pre class="code">a b c d e
a • → → → →
c   ↓ • → →
e         •  → 'ace'</pre>
  </div>"""
)

L(
  num=26, world="D", world_name="Strings", slug="longest-common-substring", fun="🪞 Mirror Words",
  ttl="Longest Common Substring",
  obj="Find the longest contiguous run of letters that appears in both strings.",
  prob="Substring (contiguous) — different from subsequence (any order-preserving).",
  story="A diff-tool wants the biggest exact &lsquo;same chunk&rsquo; between two paragraphs.",
  brute="Compare all (i,j,length) triples.",
  trans="If A[i]==B[j]: dp[i][j]=dp[i-1][j-1]+1 else 0. Track global max.",
  rec="Bottom-up clearer.",
  memo="2D cache.",
  tab="dp[i][j] as above.",
  space="2 rows.",
  dry=[
    ("A,B","'abcde','ace'"),
    ("dp","All matches reset to 1 → length 1 ✅"),
    ("Try","'AGGTAB','GXTXAYB' → 'GTAB' length? actually substring 'A','G','T','B' all 1 — best 1."),
  ],
  comp="O(n·m) time, O(n·m) space.",
  take="Reset on mismatch — that&rsquo;s the difference vs LCS.",
  challenge="Reconstruct the substring itself.",
  uiidea="Two strings; highlight equal contiguous runs in green.",
  viz="""
  <div class="viz">
    <p class="muted center">Common contiguous chunks</p>
  </div>"""
)

L(
  num=27, world="D", world_name="Strings", slug="scs", fun="✂️ Stitch the Two Notes",
  ttl="Shortest Common Supersequence",
  obj="Find the shortest string that contains both inputs as subsequences.",
  prob="Length = n + m − LCS(A,B). Optionally print one such SCS.",
  story="Take both spy notes, stitch them so each appears in order. The shortest stitched story is the SCS.",
  brute="Enumerate stitches.",
  trans="Length first via LCS. To print: walk LCS table; on match output once, on skip output the corresponding char.",
  rec="LCS recurrence.",
  memo="LCS table.",
  tab="LCS table.",
  space="2 rows for length; full table for printing.",
  dry=[
    ("A,B","'abac','cab'"),
    ("LCS","'ab' length 2"),
    ("SCS length","4+3-2=5; one SCS: 'cabac'"),
  ],
  comp="O(n·m) time and space.",
  take="Length formula = n + m − LCS.",
  challenge="If A and B have no common letters, what is the SCS length? (n+m.)",
  uiidea="Animate stitching arrows merging two strings into one.",
  viz="<div class='viz'><p class='muted center'>SCS length = n + m − LCS(A,B)</p></div>"
)

L(
  num=28, world="D", world_name="Strings", slug="min-insertions-palindrome", fun="🪞 Symmetry Insertions",
  ttl="Min Insertions to Make Palindrome",
  obj="Insert the fewest characters to turn S into a palindrome.",
  prob="Return min insertions.",
  story="Mirror the word into a palindrome by adding letters.",
  brute="Try every insertion sequence.",
  trans="Answer = n − LCS(S, reverse(S)).",
  rec="LCS recurrence.",
  memo="LCS table.",
  tab="Compute LCS(S, reverse(S)).",
  space="O(n²).",
  dry=[
    ("S","'aebcbda'"),
    ("reverse","'adbcbea'"),
    ("LCS","'abcba' length 5"),
    ("Answer","7-5=2 ✅"),
  ],
  comp="O(n²) time and space.",
  take="Many palindrome problems = LCS with reverse.",
  challenge="What if both insert AND delete are allowed at cost 1? Same answer.",
  uiidea="String with mirror line; suggest which letters to insert.",
  viz="<div class='viz'><p class='muted center'>min inserts = n − LCS(S, reverse(S))</p></div>"
)

L(
  num=29, world="D", world_name="Strings", slug="min-deletions-equal", fun="🧽 Make Twins Match",
  ttl="Min Insertions/Deletions to Equal",
  obj="Convert string A into B using only insertions and deletions, with the fewest operations.",
  prob="Return min operations (insert in A or delete from A).",
  story="Two notes must match. You can erase letters from A or write new ones. Minimise edits.",
  brute="Edit-distance-style brute force.",
  trans="ops = (n - LCS(A,B)) + (m - LCS(A,B)) = n + m − 2·LCS.",
  rec="LCS recurrence.",
  memo="LCS table.",
  tab="Compute LCS, then formula.",
  space="O(n·m).",
  dry=[
    ("A,B","'heap','pea'"),
    ("LCS","'ea' length 2"),
    ("Ops","4+3-4 = 3 ✅"),
  ],
  comp="O(n·m).",
  take="Insertions to A ≡ Deletions from B.",
  challenge="Why doesn&rsquo;t replace help here? (Because we&rsquo;re only insert/delete.)",
  uiidea="Two strings; cross out / add letters to align them.",
  viz="<div class='viz'><p class='muted center'>ops = n + m − 2·LCS(A,B)</p></div>"
)

L(
  num=30, world="D", world_name="Strings", slug="edit-distance", fun="✏️ Typo Tamer",
  ttl="Edit Distance",
  obj="Find the minimum number of single-character edits to turn A into B (insert/delete/replace).",
  prob="Levenshtein distance.",
  story="Spell-checker: how many tiny edits turn 'kitten' into 'sitting'?",
  brute="Try all sequences of edits.",
  trans=("edit(i,j) = if A[i]==B[j] → edit(i-1,j-1); else 1 + min( insert, delete, replace )."),
  rec="As above.",
  memo="2D cache.",
  tab="dp[i][j].",
  space="2 rows.",
  dry=[
    ("A,B","'kitten','sitting'"),
    ("Edits","k→s, e→i, +g → 3 ✅"),
  ],
  comp="O(n·m) time, O(min(n,m)) space.",
  take="Three operations, one cell, one min — done.",
  challenge="What if insert and delete cost 2 but replace cost 1? Add weighted ops.",
  uiidea="Animate edits as arrows on a grid; color by operation.",
  viz="""
  <div class="viz">
    <p class="muted center">Edit grid for 'kitten' → 'sitting'</p>
  </div>"""
)

L(
  num=31, world="D", world_name="Strings", slug="wildcard-matching", fun="🔮 Mystery Letters",
  ttl="Wildcard Matching",
  obj="Match a string against a pattern with '?' (any one char) and '*' (any sequence).",
  prob="Return whether pattern p matches string s.",
  story="A search box that lets users type wildcards. Match or not?",
  brute="Recursion on (i,j) trying all '*' expansions.",
  trans=("dp(i,j): if p[j]=='?' or s[i]==p[j] → dp(i-1,j-1). If p[j]=='*' → dp(i-1,j) (consume) OR dp(i,j-1) (skip *)."),
  rec="As above.",
  memo="2D cache.",
  tab="dp[i][j].",
  space="2 rows.",
  dry=[
    ("s,p","'adceb','*a*b'"),
    ("dp","Match → True ✅"),
  ],
  comp="O(n·m) time and space.",
  take="'*' = the famous &lsquo;take or skip&rsquo; choice on a different stage.",
  challenge="What does pattern '***' match? (Any string.)",
  uiidea="Live wildcard tester — type pattern + string, watch DP cells light up.",
  viz="<div class='viz'><p class='muted center'>* = any sequence; ? = any 1 char</p></div>"
)

L(
  num=32, world="D", world_name="Strings", slug="distinct-subsequences", fun="🔍 Hidden Patterns",
  ttl="Distinct Subsequences",
  obj="Count how many distinct subsequences of S equal T.",
  prob="Return number of distinct ways to delete characters of S leaving exactly T.",
  story="A puzzle book asks: in how many ways can you erase letters from a long word to reveal a shorter target word?",
  brute="Try every subset of S.",
  trans="dp(i,j): if S[i]==T[j] → dp(i-1,j-1)+dp(i-1,j); else dp(i-1,j).",
  rec="As above.",
  memo="2D cache.",
  tab="dp[i][j].",
  space="2 rows.",
  dry=[
    ("S,T","'rabbbit','rabbit'"),
    ("Count","3 ✅ (three different ways to drop one b)"),
  ],
  comp="O(n·m) time, O(n·m) space.",
  take="Counting variant of LCS-style DP.",
  challenge="Why is dp(i, 0) = 1 for all i? (Empty target is always achievable.)",
  uiidea="Animate erasing letters; counter ticks up each time T is revealed.",
  viz="<div class='viz'><p class='muted center'>Count subsequences of S equal to T</p></div>"
)

# =========================================================================
# WORLD E — LIS -----------------------------------------------------------
# =========================================================================
L(
  num=33, world="E", world_name="LIS", slug="lis-n2", fun="📈 Tallest Tower of Books",
  ttl="Longest Increasing Subsequence (O(n²))",
  obj="Find the length of the longest strictly increasing subsequence.",
  prob="Length of the longest subsequence with all increasing values.",
  story="Stack books such that each new book is taller than the one below. What is the tallest tower?",
  brute="Try all subsequences.",
  trans="dp[i] = 1 + max(dp[j] for j<i with nums[j]<nums[i]).",
  rec="As above.",
  memo="1D cache.",
  tab="Outer i, inner j.",
  space="O(n).",
  dry=[
    ("Nums","[10,9,2,5,3,7,101,18]"),
    ("LIS","[2,3,7,18] length 4 ✅"),
  ],
  comp="O(n²) time.",
  take="LIS-style DP looks left for smaller predecessors.",
  challenge="What if 'increasing' means non-strict (≤)? Replace < with ≤.",
  uiidea="Books in a row; tap to add to tower if taller than top.",
  viz="""
  <div class="viz">
    <p class="muted center">Tap books to stack increasing tower</p>
    <div class="coins">
      <div class="coin">10</div><div class="coin">9</div><div class="coin">2</div><div class="coin">5</div>
      <div class="coin">3</div><div class="coin">7</div><div class="coin">101</div><div class="coin">18</div>
    </div>
  </div>"""
)

L(
  num=34, world="E", world_name="LIS", slug="lis-bsearch", fun="⚡ Lightning Tower",
  ttl="LIS — O(n log n) with Binary Search",
  obj="Same task — but compute LIS faster using a clever sorted &lsquo;tails&rsquo; array.",
  prob="Length of LIS in O(n log n).",
  story="The librarian uses a magic notebook where every page records the smallest possible tail of an LIS of that length.",
  brute="O(n²) DP.",
  trans=("Maintain tails[]: tails[k] = smallest tail of any increasing subseq of length k+1. "
         "For each x, binary search in tails for the leftmost ≥ x; replace it (or append)."),
  rec="Iterative.",
  memo="N/A.",
  tab="Build tails by scanning nums.",
  space="O(n).",
  dry=[
    ("Nums","[10,9,2,5,3,7,101,18]"),
    ("Tails progression","[10] → [9] → [2] → [2,5] → [2,3] → [2,3,7] → [2,3,7,101] → [2,3,7,18]"),
    ("LIS length","4 ✅"),
  ],
  comp="O(n log n).",
  take="The tails array does not equal the LIS itself, but its length does.",
  challenge="Why is tails always non-decreasing? (Because a longer LIS must end with a value ≥ the shorter one&rsquo;s smallest tail.)",
  uiidea="Animate the tails array updating as numbers stream in.",
  viz="""
  <div class="viz center">
    <pre class="code">tails: [2, 3, 7, 18]   length = 4</pre>
  </div>"""
)

L(
  num=35, world="E", world_name="LIS", slug="number-of-lis", fun="🔢 Counting Towers",
  ttl="Number of Longest Increasing Subsequences",
  obj="Count how many distinct LIS of maximum length exist.",
  prob="Return the count of LISs whose length equals the LIS length.",
  story="The librarian asks: how many tallest possible towers exist? (Same height, different choices of books.)",
  brute="Enumerate.",
  trans="Run O(n²) LIS but maintain count[i] = # of LIS ending at i.",
  rec="See above.",
  memo="N/A.",
  tab="length[i], count[i].",
  space="O(n).",
  dry=[
    ("Nums","[1,3,5,4,7]"),
    ("LIS length","4"),
    ("Count","2 ([1,3,5,7] and [1,3,4,7]) ✅"),
  ],
  comp="O(n²) time.",
  take="Combine length and count DP arrays — common trick.",
  challenge="What about [2,2,2,2,2]? (LIS length 1, count 5.)",
  uiidea="Show all distinct max-towers side by side as cards.",
  viz="<div class='viz'><p class='muted center'>Two arrays side by side: length[i] and count[i]</p></div>"
)

L(
  num=36, world="E", world_name="LIS", slug="bitonic", fun="🏔️ Mountain Range",
  ttl="Longest Bitonic Subsequence",
  obj="Find the longest subsequence that strictly increases then strictly decreases.",
  prob="Up then down — find the longest such subsequence.",
  story="Find the longest mountain skyline you can carve from a list of heights.",
  brute="Try every peak.",
  trans="LIS_left[i] from left + LIS_right[i] from right − 1.",
  rec="Two LIS DPs.",
  memo="N/A.",
  tab="Run LIS forward and backward.",
  space="O(n).",
  dry=[
    ("Nums","[1,11,2,10,4,5,2,1]"),
    ("Best","[1,2,10,4,2,1] length 6 ✅"),
  ],
  comp="O(n²).",
  take="Combine two simpler DPs to solve a compound shape.",
  challenge="What if the sequence must be strictly increasing then constant then decreasing? Add a third DP.",
  uiidea="Plot heights as bars; highlight the chosen mountain shape.",
  viz="<div class='viz'><p class='muted center'>increasing→peak→decreasing</p></div>"
)

L(
  num=37, world="E", world_name="LIS", slug="largest-divisible-subset", fun="🔗 Divisibility Chain",
  ttl="Largest Divisible Subset",
  obj="Find the largest subset such that every pair (a,b) satisfies a%b==0 or b%a==0.",
  prob="Largest subset where every pair is divisible.",
  story="Chain of magic gears — each gear must divide its neighbour. Build the longest chain.",
  brute="Enumerate.",
  trans="Sort. Then it&rsquo;s LIS-style: dp[i] = max dp[j]+1 where nums[i]%nums[j]==0.",
  rec="Same.",
  memo="N/A.",
  tab="Sort first, then DP.",
  space="O(n).",
  dry=[
    ("Nums","[1,2,4,8]"),
    ("Chain","[1,2,4,8] length 4 ✅"),
  ],
  comp="O(n²).",
  take="Sort + LIS-style is a generalisation pattern.",
  challenge="What if duplicates exist? Are they allowed? (Only one copy per chain typically.)",
  uiidea="Gears with numbers; visualise chain links.",
  viz="<div class='viz'><p class='muted center'>1 → 2 → 4 → 8</p></div>"
)

L(
  num=38, world="E", world_name="LIS", slug="longest-string-chain", fun="🔤 Add a Letter",
  ttl="Longest String Chain",
  obj="Find the longest chain of words where each next word adds exactly one letter.",
  prob="A predecessor of W differs by removing exactly one character. Find longest chain.",
  story="A vocabulary-builder game: each turn, add one letter to the previous word.",
  brute="Enumerate chains.",
  trans="Sort by length. dp[w] = 1 + max(dp[predecessor]).",
  rec="Map word → length.",
  memo="HashMap-based DP.",
  tab="Sort + iterate.",
  space="O(n).",
  dry=[
    ("Words","['a','ab','abc','xy']"),
    ("Chain","'a'→'ab'→'abc' length 3 ✅"),
  ],
  comp="O(n·L²) time (L max length).",
  take="DP keys can be strings, not just indices.",
  challenge="What if removing instead of adding? Same problem, reversed.",
  uiidea="Words floating; arrows draw between predecessors.",
  viz="<div class='viz'><p class='muted center'>a → ab → abc → abcd …</p></div>"
)

# =========================================================================
# WORLD F — STOCKS --------------------------------------------------------
# =========================================================================
L(
  num=39, world="F", world_name="Stocks", slug="stock-1", fun="💹 Buy Low, Sell High (Once)",
  ttl="Best Time to Buy and Sell Stock I",
  obj="One buy, one sell. Maximise profit.",
  prob="prices[i] = price on day i. Single buy + single sell. Max profit.",
  story="A trader allowed only one trade. Track minimum so far, watch profit grow.",
  brute="Try all (buy,sell) pairs (n²).",
  trans="Track min so far; ans = max(price - min_so_far).",
  rec="Iterative.",
  memo="N/A.",
  tab="One pass.",
  space="O(1).",
  dry=[
    ("Prices","[7,1,5,3,6,4]"),
    ("Min so far","7,1,1,1,1,1"),
    ("Best","Sell at 6, bought at 1 → 5 ✅"),
  ],
  comp="O(n) time, O(1) space.",
  take="Maintain rolling min, compute best diff.",
  challenge="What if prices are all decreasing? (Profit = 0.)",
  uiidea="Mini chart with buy/sell markers.",
  viz="<div class='viz'><p class='muted center'>chart with one buy + one sell marker</p></div>"
)

L(
  num=40, world="F", world_name="Stocks", slug="stock-2", fun="🤑 Daily Hustle",
  ttl="Best Time to Buy and Sell Stock II",
  obj="Unlimited trades. Maximise profit.",
  prob="Buy/sell as many times as you like (one position at a time).",
  story="A day trader sums every uphill segment of the price chart.",
  brute="Try all sequences.",
  trans="Greedy/DP: profit += max(0, prices[i] - prices[i-1]).",
  rec="DP with state (day, holding).",
  memo="2D cache (n,2).",
  tab="dp[i][0]=max(dp[i-1][0], dp[i-1][1]+p[i]); dp[i][1]=max(dp[i-1][1], dp[i-1][0]-p[i]).",
  space="Two variables (cash, hold).",
  dry=[
    ("Prices","[7,1,5,3,6,4]"),
    ("Uphills","(1→5)=4, (3→6)=3 → total 7 ✅"),
  ],
  comp="O(n) time, O(1) space.",
  take="Two states (have stock / no stock) cover unlimited trades.",
  challenge="If you can only hold up to 2 stocks at a time, redesign the state.",
  uiidea="Chart with multiple buy/sell pairs marked.",
  viz="<div class='viz'><p class='muted center'>Profit = sum of all uphill segments</p></div>"
)

L(
  num=41, world="F", world_name="Stocks", slug="stock-3", fun="🎟️ Two Tickets Only",
  ttl="Best Time to Buy and Sell Stock III",
  obj="At most 2 transactions. Maximise profit.",
  prob="Buy+sell at most twice.",
  story="The exchange limits you to 2 trades. Plan carefully.",
  brute="Try all pairs.",
  trans="State (day, transactions_used, holding). 4 transitions.",
  rec="dp(day, k, hold).",
  memo="3D cache.",
  tab="dp[day][k][hold]; tiny since k≤2.",
  space="O(1) (constant states).",
  dry=[
    ("Prices","[3,3,5,0,0,3,1,4]"),
    ("Best","(0→5)=2 + (0→4)=4 → 6 ✅"),
  ],
  comp="O(n).",
  take="Add a transaction count to the state.",
  challenge="Verify that dp[*][0][0] = 0.",
  uiidea="Two coloured trade-pair markers on the chart.",
  viz="<div class='viz'><p class='muted center'>states: (day, k=0..2, hold=0/1)</p></div>"
)

L(
  num=42, world="F", world_name="Stocks", slug="stock-4", fun="🎫 K Tickets",
  ttl="Best Time to Buy and Sell Stock IV",
  obj="At most K transactions. Maximise profit.",
  prob="General K version.",
  story="The exchange now sets a custom limit K each season.",
  brute="Combos.",
  trans="State (day, k, hold). Same recurrence as III but k up to K.",
  rec="dp(day, k, hold).",
  memo="3D cache (n·(K+1)·2).",
  tab="Iterate days; update for each k.",
  space="O(K).",
  dry=[
    ("Prices, K","[3,2,6,5,0,3], K=2 → 7 ✅"),
  ],
  comp="O(n·K).",
  take="When K ≥ n/2, problem reduces to Stock II (unlimited).",
  challenge="Show the reduction for K large.",
  uiidea="Slider for K, chart re-marks trades.",
  viz="<div class='viz'><p class='muted center'>state (day, k, hold)</p></div>"
)

L(
  num=43, world="F", world_name="Stocks", slug="stock-cooldown", fun="❄️ One-Day Cooldown",
  ttl="Best Time to Buy and Sell Stock with Cooldown",
  obj="Unlimited trades — but after a sell, you must rest one day.",
  prob="Cannot buy on the day right after a sell.",
  story="You earned profit; the broker says &ldquo;take a breather.&rdquo;",
  brute="Recurse with state (day, holding, justSold).",
  trans=("dp_hold[i]=max(dp_hold[i-1], dp_cash[i-2]-p[i]); dp_cash[i]=max(dp_cash[i-1], dp_hold[i-1]+p[i])."),
  rec="As above.",
  memo="2D cache.",
  tab="Maintain three rolling vars.",
  space="O(1).",
  dry=[
    ("Prices","[1,2,3,0,2]"),
    ("Best","Buy 1 sell 2 cooldown buy 0 sell 2 → 3 ✅"),
  ],
  comp="O(n).",
  take="Cooldown adds one extra index of look-back.",
  challenge="What if cooldown lasts 2 days? Adjust the look-back.",
  uiidea="Chart shows greyed-out cooldown days.",
  viz="<div class='viz'><p class='muted center'>Sell ⇒ next day = cooldown 🚫</p></div>"
)

L(
  num=44, world="F", world_name="Stocks", slug="stock-fee", fun="💸 The Tax Man",
  ttl="Best Time to Buy and Sell Stock with Transaction Fee",
  obj="Unlimited trades — but each sale charges a fixed fee.",
  prob="profit -= fee on every sell.",
  story="The broker takes a cut on every sale. Trade only when worth it.",
  brute="Combos.",
  trans="dp_hold[i]=max(dp_hold[i-1], dp_cash[i-1]-p[i]); dp_cash[i]=max(dp_cash[i-1], dp_hold[i-1]+p[i]-fee).",
  rec="As above.",
  memo="2D cache.",
  tab="Two rolling vars.",
  space="O(1).",
  dry=[
    ("Prices, fee","[1,3,2,8,4,9], fee=2 → 8 ✅"),
  ],
  comp="O(n).",
  take="Fees move the break-even point — the recurrence barely changes.",
  challenge="What if fee depends on amount? Modify the formula.",
  uiidea="Chart with a shrinking profit bar after each sell (fee).",
  viz="<div class='viz'><p class='muted center'>Each sell charges fee — fewer but bigger trades win.</p></div>"
)

# =========================================================================
# WORLD G — PARTITION DP --------------------------------------------------
# =========================================================================
L(
  num=45, world="G", world_name="Partition DP", slug="mcm", fun="🧮 Where to Multiply First?",
  ttl="Matrix Chain Multiplication",
  obj="Choose the parenthesisation of a chain of matrix multiplications that minimises scalar multiplications.",
  prob="Given dims[], minimise cost of multiplying the chain.",
  story="Matrices are friends but multiplication order matters. Save your CPU some grief.",
  brute="Try every split (Catalan).",
  trans="dp(i,j) = min over k of dp(i,k)+dp(k+1,j) + dims[i-1]·dims[k]·dims[j].",
  rec="As above.",
  memo="2D cache.",
  tab="Fill by chain length.",
  space="O(n²).",
  dry=[
    ("Dims","[10,30,5,60]"),
    ("Best","(A·B)·C = 10·30·5 + 10·5·60 = 1500+3000 = 4500 ✅"),
  ],
  comp="O(n³).",
  take="When you ask &lsquo;where to split?&rsquo; — partition DP.",
  challenge="Reconstruct the parenthesisation.",
  uiidea="Drag parentheses around matrices; total cost recomputes live.",
  viz="<div class='viz'><p class='muted center'>(A·(B·C)) vs ((A·B)·C)</p></div>"
)

L(
  num=46, world="G", world_name="Partition DP", slug="cut-stick", fun="🪓 Where to Cut the Stick?",
  ttl="Minimum Cost to Cut a Stick",
  obj="Cut a stick at given positions in any order to minimise total cost (cost = current piece length).",
  prob="cuts[] gives positions; choose order to minimise total cut cost.",
  story="A carpenter must cut at given marks. Each cut costs the full piece&rsquo;s length. Order matters.",
  brute="Try every order.",
  trans="Sort cuts (with 0 and n added). dp(i,j)= min over k of dp(i,k)+dp(k,j) + (cuts[j]-cuts[i]).",
  rec="As above.",
  memo="2D cache.",
  tab="Fill by interval length.",
  space="O(n²).",
  dry=[
    ("Stick=7, cuts=[1,3,4,5]","Optimal answer = 16."),
  ],
  comp="O(n³).",
  take="Same partition skeleton as MCM.",
  challenge="What if cost = constant 1? Order doesn&rsquo;t matter.",
  uiidea="Stick with red marks; tap to choose cut order; total cost shown.",
  viz="<div class='viz'><p class='muted center'>cut order matters!</p></div>"
)

L(
  num=47, world="G", world_name="Partition DP", slug="burst-balloons", fun="🎈 Pop the Balloons",
  ttl="Burst Balloons",
  obj="Burst balloons in an order that maximises coins (coins = left·me·right at burst time).",
  prob="Each balloon has a value. Pop one — earn left·me·right of remaining neighbours.",
  story="Pop balloons cleverly; pop big ones first so they earn more from juicy neighbours.",
  brute="Try every permutation.",
  trans=("Add 1 to both ends. dp(i,j) = max over k in (i,j) of dp(i,k)+dp(k,j)+nums[i]·nums[k]·nums[j]."),
  rec="As above.",
  memo="2D cache.",
  tab="Fill by interval length.",
  space="O(n²).",
  dry=[
    ("Nums","[3,1,5,8] → answer 167 ✅"),
  ],
  comp="O(n³).",
  take="Think &lsquo;what if k is the LAST balloon to burst in this range?&rsquo; — the trick of this problem.",
  challenge="Prove why &lsquo;last to burst&rsquo; framing is correct.",
  uiidea="Balloons in a row; tap to pop; live coin counter.",
  viz="<div class='viz'><p class='muted center'>🎈🎈🎈🎈 — pick the LAST one in each interval</p></div>"
)

L(
  num=48, world="G", world_name="Partition DP", slug="palindrome-partition-2", fun="🔪 Slice into Palindromes",
  ttl="Palindrome Partitioning II",
  obj="Cut a string into palindromic pieces with the minimum number of cuts.",
  prob="Min cuts so every piece is a palindrome.",
  story="A printer accepts only palindrome words. Slice the message into the fewest palindrome chunks.",
  brute="Try every cut combination.",
  trans="dp[i] = min cuts for s[0..i]; if s[j..i] palindrome → dp[i] = min(dp[i], 1+dp[j-1]).",
  rec="With memo.",
  memo="1D + palindrome table.",
  tab="Precompute palindrome[i][j], then DP.",
  space="O(n²).",
  dry=[
    ("S","'aab'"),
    ("Best","'aa'|'b' → 1 cut ✅"),
  ],
  comp="O(n²).",
  take="Precomputing palindrome flags speeds the inner loop.",
  challenge="Reconstruct the cut positions.",
  uiidea="String with movable scissors; pieces turn green if palindrome.",
  viz="<div class='viz'><p class='muted center'>'aabb' → 'aa'|'bb' (1 cut)</p></div>"
)

L(
  num=49, world="G", world_name="Partition DP", slug="partition-max-sum", fun="📦 K-Sized Boxes",
  ttl="Partition Array for Maximum Sum",
  obj="Partition array into chunks of length ≤ K. Each chunk becomes max-of-chunk · length. Maximise total.",
  prob="Maximise sum of (max·len) across all chunks.",
  story="Pack items into boxes of size ≤ K; you can pretend every item in a box is the heaviest one. Maximise total.",
  brute="Try all partitions.",
  trans="dp[i] = max over j=1..K of dp[i-j] + j·max(arr[i-j..i-1]).",
  rec="With memo.",
  memo="1D cache.",
  tab="As above.",
  space="O(n).",
  dry=[
    ("Arr, K","[1,15,7,9,2,5,10], K=3 → 84 ✅"),
  ],
  comp="O(n·K).",
  take="Decide where the next chunk ends, take max, recurse.",
  challenge="What if K = n? You always pick max·n. Verify.",
  uiidea="Boxes drag-resize up to size K; total updates.",
  viz="<div class='viz'><p class='muted center'>chunks ≤ K · each contributes max·len</p></div>"
)

# =========================================================================
# WORLD H — ADVANCED ------------------------------------------------------
# =========================================================================
L(
  num=50, world="H", world_name="Advanced", slug="largest-rect-histogram", fun="📊 Tallest Hidden Rectangle",
  ttl="Largest Rectangle in Histogram",
  obj="Given heights[], find the area of the largest rectangle that fits within the histogram.",
  prob="Largest axis-aligned rectangle inside the histogram.",
  story="A stack-of-bars puzzle: what&rsquo;s the biggest rectangle hiding inside?",
  brute="Try every (l,r) pair (n²).",
  trans=("Use a monotonic stack: for each bar, find Previous-Smaller-Element and Next-Smaller-Element. "
         "Width = NSE - PSE - 1; area = h[i]·width."),
  rec="N/A — iterative stack technique.",
  memo="N/A.",
  tab="Single stack pass.",
  space="O(n).",
  dry=[
    ("Heights","[2,1,5,6,2,3]"),
    ("Best","(5,6) gives 2·5? actually width 2 height 5 = 10 ✅"),
  ],
  comp="O(n).",
  take="Stack DP solves &lsquo;range smallest&rsquo; problems in O(n).",
  challenge="Print the (l,r) of the largest rectangle.",
  uiidea="Histogram bars; outline the winning rectangle.",
  viz="<div class='viz'><p class='muted center'>Use a monotonic stack for O(n).</p></div>"
)

L(
  num=51, world="H", world_name="Advanced", slug="maximum-rectangle", fun="🟦 Biggest White Square",
  ttl="Maximum Rectangle (Binary Matrix)",
  obj="Find the largest rectangle of 1s in a 0/1 matrix.",
  prob="Largest rectangle containing only 1s.",
  story="A floor of light/dark tiles. Largest light slab?",
  brute="O((mn)²)",
  trans="For each row, treat heights[j] = consecutive 1s above row j; apply Largest Rectangle in Histogram per row.",
  rec="N/A.",
  memo="N/A.",
  tab="Heights per row; histogram each row.",
  space="O(n).",
  dry=[
    ("Matrix","[[1,0,1,0,0],[1,0,1,1,1],[1,1,1,1,1],[1,0,0,1,0]]"),
    ("Answer","6 ✅"),
  ],
  comp="O(m·n).",
  take="Combine per-row preprocessing with histogram solution.",
  challenge="If matrix is all 1s of size m×n, answer = m·n.",
  uiidea="Heat-map the matrix; outline winning rectangle.",
  viz="<div class='viz'><p class='muted center'>Row heights → histogram → max rectangle.</p></div>"
)

L(
  num=52, world="H", world_name="Advanced", slug="word-break", fun="📖 Dictionary Detective",
  ttl="Word Break",
  obj="Decide if a string can be split into a sequence of dictionary words.",
  prob="Return true/false: can s be split into dict words?",
  story="A messageless string of letters — can we split it into real words?",
  brute="Try every split.",
  trans="dp[i] = true if some j&lt;i has dp[j] && s[j..i] in dict.",
  rec="With memo.",
  memo="1D cache.",
  tab="Dict in a set; iterate i.",
  space="O(n).",
  dry=[
    ("S, dict","'leetcode', {'leet','code'}"),
    ("Result","true ✅"),
  ],
  comp="O(n²) time.",
  take="Boolean prefix DP — &lsquo;reach this point&rsquo; using a known building block.",
  challenge="What if dict = {''}? (Trivially true if you allow empty.)",
  uiidea="String slider; segments highlight green if a dict word.",
  viz="<div class='viz'><p class='muted center'>'leetcode' = 'leet' + 'code' ✅</p></div>"
)

L(
  num=53, world="H", world_name="Advanced", slug="word-break-2", fun="📚 All Possible Sentences",
  ttl="Word Break II",
  obj="Return ALL possible sentences from valid splits, not just whether one exists.",
  prob="List every valid split of s using dict words.",
  story="The detective wants every possible reading of the cryptic note.",
  brute="DFS + dict checks.",
  trans="memo[i] = list of strings starting at i. Combine with each valid prefix from dict.",
  rec="With memo of substrings.",
  memo="map from suffix index → list.",
  tab="Top-down memo is most natural.",
  space="O(answers).",
  dry=[
    ("S, dict","'pineapplepenapple', {'apple','pen','applepen','pine','pineapple'}"),
    ("Sentences","'pine apple pen apple', 'pineapple pen apple', 'pine applepen apple' ✅"),
  ],
  comp="Exponential in worst case (output-bounded).",
  take="When asked to list all answers, store lists in the memo.",
  challenge="Estimate the maximum number of sentences for a length-N string.",
  uiidea="Tree of expansions; each leaf is a valid sentence.",
  viz="<div class='viz'><p class='muted center'>memo: suffix → list of sentence-tails</p></div>"
)

# --------------------------------------------------------------------------
# Render template
# --------------------------------------------------------------------------
def render_level(L, prev_link, next_link, prev_title, next_title):
  num = L["num"]
  filename = f"level-{num:02d}-{L['slug']}.html"
  pretty_num = f"Level {num:02d}"
  body = ""
  body += section("🎮", "Objective", f"<p>{L['obj']}</p>")
  body += section("🧠", "Problem (in tiny words)", f"<p>{L['prob']}</p>")
  body += section("🎭", "Story", f"<p>{L['story']}</p>")
  body += section("😵", "Brute force (the painful way)", f"<p>{L['brute']}</p>")
  body += section("🌱", "From brute → recursion", f"<p>{L['trans']}</p>")
  body += section("🔁", "Recursion", f"<p>{L['rec']}</p>" + code_block(f"# pseudo\n{L['rec']}"))
  body += section("🧩", "Memoization", f"<p>{L['memo']}</p>")
  body += section("🧱", "Tabulation", f"<p>{L['tab']}</p>")
  body += section("🚀", "Space optimisation", f"<p>{L['space']}</p>")

  # Dry run as stepper
  steps_html = ""
  for label, txt in L["dry"]:
    steps_html += f'<div class="dryrun-step hidden"><div class="label">{html.escape(label)}</div>{txt}</div>'
  dry = f"""
    <p>Tap <em>Next step</em> to walk through the table cell-by-cell.</p>
    <div data-stepper>
      <div class="stepper">
        <button data-step="prev" class="ghost">⟵ Prev</button>
        <button data-step="next">Next ⟶</button>
        <button data-step="all" class="ghost">Show all</button>
        <button data-step="reset" class="ghost">↺</button>
        <div class="progress"><span></span></div>
        <div class="label">Step 1 / {len(L['dry'])}</div>
      </div>
      {steps_html}
    </div>
    {L['viz']}
  """
  body += section("🧪", "Dry run", dry)
  body += section("📊", "Complexity", f"<p>{L['comp']}</p>")
  body += section("💡", "Key takeaway", f"<p><strong>{L['take']}</strong></p>")

  body += section("🎯", "Mini challenge",
      f"<p>{L['challenge']}</p>"
      f"<p><button class='btn small' data-celebrate>I tried it ✅</button></p>")

  body += section("🎮", "Game UI idea", f"<p>{L['uiidea']}</p>")

  prev_html = (f'<a class="up" href="{prev_link}">⟵ {prev_title}</a>'
               if prev_link else '<a class="up" href="../dp-roadmap.html">↑ Roadmap</a>')
  next_html = (f'<a class="next" href="{next_link}">{next_title} ⟶</a>'
               if next_link else '<a class="next" href="../dp-roadmap.html">🏁 Roadmap</a>')

  page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{pretty_num}: {html.escape(L['fun'])} — DP Adventure</title>
<meta name="description" content="{html.escape(L['ttl'])} — playful walkthrough.">
<link rel="stylesheet" href="../styles.css">
<link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><text y='52' font-size='52'>🧩</text></svg>">
</head>
<body>

<header class="topbar">
  <a href="../index.html" class="brand">
    <span class="logo">A</span><span>Algos&nbsp;Adventure</span>
  </a>
  <nav>
    <a href="../dp-roadmap.html">Roadmap</a>
    <a href="../index.html">Home</a>
  </nav>
</header>

<main class="container-narrow">

  <section class="level-header">
    <div class="crumbs"><a href="../dp-roadmap.html">Roadmap</a> · World {L['world']} · {L['world_name']}</div>
    <span class="level-tag">{pretty_num}</span>
    <h1>{html.escape(L['fun'])}</h1>
    <p class="muted">{html.escape(L['ttl'])}</p>
    <div class="pillrow">
      <span class="badge">World {L['world']}</span>
      <span class="badge alt">{L['world_name']}</span>
    </div>
  </section>

  {body}

  <nav class="bottom-nav">
    {prev_html}
    {next_html}
  </nav>

</main>

<footer class="site">Algos Adventure · <a href="../index.html">Home</a> · <a href="../dp-roadmap.html">Roadmap</a></footer>
<script src="../script.js"></script>
</body>
</html>
"""
  return filename, page

# --------------------------------------------------------------------------
# Roadmap renderer
# --------------------------------------------------------------------------
WORLDS = [
  ("A","Basics (1D DP)","🪜 1D foundations — start here. Tiny problems, big a-ha moments."),
  ("B","Grid DP","🌐 2D grids and paths."),
  ("C","Subsequences / Knapsack","🎒 Pick or skip. Pebbles, coins, rods."),
  ("D","Strings","🔤 Letters, edits, alignments."),
  ("E","LIS","📈 Longest increasing magic."),
  ("F","Stocks","💸 Buy low, sell high."),
  ("G","Partition DP","✂️ Where to cut?"),
  ("H","Advanced","🏰 Boss-fight problems."),
]

def render_roadmap():
  parts = []
  parts.append("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DP Roadmap — Algos Adventure</title>
<meta name="description" content="The 53-level Dynamic Programming roadmap, grouped into 8 friendly worlds.">
<link rel="stylesheet" href="styles.css">
<link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><text y='52' font-size='52'>🗺️</text></svg>">
</head>
<body>

<header class="topbar">
  <a href="index.html" class="brand"><span class="logo">A</span><span>Algos&nbsp;Adventure</span></a>
  <nav>
    <a href="index.html">Home</a>
    <a href="https://github.com/tools-maker-art/algos" target="_blank" rel="noopener">GitHub</a>
  </nav>
</header>

<main class="container">

  <section class="hero">
    <span class="badge">53 levels · 8 worlds</span>
    <h1>The DP <span class="gradient">Roadmap</span></h1>
    <p class="lead">Pick a world, pick a level. Each one is a tiny game.</p>
  </section>
""")
  for letter, name, desc in WORLDS:
    parts.append(f'  <section class="section" id="world-{letter}">\n')
    parts.append(f'    <h2><span class="group-tag">World {letter}</span> {name}</h2>\n')
    parts.append(f'    <p class="group-desc">{desc}</p>\n')
    parts.append('    <div class="levels-grid">\n')
    in_world = [L for L in LEVELS if L["world"] == letter]
    for lv in in_world:
      filename = f"level-{lv['num']:02d}-{lv['slug']}.html"
      parts.append(
        f'      <a class="level-card" data-href="levels/{filename}" href="levels/{filename}">'
        f'<span class="num">{lv["num"]:02d}</span>'
        f'<span class="meta"><span class="ttl">{html.escape(lv["fun"])}</span>'
        f'<span class="sub">{html.escape(lv["ttl"])}</span></span></a>\n'
      )
    parts.append('    </div>\n')
    parts.append('  </section>\n')
  parts.append("""
</main>

<footer class="site">Made with 💜 · <a href="index.html">Home</a></footer>
<script src="script.js"></script>
</body>
</html>
""")
  return "".join(parts)

# --------------------------------------------------------------------------
# WRITE EVERYTHING
# --------------------------------------------------------------------------
def main():
  # roadmap
  (ROOT / "dp-roadmap.html").write_text(render_roadmap(), encoding="utf-8")

  # levels
  for i, lv in enumerate(LEVELS):
    prev_link = next_link = ""
    prev_title = next_title = ""
    if i > 0:
      p = LEVELS[i-1]
      prev_link = f"level-{p['num']:02d}-{p['slug']}.html"
      prev_title = f"L{p['num']:02d} {p['fun']}"
    if i < len(LEVELS)-1:
      n = LEVELS[i+1]
      next_link = f"level-{n['num']:02d}-{n['slug']}.html"
      next_title = f"L{n['num']:02d} {n['fun']}"
    fname, content = render_level(lv, prev_link, next_link, prev_title, next_title)
    (LEVELS_DIR / fname).write_text(content, encoding="utf-8")

  print(f"Generated {len(LEVELS)} levels + roadmap.")
  print(f"Worlds present:", sorted({l['world'] for l in LEVELS}))

if __name__ == "__main__":
  main()
