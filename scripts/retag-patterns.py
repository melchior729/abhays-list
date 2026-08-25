#!/usr/bin/env python3
"""Retag NeetCode All problems from optimal/intended solution approaches."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALL_PATH = ROOT / "data" / "neetcode-all.json"
CACHE_DIR = ROOT / "data" / "neetcode-meta-cache"
OUT_PATH = ROOT / "data" / "neetcode-all-true-patterns.json"
META_URL = "https://us-central1-neetcode-dd170.cloudfunctions.net/getProblemMetadataFunctionHttp"

# Canonical pattern slugs used by this app (+ advanced-graphs from NC All)
CANONICAL = [
    "arrays-hashing",
    "two-pointers",
    "sliding-window",
    "stack",
    "binary-search",
    "linked-list",
    "trees",
    "tries",
    "heap",
    "backtracking",
    "graphs",
    "advanced-graphs",
    "intervals",
    "greedy",
    "dp-1d",
    "dp-2d",
    "bit-manipulation",
    "math-geometry",
]


def fetch_metadata(pid: str) -> dict:
    req = urllib.request.Request(
        META_URL,
        data=json.dumps({"data": {"problemId": pid}}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["data"]


def load_or_fetch(pid: str) -> dict | None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{pid}.json"
    if path.exists():
        try:
            cached = json.loads(path.read_text())
            # Cached API misses are stored as JSON null — keep as miss
            if cached is None:
                return None
            return cached
        except json.JSONDecodeError:
            pass
    for attempt in range(4):
        try:
            data = fetch_metadata(pid)
            path.write_text(json.dumps(data))
            return data
        except Exception as e:
            if attempt == 3:
                print(f"FAIL {pid}: {e}")
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def clean_o_inner(inner: str) -> str:
    s = inner.replace("\\log", "log").replace("\\", "")
    s = re.sub(r"\s+", "", s)
    return s


def parse_o_from_text(text: str) -> str | None:
    m = re.search(r"O\(([^)]+)\)", text.replace("\\log", "log"))
    if not m:
        return None
    return clean_o_inner(m.group(1))


def complexity_score(expr: str | tuple | None) -> tuple:
    """Lower is better. Handles 'or' tuples by taking the worse alternative."""
    if expr is None:
        return (10**9,)
    if isinstance(expr, tuple) and expr and expr[0] == "or":
        return max(complexity_score(x) for x in expr[1])

    s = str(expr).lower().strip()
    s = s.replace("**", "^")
    s = re.sub(r"(\d+)\*", "", s)  # 32*n -> n

    # Exponential / factorial
    if re.search(r"2\^n|2\*\*n|n!", s):
        return (6, 0, 0, s)
    if re.search(r"n\^n", s):
        return (7, 0, 0, s)

    # Extract poly degree on n (or primary var)
    deg = 0
    if re.search(r"n\^4", s):
        deg = 4
    elif re.search(r"n\^3", s):
        deg = 3
    elif re.search(r"n\^2", s):
        deg = 2
    elif "n" in s or "m" in s or "k" in s or "v" in s or "e" in s or "s" in s or "q" in s:
        deg = 1

    logs = len(re.findall(r"log", s))

    # Product of two linear dims (n*m, k*n without n^2) ≈ quadratic-ish
    # but n*log m should stay near-linear
    body = re.sub(r"log[a-z]*", "", s)
    # count '*' separators between alphanumeric atoms
    atoms = [a for a in re.split(r"[*+/]", body) if a and not a.isdigit()]
    product_penalty = 0
    if deg == 1 and len(atoms) >= 2 and "*" in body:
        # n*m or k*n -> treat as deg 2 for comparison vs n log m
        # BUT n*logm already had log stripped from body leaving n*m — careful
        # Original s has log: n*logm -> body n*m after strip — false positive
        if logs == 0:
            product_penalty = 1  # bump to compete like n^2
            deg = 2

    if s in {"1", ""} or (deg == 0 and logs == 0 and "1" in s):
        return (0, 0, 0, s)

    if deg == 0 and logs > 0:
        return (0, logs, 0, s)  # O(log n)

    # Primary key: degree (+ product), then logs
    return (deg + product_penalty, logs, 0, s)


def parse_space_expr(raw: str):
    raw_flat = raw.replace("\\log", "log").replace("\\", "")
    opts = re.findall(r"O\(([^)]+)\)", raw_flat)
    opts = [clean_o_inner(o) for o in opts]
    if not opts:
        return None
    if len(opts) == 1:
        return opts[0]
    return ("or", opts)


def parse_approaches(article: str) -> list[dict]:
    if not article:
        return []
    parts = re.split(r"\n##\s+(\d+)\.\s+([^\n]+)\n", article)
    out = []
    i = 1
    while i + 2 < len(parts):
        num, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        # Ignore follow-up-only sections for primary optimality? keep them; ranking handles it
        time_m = re.search(r"[*-]\s*Time complexity:\s*(.+)", body)
        space_m = re.search(r"[*-]\s*Space complexity:\s*(.+)", body)
        t = parse_o_from_text(time_m.group(1)) if time_m else None
        s = parse_space_expr(space_m.group(1)) if space_m else None
        out.append(
            {
                "n": int(num),
                "title": title,
                "time": t,
                "space": s if not isinstance(s, str) else s,
                "time_score": complexity_score(t),
                "space_score": complexity_score(s),
            }
        )
        i += 3
    return out


def parse_recommended(description: str) -> tuple[str | None, str | None]:
    if not description:
        return None, None
    m = re.search(
        r"Recommended Time & Space Complexity.*?<p>(.*?)</p>",
        description,
        re.S | re.I,
    )
    if not m:
        return None, None
    text = re.sub(r"<[^>]+>", " ", m.group(1))
    text = re.sub(r"\s+", " ", text)
    # "O(n) time and O(n) space" or "O(nlogm) time and O(1) space"
    ms = re.findall(r"O\(([^)]+)\)", text.replace("\\log", "log"))
    ms = [clean_o_inner(x) for x in ms]
    if len(ms) >= 2:
        return ms[0], ms[1]
    if len(ms) == 1:
        return ms[0], None
    return None, None


def is_non_pattern_approach(title: str) -> bool:
    t = title.lower().strip()
    if "brute" in t:
        return True
    # Bare recursion only — not "Recursion (Optimal)" / tree recursion variants
    if t == "recursion":
        return True
    if "follow-up" in t or "follow up" in t:
        return True
    if "divide" in t and "conquer" in t:
        return True
    if "better approach" in t:
        return True
    return False


def title_to_patterns(title: str, neetcode_pattern: str | None = None) -> list[str]:
    t = title.lower()
    if is_non_pattern_approach(title):
        return []

    patterns: list[str] = []

    def add(p: str):
        if p in CANONICAL and p not in patterns:
            patterns.append(p)

    nc = (neetcode_pattern or "").lower()

    def nc_is(*keys: str) -> bool:
        return any(k in nc for k in keys)

    if "kadane" in t or "boyer-moore" in t or "boyer moore" in t:
        add("dp-1d" if "kadane" in t else "arrays-hashing")
    if "morris" in t:
        add("trees")
    if "trie" in t:
        add("tries")
    if any(
        x in t
        for x in (
            "dijkstra",
            "bellman",
            "floyd warshall",
            "kruskal",
            "prim",
            "minimum spanning",
            " spo ",
            "shortest path",
        )
    ):
        add("advanced-graphs")
    if "union find" in t or "union-find" in t or "disjoint" in t:
        add("graphs")
    if "topolog" in t:
        add("graphs")
    if "monotonic queue" in t:
        add("sliding-window")
    if "monotonic stack" in t or re.search(r"\bstack\b", t):
        add("stack")
    if "sliding window" in t:
        add("sliding-window")
    if "two pointer" in t or "three pointer" in t or "three-pointer" in t:
        add("two-pointers")
    if "fast and slow" in t or "fast & slow" in t or "tortoise" in t:
        add("linked-list")
    if "linked list" in t or "cyclic traversal" in t:
        add("linked-list")
    if "binary search" in t:
        add("binary-search")
    if "backtrack" in t:
        add("backtracking")
    if "heap" in t or "priority queue" in t:
        add("heap")
    if (
        re.search(r"\bbit\b", t)
        or "bitmask" in t
        or "bit manipulation" in t
        or "bitwise" in t
    ):
        add("bit-manipulation")
    if "interval" in t:
        add("intervals")
    if "greedy" in t:
        add("greedy")
    if (
        "dynamic programming" in t
        or re.search(r"\bdp\b", t)
        or "memoization" in t
        or "memo" in t
        or "kadane" in t
    ):
        if (
            "2-d" in t
            or "2d" in t
            or "two-dimensional" in t
            or "two dimensional" in t
            or nc_is("2-d", "2d")
        ):
            add("dp-2d")
        else:
            add("dp-1d")

    # DFS / BFS — disambiguate trees vs graphs via NeetCode bucket when needed
    if "depth first" in t or re.search(r"\bdfs\b", t):
        if nc_is("tree"):
            add("trees")
        elif nc_is("graph", "advanced"):
            add("graphs")
        elif nc_is("backtrack"):
            add("backtracking")
        else:
            # default: graphs for generic DFS unless clearly tree-named
            add("graphs")
    if "breadth first" in t or re.search(r"\bbfs\b", t) or "bidirectional breadth" in t:
        if nc_is("tree"):
            add("trees")
        else:
            add("graphs")

    if "hash" in t or "frequency" in t or "counting" in t or "count frequency" in t or "count negative" in t:
        add("arrays-hashing")
    if (
        t == "array"
        or t.startswith("array ")
        or "prefix" in t
        or "suffix" in t
        or "boolean array" in t
    ):
        add("arrays-hashing")
    if "sorting" in t or "custom sort" in t or re.match(r"^sort\b", t):
        add("arrays-hashing")
    if "negative marking" in t or ("marking" in t and "negative" in t):
        add("arrays-hashing")
    if any(x in t for x in ("binary tree", "bst", "inorder", "preorder", "postorder")) or (
        re.search(r"\btree\b", t) and "trie" not in t
    ):
        add("trees")
    if "math" in t or "geometry" in t or "combinatorics" in t or "modulo" in t or "inclusion-exclusion" in t:
        add("math-geometry")
    if t == "iteration" or t.startswith("iteration"):
        # Generic loop titles
        if nc_is("math", "geometry") or "integer" in (neetcode_pattern or "").lower():
            add("math-geometry")
        elif nc_is("linked"):
            add("linked-list")
        else:
            add("arrays-hashing")
    if "max-heap" in t or "min-heap" in t or ("heap" in t and "hash" not in t):
        add("heap")
    if "reverse list" in t:
        add("linked-list")
    if "enumeration" in t:
        add("math-geometry")
    if "matrix" in t and not patterns:
        add("math-geometry")
    if "simulation" in t:
        # simulation alone is weak; prefer arrays/math based on NC bucket
        if nc_is("math", "geometry"):
            add("math-geometry")
        else:
            add("arrays-hashing")
    if "encoding" in t or "decoding" in t:
        add("arrays-hashing")
    if "string parsing" in t or "character-based" in t or "one pass" in t or "two pass" in t:
        add("arrays-hashing")
    if "linear search" in t:
        add("arrays-hashing")
    if "first and last index" in t:
        add("arrays-hashing")
    if "track the sign" in t or "start with zero" in t or "two maximums" in t:
        add("arrays-hashing")
    if "counting sort" in t or "bucket" in t or "quickselect" in t or "quick select" in t:
        add("arrays-hashing")
    if "segment tree" in t or "fenwick" in t or "binary indexed" in t:
        add("trees")
    if "graph" in t and "tree" not in t:
        add("graphs")

    # Remaining NeetCode article approach titles
    if "deque" in t:
        add("sliding-window")
    if "queue" in t and "priority" not in t:
        if "stack" in t:
            add("stack")
        elif nc_is("graph"):
            add("graphs")
        else:
            add("stack")  # queue-via-stacks / design queue
    if "two stack" in t or "using two stacks" in t:
        add("stack")
    if "staircase" in t:
        add("binary-search" if nc_is("binary") else "arrays-hashing")
    if "reverse and merge" in t or ("reverse the" in t and ("half" in t or "merge" in t)):
        add("linked-list")
    if "line sweep" in t or "sweep" in t:
        add("intervals")
    if "indegree" in t or "outdegree" in t or "hierholzer" in t:
        add("graphs")
    if "binary exponentiation" in t or "sieve" in t or "eratosthenes" in t:
        add("math-geometry")
    if "multiplication" in t and "addition" in t:
        add("math-geometry")
    if "rotate" in t or "transpose" in t:
        add("math-geometry")
    if "serialization" in t or "pattern matching" in t:
        add("trees" if nc_is("tree") else "arrays-hashing")
    if "convert to array" in t:
        add("linked-list" if nc_is("linked") else "arrays-hashing")
    if "space optimized" in t:
        if nc_is("2-d", "2d"):
            add("dp-2d")
        elif nc_is("1-d", "1d", "dynamic"):
            add("dp-1d")
        elif nc_is("bit"):
            add("bit-manipulation")
        elif nc_is("linked"):
            add("linked-list")
        elif nc_is("graph"):
            add("graphs")
        elif nc_is("tree"):
            add("trees")
        # else: rely on other title cues; don't default to arrays-hashing
    if "recursion (optimal" in t or "recursion (space" in t or t.startswith("recursion"):
        if nc_is("tree"):
            add("trees")
        elif nc_is("linked"):
            add("linked-list")
        elif nc_is("backtrack"):
            add("backtracking")
        elif nc_is("graph"):
            add("graphs")
        elif "quad" in nc:
            add("trees")
    if "in-built" in t or "built-in" in t:
        if nc_is("math"):
            add("math-geometry")
        else:
            add("arrays-hashing")
    if t.strip() == "return true":
        add("math-geometry" if nc_is("math") else "arrays-hashing")

    return patterns



def scores_equal(a: tuple, b: tuple) -> bool:
    # compare first 3 numeric keys only
    return a[:3] == b[:3]


def meets_recommended(approach: dict, rec_t: str | None, rec_s: str | None) -> bool:
    if rec_t is None:
        return False
    # approach time must be <= recommended (score)
    if approach["time_score"][:3] > complexity_score(rec_t)[:3]:
        return False
    if rec_s is not None and approach["space"] is not None:
        if approach["space_score"][:3] > complexity_score(rec_s)[:3]:
            return False
    return True


def violates_recommended_constraints(title: str, description: str) -> bool:
    """Drop approaches that break constraints called out in the recommended blurb."""
    m = re.search(
        r"Recommended Time & Space Complexity.*?<p>(.*?)</p>",
        description or "",
        re.S | re.I,
    )
    if not m:
        return False
    text = re.sub(r"<[^>]+>", " ", m.group(1)).lower()
    t = title.lower()
    if "without modifying" in text or "without changing" in text or "do not modify" in text:
        if "negative marking" in t or "marking" in t:
            return True
    return False


def select_optimal(approaches: list[dict], description: str) -> list[dict]:
    usable = [
        a
        for a in approaches
        if a["time"] is not None
        and not is_non_pattern_approach(a["title"])
        and not violates_recommended_constraints(a["title"], description)
    ]
    # Also allow non-pattern if they're the only ones? No — skip brutes always.
    all_with_complexity = [a for a in approaches if a["time"] is not None]

    rec_t, rec_s = parse_recommended(description)

    if rec_t is not None:
        matching = [a for a in usable if meets_recommended(a, rec_t, rec_s)]
        if matching:
            # Among those meeting recommended, keep those with best (time,space)
            best_t = min(a["time_score"] for a in matching)
            matching = [a for a in matching if scores_equal(a["time_score"], best_t)]
            best_s = min(a["space_score"] for a in matching)
            matching = [a for a in matching if scores_equal(a["space_score"], best_s)]
            return matching

    # Fallback: Pareto-optimal on time then space among pattern approaches
    pool = usable if usable else [a for a in all_with_complexity if "brute" not in a["title"].lower()]
    if not pool:
        return []
    best_t = min(a["time_score"] for a in pool)
    by_t = [a for a in pool if scores_equal(a["time_score"], best_t)]
    best_s = min(a["space_score"] for a in by_t)
    return [a for a in by_t if scores_equal(a["space_score"], best_s)]


def patterns_from_optimal(
    optimal: list[dict],
    neetcode_pattern: str | None = None,
    problem_name: str | None = None,
) -> list[str]:
    out: list[str] = []
    for a in optimal:
        for p in title_to_patterns(a["title"], neetcode_pattern):
            if p not in out:
                out.append(p)
    # Digit / numeric iteration problems are math, not arrays-hashing
    name = (problem_name or "").lower()
    if out == ["arrays-hashing"] and any(
        k in name for k in ("reverse integer", "palindrome number", "plus one")
    ):
        return ["math-geometry"]
    return out


def process_problem(entry: dict) -> dict:
    pid = entry["slug"]
    meta = load_or_fetch(pid)
    result = {
        "slug": pid,
        "name": entry.get("name"),
        "neetcodePattern": entry.get("pattern"),
        "difficulty": entry.get("difficulty"),
        "truePatterns": [],
        "optimalApproaches": [],
        "recommended": None,
        "status": "ok",
    }
    if not meta:
        result["status"] = "fetch_failed"
        return result

    # Prefer metadata name
    result["name"] = meta.get("name") or result["name"]
    article = meta.get("article_body") or ""
    desc = meta.get("description") or ""
    rec_t, rec_s = parse_recommended(desc)
    if rec_t:
        result["recommended"] = {"time": rec_t, "space": rec_s}

    if not meta.get("has_article") or not article:
        result["status"] = "no_article"
        # fallback: keep empty truePatterns for manual later
        return result

    approaches = parse_approaches(article)
    optimal = select_optimal(approaches, desc)
    result["optimalApproaches"] = [
        {"title": a["title"], "time": a["time"], "space": a["space"]} for a in optimal
    ]
    result["truePatterns"] = patterns_from_optimal(optimal, entry.get("pattern"), result.get("name") or entry.get("name"))
    if not result["truePatterns"]:
        result["status"] = "unmapped_approaches"
    return result


def main():
    problems = json.loads(ALL_PATH.read_text())
    print(f"Processing {len(problems)} problems...")

    results = []
    # sequential with light parallelism
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(process_problem, p): p["slug"] for p in problems}
        done = 0
        for fut in as_completed(futs):
            results.append(fut.result())
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(problems)}")

    # stable order like input
    by_slug = {r["slug"]: r for r in results}
    ordered = [by_slug[p["slug"]] for p in problems if p["slug"] in by_slug]

    OUT_PATH.write_text(json.dumps(ordered, indent=2) + "\n")

    # summary
    from collections import Counter

    status = Counter(r["status"] for r in ordered)
    multi = sum(1 for r in ordered if len(r["truePatterns"]) > 1)
    changed = sum(
        1
        for r, p in zip(ordered, problems)
        if r["truePatterns"]
        and _nc_pattern_to_slug(p["pattern"]) not in r["truePatterns"]
    )
    print("Wrote", OUT_PATH)
    print("status", dict(status))
    print("multi-pattern", multi)
    print("pattern changed vs NC bucket", changed)


def _nc_pattern_to_slug(name: str) -> str:
    m = {
        "Arrays & Hashing": "arrays-hashing",
        "Two Pointers": "two-pointers",
        "Sliding Window": "sliding-window",
        "Stack": "stack",
        "Binary Search": "binary-search",
        "Linked List": "linked-list",
        "Trees": "trees",
        "Tries": "tries",
        "Heap / Priority Queue": "heap",
        "Backtracking": "backtracking",
        "Graphs": "graphs",
        "Advanced Graphs": "advanced-graphs",
        "1-D Dynamic Programming": "dp-1d",
        "2-D Dynamic Programming": "dp-2d",
        "Greedy": "greedy",
        "Intervals": "intervals",
        "Math & Geometry": "math-geometry",
        "Bit Manipulation": "bit-manipulation",
        "JavaScript": "javascript",
    }
    return m.get(name, name)


if __name__ == "__main__":
    # quick self-check mode
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "check":
        samples = [
            "duplicate-integer",
            "find-duplicate-integer",
            "buy-and-sell-crypto",
            "buildings-with-an-ocean-view",
            "maximum-subarray",
            "split-array-largest-sum",
            "is-subsequence",
            "eating-bananas",
            "reverse-integer",
        ]
        all_problems = {p["slug"]: p for p in json.loads(ALL_PATH.read_text())}
        for s in samples:
            r = process_problem(all_problems[s])
            print(json.dumps(r, indent=2))
    else:
        main()
