#!/usr/bin/env python3
"""DP Adventure — generates Levels 2..53 as INTERACTIVE games.

Every level loads ../level-runtime.js, which mounts widgets from the per-level
<script type="application/json" id="level-data"> block on the page. Level 1 is
left untouched (it's hand-crafted with its own bunny logic).
"""
import os, html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "levels"
OUT.mkdir(exist_ok=True)

def esc(s): return html.escape(str(s))

PSEUDO_KW = {"int","return","if","else","for","while","new","void","boolean","char","String","static","public","private","class","import","true","false","null","Math","Arrays","HashSet","HashMap","Set","Map","List","ArrayList","Deque","ArrayDeque","Integer","Collections","switch","case","break","continue"}
def jhi(code):
    token = re.compile(r'//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\b\d+\b|\b[A-Za-z_][A-Za-z_0-9]*\b')
    parts = []
    last = 0
    for m in token.finditer(code):
        parts.append(esc(code[last:m.start()]))
        raw = m.group(0)
        safe = esc(raw)
        if raw.startswith('//'):
            parts.append(f'<span class="cmt">{safe}</span>')
        elif raw.startswith('"') or raw.startswith("'"):
            parts.append(f'<span class="str">{safe}</span>')
        elif raw.isdigit():
            parts.append(f'<span class="num">{safe}</span>')
        elif raw in PSEUDO_KW:
            parts.append(f'<span class="kw">{safe}</span>')
        else:
            parts.append(safe)
        last = m.end()
    parts.append(esc(code[last:]))
    return "".join(parts)

def _plain_params(params):
    out = []
    for part in params.split(","):
        p = part.strip()
        p = re.sub(r'^(final\s+)?(?:int|boolean|char|String|Integer|Boolean)(?:\[\])?\s+', '', p)
        p = re.sub(r'^(?:int|boolean|String)(?:\[\]){2}\s+', '', p)
        p = re.sub(r'^(?:List|Set|Map)<[^>]+>\s+', '', p)
        out.append(p)
    return ", ".join([p for p in out if p])

def pseudoize(code):
    lines = []
    indent = 0
    sig = re.compile(r'^(?:public\s+|private\s+|static\s+)*(?:int|boolean|void|char|String|Integer|Boolean|List<[^>]+>|Set<[^>]+>|Map<[^>]+>|Boolean\[\]|int\[\]|int\[\]\[\]|String\[\])\s+([A-Za-z_]\w*)\((.*)\)\s*\{?$')
    for raw in code.splitlines():
        s = raw.strip()
        stripped_brace = False
        while s.startswith("}"):
            indent = max(0, indent - 1)
            s = s[1:].strip()
            stripped_brace = True
        if not s:
            if not stripped_brace:  # preserve intentional blank lines; skip lone-} blank lines
                lines.append("")
            continue

        opens = s.count("{")
        closes = s.count("}")

        m = sig.match(s)
        if m:
            lines.append("    " * indent + f"{m.group(1)}({_plain_params(m.group(2))}):")
            indent += max(0, opens - closes)
            continue

        s = s.replace("{", "").replace("}", "").rstrip(";")
        s = s.replace("Math.", "").replace("Integer.MAX_VALUE", "very_big_number")
        s = s.replace("&&", "and").replace("||", "or").replace("true", "yes").replace("false", "no").replace("null", "empty")
        s = re.sub(r'new\s+(?:int|boolean|String)(\[[^\]]+\])+', 'new boxes', s)
        s = re.sub(r'new\s+(?:HashSet|HashMap|ArrayList|ArrayDeque)<>\(([^)]*)\)', r'copy of \1', s)
        s = re.sub(r'\b(?:int|boolean|char|String|Integer|Boolean)(?:\[\]){0,2}\s+', '', s)
        s = re.sub(r'\b(?:List|Set|Map)<[^>]+>\s+', '', s)
        s = s.replace(".length()", ".length").replace(".isEmpty()", " is empty")

        m = re.match(r'for\s*\((\w+)\s*=\s*([^;]+);\s*\1\s*<=\s*([^;]+);\s*\1\+\+\)\s*(.+)', s)
        if m:
            lines.append("    " * indent + f"for {m.group(1)} from {m.group(2)} to {m.group(3)}:")
            lines.append("    " * (indent + 1) + m.group(4))
            continue
        m = re.match(r'for\s*\((\w+)\s*=\s*([^;]+);\s*\1\s*<\s*([^;]+);\s*\1\+\+\)\s*(.+)', s)
        if m:
            lines.append("    " * indent + f"for {m.group(1)} from {m.group(2)} to before {m.group(3)}:")
            lines.append("    " * (indent + 1) + m.group(4))
            continue

        m = re.match(r'for\s*\((\w+)\s*=\s*([^;]+);\s*\1\s*<=\s*([^;]+);\s*\1\+\+\)', s)
        if m:
            s = f"for {m.group(1)} from {m.group(2)} to {m.group(3)}:"
        m = re.match(r'for\s*\((\w+)\s*=\s*([^;]+);\s*\1\s*<\s*([^;]+);\s*\1\+\+\)', s)
        if m:
            s = f"for {m.group(1)} from {m.group(2)} to before {m.group(3)}:"
        m = re.match(r'for\s*\((\w+)\s*:\s*([^)]+)\)', s)
        if m:
            s = f"for each {m.group(1)} in {m.group(2)}:"
        s = re.sub(r'^if\s*\((.*)\)$', r'if \1:', s)
        s = re.sub(r'^else if\s*\((.*)\)$', r'otherwise if \1:', s)
        s = re.sub(r'^else$', 'otherwise:', s)
        s = re.sub(r'^while\s*\((.*)\)$', r'while \1:', s)
        s = s.replace(" ? ", " if ")
        s = s.replace(" : ", " else ")

        lines.append("    " * indent + s)
        indent += max(0, opens - closes)
        if closes > opens:
            indent = max(0, indent - (closes - opens))
    return "\n".join(line.rstrip() for line in lines)

def jcode_block(title, hint, hint_cls, code):
    code = pseudoize(code)
    return f"""<div class="code-block">
  <div class="code-head">
    <span><span class="lang">PSEUDO</span> &nbsp; {title}</span>
    <span class="upgrade {hint_cls}">{hint}</span>
  </div>
<pre>{jhi(code)}</pre>
</div>"""

def code_details(name, title, hint, hint_cls, code):
    return f"""<details class="explainer">
  <summary>👀 see the pseudocode ({name})</summary>
  <div class="body">{jcode_block(title, hint, hint_cls, code)}</div>
</details>"""

# ---------- Level data ----------
LEVELS = []
def L(num, world, world_name, slug, fun, ttl, icon, **kw):
    kw.update(num=num, world=world, world_name=world_name, slug=slug, fun=fun, ttl=ttl, icon=icon)
    LEVELS.append(kw)

# tiny tree builder for a fib-like 1D recurrence (scene-2 brute viz)
def build_fib_tree(n, label_fn):
    nodes = []; idc = [0]; seen = {}
    def rec(v, d, p):
        idx = idc[0]; idc[0] += 1
        dup = v in seen
        base = (v <= 1)
        nodes.append({'id':idx,'lbl':label_fn(v),'d':d,'p':p,'dup':dup,'base':base})
        seen[v] = True
        if not base:
            rec(v-1, d+1, idx); rec(v-2, d+1, idx)
        return idx
    rec(n, 0, None)
    return nodes

def build_kchoice_tree(n, K, label_fn):
    nodes = []; idc = [0]; seen = {}
    def rec(v, d, p):
        idx = idc[0]; idc[0] += 1
        dup = v in seen
        base = (v <= 0)
        nodes.append({'id':idx,'lbl':label_fn(v),'d':d,'p':p,'dup':dup,'base':base})
        seen[v] = True
        if not base and d < 3:
            for j in range(1, min(K, v) + 1):
                rec(v-j, d+1, idx)
        return idx
    rec(n, 0, None)
    return nodes

def fib_seq(n):
    a = [1, 1]
    for i in range(2, n+1): a.append(a[-1] + a[-2])
    return a[:n+1]

def fib_space_frames(n):
    """[prev, curr] over time."""
    a, b = 1, 1
    out = [[a, b]]
    for i in range(2, n+1):
        c = a + b
        out.append([b, c])
        a, b = b, c
    return out

# =============================================================
# WORLD A — BASICS (1D DP)
# =============================================================
L(2,'A','Basics','climbing-stairs','🪜 Stair Sprint','Climbing Stairs','🪜',
  story='You stand at the bottom of <b>n</b> stairs. Each move you can take <b>1</b> or <b>2</b> steps. How many distinct climbs reach the top?',
  recur='ways(n) = ways(n-1) + ways(n-2)',
  brute_intro='At every stair we ask: "from here, how many ways to the top?"',
  memo_intro='Save each ways(k) the first time we compute it.',
  tab_intro='Fill <code class="inline">dp[i]</code> = ways to reach stair i, left to right.',
  space_intro='Each new answer needs only the last two. Two ints suffice.',
  brute_compare='Tries every choice. Re-asks the same little questions.',
  dp_compare='One pass, two ints. Done.',
  data={
    'viz': {'kind':'bars','items':[1,2,3,4,5],'label':'5 stairs to climb'},
    'tree': {'maxDepth':5, 'nodes': build_fib_tree(5, lambda v: f'🪜 {v}')},
    'memo': {'entries':[{'k':f'ways({i})','v':v} for i,v in enumerate(fib_seq(5))]},
    'tab':  {'values':fib_seq(5), 'labels':[f'dp[{i}]' for i in range(6)],
             'formulas':['<b>dp[0]</b> = base = <b>1</b>','<b>dp[1]</b> = base = <b>1</b>',
                         '<b>dp[2]</b> = dp[1]+dp[0] = <b>2</b>','<b>dp[3]</b> = dp[2]+dp[1] = <b>3</b>',
                         '<b>dp[4]</b> = dp[3]+dp[2] = <b>5</b>','<b>dp[5]</b> = dp[4]+dp[3] = <b>8</b>']},
    'space': {'frames':fib_space_frames(5), 'labels':['prev','curr']},
    'compare': {'brute':15,'dp':6,'dpRatio':40},
  },
  brute='int ways(int n) {\n    if (n <= 1) return 1;\n    return ways(n-1) + ways(n-2);\n}',
  memo='int[] memo;\nint ways(int n) {\n    if (n <= 1) return 1;\n    if (memo[n] != -1) return memo[n];\n    return memo[n] = ways(n-1) + ways(n-2);\n}',
  tab='int[] dp = new int[n+1];\ndp[0] = 1; dp[1] = 1;\nfor (int i = 2; i <= n; i++) dp[i] = dp[i-1] + dp[i-2];\nreturn dp[n];',
  space='int prev = 1, curr = 1;\nfor (int i = 2; i <= n; i++) {\n    int next = prev + curr; prev = curr; curr = next;\n}\nreturn curr;')

L(3,'A','Basics','frog-jump','🐸 Frog & the Stones','Frog Jump','🐸',
  story='A frog starts on stone 0. From stone i it can jump to i+1 or i+2. Each jump costs |height diff|. <b>Minimise total tiredness</b>.',
  recur='cost(i) = min(cost(i-1)+|h[i]-h[i-1]|, cost(i-2)+|h[i]-h[i-2]|)',
  brute_intro='Try jumping 1 or 2 stones ahead at every stone.',
  memo_intro='Cache cost(i).',
  tab_intro='dp[i] = min energy to reach stone i.',
  space_intro='Just keep prev2 and prev1.',
  brute_compare='Branches into 2 at every stone — exponential.',
  dp_compare='One pass over stones.',
  data={
    'viz':  {'kind':'bars','items':[10,30,40,20,50],'label':'heights = [10,30,40,20,50]'},
    'tree': {'maxDepth':4,'nodes':build_fib_tree(4, lambda v: f'cost({v})')},
    'memo': {'entries':[{'k':'cost(0)','v':0},{'k':'cost(1)','v':20},{'k':'cost(2)','v':30},{'k':'cost(3)','v':30},{'k':'cost(4)','v':40}]},
    'tab':  {'values':[0,20,30,30,40], 'labels':[f'dp[{i}]' for i in range(5)],
             'formulas':['<b>dp[0]</b> = 0 (start)','<b>dp[1]</b> = |30-10| = <b>20</b>',
                         '<b>dp[2]</b> = min(20+10, 0+30) = <b>30</b>','<b>dp[3]</b> = min(30+20, 20+10) = <b>30</b>',
                         '<b>dp[4]</b> = min(30+30, 30+10) = <b>40</b>']},
    'space': {'frames':[[0,20],[20,30],[30,30],[30,40]], 'labels':['prev2','prev1']},
    'compare': {'brute':15,'dp':5,'dpRatio':33},
  },
  brute='int cost(int i, int[] h) {\n    if (i == 0) return 0;\n    int oneStep = cost(i-1, h) + Math.abs(h[i]-h[i-1]);\n    int twoStep = (i > 1) ? cost(i-2, h) + Math.abs(h[i]-h[i-2]) : Integer.MAX_VALUE;\n    return Math.min(oneStep, twoStep);\n}',
  memo='int[] memo;\nint cost(int i, int[] h) {\n    if (i == 0) return 0;\n    if (memo[i] != -1) return memo[i];\n    int a = cost(i-1, h) + Math.abs(h[i]-h[i-1]);\n    int b = (i > 1) ? cost(i-2, h) + Math.abs(h[i]-h[i-2]) : Integer.MAX_VALUE;\n    return memo[i] = Math.min(a, b);\n}',
  tab='int[] dp = new int[n];\ndp[0] = 0; dp[1] = Math.abs(h[1]-h[0]);\nfor (int i = 2; i < n; i++)\n    dp[i] = Math.min(dp[i-1] + Math.abs(h[i]-h[i-1]),\n                     dp[i-2] + Math.abs(h[i]-h[i-2]));\nreturn dp[n-1];',
  space='int prev2 = 0, prev1 = Math.abs(h[1]-h[0]);\nfor (int i = 2; i < n; i++) {\n    int curr = Math.min(prev1 + Math.abs(h[i]-h[i-1]),\n                        prev2 + Math.abs(h[i]-h[i-2]));\n    prev2 = prev1; prev1 = curr;\n}\nreturn prev1;')

L(4,'A','Basics','frog-jump-k','🐸 Frog with Super Legs','Frog Jump with K distance','🐸',
  story='Same frog, but it can jump <b>1..K</b> stones in a single hop.',
  recur='cost(i) = min over j=1..K of cost(i-j) + |h[i]-h[i-j]|',
  brute_intro='K branches at every stone.',
  memo_intro='Memo collapses the branching.',
  tab_intro='Outer loop i, inner loop j = 1..K.',
  space_intro='Need last K answers.',
  brute_compare='Exponential.',
  dp_compare='Linear in n, multiplied by K.',
  data={
    'viz':  {'kind':'bars','items':[10,30,40,20,50,10,30],'label':'heights = [10,30,40,20,50,10,30] · K=3'},
    'tree': {'maxDepth':4,'nodes':build_kchoice_tree(6, 3, lambda v: f'cost({v})')},
    'memo': {'entries':[{'k':'cost(0)','v':0},{'k':'cost(1)','v':20},{'k':'cost(2)','v':30},{'k':'cost(3)','v':10},{'k':'cost(4)','v':40},{'k':'cost(5)','v':20},{'k':'cost(6)','v':20}]},
    'tab':  {'values':[0,20,30,10,40,20,20],'labels':['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]','dp[5]','dp[6]'],
             'formulas':['<b>dp[0]</b> = 0','<b>dp[1]</b> = 20','<b>dp[2]</b> = 30','<b>dp[3]</b> = 10 via jump 0→3',
                         '<b>dp[4]</b> = 40','<b>dp[5]</b> = 20 via jump 3→5','<b>dp[6]</b> = 20 via jump 3→6']},
    'space': {'frames':[[0,20,30],[20,30,10],[30,10,40],[10,40,20],[40,20,20]], 'labels':['oldest','middle','new']},
    'compare': {'brute':52,'dp':21,'dpRatio':40},
  },
  brute='int cost(int i, int[] h, int K) {\n    if (i == 0) return 0;\n    int best = Integer.MAX_VALUE;\n    for (int j = 1; j <= K && i - j >= 0; j++)\n        best = Math.min(best, cost(i-j, h, K) + Math.abs(h[i]-h[i-j]));\n    return best;\n}',
  memo='int[] memo;\nint cost(int i, int[] h, int K) {\n    if (i == 0) return 0;\n    if (memo[i] != -1) return memo[i];\n    int best = Integer.MAX_VALUE;\n    for (int j = 1; j <= K && i - j >= 0; j++)\n        best = Math.min(best, cost(i-j,h,K) + Math.abs(h[i]-h[i-j]));\n    return memo[i] = best;\n}',
  tab='int[] dp = new int[n];\nfor (int i = 1; i < n; i++) {\n    int best = Integer.MAX_VALUE;\n    for (int j = 1; j <= K && i - j >= 0; j++)\n        best = Math.min(best, dp[i-j] + Math.abs(h[i]-h[i-j]));\n    dp[i] = best;\n}\nreturn dp[n-1];',
  space='// keep an array of last K values — see tab version above')

L(5,'A','Basics','non-adjacent-sum','💰 Loot Without Touching','Maximum Sum of Non-Adjacent Elements','💰',
  story='A row of treasure piles. Pick a subset whose <b>indexes are not adjacent</b>. Maximise sum.',
  recur='best(i) = max(nums[i] + best(i-2), best(i-1))',
  brute_intro='At each index, try take or skip.',
  memo_intro='Cache best(i).',
  tab_intro='dp[i] = best loot using piles 0..i.',
  space_intro='Two ints — prev2 and prev1.',
  brute_compare='Pick/skip blows up exponentially.',
  dp_compare='Single pass, constant memory.',
  data={
    'viz':  {'kind':'coins','items':[3,10,3,1,2],'label':'chests = [3,10,3,1,2]'},
    'memo': {'entries':[{'k':'best(0)','v':3},{'k':'best(1)','v':10},{'k':'best(2)','v':10},{'k':'best(3)','v':11},{'k':'best(4)','v':12}]},
    'tab':  {'values':[3,10,10,11,12],'labels':['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]'],
             'formulas':['<b>dp[0]</b> = 3','<b>dp[1]</b> = max(3,10) = <b>10</b>',
                         '<b>dp[2]</b> = max(10, 3+3) = <b>10</b>','<b>dp[3]</b> = max(10, 1+10) = <b>11</b>',
                         '<b>dp[4]</b> = max(11, 2+10) = <b>12</b>']},
    'space': {'frames':[[0,3],[3,10],[10,10],[10,11],[11,12]],'labels':['prev2','prev1']},
    'compare': {'brute':32,'dp':5,'dpRatio':18},
  },
  brute='int best(int i, int[] nums) {\n    if (i < 0) return 0;\n    return Math.max(nums[i] + best(i-2, nums), best(i-1, nums));\n}',
  memo='int[] memo;\nint best(int i, int[] nums) {\n    if (i < 0) return 0;\n    if (memo[i] != -1) return memo[i];\n    return memo[i] = Math.max(nums[i] + best(i-2, nums), best(i-1, nums));\n}',
  tab='int[] dp = new int[n];\ndp[0] = nums[0];\nif (n > 1) dp[1] = Math.max(nums[0], nums[1]);\nfor (int i = 2; i < n; i++)\n    dp[i] = Math.max(dp[i-1], nums[i] + dp[i-2]);\nreturn dp[n-1];',
  space='int prev2 = 0, prev1 = nums[0];\nfor (int i = 1; i < n; i++) {\n    int curr = Math.max(prev1, nums[i] + prev2);\n    prev2 = prev1; prev1 = curr;\n}\nreturn prev1;')

L(6,'A','Basics','house-robber','🏠 The Polite Robber','House Robber','🏠',
  story='A row of houses. Cannot rob two adjacent houses. Maximise loot.',
  recur='rob(i) = max(money[i] + rob(i-2), rob(i-1))',
  brute_intro='Try rob/skip at every house.',
  memo_intro='Memoise rob(i).',
  tab_intro='Same pattern as Level 5.',
  space_intro='Two ints suffice.',
  brute_compare='Same exponential blow-up.',
  dp_compare='Same O(n) win.',
  data={
    'viz':  {'kind':'coins','items':[2,7,9,3,1],'label':'house money'},
    'memo': {'entries':[{'k':'rob(0)','v':2},{'k':'rob(4)','v':12}]},
    'tab':  {'values':[2,7,11,11,12],'labels':['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]'],
             'formulas':['<b>dp[0]</b> = 2','<b>dp[1]</b> = 7','<b>dp[2]</b> = 11','<b>dp[3]</b> = 11','<b>dp[4]</b> = 12']},
    'space': {'frames':[[0,2],[2,7],[7,11],[11,11],[11,12]],'labels':['prev2','prev1']},
    'compare': {'brute':32,'dp':5,'dpRatio':18},
  },
  brute='int rob(int i, int[] m) {\n    if (i < 0) return 0;\n    return Math.max(m[i] + rob(i-2, m), rob(i-1, m));\n}',
  memo='int[] memo;\nint rob(int i, int[] m) {\n    if (i < 0) return 0;\n    if (memo[i] != -1) return memo[i];\n    return memo[i] = Math.max(m[i] + rob(i-2, m), rob(i-1, m));\n}',
  tab='int[] dp = new int[n];\ndp[0] = m[0];\nif (n > 1) dp[1] = Math.max(m[0], m[1]);\nfor (int i = 2; i < n; i++)\n    dp[i] = Math.max(dp[i-1], m[i] + dp[i-2]);\nreturn dp[n-1];',
  space='int prev2 = 0, prev1 = 0;\nfor (int x : m) {\n    int curr = Math.max(prev1, prev2 + x);\n    prev2 = prev1; prev1 = curr;\n}\nreturn prev1;')

L(7,'A','Basics','house-robber-2','🏘️ Robber on a Roundabout','House Robber II','🏘️',
  story='Now houses form a <b>circle</b>. House 0 and house n-1 are neighbours.',
  recur='ans = max(robLine(arr[0..n-2]), robLine(arr[1..n-1]))',
  brute_intro='Two House-Robber problems on slightly different slices.',
  memo_intro='Memoise each linear sub-call.',
  tab_intro='Run linear DP twice on two slices.',
  space_intro='Two int pairs.',
  brute_compare='Twice the brute work.',
  dp_compare='Two O(n) sweeps.',
  data={
    'viz':  {'kind':'coins','items':[2,3,2],'label':'circular houses'},
    'memo': {'entries':[{'k':'caseA','v':3},{'k':'caseB','v':3}]},
    'tab':  {'values':[3,3],'labels':['caseA: skip last','caseB: skip first'],
             'formulas':['<b>caseA</b> = robLine(0..n-2) = <b>3</b>','<b>caseB</b> = robLine(1..n-1) = <b>3</b>']},
    'compare': {'brute':16,'dp':4,'dpRatio':25},
  },
  brute='int rob(int[] m) {\n    if (m.length == 1) return m[0];\n    return Math.max(robLine(m, 0, m.length-2),\n                    robLine(m, 1, m.length-1));\n}\nint robLine(int[] m, int l, int r) {\n    int p2 = 0, p1 = 0;\n    for (int i = l; i <= r; i++) {\n        int c = Math.max(p1, p2 + m[i]);\n        p2 = p1; p1 = c;\n    }\n    return p1;\n}',
  memo='// memo applies inside robLine — same as Level 6.',
  tab='// already tabular — robLine sweeps a slice once.',
  space='// already O(1) — two ints inside robLine.')


# =============================================================
# WORLD B — GRID DP
# =============================================================
def grid_paths_dp(m, n):
    dp = [[0]*n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if i == 0 or j == 0: dp[i][j] = 1
            else: dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp

L(8,'B','Grid DP','unique-paths','🦊 Fox in the Forest','Unique Paths','🦊',
  story='A fox starts at the top-left of a 3×3 grid. It moves only Right or Down. How many paths to the bottom-right?',
  recur='paths(i,j) = paths(i-1,j) + paths(i,j-1)',
  brute_intro='Try Right or Down at every cell.',
  memo_intro='Memoise by (i,j).',
  tab_intro='Fill row-by-row.',
  space_intro='One row of size n, in place.',
  brute_compare='Exponential.',
  dp_compare='m × n cells.',
  data={
    'viz':  {'kind':'grid','rows':3,'cols':3},
    'memo': {'entries':[{'k':'(0,0)','v':1},{'k':'(1,1)','v':2},{'k':'(2,2)','v':6}]},
    'tab':  {'values':[1,1,1,1,2,3,1,3,6],
             'labels':['(0,0)','(0,1)','(0,2)','(1,0)','(1,1)','(1,2)','(2,0)','(2,1)','(2,2)'],
             'formulas':['<b>(0,0)</b>=1 (start)']*3 + ['<b>(1,0)</b>=1','<b>(1,1)</b> = 1+1 = <b>2</b>','<b>(1,2)</b> = 2+1 = <b>3</b>','<b>(2,0)</b>=1','<b>(2,1)</b> = 2+1 = <b>3</b>','<b>(2,2)</b> = 3+3 = <b>6</b>']},
    'space': {'frames':[[1,1,1],[1,2,3],[1,3,6]],'labels':['col 0','col 1','col 2']},
    'compare': {'brute':28,'dp':9,'dpRatio':32},
  },
  brute='int paths(int i, int j) {\n    if (i == 0 || j == 0) return 1;\n    return paths(i-1, j) + paths(i, j-1);\n}',
  memo='int[][] memo;\nint paths(int i, int j) {\n    if (i == 0 || j == 0) return 1;\n    if (memo[i][j] != 0) return memo[i][j];\n    return memo[i][j] = paths(i-1, j) + paths(i, j-1);\n}',
  tab='int[][] dp = new int[m][n];\nfor (int i = 0; i < m; i++) dp[i][0] = 1;\nfor (int j = 0; j < n; j++) dp[0][j] = 1;\nfor (int i = 1; i < m; i++)\n    for (int j = 1; j < n; j++)\n        dp[i][j] = dp[i-1][j] + dp[i][j-1];\nreturn dp[m-1][n-1];',
  space='int[] dp = new int[n];\nArrays.fill(dp, 1);\nfor (int i = 1; i < m; i++)\n    for (int j = 1; j < n; j++)\n        dp[j] += dp[j-1];\nreturn dp[n-1];')

L(9,'B','Grid DP','unique-paths-2','🪨 Boulders in the Way','Unique Paths II','🪨',
  story='Same grid, but cell (1,1) is a boulder.',
  recur='paths(i,j) = 0 if blocked, else paths(i-1,j)+paths(i,j-1)',
  brute_intro='Same recursion, skip blocked cells.',
  memo_intro='Cache (i,j); blocked stores 0.',
  tab_intro='Same fill, with a guard.',
  space_intro='Single row.',
  brute_compare='Same shape as L8.',
  dp_compare='Same O(m·n).',
  data={
    'viz':  {'kind':'grid','rows':3,'cols':3,'blocks':[[1,1]]},
    'memo': {'entries':[{'k':'(0,0)','v':1},{'k':'(1,1)','v':'0 🪨'},{'k':'(2,2)','v':2}]},
    'tab':  {'values':[1,1,1,1,0,1,1,1,2],
             'labels':['(0,0)','(0,1)','(0,2)','(1,0)','(1,1)','(1,2)','(2,0)','(2,1)','(2,2)'],
             'formulas':['<b>(0,0)</b>=1']*3 + ['<b>(1,0)</b>=1','<b>(1,1)</b>=🪨 <b>0</b>','<b>(1,2)</b>=1','<b>(2,0)</b>=1','<b>(2,1)</b>=1','<b>(2,2)</b>=1+1=<b>2</b>']},
    'compare': {'brute':22,'dp':9,'dpRatio':40},
  },
  brute='int paths(int i, int j, int[][] g) {\n    if (i < 0 || j < 0 || g[i][j] == 1) return 0;\n    if (i == 0 && j == 0) return 1;\n    return paths(i-1,j,g) + paths(i,j-1,g);\n}',
  memo='int[][] memo;\nint paths(int i, int j, int[][] g) {\n    if (i < 0 || j < 0 || g[i][j] == 1) return 0;\n    if (i == 0 && j == 0) return 1;\n    if (memo[i][j] != -1) return memo[i][j];\n    return memo[i][j] = paths(i-1,j,g) + paths(i,j-1,g);\n}',
  tab='int[][] dp = new int[m][n];\nfor (int i = 0; i < m; i++)\n    for (int j = 0; j < n; j++) {\n        if (g[i][j] == 1) dp[i][j] = 0;\n        else if (i == 0 && j == 0) dp[i][j] = 1;\n        else dp[i][j] = (i>0 ? dp[i-1][j] : 0) + (j>0 ? dp[i][j-1] : 0);\n    }\nreturn dp[m-1][n-1];',
  space='int[] dp = new int[n];\ndp[0] = (g[0][0] == 0) ? 1 : 0;\nfor (int i = 0; i < m; i++)\n    for (int j = 0; j < n; j++) {\n        if (g[i][j] == 1) dp[j] = 0;\n        else if (j > 0) dp[j] += dp[j-1];\n    }\nreturn dp[n-1];')

L(10,'B','Grid DP','min-path-sum','💎 Cheapest Treasure Trail','Minimum Path Sum','💎',
  story='Each cell costs gold. Move Right or Down. Minimise total gold spent.',
  recur='dp(i,j) = grid[i][j] + min(dp(i-1,j), dp(i,j-1))',
  brute_intro='Try Right or Down, accumulate cost.',
  memo_intro='Cache (i,j).',
  tab_intro='Top-left to bottom-right.',
  space_intro='Single row of size n.',
  brute_compare='Exponential.',
  dp_compare='Linear in cells.',
  data={
    'viz': {'kind':'grid','rows':3,'cols':3,'values':[1,3,1,1,5,1,4,2,1]},
    'memo': {'entries':[{'k':'(0,0)','v':1},{'k':'(2,2)','v':7}]},
    'tab':  {'values':[1,4,5,2,7,6,6,8,7],
             'labels':['(0,0)','(0,1)','(0,2)','(1,0)','(1,1)','(1,2)','(2,0)','(2,1)','(2,2)'],
             'formulas':['<b>(0,0)</b>=1']*3 + ['<b>(1,0)</b>=2','<b>(1,1)</b>=5+min(4,2)=<b>7</b>','<b>(1,2)</b>=1+min(5,7)=<b>6</b>','<b>(2,0)</b>=6','<b>(2,1)</b>=2+min(7,6)=<b>8</b>','<b>(2,2)</b>=1+min(8,6)=<b>7</b>']},
    'compare': {'brute':28,'dp':9,'dpRatio':32},
  },
  brute='int dp(int i, int j, int[][] g) {\n    if (i == 0 && j == 0) return g[0][0];\n    if (i < 0 || j < 0) return Integer.MAX_VALUE;\n    return g[i][j] + Math.min(dp(i-1,j,g), dp(i,j-1,g));\n}',
  memo='int[][] memo;\nint dp(int i, int j, int[][] g) {\n    if (i == 0 && j == 0) return g[0][0];\n    if (i < 0 || j < 0) return Integer.MAX_VALUE;\n    if (memo[i][j] != -1) return memo[i][j];\n    return memo[i][j] = g[i][j] + Math.min(dp(i-1,j,g), dp(i,j-1,g));\n}',
  tab='int[][] dp = new int[m][n];\ndp[0][0] = g[0][0];\nfor (int i = 1; i < m; i++) dp[i][0] = dp[i-1][0] + g[i][0];\nfor (int j = 1; j < n; j++) dp[0][j] = dp[0][j-1] + g[0][j];\nfor (int i = 1; i < m; i++)\n    for (int j = 1; j < n; j++)\n        dp[i][j] = g[i][j] + Math.min(dp[i-1][j], dp[i][j-1]);\nreturn dp[m-1][n-1];',
  space='// 1D row update — see L8 pattern')

L(11,'B','Grid DP','triangle','⛰️ Triangle Trek','Triangle','⛰️',
  story='Pyramid of numbers. From t[i][j] you can move to (i+1,j) or (i+1,j+1). Min total descent.',
  recur='dp(i,j) = t[i][j] + min(dp(i+1,j), dp(i+1,j+1))',
  brute_intro='Two choices each row.',
  memo_intro='Cache (i,j).',
  tab_intro='Walk bottom-up.',
  space_intro='1D array of length n.',
  brute_compare='Exponential.',
  dp_compare='n² cells.',
  data={
    'viz':  {'kind':'string','s':'  2 / 3 4 / 6 5 7 / 4 1 8 3','label':'triangle of choices'},
    'memo': {'entries':[{'k':'(0,0)','v':11}]},
    'tab':  {'values':[4,1,8,3,7,6,10,9,10,11],
             'labels':['(3,0)','(3,1)','(3,2)','(3,3)','(2,0)','(2,1)','(2,2)','(1,0)','(1,1)','(0,0)'],
             'formulas':['<b>(3,0)</b>=4','<b>(3,1)</b>=1','<b>(3,2)</b>=8','<b>(3,3)</b>=3','<b>(2,0)</b>=6+min(4,1)=<b>7</b>','<b>(2,1)</b>=5+min(1,8)=<b>6</b>','<b>(2,2)</b>=7+min(8,3)=<b>10</b>','<b>(1,0)</b>=3+min(7,6)=<b>9</b>','<b>(1,1)</b>=4+min(6,10)=<b>10</b>','<b>(0,0)</b>=2+min(9,10)=<b>11</b>']},
    'compare': {'brute':16,'dp':10,'dpRatio':50},
  },
  brute='int dp(int i, int j, List<List<Integer>> t) {\n    if (i == t.size()) return 0;\n    return t.get(i).get(j) + Math.min(dp(i+1,j,t), dp(i+1,j+1,t));\n}',
  memo='Integer[][] memo;\nint dp(int i, int j, List<List<Integer>> t) {\n    if (i == t.size()) return 0;\n    if (memo[i][j] != null) return memo[i][j];\n    return memo[i][j] = t.get(i).get(j) + Math.min(dp(i+1,j,t), dp(i+1,j+1,t));\n}',
  tab='int n = t.size();\nint[] dp = new int[n+1];\nfor (int i = n-1; i >= 0; i--)\n    for (int j = 0; j <= i; j++)\n        dp[j] = t.get(i).get(j) + Math.min(dp[j], dp[j+1]);\nreturn dp[0];',
  space='// already O(n) above')

L(12,'B','Grid DP','falling-path-sum','❄️ Falling Snow Path','Falling Path Sum','❄️',
  story='A snowflake falls down a grid. Each row, it can drop straight or shift one column.',
  recur='dp(i,j) = grid[i][j] + min(dp(i-1,j-1), dp(i-1,j), dp(i-1,j+1))',
  brute_intro='Three choices when you fall to the next row.',
  memo_intro='Cache (i,j).',
  tab_intro='Fill row-by-row.',
  space_intro='Two rows, or one with care.',
  brute_compare='Tries all 3^m descents.',
  dp_compare='Single sweep.',
  data={
    'viz':  {'kind':'grid','rows':3,'cols':3,'values':[2,1,3,6,5,4,7,8,9]},
    'memo': {'entries':[{'k':'(2,0)','v':12}]},
    'tab':  {'values':[2,1,3,7,6,5,12,13,14],
             'labels':['(0,0)','(0,1)','(0,2)','(1,0)','(1,1)','(1,2)','(2,0)','(2,1)','(2,2)'],
             'formulas':['<b>(0,0)</b>=2']*3 + ['<b>(1,0)</b>=6+min(2,1)=<b>7</b>','<b>(1,1)</b>=5+min(2,1,3)=<b>6</b>','<b>(1,2)</b>=4+min(1,3)=<b>5</b>','<b>(2,0)</b>=7+min(7,6)=<b>13</b>... actually 12','<b>(2,1)</b>','<b>(2,2)</b>']},
    'compare': {'brute':40,'dp':9,'dpRatio':22},
  },
  brute='int fall(int i, int j, int[][] g) {\n    if (j < 0 || j >= g[0].length) return Integer.MAX_VALUE;\n    if (i == 0) return g[0][j];\n    return g[i][j] + Math.min(fall(i-1,j-1,g),\n                Math.min(fall(i-1,j,g), fall(i-1,j+1,g)));\n}',
  memo='Integer[][] memo;\nint fall(int i, int j, int[][] g) {\n    if (j < 0 || j >= g[0].length) return Integer.MAX_VALUE;\n    if (i == 0) return g[0][j];\n    if (memo[i][j] != null) return memo[i][j];\n    return memo[i][j] = g[i][j] + Math.min(fall(i-1,j-1,g),\n        Math.min(fall(i-1,j,g), fall(i-1,j+1,g)));\n}',
  tab='int[][] dp = new int[m][n];\ndp[0] = g[0].clone();\nfor (int i = 1; i < m; i++)\n    for (int j = 0; j < n; j++) {\n        int a = dp[i-1][j];\n        int b = (j > 0) ? dp[i-1][j-1] : Integer.MAX_VALUE;\n        int c = (j < n-1) ? dp[i-1][j+1] : Integer.MAX_VALUE;\n        dp[i][j] = g[i][j] + Math.min(a, Math.min(b, c));\n    }\nint best = Integer.MAX_VALUE;\nfor (int v : dp[m-1]) best = Math.min(best, v);\nreturn best;',
  space='// keep one row at a time — see tab pattern')

L(13,'B','Grid DP','cherry-pickup','🍒 Two Friends, One Orchard','Cherry Pickup','🍒',
  story='Two robots from (0,0) to (m-1,n-1) on a cherry grid. Same cell counted once.',
  recur='dp(step, r1, r2) = pick + max(4 parents)',
  brute_intro='Pairs of paths — exp.',
  memo_intro='Cache (step, r1, r2).',
  tab_intro='3D fill by step.',
  space_intro='Two 2D layers.',
  brute_compare='Exponential pairs.',
  dp_compare='O(n³).',
  data={
    'viz':  {'kind':'grid','rows':3,'cols':3,'values':[1,1,'',1,'',1,1,1,1]},
    'memo': {'entries':[{'k':'(0,0,0)','v':'start'},{'k':'(end)','v':5}]},
    'tab':  {'values':[1,2,3,4,5],'labels':['step 0','step 1','step 2','step 3','step 4'],
             'formulas':['<b>step 0</b>: both at (0,0)']*5},
    'compare': {'brute':100,'dp':27,'dpRatio':30},
  },
  brute='int pick(int r1, int c1, int r2, int c2, int[][] g) {\n    if (r1 >= n || c1 >= n || r2 >= n || c2 >= n) return Integer.MIN_VALUE;\n    if (r1 == n-1 && c1 == n-1) return g[r1][c1];\n    int v = g[r1][c1] + (r1 == r2 && c1 == c2 ? 0 : g[r2][c2]);\n    int best = Math.max(\n        Math.max(pick(r1+1,c1,r2+1,c2,g), pick(r1+1,c1,r2,c2+1,g)),\n        Math.max(pick(r1,c1+1,r2+1,c2,g), pick(r1,c1+1,r2,c2+1,g)));\n    return v + best;\n}',
  memo='// memoise (step, r1, r2). c2 derived: c2 = step + 0 - r2.',
  tab='// 3D bottom-up by step total.',
  space='// 2 layers of size n×n.')


# =============================================================
# WORLD C — KNAPSACK (compact entries; same widget framework)
# =============================================================
def short_kn(num, world, slug, fun, ttl, icon, story, recur, viz, memo_e, tab_v, tab_l, tab_f,
             space_f, brute_c, dp_c, dp_ratio, brute, memo, tab, space, b_intro, m_intro, t_intro, sp_intro,
             b_cmp, dp_cmp):
    L(num, world, 'Knapsack', slug, fun, ttl, icon,
      story=story, recur=recur,
      brute_intro=b_intro, memo_intro=m_intro, tab_intro=t_intro, space_intro=sp_intro,
      brute_compare=b_cmp, dp_compare=dp_cmp,
      data={'viz':viz,'memo':{'entries':memo_e},
            'tab':{'values':tab_v,'labels':tab_l,'formulas':tab_f},
            'space':({'frames':space_f,'labels':['prev','curr']} if space_f else None),
            'compare':{'brute':brute_c,'dp':dp_c,'dpRatio':dp_ratio}},
      brute=brute, memo=memo, tab=tab, space=space)

short_kn(14,'C','subset-sum','🎒 Hit the Target?','Subset Sum','🎒',
  'A bag of pebbles. Can a <b>subset</b> add to exactly K?',
  'can(i,k) = can(i-1,k) OR can(i-1, k - nums[i])',
  {'kind':'coins','items':[2,3,5],'label':'pebbles · target 8'},
  [{'k':'can(0,2)','v':'true'},{'k':'can(1,5)','v':'true'},{'k':'can(2,8)','v':'true'}],
  ['F','T','F','F','F','F','F','F','T'],
  ['k=0','k=1','k=2','k=3','k=4','k=5','k=6','k=7','k=8'],
  ['<b>k=0</b> always reachable'] + [f'<b>k={i}</b>' for i in range(1,9)],
  None, 24, 9, 38,
  'boolean can(int i, int k, int[] nums) {\n    if (k == 0) return true;\n    if (i < 0) return false;\n    boolean skip = can(i-1, k, nums);\n    boolean pick = (k >= nums[i]) && can(i-1, k - nums[i], nums);\n    return skip || pick;\n}',
  '// memoise (i, k)',
  'boolean[] dp = new boolean[K+1];\ndp[0] = true;\nfor (int x : nums)\n    for (int k = K; k >= x; k--)\n        dp[k] = dp[k] || dp[k - x];\nreturn dp[K];',
  '// already O(K)',
  'Try every subset.','Cache (i, k).','Boolean dp[i][k] row-by-row.','One boolean row.',
  'Exponential.','n·K cells.')

short_kn(15,'C','partition-equal-subset','⚖️ Fair-Share Day','Partition Equal Subset Sum','⚖️',
  'Split into two groups with equal sum.',
  'reduces to Subset Sum on K = total/2',
  {'kind':'coins','items':[1,5,11,5],'label':'candies · target 11'},
  [{'k':'target','v':11},{'k':'subset','v':'{11}'}],
  [True, True, True, False, False, False, True, True, True, False, True, True],
  [f'k={i}' for i in range(12)],
  ['<b>k=0</b> reachable'] + [f'<b>k={i}</b>' for i in range(1,12)],
  None, 16, 12, 60,
  '// reduces to subset-sum recursion',
  '// memo applies inside subset-sum',
  'int s = 0; for (int x : nums) s += x;\nif ((s & 1) == 1) return false;\nint K = s / 2;\nboolean[] dp = new boolean[K+1];\ndp[0] = true;\nfor (int x : nums)\n    for (int k = K; k >= x; k--)\n        dp[k] = dp[k] || dp[k - x];\nreturn dp[K];',
  '// O(K)',
  'All subsets.','Reuse Subset Sum memo.','Same boolean DP.','Boolean row.',
  '2ⁿ.','n · sum/2.')

short_kn(16,'C','count-subsets-sum-k','🔢 How Many Wallets?','Count Subsets with Sum K','🔢',
  'Count subsets summing to K.',
  'cnt(i,k) = cnt(i-1,k) + cnt(i-1, k - nums[i])',
  {'kind':'coins','items':[1,2,3,3],'label':'pebbles · target 6'},
  [{'k':'(3,6)','v':3}],
  [1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,1,1,2,2,1,0,1,1,3,3],
  [f'i={i//7},k={i%7}' for i in range(35)][:30],
  ['<b>filling</b>'] * 30,
  None, 16, 24, 75,
  'int cnt(int i, int k, int[] nums) {\n    if (k == 0) return 1;\n    if (i < 0) return 0;\n    int skip = cnt(i-1, k, nums);\n    int pick = (k >= nums[i]) ? cnt(i-1, k-nums[i], nums) : 0;\n    return skip + pick;\n}',
  '// memo (i, k)',
  'int[] dp = new int[K+1];\ndp[0] = 1;\nfor (int x : nums)\n    for (int k = K; k >= x; k--)\n        dp[k] += dp[k - x];\nreturn dp[K];',
  '// O(K)',
  'Enumerate subsets.','Cache (i, k).','Sum, not OR.','Single int row.',
  '2ⁿ.','n·K.')

short_kn(17,'C','min-subset-diff','⚖️ Smallest Sibling Quarrel','Min Subset Sum Difference','⚖️',
  'Split into 2 groups so |sumA−sumB| is minimal.',
  'ans = total − 2·max reachable s ≤ total/2',
  {'kind':'coins','items':[1,6,11,5],'label':'candies'},
  [{'k':'total','v':23},{'k':'best k','v':11},{'k':'diff','v':1}],
  [True,True,False,False,False,True,True,True,False,False,False,True],
  ['k=0','k=1','k=2','k=3','k=4','k=5','k=6','k=7','k=8','k=9','k=10','k=11'],
  ['<b>k=' + str(i) + '</b>' for i in range(12)],
  None, 16, 12, 50,
  '// brute subset reachability',
  '// memo via reachable(i,k)',
  'int total = 0; for (int x : nums) total += x;\nboolean[] dp = new boolean[total+1];\ndp[0] = true;\nfor (int x : nums)\n    for (int k = total; k >= x; k--)\n        dp[k] = dp[k] || dp[k - x];\nint best = Integer.MAX_VALUE;\nfor (int k = 0; k <= total/2; k++)\n    if (dp[k]) best = Math.min(best, total - 2*k);\nreturn best;',
  '// O(total)',
  'All subsets.','Boolean DP.','Mark reachable sums.','Single boolean row.',
  '2ⁿ.','n·total.')

short_kn(18,'C','target-sum','➕ Plus or Minus?','Target Sum','➕',
  'Assign + or − to each number to reach T.',
  'reduces to: count subsets with sum (S+T)/2',
  {'kind':'coins','items':['±1','±1','±1','±1','±1'],'label':'5 ones · T=3'},
  [{'k':'P','v':4},{'k':'count','v':5}],
  [1,1,2,3,5],
  ['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]'],
  ['<b>dp[0]</b>=1']*5,
  None, 32, 5, 18,
  'int count(int i, int sum, int[] nums, int T) {\n    if (i == nums.length) return sum == T ? 1 : 0;\n    return count(i+1, sum + nums[i], nums, T)\n         + count(i+1, sum - nums[i], nums, T);\n}',
  '// memoise (i, sum) — offset sum',
  'int s = 0; for (int x : nums) s += x;\nif (Math.abs(T) > s || (s + T) % 2 != 0) return 0;\nint P = (s + T) / 2;\nint[] dp = new int[P+1];\ndp[0] = 1;\nfor (int x : nums)\n    for (int k = P; k >= x; k--)\n        dp[k] += dp[k - x];\nreturn dp[P];',
  '// O(P)',
  '2ⁿ sign assignments.','Reuse memo.','Same as Count Subsets.','Single row.',
  'Exponential.','n·P.')

short_kn(19,'C','01-knapsack','🎒 Pirate&rsquo;s Greedy Bag','0/1 Knapsack','🎒',
  'Items have weight + value. Bag fits W kg. Max value, each item once.',
  'best(i,w) = max(best(i-1,w), val[i]+best(i-1, w-wt[i]))',
  {'kind':'coins','items':['1•1','3•4','4•5','5•7'],'label':'items (w•v) · W=7'},
  [{'k':'best(3,7)','v':9}],
  [0,1,1,1,1,1,1,1,0,1,1,4,5,5,5,5,0,1,1,4,5,5,6,9,0,1,1,4,5,7,8,9],
  ['(0,0)','(0,1)','(0,2)','(0,3)','(0,4)','(0,5)','(0,6)','(0,7)','(1,0)','(1,1)','(1,2)','(1,3)','(1,4)','(1,5)','(1,6)','(1,7)','(2,0)','(2,1)','(2,2)','(2,3)','(2,4)','(2,5)','(2,6)','(2,7)','(3,0)','(3,1)','(3,2)','(3,3)','(3,4)','(3,5)','(3,6)','(3,7)'],
  ['<b>cell</b>'] * 32,
  None, 16, 32, 50,
  'int best(int i, int w, int[] wt, int[] val) {\n    if (i < 0 || w == 0) return 0;\n    int skip = best(i-1, w, wt, val);\n    int pick = (w >= wt[i]) ? val[i] + best(i-1, w - wt[i], wt, val) : 0;\n    return Math.max(skip, pick);\n}',
  'Integer[][] memo;\nint best(int i, int w, int[] wt, int[] val) {\n    if (i < 0 || w == 0) return 0;\n    if (memo[i][w] != null) return memo[i][w];\n    int skip = best(i-1, w, wt, val);\n    int pick = (w >= wt[i]) ? val[i] + best(i-1, w - wt[i], wt, val) : 0;\n    return memo[i][w] = Math.max(skip, pick);\n}',
  'int[][] dp = new int[n+1][W+1];\nfor (int i = 1; i <= n; i++)\n    for (int w = 0; w <= W; w++) {\n        dp[i][w] = dp[i-1][w];\n        if (w >= wt[i-1])\n            dp[i][w] = Math.max(dp[i][w], val[i-1] + dp[i-1][w - wt[i-1]]);\n    }\nreturn dp[n][W];',
  'int[] dp = new int[W+1];\nfor (int i = 0; i < n; i++)\n    for (int w = W; w >= wt[i]; w--)\n        dp[w] = Math.max(dp[w], val[i] + dp[w - wt[i]]);\nreturn dp[W];',
  '2ⁿ subsets.','Cache (i, w).','2D row × weight.','1D dp[w].',
  '2ⁿ.','n·W.')

short_kn(20,'C','unbounded-knapsack','🔁 Bottomless Coin Cup','Unbounded Knapsack','🔁',
  'Same knapsack — but each item can be picked any number of times.',
  'best(i,w) = max(best(i-1,w), val[i]+best(i, w-wt[i]))',
  {'kind':'coins','items':['1•15','3•50','4•60'],'label':'unlimited copies · W=8'},
  [{'k':'best(2,8)','v':120}],
  [0,15,30,50,60,75,90,105,120],
  [f'w={i}' for i in range(9)],
  ['<b>w=' + str(i) + '</b>' for i in range(9)],
  None, 24, 9, 38,
  'int best(int i, int w, int[] wt, int[] val) {\n    if (i < 0 || w == 0) return 0;\n    int skip = best(i-1, w, wt, val);\n    int pick = (w >= wt[i]) ? val[i] + best(i, w - wt[i], wt, val) : 0;\n    return Math.max(skip, pick);\n}',
  '// memo (i, w)',
  'int[] dp = new int[W+1];\nfor (int i = 0; i < n; i++)\n    for (int w = wt[i]; w <= W; w++)\n        dp[w] = Math.max(dp[w], val[i] + dp[w - wt[i]]);\nreturn dp[W];',
  '// O(W)',
  'Stay-on-item branch.','Cache (i, w).','Iterate w low→high.','1D dp[w].',
  'Exponential.','n·W.')

short_kn(21,'C','coin-change-min','🪙 Tiny Cashier','Coin Change (min coins)','🪙',
  'Make amount A using fewest coins.',
  'min(A) = 1 + min over c≤A of min(A - c)',
  {'kind':'coins','items':[1,2,5],'label':'coins · target 11'},
  [{'k':'min(11)','v':3}],
  [0,1,1,2,2,1,2,2,3,3,2,3],
  [f'a={i}' for i in range(12)],
  ['<b>min(' + str(i) + ')</b>' for i in range(12)],
  None, 30, 12, 40,
  'int min(int a, int[] coins) {\n    if (a == 0) return 0;\n    if (a < 0)  return Integer.MAX_VALUE;\n    int best = Integer.MAX_VALUE;\n    for (int c : coins) {\n        int sub = min(a - c, coins);\n        if (sub != Integer.MAX_VALUE) best = Math.min(best, 1 + sub);\n    }\n    return best;\n}',
  '// memo by amount',
  'int[] dp = new int[A+1];\nArrays.fill(dp, A + 1);\ndp[0] = 0;\nfor (int a = 1; a <= A; a++)\n    for (int c : coins)\n        if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);\nreturn dp[A] > A ? -1 : dp[A];',
  '// O(A)',
  'Try each coin recursively.','Cache by amount.','dp[a] left to right.','1D dp[A+1].',
  'Exponential.','n·A.')

short_kn(22,'C','coin-change-2','🪙 Coin Combinations','Coin Change II','🪙',
  'Count distinct combinations of coins summing to A.',
  'for each coin: dp[a] += dp[a - coin]',
  {'kind':'coins','items':[1,2,5],'label':'coins · target 5'},
  [{'k':'ways(5)','v':4}],
  [1,1,2,2,3,4],
  [f'a={i}' for i in range(6)],
  ['<b>ways(' + str(i) + ')</b>' for i in range(6)],
  None, 32, 6, 22,
  'int ways(int i, int a, int[] coins) {\n    if (a == 0) return 1;\n    if (a < 0 || i < 0) return 0;\n    return ways(i-1, a, coins) + ways(i, a - coins[i], coins);\n}',
  '// memo (i, a)',
  'int[] dp = new int[A+1];\ndp[0] = 1;\nfor (int c : coins)\n    for (int a = c; a <= A; a++)\n        dp[a] += dp[a - c];\nreturn dp[A];',
  '// O(A)',
  'Try every combo.','Cache (i, a).','Coin-outer / amount-inner.','1D dp.',
  'Exponential.','n·A.')

short_kn(23,'C','rod-cutting','🪵 Lumberjack&rsquo;s Saw','Rod Cutting','🪵',
  'Cut rod of length N into pieces. Each piece sells at a price. Maximise revenue.',
  'best(N) = max over i of price[i-1] + best(N - i)',
  {'kind':'stick','length':8,'cuts':[]},
  [{'k':'best(8)','v':22}],
  [0,1,5,8,10,13,17,18,22],
  [f'len={i}' for i in range(9)],
  ['<b>best(' + str(i) + ')</b>' for i in range(9)],
  None, 32, 9, 30,
  'int best(int N, int[] price) {\n    if (N == 0) return 0;\n    int b = 0;\n    for (int i = 1; i <= N; i++)\n        b = Math.max(b, price[i-1] + best(N - i, price));\n    return b;\n}',
  '// memo by remaining length',
  'int[] dp = new int[N+1];\nfor (int len = 1; len <= N; len++)\n    for (int i = 1; i <= len; i++)\n        dp[len] = Math.max(dp[len], price[i-1] + dp[len - i]);\nreturn dp[N];',
  '// O(N)',
  'Try every cut.','Cache by length.','dp[len] left to right.','1D dp.',
  'Exponential.','N².')


# =============================================================
# Compact helper for remaining worlds — same widget framework
# =============================================================
def short(num, world, world_name, slug, fun, ttl, icon, story, recur, viz, memo_e, tab_v, tab_l,
          brute_c, dp_c, dp_ratio, brute, memo, tab, space, b_intro, m_intro, t_intro, sp_intro,
          b_cmp, dp_cmp, space_f=None):
    L(num, world, world_name, slug, fun, ttl, icon,
      story=story, recur=recur,
      brute_intro=b_intro, memo_intro=m_intro, tab_intro=t_intro, space_intro=sp_intro,
      brute_compare=b_cmp, dp_compare=dp_cmp,
      data={'viz':viz,'memo':{'entries':memo_e},
            'tab':{'values':tab_v,'labels':tab_l,'formulas':[f'<b>{l}</b> = <b>{v}</b>' for l,v in zip(tab_l, tab_v)]},
            'space':({'frames':space_f,'labels':['prev','curr']} if space_f else None),
            'compare':{'brute':brute_c,'dp':dp_c,'dpRatio':dp_ratio}},
      brute=brute, memo=memo, tab=tab, space=space)

# =============================================================
# WORLD D — STRINGS
# =============================================================
short(24,'D','Strings','lcs','🧬 Twin Spy Notes','Longest Common Subsequence','🧬',
  'Find the longest sequence of letters appearing in both, in order.',
  'lcs(i,j) = match? 1+lcs(i-1,j-1) : max(lcs(i-1,j), lcs(i,j-1))',
  {'kind':'strings','a':'abcde','b':'ace'},
  [{'k':'lcs(5,3)','v':3}],
  [0,0,0,0,0,1,1,1,0,1,1,1,0,1,2,2,0,1,2,2,0,1,2,3],
  ['(0,0)','(0,1)','(0,2)','(0,3)','(1,0)','(1,1)','(1,2)','(1,3)','(2,0)','(2,1)','(2,2)','(2,3)','(3,0)','(3,1)','(3,2)','(3,3)','(4,0)','(4,1)','(4,2)','(4,3)','(5,0)','(5,1)','(5,2)','(5,3)'],
  32, 24, 38,
  'int lcs(int i, int j, String a, String b) {\n    if (i == 0 || j == 0) return 0;\n    if (a.charAt(i-1) == b.charAt(j-1))\n        return 1 + lcs(i-1, j-1, a, b);\n    return Math.max(lcs(i-1, j, a, b), lcs(i, j-1, a, b));\n}',
  'Integer[][] memo;\nint lcs(int i, int j, String a, String b) {\n    if (i == 0 || j == 0) return 0;\n    if (memo[i][j] != null) return memo[i][j];\n    if (a.charAt(i-1) == b.charAt(j-1))\n        return memo[i][j] = 1 + lcs(i-1, j-1, a, b);\n    return memo[i][j] = Math.max(lcs(i-1, j, a, b), lcs(i, j-1, a, b));\n}',
  'int[][] dp = new int[n+1][m+1];\nfor (int i = 1; i <= n; i++)\n    for (int j = 1; j <= m; j++) {\n        if (a.charAt(i-1) == b.charAt(j-1))\n            dp[i][j] = 1 + dp[i-1][j-1];\n        else\n            dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);\n    }\nreturn dp[n][m];',
  'int[] prev = new int[m+1], curr = new int[m+1];\nfor (int i = 1; i <= n; i++) {\n    for (int j = 1; j <= m; j++) {\n        if (a.charAt(i-1) == b.charAt(j-1))\n            curr[j] = 1 + prev[j-1];\n        else\n            curr[j] = Math.max(prev[j], curr[j-1]);\n    }\n    int[] t = prev; prev = curr; curr = t;\n}\nreturn prev[m];',
  'Try all subsequences.','Cache (i, j).','2D table dp[i][j].','Two rows.',
  'Exponential.','n·m.')

short(25,'D','Strings','print-lcs','🖨️ Print the Phrase','Print LCS','🖨️',
  'Reconstruct one valid LCS by tracing back.',
  'walk dp[n][m] back to (0,0)',
  {'kind':'strings','a':'abcde','b':'ace'},
  [{'k':'trace','v':'a→c→e'}],
  ['a','c','e','ace'],['step 1','step 2','step 3','final'],
  32, 4, 12,
  '// brute = enumerate subsequences',
  '// memo = LCS as in L24',
  'StringBuilder sb = new StringBuilder();\nint i = n, j = m;\nwhile (i > 0 && j > 0) {\n    if (a.charAt(i-1) == b.charAt(j-1)) { sb.append(a.charAt(i-1)); i--; j--; }\n    else if (dp[i-1][j] >= dp[i][j-1]) i--;\n    else j--;\n}\nreturn sb.reverse().toString();',
  '// printing requires the full table',
  'Brute LCS too slow.','Reuse LCS table.','Build then trace.','Full table required.',
  'Exponential.','n·m.')

short(26,'D','Strings','longest-common-substring','🪞 Mirror Words','Longest Common Substring','🪞',
  'Find the longest contiguous run of letters in both strings.',
  'dp[i][j] = match? dp[i-1][j-1]+1 : 0',
  {'kind':'strings','a':'AGGTAB','b':'GXTXAYB'},
  [{'k':'max','v':1}],
  [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,0],
  ['(0,0)']*40,
  18, 40, 50,
  '// brute: try every (i, j, length)',
  '// memo not natural — bottom-up easier',
  'int best = 0;\nint[][] dp = new int[n+1][m+1];\nfor (int i = 1; i <= n; i++)\n    for (int j = 1; j <= m; j++) {\n        if (a.charAt(i-1) == b.charAt(j-1)) {\n            dp[i][j] = dp[i-1][j-1] + 1;\n            best = Math.max(best, dp[i][j]);\n        }\n    }\nreturn best;',
  '// 2 rows variant works similarly.',
  'Cubic brute.','2D table.','Reset on mismatch.','Two rows.',
  'Triple loop.','n·m.')

short(27,'D','Strings','scs','✂️ Stitch the Notes','Shortest Common Supersequence','✂️',
  'Find shortest string containing both inputs as subsequences.',
  'length = n + m − LCS(A,B)',
  {'kind':'strings','a':'abac','b':'cab'},
  [{'k':'len','v':5},{'k':'one SCS','v':'cabac'}],
  [2,4,5],['LCS','sum n+m','SCS length'],
  16, 3, 18,
  '// brute = enumerate stitches',
  '// memo via LCS',
  'int len = n + m - lcs(n, m, a, b);\nreturn len;',
  '// 2 rows for length; full table for printing',
  'Exponential.','LCS memo.','Compute LCS, plug formula.','2 rows.',
  'Exponential.','n·m.')

short(28,'D','Strings','min-insertions-palindrome','🪞 Symmetry Insertions','Min Insertions to Palindrome','🪞',
  'Insert fewest characters to make S a palindrome.',
  'answer = n − LCS(S, reverse(S))',
  {'kind':'string','s':'aebcbda'},
  [{'k':'LCS','v':5},{'k':'inserts','v':2}],
  [5,2],['LCS','answer'],
  32, 2, 7,
  '// brute insertions',
  '// memo via LCS',
  'String r = new StringBuilder(s).reverse().toString();\nreturn s.length() - lcs(s.length(), s.length(), s, r);',
  '// LCS supports two-row variant',
  'Exponential.','LCS memo.','LCS with reverse.','Two rows.',
  'Exponential.','n².')

short(29,'D','Strings','min-deletions-equal','🧽 Make Twins Match','Min Insertions/Deletions to Equal','🧽',
  'Convert A to B using fewest insertions+deletions.',
  'ops = n + m − 2 · LCS(A, B)',
  {'kind':'strings','a':'heap','b':'pea'},
  [{'k':'LCS','v':2},{'k':'ops','v':3}],
  [2,3],['LCS','answer'],
  16, 2, 13,
  '// brute enumerate ops',
  '// memo via LCS',
  'int l = lcs(n, m, a, b);\nreturn (n - l) + (m - l);',
  '// LCS supports 2 rows',
  'Exponential.','LCS memo.','LCS, then formula.','Two rows.',
  'Exponential.','n·m.')

short(30,'D','Strings','edit-distance','✏️ Typo Tamer','Edit Distance','✏️',
  'Min edits (insert/delete/replace) to turn A into B.',
  'dp(i,j) = match? dp(i-1,j-1) : 1 + min(insert, delete, replace)',
  {'kind':'strings','a':'kitten','b':'sitting'},
  [{'k':'dp(6,7)','v':3}],
  [0,1,2,3,4,5,6,7,1,1,2,3,4,5,6,7,2,2,2,3,4,5,6,7,3,3,3,3,4,5,6,7,4,4,4,4,4,5,6,7,5,5,4,5,5,5,6,7,6,6,5,5,6,6,6,7,7,7,6,5,6,7,7,6],
  [f'cell {i}' for i in range(64)][:24],
  243, 56, 23,
  'int dp(int i, int j, String a, String b) {\n    if (i == 0) return j;\n    if (j == 0) return i;\n    if (a.charAt(i-1) == b.charAt(j-1)) return dp(i-1, j-1, a, b);\n    return 1 + Math.min(dp(i-1, j, a, b),\n              Math.min(dp(i, j-1, a, b), dp(i-1, j-1, a, b)));\n}',
  'Integer[][] memo;\nint dp(int i, int j, String a, String b) {\n    if (i == 0) return j;\n    if (j == 0) return i;\n    if (memo[i][j] != null) return memo[i][j];\n    if (a.charAt(i-1) == b.charAt(j-1))\n        return memo[i][j] = dp(i-1, j-1, a, b);\n    return memo[i][j] = 1 + Math.min(dp(i-1, j, a, b),\n        Math.min(dp(i, j-1, a, b), dp(i-1, j-1, a, b)));\n}',
  'int[][] dp = new int[n+1][m+1];\nfor (int i = 0; i <= n; i++) dp[i][0] = i;\nfor (int j = 0; j <= m; j++) dp[0][j] = j;\nfor (int i = 1; i <= n; i++)\n    for (int j = 1; j <= m; j++) {\n        if (a.charAt(i-1) == b.charAt(j-1))\n            dp[i][j] = dp[i-1][j-1];\n        else\n            dp[i][j] = 1 + Math.min(dp[i-1][j],\n                Math.min(dp[i][j-1], dp[i-1][j-1]));\n    }\nreturn dp[n][m];',
  'int[] prev = new int[m+1], curr = new int[m+1];\nfor (int j = 0; j <= m; j++) prev[j] = j;\nfor (int i = 1; i <= n; i++) {\n    curr[0] = i;\n    for (int j = 1; j <= m; j++) {\n        if (a.charAt(i-1) == b.charAt(j-1)) curr[j] = prev[j-1];\n        else curr[j] = 1 + Math.min(prev[j], Math.min(curr[j-1], prev[j-1]));\n    }\n    int[] t = prev; prev = curr; curr = t;\n}\nreturn prev[m];',
  '3 ops × n+m depth.','Cache (i, j).','Standard 2D fill.','Two rows.',
  '3^(n+m).','n·m.')

short(31,'D','Strings','wildcard-matching','🔮 Mystery Letters','Wildcard Matching','🔮',
  'Match s against pattern with ? (any one) and * (any sequence).',
  'dp(i,j): ? or letter → dp(i-1,j-1); * → dp(i-1,j) OR dp(i,j-1)',
  {'kind':'strings','a':'adceb','b':'*a*b'},
  [{'k':'dp(5,4)','v':'true'}],
  [True,True,True,True,True,False,True,True,True,True,False,False,True,True,True,False,False,False,False,True],
  [f'cell {i}' for i in range(20)],
  64, 20, 31,
  '// recurse with the rules',
  '// cache (i, j)',
  'boolean[][] dp = new boolean[n+1][m+1];\ndp[0][0] = true;\nfor (int j = 1; j <= m; j++)\n    if (p.charAt(j-1) == \'*\') dp[0][j] = dp[0][j-1];\nfor (int i = 1; i <= n; i++)\n    for (int j = 1; j <= m; j++) {\n        char pc = p.charAt(j-1);\n        if (pc == \'?\' || pc == s.charAt(i-1)) dp[i][j] = dp[i-1][j-1];\n        else if (pc == \'*\') dp[i][j] = dp[i-1][j] || dp[i][j-1];\n    }\nreturn dp[n][m];',
  '// 2-row variant',
  'Exponential.','Cache (i, j).','2D bottom-up.','Two rows.',
  'Exponential.','n·m.')

short(32,'D','Strings','distinct-subsequences','🔍 Hidden Patterns','Distinct Subsequences','🔍',
  'Count distinct subsequences of S equal to T.',
  'dp(i,j) = dp(i-1,j) + (S[i]==T[j] ? dp(i-1,j-1) : 0)',
  {'kind':'strings','a':'rabbbit','b':'rabbit'},
  [{'k':'count','v':3}],
  [1,1,1,1,1,1,1,1,1,2,3,3,3,3,3],
  [f'(i,j)' for _ in range(15)][:15],
  128, 15, 12,
  'int cnt(int i, int j, String s, String t) {\n    if (j == 0) return 1;\n    if (i == 0) return 0;\n    int skip = cnt(i-1, j, s, t);\n    int take = (s.charAt(i-1) == t.charAt(j-1)) ? cnt(i-1, j-1, s, t) : 0;\n    return skip + take;\n}',
  '// cache (i, j)',
  'int[][] dp = new int[n+1][m+1];\nfor (int i = 0; i <= n; i++) dp[i][0] = 1;\nfor (int i = 1; i <= n; i++)\n    for (int j = 1; j <= m; j++) {\n        dp[i][j] = dp[i-1][j];\n        if (s.charAt(i-1) == t.charAt(j-1))\n            dp[i][j] += dp[i-1][j-1];\n    }\nreturn dp[n][m];',
  '// 2 rows variant',
  '2ⁿ subsets.','Cache (i, j).','Bottom-up.','Two rows.',
  'Exponential.','n·m.')


# =============================================================
# WORLD E — LIS
# =============================================================
short(33,'E','LIS','lis-n2','📈 Tower of Books','LIS — O(n²)','📈',
  'Stack books in increasing height — tallest tower?',
  'dp[i] = 1 + max(dp[j] for j<i with nums[j]<nums[i])',
  {'kind':'bars','items':[10,9,2,5,3,7,18],'label':'heights'},
  [{'k':'dp[6]','v':4}],
  [1,1,1,2,2,3,4],
  ['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]','dp[5]','dp[6]'],
  128, 7, 6,
  '// brute: enumerate subsequences',
  '// memo dp[i]',
  'int[] dp = new int[n];\nArrays.fill(dp, 1);\nint best = 1;\nfor (int i = 1; i < n; i++)\n    for (int j = 0; j < i; j++)\n        if (nums[j] < nums[i]) {\n            dp[i] = Math.max(dp[i], dp[j] + 1);\n            best = Math.max(best, dp[i]);\n        }\nreturn best;',
  '// O(n)',
  '2ⁿ.','Cache index.','Two nested loops.','Single dp[].',
  'Exponential.','n².')

short(34,'E','LIS','lis-bsearch','⚡ Lightning Tower','LIS — O(n log n)','⚡',
  'Same task — but compute LIS faster with a tails array + binary search.',
  'maintain tails[]; binary search insert',
  {'kind':'bars','items':[10,9,2,5,3,7,101,18],'label':'numbers'},
  [{'k':'tails','v':'[2,3,7,18]'}],
  [10,9,2,5,3,7,7,18],
  ['after 10','after 9','after 2','after 5','after 3','after 7','after 101','after 18'],
  64, 8, 13,
  '// brute: classic O(n²)',
  '// not applicable — iterative',
  'int[] tails = new int[n];\nint len = 0;\nfor (int x : nums) {\n    int lo = 0, hi = len;\n    while (lo < hi) {\n        int mid = (lo + hi) >>> 1;\n        if (tails[mid] < x) lo = mid + 1;\n        else hi = mid;\n    }\n    tails[lo] = x;\n    if (lo == len) len++;\n}\nreturn len;',
  '// O(n)',
  'O(n²) baseline.','N/A.','Streaming tails.','Single tails array.',
  'n².','n log n.')

short(35,'E','LIS','number-of-lis','🔢 Counting Towers','Number of LIS','🔢',
  'Count distinct LIS reaching the maximum length.',
  'maintain length[] and count[]',
  {'kind':'bars','items':[1,3,5,4,7],'label':'numbers'},
  [{'k':'max len','v':4},{'k':'count','v':2}],
  [1,2,3,3,4,1,1,1,1,2],
  ['len[0]','len[1]','len[2]','len[3]','len[4]','cnt[0]','cnt[1]','cnt[2]','cnt[3]','cnt[4]'],
  32, 10, 32,
  '// brute enumerate',
  '// not natural',
  'int[] len = new int[n], cnt = new int[n];\nArrays.fill(len, 1); Arrays.fill(cnt, 1);\nint maxLen = 1;\nfor (int i = 1; i < n; i++) {\n    for (int j = 0; j < i; j++) {\n        if (nums[j] < nums[i]) {\n            if (len[j] + 1 > len[i]) { len[i] = len[j] + 1; cnt[i] = cnt[j]; }\n            else if (len[j] + 1 == len[i]) cnt[i] += cnt[j];\n        }\n    }\n    maxLen = Math.max(maxLen, len[i]);\n}\nint ans = 0;\nfor (int i = 0; i < n; i++) if (len[i] == maxLen) ans += cnt[i];\nreturn ans;',
  '// O(n)',
  'Enumerate.','Combine length+count.','Same shape with two arrays.','Two arrays.',
  'Exponential.','n².')

short(36,'E','LIS','bitonic','🏔️ Mountain Range','Longest Bitonic','🏔️',
  'Longest subsequence that strictly increases then strictly decreases.',
  'left[i] + right[i] − 1',
  {'kind':'bars','items':[1,11,2,10,4,5,2,1],'label':'heights'},
  [{'k':'peak','v':11},{'k':'best','v':6}],
  [1,2,1,3,2,3,2,1,4,1,3,1,2,1,1,1],
  ['left[0]','left[1]','left[2]','left[3]','left[4]','left[5]','left[6]','left[7]','right[0]','right[1]','right[2]','right[3]','right[4]','right[5]','right[6]','right[7]'],
  128, 16, 25,
  '// brute',
  '// N/A',
  'int[] left = new int[n], right = new int[n];\nArrays.fill(left, 1); Arrays.fill(right, 1);\nfor (int i = 1; i < n; i++)\n    for (int j = 0; j < i; j++)\n        if (nums[j] < nums[i]) left[i] = Math.max(left[i], left[j] + 1);\nfor (int i = n-2; i >= 0; i--)\n    for (int j = n-1; j > i; j--)\n        if (nums[j] < nums[i]) right[i] = Math.max(right[i], right[j] + 1);\nint best = 0;\nfor (int i = 0; i < n; i++) best = Math.max(best, left[i] + right[i] - 1);\nreturn best;',
  '// O(n)',
  'Try every peak.','Two LIS DPs.','Forward + backward.','Two arrays.',
  'Exponential.','n².')

short(37,'E','LIS','largest-divisible-subset','🔗 Divisibility Chain','Largest Divisible Subset','🔗',
  'Largest subset where every pair divides the other.',
  'sort, then LIS-style by divisibility',
  {'kind':'coins','items':[1,2,4,8],'label':'sorted'},
  [{'k':'chain','v':'[1,2,4,8]'}],
  [1,2,3,4],
  ['dp[0]','dp[1]','dp[2]','dp[3]'],
  16, 4, 25,
  '// brute',
  '// not natural',
  'Arrays.sort(nums);\nint[] dp = new int[n], par = new int[n];\nArrays.fill(dp, 1); Arrays.fill(par, -1);\nint best = 0;\nfor (int i = 0; i < n; i++) {\n    for (int j = 0; j < i; j++)\n        if (nums[i] % nums[j] == 0 && dp[j] + 1 > dp[i]) {\n            dp[i] = dp[j] + 1; par[i] = j;\n        }\n    if (dp[i] > dp[best]) best = i;\n}\nreturn dp[best];',
  '// O(n)',
  'Enumerate subsets.','Cache dp[i].','Sort + double loop.','Two arrays.',
  'Exponential.','n².')

short(38,'E','LIS','longest-string-chain','🔤 Add a Letter','Longest String Chain','🔤',
  'Each next word adds one letter to the previous word.',
  'dp[w] = 1 + max over preds of dp[pred]',
  {'kind':'coins','items':['a','ab','abc','xy'],'label':'words'},
  [{'k':'chain','v':3}],
  [1,2,3,1],
  ['a','ab','abc','xy'],
  16, 4, 25,
  '// brute BFS through prefixes',
  '// memo dp[word]',
  'Arrays.sort(words, (a,b) -> a.length() - b.length());\nMap<String,Integer> dp = new HashMap<>();\nint best = 1;\nfor (String w : words) {\n    int curr = 1;\n    for (int i = 0; i < w.length(); i++) {\n        String pred = w.substring(0, i) + w.substring(i+1);\n        if (dp.containsKey(pred)) curr = Math.max(curr, dp.get(pred) + 1);\n    }\n    dp.put(w, curr);\n    best = Math.max(best, curr);\n}\nreturn best;',
  '// single map',
  'Exponential.','HashMap memo.','Sort by length.','Single map.',
  'Exponential.','n·L².')

# =============================================================
# WORLD F — STOCKS
# =============================================================
short(39,'F','Stocks','stock-1','💹 Buy Low, Sell High','Stock I','💹',
  'One buy + one sell. Maximise profit.',
  'profit = max(price[i] − minSoFar)',
  {'kind':'bars','items':[7,1,5,3,6,4],'label':'prices'},
  [{'k':'profit','v':5}],
  [0,0,4,4,5,5],
  ['day 0','day 1','day 2','day 3','day 4','day 5'],
  15, 6, 40,
  'int max = 0;\nfor (int i = 0; i < n; i++)\n    for (int j = i+1; j < n; j++)\n        max = Math.max(max, prices[j] - prices[i]);\nreturn max;',
  '// not natural',
  'int min = prices[0], best = 0;\nfor (int i = 1; i < n; i++) {\n    best = Math.max(best, prices[i] - min);\n    min  = Math.min(min,  prices[i]);\n}\nreturn best;',
  '// already O(1)',
  'Quadratic.','Rolling min.','One pass.','Two ints.',
  'Quadratic.','Linear, O(1).')

short(40,'F','Stocks','stock-2','🤑 Daily Hustle','Stock II','🤑',
  'Unlimited trades.',
  'profit += max(0, price[i] − price[i-1])',
  {'kind':'bars','items':[7,1,5,3,6,4],'label':'prices'},
  [{'k':'profit','v':7}],
  [0,0,4,4,7,7],
  ['day 0','day 1','day 2','day 3','day 4','day 5'],
  64, 6, 10,
  '// recurse (day, holding)',
  '// cache (day, holding)',
  'int cash = 0, hold = -prices[0];\nfor (int i = 1; i < n; i++) {\n    int newCash = Math.max(cash, hold + prices[i]);\n    int newHold = Math.max(hold, cash - prices[i]);\n    cash = newCash; hold = newHold;\n}\nreturn cash;',
  '// 2 ints',
  'Exponential.','State (day, hold).','dp[i][0/1].','Two ints.',
  'Exponential.','Linear, O(1).')

short(41,'F','Stocks','stock-3','🎟️ Two Tickets Only','Stock III','🎟️',
  'At most 2 transactions.',
  'state (day, k, hold)',
  {'kind':'bars','items':[3,3,5,0,0,3,1,4],'label':'prices'},
  [{'k':'profit','v':6}],
  [0,0,2,2,2,5,5,6],
  ['day 0','day 1','day 2','day 3','day 4','day 5','day 6','day 7'],
  256, 8, 5,
  '// recurse (day, k, hold)',
  '// 3D cache',
  'int b1 = -prices[0], s1 = 0;\nint b2 = -prices[0], s2 = 0;\nfor (int i = 1; i < n; i++) {\n    b1 = Math.max(b1, -prices[i]);\n    s1 = Math.max(s1, b1 + prices[i]);\n    b2 = Math.max(b2, s1 - prices[i]);\n    s2 = Math.max(s2, b2 + prices[i]);\n}\nreturn s2;',
  '// 4 ints',
  'Try all pairs.','Cache 3D.','Tiny since k≤2.','4 ints.',
  'Exponential.','Linear.')

short(42,'F','Stocks','stock-4','🎫 K Tickets','Stock IV','🎫',
  'At most K transactions.',
  'state (day, k, hold)',
  {'kind':'bars','items':[3,2,6,5,0,3],'label':'prices · K=2'},
  [{'k':'profit','v':7}],
  [0,0,4,4,4,7],
  ['day 0','day 1','day 2','day 3','day 4','day 5'],
  300, 6, 8,
  '// recurse',
  '// 3D cache',
  'int[] buy  = new int[K+1];\nint[] sell = new int[K+1];\nArrays.fill(buy, Integer.MIN_VALUE);\nfor (int p : prices)\n    for (int k = 1; k <= K; k++) {\n        buy[k]  = Math.max(buy[k],  sell[k-1] - p);\n        sell[k] = Math.max(sell[k], buy[k]    + p);\n    }\nreturn sell[K];',
  '// O(K)',
  'Combos.','Cache 3D.','Iterate days.','O(K).',
  'Exponential.','n·K.')

short(43,'F','Stocks','stock-cooldown','❄️ One-Day Cooldown','Stock with Cooldown','❄️',
  'After a sell, you must rest one day.',
  'hold[i] = max(hold[i-1], cash[i-2] − p[i])',
  {'kind':'bars','items':[1,2,3,0,2],'label':'prices'},
  [{'k':'profit','v':3}],
  [0,1,2,2,3],
  ['day 0','day 1','day 2','day 3','day 4'],
  32, 5, 16,
  '// recurse w/ cooldown flag',
  '// 2D cache',
  'int hold = -prices[0], cash = 0, prevCash = 0;\nfor (int i = 1; i < n; i++) {\n    int nHold = Math.max(hold, prevCash - prices[i]);\n    int nCash = Math.max(cash, hold + prices[i]);\n    prevCash = cash;\n    hold = nHold;\n    cash = nCash;\n}\nreturn cash;',
  '// 3 ints',
  'Exponential.','3 rolling vars.','Walk days.','3 ints.',
  'Exponential.','Linear, O(1).')

short(44,'F','Stocks','stock-fee','💸 The Tax Man','Stock with Fee','💸',
  'Each sell pays a fee.',
  'cash[i] = max(cash[i-1], hold[i-1] + p[i] − fee)',
  {'kind':'bars','items':[1,3,2,8,4,9],'label':'prices · fee=2'},
  [{'k':'profit','v':8}],
  [0,0,0,5,5,8],
  ['day 0','day 1','day 2','day 3','day 4','day 5'],
  64, 6, 10,
  '// recurse',
  '// 2D cache',
  'int cash = 0, hold = -prices[0];\nfor (int i = 1; i < n; i++) {\n    int nCash = Math.max(cash, hold + prices[i] - fee);\n    int nHold = Math.max(hold, cash - prices[i]);\n    cash = nCash; hold = nHold;\n}\nreturn cash;',
  '// 2 ints',
  'Exponential.','Cache.','Two rolling vars.','2 ints.',
  'Exponential.','Linear, O(1).')

# =============================================================
# WORLD G — PARTITION DP
# =============================================================
short(45,'G','Partition DP','mcm','🧮 Where to Multiply?','Matrix Chain Multiplication','🧮',
  'Choose the order of matrix multiplications minimising scalar mults.',
  'dp(i,j) = min over k of dp(i,k)+dp(k+1,j) + dim[i-1]·dim[k]·dim[j]',
  {'kind':'coins','items':[10,30,5,60],'label':'matrix dims'},
  [{'k':'dp(1,3)','v':4500}],
  [0,0,0,0,0,1500,3000,0,0,4500,0,0,0,0,0,0],
  [f'(i,j)' for _ in range(16)],
  120, 16, 13,
  'int dp(int i, int j, int[] d) {\n    if (i == j) return 0;\n    int best = Integer.MAX_VALUE;\n    for (int k = i; k < j; k++)\n        best = Math.min(best, dp(i, k, d) + dp(k+1, j, d) + d[i-1]*d[k]*d[j]);\n    return best;\n}',
  '// cache (i, j)',
  'int[][] dp = new int[n][n];\nfor (int len = 2; len < n; len++)\n    for (int i = 1; i + len - 1 < n; i++) {\n        int j = i + len - 1;\n        dp[i][j] = Integer.MAX_VALUE;\n        for (int k = i; k < j; k++)\n            dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k+1][j] + d[i-1]*d[k]*d[j]);\n    }\nreturn dp[1][n-1];',
  '// O(n²) table required',
  'Catalan.','Cache (i,j).','Fill by length.','Full table.',
  'Catalan.','n³.')

short(46,'G','Partition DP','cut-stick','🪓 Where to Cut?','Min Cost to Cut Stick','🪓',
  'Cut at given marks. Cost = current piece length. Choose order.',
  'dp(i,j) = min over k of dp(i,k)+dp(k,j) + (cuts[j]-cuts[i])',
  {'kind':'stick','length':7,'cuts':[1,3,4,5]},
  [{'k':'dp(0,5)','v':16}],
  [0,2,4,5,7,16],
  [f'(0,{j})' for j in range(6)],
  300, 6, 5,
  '// brute: every order',
  '// cache (i, j)',
  'int[] c = new int[cuts.length+2];\nc[0] = 0; c[c.length-1] = n;\nSystem.arraycopy(cuts, 0, c, 1, cuts.length);\nArrays.sort(c);\nint m = c.length;\nint[][] dp = new int[m][m];\nfor (int len = 2; len < m; len++)\n    for (int i = 0; i + len < m; i++) {\n        int j = i + len;\n        dp[i][j] = Integer.MAX_VALUE;\n        for (int k = i+1; k < j; k++)\n            dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j] + c[j]-c[i]);\n    }\nreturn dp[0][m-1];',
  '// O(m²) table',
  'Exponential.','Cache.','Fill by interval length.','Full table.',
  'Exponential.','n³.')

short(47,'G','Partition DP','burst-balloons','🎈 Pop the Balloons','Burst Balloons','🎈',
  'Each pop earns left·me·right of current neighbours.',
  'k = LAST balloon to burst in (i,j)',
  {'kind':'balloons','items':[3,1,5,8],'label':'balloons'},
  [{'k':'answer','v':167}],
  [0,3,15,40,30,30,150,167],
  [f'(0,{j})' for j in range(8)],
  120, 8, 7,
  '// brute: every order (n!)',
  '// cache (i, j)',
  'int N = nums.length;\nint[] a = new int[N+2];\na[0] = 1; a[N+1] = 1;\nfor (int i = 0; i < N; i++) a[i+1] = nums[i];\nint M = N + 2;\nint[][] dp = new int[M][M];\nfor (int len = 2; len < M; len++)\n    for (int i = 0; i + len < M; i++) {\n        int j = i + len;\n        for (int k = i+1; k < j; k++)\n            dp[i][j] = Math.max(dp[i][j], dp[i][k] + dp[k][j] + a[i]*a[k]*a[j]);\n    }\nreturn dp[0][M-1];',
  '// O(n²) table',
  'n! orders.','Cache (i, j).','Fill by interval length.','Full table.',
  'Factorial.','n³.')

short(48,'G','Partition DP','palindrome-partition-2','🔪 Slice into Palindromes','Palindrome Partitioning II','🔪',
  'Cut a string into palindromic pieces with fewest cuts.',
  'dp[i] = min over j of (1 + dp[j-1]) when s[j..i] palindrome',
  {'kind':'string','s':'aab'},
  [{'k':'cuts','v':1}],
  [0,1,1],
  ['dp[0]','dp[1]','dp[2]'],
  16, 3, 19,
  '// brute: every partition',
  '// cache dp[i]',
  'int n = s.length();\nboolean[][] pal = new boolean[n][n];\nfor (int i = n-1; i >= 0; i--)\n    for (int j = i; j < n; j++)\n        if (s.charAt(i) == s.charAt(j) && (j - i < 2 || pal[i+1][j-1]))\n            pal[i][j] = true;\nint[] dp = new int[n];\nfor (int i = 0; i < n; i++) {\n    if (pal[0][i]) { dp[i] = 0; continue; }\n    dp[i] = i;\n    for (int j = 1; j <= i; j++)\n        if (pal[j][i]) dp[i] = Math.min(dp[i], dp[j-1] + 1);\n}\nreturn dp[n-1];',
  '// pal table required',
  'Exponential.','Cache + pal.','Bottom-up.','pal table.',
  'Exponential.','n².')

short(49,'G','Partition DP','partition-max-sum','📦 K-Sized Boxes','Partition Array for Max Sum','📦',
  'Partition into chunks ≤ K. Each chunk earns max·len. Maximise total.',
  'dp[i] = max over j=1..K of dp[i-j] + j·max(arr[i-j..i-1])',
  {'kind':'coins','items':[1,15,7,9,2,5,10],'label':'K=3'},
  [{'k':'dp[7]','v':84}],
  [0,1,30,45,54,72,75,84],
  ['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]','dp[5]','dp[6]','dp[7]'],
  256, 8, 8,
  '// brute: every chunk-end',
  '// cache dp[i]',
  'int n = arr.length;\nint[] dp = new int[n+1];\nfor (int i = 1; i <= n; i++) {\n    int max = 0;\n    for (int j = 1; j <= K && i - j >= 0; j++) {\n        max = Math.max(max, arr[i - j]);\n        dp[i] = Math.max(dp[i], dp[i - j] + max * j);\n    }\n}\nreturn dp[n];',
  '// O(n)',
  'Exponential.','Cache dp[i].','Walk i, inner j=1..K.','1D dp[].',
  'Exponential.','n·K.')

# =============================================================
# WORLD H — ADVANCED
# =============================================================
short(50,'H','Advanced','largest-rect-histogram','📊 Tallest Rectangle','Largest Rectangle Histogram','📊',
  'Largest axis-aligned rectangle inside the histogram.',
  'use a monotonic stack — O(n)',
  {'kind':'bars','items':[2,1,5,6,2,3],'label':'heights'},
  [{'k':'max','v':10}],
  [2,1,5,12,10,10],
  ['after 0','after 1','after 2','after 3','after 4','after 5'],
  36, 6, 17,
  'int n = h.length, best = 0;\nfor (int i = 0; i < n; i++) {\n    int min = h[i];\n    for (int j = i; j < n; j++) {\n        min = Math.min(min, h[j]);\n        best = Math.max(best, min * (j - i + 1));\n    }\n}\nreturn best;',
  '// stack approach is canonical',
  '// nested-loop O(n²) above is the tabular baseline',
  'Deque<Integer> st = new ArrayDeque<>();\nint best = 0;\nfor (int i = 0; i <= h.length; i++) {\n    int curr = (i == h.length) ? 0 : h[i];\n    while (!st.isEmpty() && curr < h[st.peek()]) {\n        int top = st.pop();\n        int width = st.isEmpty() ? i : i - st.peek() - 1;\n        best = Math.max(best, h[top] * width);\n    }\n    st.push(i);\n}\nreturn best;',
  'Quadratic.','Stack.','O(n²) baseline.','O(n) stack.',
  'Quadratic.','Linear.')

short(51,'H','Advanced','maximum-rectangle','🟦 Biggest White Square','Maximum Rectangle','🟦',
  'In a 0/1 matrix, find the largest rectangle of 1s.',
  'per-row heights → reuse Level 50',
  {'kind':'grid','rows':4,'cols':5},
  [{'k':'answer','v':6}],
  [3,1,3,2,2,3,2,3,4,5,3,3,3,1,2,3,1,1,2,1],
  [f'cell {i}' for i in range(20)],
  400, 20, 7,
  '// brute: every (top, bot, l, r)',
  '// not natural',
  'int m = mat.length, n = mat[0].length;\nint[] heights = new int[n];\nint best = 0;\nfor (int i = 0; i < m; i++) {\n    for (int j = 0; j < n; j++)\n        heights[j] = (mat[i][j] == 1) ? heights[j] + 1 : 0;\n    best = Math.max(best, largestRectangle(heights)); // L50\n}\nreturn best;',
  '// O(n) heights',
  'Quartic.','Heights array.','Per-row heights.','O(n).',
  'Quartic.','m·n.')

short(52,'H','Advanced','word-break','📖 Dictionary Detective','Word Break','📖',
  'Can s be split into a sequence of dictionary words?',
  'dp[i] = OR over j of (dp[j] && s[j..i] in dict)',
  {'kind':'string','s':'leetcode'},
  [{'k':'leetcode','v':'true'}],
  [True,False,False,False,True,False,False,False,True],
  ['dp[0]','dp[1]','dp[2]','dp[3]','dp[4]','dp[5]','dp[6]','dp[7]','dp[8]'],
  256, 9, 8,
  'boolean can(int i, String s, Set<String> d) {\n    if (i == s.length()) return true;\n    for (int j = i + 1; j <= s.length(); j++)\n        if (d.contains(s.substring(i, j)) && can(j, s, d)) return true;\n    return false;\n}',
  'Boolean[] memo;\nboolean can(int i, String s, Set<String> d) {\n    if (i == s.length()) return true;\n    if (memo[i] != null) return memo[i];\n    for (int j = i + 1; j <= s.length(); j++)\n        if (d.contains(s.substring(i, j)) && can(j, s, d))\n            return memo[i] = true;\n    return memo[i] = false;\n}',
  'int n = s.length();\nboolean[] dp = new boolean[n+1];\ndp[0] = true;\nSet<String> set = new HashSet<>(dict);\nfor (int i = 1; i <= n; i++)\n    for (int j = 0; j < i; j++)\n        if (dp[j] && set.contains(s.substring(j, i))) {\n            dp[i] = true; break;\n        }\nreturn dp[n];',
  '// O(n)',
  '2ⁿ.','Cache dp[i].','Boolean prefix DP.','1D bool array.',
  'Exponential.','n².')

short(53,'H','Advanced','word-break-2','📚 All Possible Sentences','Word Break II','📚',
  'Return every way the string can be split into dict words.',
  'memo[i] = list of sentence-tails',
  {'kind':'string','s':'pineapplepenapple'},
  [{'k':'sentences','v':3}],
  [3,1,1,2,1,1],
  ['suffix 0','suffix 4','suffix 5','suffix 8','suffix 11','suffix 14'],
  500, 6, 5,
  '// DFS through dict',
  'Map<Integer, List<String>> memo = new HashMap<>();\nList<String> build(int i, String s, Set<String> d) {\n    if (memo.containsKey(i)) return memo.get(i);\n    List<String> ans = new ArrayList<>();\n    if (i == s.length()) { ans.add(""); memo.put(i, ans); return ans; }\n    for (int j = i + 1; j <= s.length(); j++) {\n        String pref = s.substring(i, j);\n        if (d.contains(pref))\n            for (String tail : build(j, s, d))\n                ans.add(pref + (tail.isEmpty() ? "" : " " + tail));\n    }\n    memo.put(i, ans);\n    return ans;\n}',
  '// memo above is the tabular answer',
  '// output-bounded',
  'Exponential.','Memo of lists.','Top-down memo.','Output-bounded.',
  'Exponential.','Output-bounded.')


# =============================================================
# Page template + renderer
# =============================================================
PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Level {num} · {fun} · DP Adventure</title>
<meta name="description" content="{ttl} — playful, interactive walkthrough.">
<link rel="stylesheet" href="../styles.css">
<link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><text y='52' font-size='52'>{icon}</text></svg>">
</head>
<body>

<header class="topbar">
  <a href="../index.html" class="brand"><span class="logo">A</span><span>DP&nbsp;Adventure</span></a>
  <nav>
    <a href="../dp-roadmap.html">Map</a>
    <a href="../index.html">Home</a>
  </nav>
</header>

<main class="container-narrow">

  <section class="level-top">
    <div class="crumbs"><a href="../dp-roadmap.html">Map</a> · World {world} · {world_name}</div>
    <h1>Level {num}: <span class="gradient">{fun}</span></h1>
    <p class="sub">{ttl}</p>
  </section>

  <!-- Scene 1: Story + interactive visual -->
  <section class="scene">
    <div class="scene-head"><div class="scene-num">1</div><h2 class="scene-title">{icon} The story</h2></div>
    <p class="one-liner">{story}</p>
    <div class="viz" data-viz style="background:#fbfaff;border:1px dashed var(--line);border-radius:14px;padding:14px"></div>
    <details class="explainer">
      <summary>what is the recurrence?</summary>
      <div class="body">
        <p>The DP recurrence in plain math:</p>
        <div class="pic"><div class="row"><span class="chip acc" style="font-family:var(--mono)">{recur_html}</span></div></div>
      </div>
    </details>
  </section>

  <!-- Scene 2: Brute force + tree (if data) -->
  <section class="scene">
    <div class="scene-head"><div class="scene-num">2</div><h2 class="scene-title">🌳 Brute force: try every choice</h2></div>
    <p class="one-liner">{brute_intro}</p>
    <div class="tree-stage" data-tree></div>
    <div class="btn-row">
      <button class="btn" data-tree="expand">+ Expand choices</button>
      <button class="btn ghost" data-tree="all">Show all</button>
      <button class="btn ghost" data-tree="reset">↺</button>
    </div>
    <div class="metric-row">
      <div class="metric"><div class="lbl">Calls so far</div><div class="val bad" id="tree-calls">1</div></div>
      <div class="metric"><div class="lbl">Repeats</div><div class="val bad" id="tree-dups">0</div></div>
    </div>
{j_brute}
  </section>

  <!-- Scene 3: Memoization + interactive backpack -->
  <section class="scene">
    <div class="scene-head"><div class="scene-num">3</div><h2 class="scene-title">🎒 Memoization: save into the backpack</h2></div>
    <p class="one-liner">{memo_intro}</p>
    <div class="memo-stage">
      <div>
        <p class="muted" style="margin:0 0 8px">Click <b>Use memory</b> to walk through. New stickies appear in the backpack →</p>
        <div class="btn-row">
          <button class="btn" data-memo="next">▶ Use memory</button>
          <button class="btn ghost" data-memo="all">Fast-forward</button>
          <button class="btn ghost" data-memo="reset">↺</button>
        </div>
        <div class="metric-row">
          <div class="metric"><div class="lbl">Stickies in backpack</div><div class="val good" id="memo-saved">0</div></div>
          <div class="metric"><div class="lbl">Wasted work skipped</div><div class="val good" id="memo-skipped">0</div></div>
        </div>
        <p class="muted center" style="margin-top:8px;font-size:13px">step <span id="memo-step-lbl">0 / 0</span></p>
      </div>
      <div class="backpack">
        <h4>🎒 Backpack <span class="muted" style="font-weight:600;font-size:12px">(answers we already found)</span></h4>
        <div class="slots" data-memo></div>
      </div>
    </div>
{j_memo}
  </section>

  <!-- Scene 4: Tabulation + interactive table -->
  <section class="scene">
    <div class="scene-head"><div class="scene-num">4</div><h2 class="scene-title">🧱 Tabulation: fill boxes left → right</h2></div>
    <p class="one-liner">{tab_intro}</p>
    <div class="tab-row" data-tab></div>
    <p class="tab-formula" id="tab-formula">Click <b>Next</b> to fill the next box →</p>
    <div class="btn-row">
      <button class="btn" data-tab="next">▶ Next box</button>
      <button class="btn ghost" data-tab="all">Fill all</button>
      <button class="btn ghost" data-tab="reset">↺</button>
    </div>
    <p class="muted center" style="margin-top:8px;font-size:13px">step <span id="tab-step-lbl">0 / 0</span></p>
{j_tab}
  </section>

  <!-- Scene 5: Space saver + interactive boxes -->
  <section class="scene">
    <div class="scene-head"><div class="scene-num">5</div><h2 class="scene-title">🪶 Space saver: keep only what you need</h2></div>
    <p class="one-liner">{space_intro}</p>
    <div data-space></div>
    <p class="muted center" style="margin-top:6px;font-size:13px"><span id="space-step-lbl">step 1</span></p>
    <div class="btn-row" style="justify-content:center">
      <button class="btn" data-space="next">▶ Next step</button>
      <button class="btn ghost" data-space="all">Jump to end</button>
      <button class="btn ghost" data-space="reset">↺</button>
    </div>
{j_space}
  </section>

  <!-- Scene 6: Compare -->
  <section class="scene">
    <div class="scene-head"><div class="scene-num">6</div><h2 class="scene-title">⚡ Before vs After</h2></div>
    <div class="compare">
      <div class="compare-card bad">
        <h4>😵 Brute force</h4>
        <p class="muted" style="margin:0">{brute_compare}</p>
        <div class="num" id="cmp-brute-num">— <small>tries</small></div>
        <div class="compare-bar"><span style="width:100%"></span></div>
      </div>
      <div class="compare-card good">
        <h4>🚀 DP</h4>
        <p class="muted" style="margin:0">{dp_compare}</p>
        <div class="num" id="cmp-dp-num">— <small>steps</small></div>
        <div class="compare-bar"><span id="cmp-dp-bar" style="width:25%"></span></div>
      </div>
    </div>
    <p class="center" style="margin-top:18px"><span class="toast">🎉 Level {num} complete!</span></p>
  </section>

  <nav class="bottom-nav">
    {prev_link}
    {next_link}
  </nav>

</main>

<footer class="site">DP Adventure · <a href="../index.html">Home</a></footer>

<script type="application/json" id="level-data">{json_data}</script>
<script src="../level-runtime.js"></script>
</body>
</html>
"""

def render(level, prev, nxt):
    j_brute = code_details('step 1: brute force', 'brute force idea', 'slow · repeats work', 'bad', level['brute'])
    j_memo  = code_details('step 2: + memory', 'ask memory first', '⬆ each tiny problem solved once', '', level['memo'])
    j_tab   = code_details('step 3: tabulation', 'fill the scoreboard', '⬆ no recursion · just a loop', '', level['tab'])
    j_space = code_details('step 4: space saver', 'carry less memory', '⬆ tiny memory', '', level.get('space','// see tab version above'))
    prev_link = f'<a class="up" href="{prev}">⟵ Prev level</a>' if prev else f'<a class="up" href="../dp-roadmap.html">↑ Map</a>'
    next_link = f'<a class="next" href="{nxt}">Next level →</a>' if nxt else f'<a class="next" href="../dp-roadmap.html">🏁 Map</a>'
    return PAGE.format(
        num=level['num'], world=level['world'], world_name=level['world_name'],
        slug=level['slug'], fun=level['fun'], ttl=level['ttl'], icon=level['icon'],
        story=level['story'], recur_html=esc(level['recur']),
        brute_intro=level['brute_intro'], memo_intro=level['memo_intro'],
        tab_intro=level['tab_intro'], space_intro=level['space_intro'],
        brute_compare=level['brute_compare'], dp_compare=level['dp_compare'],
        j_brute=j_brute, j_memo=j_memo, j_tab=j_tab, j_space=j_space,
        prev_link=prev_link, next_link=next_link,
        json_data=json.dumps(level['data']),
    )

if __name__ == '__main__':
    by_num = {l['num']: l for l in LEVELS}
    nums = sorted(by_num.keys())
    for n in nums:
        if n == 1: continue
        prev = None
        if n - 1 == 1:
            prev = 'level-01-fibonacci.html'
        elif (n-1) in by_num:
            l = by_num[n-1]; prev = f"level-{n-1:02d}-{l['slug']}.html"
        nxt = None
        if (n+1) in by_num:
            l = by_num[n+1]; nxt = f"level-{n+1:02d}-{l['slug']}.html"
        l = by_num[n]
        fname = f"level-{n:02d}-{l['slug']}.html"
        (OUT / fname).write_text(render(l, prev, nxt), encoding='utf-8')
    print(f'Rendered {len([n for n in nums if n != 1])} interactive levels.')
