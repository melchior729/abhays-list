#!/usr/bin/env python3
"""Audit curriculum pattern lists with explicit decision functions.

Global prerequisites (every audit):
  - Exclude Pro + JavaScript problems
  - Exclude dead NeetCode links (isLiveOnNeetCode)

Ordering (every pattern):
  difficulty → design-before-use → technique family → within-family rank → name
  Construction / implement-X problems lead their difficulty band.

Usage:
  python scripts/audit-pattern-list.py --pattern arrays
  python scripts/audit-pattern-list.py --pattern hashing --apply
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "neetcode-meta-cache"
OVERRIDES_PATH = DATA / "pattern-overrides.json"
NEEDS_REVIEW_PATH = DATA / "needs-review.json"

DIFF_RANK = {"easy": 0, "medium": 1, "hard": 2}

HASH_TITLE_RE = re.compile(
    r"\b(hash|dictionary|counter|frequency|hashmap|hashset|hashtable|rolling hash|"
    r"counting sort|boolean array|count array|freq array)\b",
    re.I,
)
HASH_CODE_RE = re.compile(
    r"\b(set\s*\(|Counter\s*\(|defaultdict\s*\(|HashMap\b|HashSet\b|"
    r"unordered_map\b|unordered_set\b|map\s*<|set\s*<)",
)
NON_HASHING_MAIN_RE = re.compile(
    r"\b(sorting|iteration|built-in|two pointer|sliding window|boyer-moore|"
    r"knuth-morris|\bkmp\b|z-algorithm|binary search|dynamic programming|"
    r"backtrack|depth first search|breadth first search|cycle sort)\b",
    re.I,
)
TWO_POINTER_TITLE_RE = re.compile(
    r"\b(two pointer|three pointer|two pointers|three pointers)\b",
    re.I,
)
NON_TWO_POINTER_MAIN_RE = re.compile(
    r"\b(breadth first|depth first|stack|heap|min heap|max heap|binary search|"
    r"dynamic programming|sliding window|counting sort|greedy|reverse the integer|"
    r"group numbers|built-in|sweep line)\b",
    re.I,
)
SW_TITLE_RE = re.compile(
    r"\b(sliding window|monotonic queue|deque)\b",
    re.I,
)
NON_SW_MAIN_RE = re.compile(
    r"\b(breadth first|depth first|binary search|dynamic programming|"
    r"top-down|heap|stack)\b",
    re.I,
)
BS_TITLE_RE = re.compile(
    r"\b(binary search|upper bound|lower bound|iterative binary)\b",
    re.I,
)
NON_BS_MAIN_RE = re.compile(
    r"\b(dijkstra|kruskal|segment tree|dynamic programming|greedy|"
    r"breadth first|depth first|linear search|in-built|built-in|"
    r"staircase|bit manipulation)\b",
    re.I,
)
STACK_TITLE_RE = re.compile(
    r"\b(stack|monotonic stack|two stacks|stack of stacks)\b",
    re.I,
)
NON_STACK_MAIN_RE = re.compile(
    r"\b(without stack|reverse list|doubly linked list|dynamic array|"
    r"two pointer|breadth first|depth first|binary search|dynamic programming|"
    r"greedy|iteration)\b",
    re.I,
)
LL_TITLE_RE = re.compile(
    r"\b(linked list|doubly linked|singly linked|fast and slow|fast & slow|"
    r"reverse list|reverse the|reverse and merge|reverse linked)\b",
    re.I,
)
NON_LL_MAIN_RE = re.compile(
    r"\b(cyclic traversal|using reverse|convert to array|bit manipulation|"
    r"built-in data structure)\b",
    re.I,
)
LINKED_LIST_SLUG_RE = re.compile(
    r"linked-list|linked-lists|"
    r"^reverse-a-linked|^merge-two-sorted|^merge-k-sorted|"
    r"^add-two-numbers|^copy-linked|^reorder-linked|^remove-linked|"
    r"^remove-node-from-end|^reverse-linked|^reverse-nodes|^rotate-list|"
    r"^insertion-sort-list|^maximum-twin|^palindrome-linked|^middle-of-the|"
    r"^lru-cache$|^lfu-cache$|^design-linked|^design-circular",
    re.I,
)
TREES_TITLE_RE = re.compile(
    r"\b(depth first|breadth first|morris|binary tree|binary search tree|"
    r"postorder|preorder|inorder|iterative dfs|recursive dfs)\b",
    re.I,
)
NON_TREES_MAIN_RE = re.compile(
    r"\b(segment tree|dynamic programming|topological|sweep line|"
    r"prefix tree|knuth-morris|rabin-karp|z-algorithm|sorting)\b",
    re.I,
)
TREES_SLUG_RE = re.compile(
    r"binary-tree|binary-search-tree|\-bst$|^bst-|"
    r"invert-a-binary|same-binary|depth-of-binary|subtree-of|"
    r"merge-two-binary|path-sum|range-sum-of-bst|count-good-nodes|"
    r"delete-leaves|delete-node-in-a-bst|insert-into-a-binary|"
    r"kth-smallest-integer-in-bst|lowest-common-ancestor|"
    r"populating-next-right|recover-binary|sum-root-to-leaf|"
    r"valid-binary-search|serialize-and-deserialize|"
    r"construct-quad-tree|n-ary-tree|level-order-traversal|"
    r"check-completeness",
    re.I,
)

# --- Per-pattern technique families + pedagogical ranks ---

FAMILY_RANK: dict[str, dict[str, int]] = {
    "arrays": {
        "scan": 0,
        "neighbor": 1,
        "prefix": 2,
        "suffix": 3,
        "simulation": 4,
        "encode": 5,
        "matrix": 6,
    },
    "hashing": {
        "set_membership": 0,
        "freq_count": 1,
        "map_lookup": 2,
        "counting_sort": 3,
        "design_map": 4,
        "prefix_hash": 5,
        "index_marking": 6,
        "geometry_hash": 7,
    },
    "two-pointers": {
        "opposite_ends": 0,
        "same_direction": 1,
        "merge": 2,
        "partition": 3,
        "expand_center": 4,
        "greedy_pair": 5,
        "linked_list": 6,
    },
    "sliding-window": {
        "fixed_k": 0,
        "variable": 1,
        "freq_window": 2,
        "min_window": 3,
        "deque": 4,
    },
    "binary-search": {
        "basic": 0,
        "bound": 1,
        "rotated": 2,
        "answer_space": 3,
        "design_bs": 4,
    },
    "stack": {
        "design": 0,
        "basic": 1,
        "monotonic": 2,
        "parsing": 3,
        "simulation": 4,
        "advanced": 5,
    },
    "linked-list": {
        "reverse": 0,
        "traversal": 1,
        "fast_slow": 2,
        "two_pointer": 3,
        "design": 4,
        "advanced": 5,
    },
    "trees": {
        "basics": 0,
        "traversal": 1,
        "bfs": 2,
        "bst": 3,
        "construct": 4,
        "path": 5,
        "design": 6,
        "advanced": 7,
    },
}

PEDAGOGY: dict[str, dict[str, tuple[str, int]]] = {
    "arrays": {
        "concatenation-of-array": ("scan", 0),
        "score-of-a-string": ("scan", 1),
        "length-of-last-word": ("scan", 2),
        "largest-3-same-digit-number-in-string": ("scan", 3),
        "minimum-changes-to-make-alternating-binary-string": ("scan", 4),
        "monotonic-array": ("neighbor", 0),
        "maximum-ascending-subarray-sum": ("neighbor", 1),
        "longest-strictly-increasing-or-strictly-decreasing-subarray": ("neighbor", 2),
        "maximum-product-difference-between-two-pairs": ("neighbor", 3),
        "longest-common-prefix": ("prefix", 0),
        "maximum-score-after-splitting-a-string": ("prefix", 1),
        "find-pivot-index": ("prefix", 2),
        "range-sum-query-immutable": ("prefix", 3),
        "minimum-number-of-operations-to-move-all-balls-to-each-box": ("prefix", 4),
        "products-of-array-discluding-self": ("prefix", 5),
        "range-sum-query-2d-immutable": ("prefix", 6),
        "replace-elements-with-greatest-element-on-right-side": ("suffix", 0),
        "time-needed-to-buy-tickets": ("simulation", 0),
        "average-waiting-time": ("simulation", 1),
        "string-encode-and-decode": ("encode", 0),
    },
    "hashing": {
        "duplicate-integer": ("set_membership", 0),
        "contains-duplicate-ii": ("set_membership", 1),
        "divide-array-into-equal-pairs": ("map_lookup", 0),
        "intersection-of-two-arrays": ("set_membership", 2),
        "find-the-difference-of-two-arrays": ("set_membership", 3),
        "path-crossing": ("set_membership", 4),
        "kth-distinct-string-in-an-array": ("map_lookup", 1),
        "word-pattern": ("map_lookup", 2),
        "first-unique-character-in-a-string": ("freq_count", 0),
        "ransom-note": ("freq_count", 1),
        "find-common-characters": ("freq_count", 2),
        "maximum-number-of-balloons": ("freq_count", 3),
        "number-of-students-unable-to-eat-lunch": ("freq_count", 4),
        "redistribute-characters-to-make-all-strings-equal": ("freq_count", 5),
        "is-anagram": ("freq_count", 6),
        "isomorphic-strings": ("map_lookup", 3),
        "two-integer-sum": ("map_lookup", 4),
        "roman-to-integer": ("map_lookup", 5),
        "find-the-difference": ("map_lookup", 6),
        "find-words-that-can-be-formed-by-characters": ("freq_count", 7),
        "largest-substring-between-two-equal-characters": ("map_lookup", 7),
        "number-of-good-pairs": ("map_lookup", 8),
        "height-checker": ("counting_sort", 0),
        "relative-sort-array": ("counting_sort", 1),
        "minimum-number-of-moves-to-seat-everyone": ("counting_sort", 2),
        "special-array-with-x-elements-greater-than-or-equal-x": ("counting_sort", 3),
        "sort-array-by-increasing-frequency": ("counting_sort", 4),
        "sort-an-array": ("counting_sort", 5),
        "sort-the-people": ("counting_sort", 6),
        "maximum-difference-between-even-and-odd-frequency-i": ("freq_count", 8),
        "design-hashset": ("design_map", 0),
        "design-hashmap": ("design_map", 1),
        "insert-delete-getrandom-o1": ("design_map", 2),
        "find-all-numbers-disappeared-in-an-array": ("index_marking", 0),
        "longest-consecutive-sequence": ("set_membership", 5),
        "find-the-index-of-the-first-occurrence-in-a-string": ("prefix_hash", 1),
        "anagram-groups": ("freq_count", 9),
        "subarray-sum-equals-k": ("prefix_hash", 0),
        "continuous-subarray-sum": ("prefix_hash", 2),
        "subarray-sums-divisible-by-k": ("prefix_hash", 3),
        "number-of-sub-arrays-with-odd-sum": ("prefix_hash", 4),
        "make-sum-divisible-by-p": ("prefix_hash", 5),
        "count-vowel-strings-in-ranges": ("prefix_hash", 6),
        "brick-wall": ("geometry_hash", 0),
        "count-squares": ("geometry_hash", 1),
        "analyze-user-website-visit-pattern": ("geometry_hash", 2),
        "4sum": ("map_lookup", 9),
        "hand-of-straights": ("map_lookup", 10),
        "custom-sort-string": ("freq_count", 10),
        "reorganize-string": ("freq_count", 11),
        "remove-sub-folders-from-the-filesystem": ("set_membership", 6),
        "unique-length-3-palindromic-subsequences": ("map_lookup", 11),
        "first-missing-positive": ("index_marking", 1),
    },
    "two-pointers": {
        # opposite_ends
        "reverse-string": ("opposite_ends", 0),
        "is-palindrome": ("opposite_ends", 1),
        "valid-palindrome-ii": ("opposite_ends", 2),
        "squares-of-a-sorted-array": ("opposite_ends", 3),
        "two-integer-sum-ii": ("opposite_ends", 4),
        "max-water-container": ("opposite_ends", 5),
        "three-integer-sum": ("opposite_ends", 6),
        "find-k-closest-elements": ("opposite_ends", 7),
        "trapping-rain-water": ("opposite_ends", 8),
        "median-of-two-sorted-arrays": ("opposite_ends", 9),
        # same_direction
        "merge-strings-alternately": ("same_direction", 0),
        "is-subsequence": ("same_direction", 1),
        "valid-word-abbreviation": ("same_direction", 2),
        "move-zeroes": ("same_direction", 3),
        "remove-element": ("same_direction", 4),
        "remove-duplicates-from-sorted-array": ("same_direction", 5),
        "remove-duplicates-from-sorted-array-ii": ("same_direction", 6),
        "append-characters-to-string-to-make-subsequence": ("same_direction", 7),
        "string-compression": ("same_direction", 8),
        "buy-and-sell-crypto": ("same_direction", 9),
        "rotating-the-box": ("same_direction", 10),
        # merge
        "merge-sorted-array": ("merge", 0),
        # partition
        "sort-array-by-parity": ("partition", 0),
        "sort-colors": ("partition", 1),
        "rearrange-array-elements-by-sign": ("partition", 2),
        # expand_center
        "longest-palindromic-substring": ("expand_center", 0),
        "palindromic-substrings": ("expand_center", 1),
        # greedy_pair
        "assign-cookies": ("greedy_pair", 0),
        "boats-to-save-people": ("greedy_pair", 1),
        "gas-station": ("greedy_pair", 2),
        "partition-labels": ("greedy_pair", 3),
    },
    "sliding-window": {
        "minimum-recolors-to-get-k-consecutive-black-blocks": ("fixed_k", 0),
        "minimum-difference-between-highest-and-lowest-of-k-scores": ("fixed_k", 1),
        "number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold": ("fixed_k", 2),
        "grumpy-bookstore-owner": ("fixed_k", 3),
        "maximum-points-you-can-obtain-from-cards": ("fixed_k", 4),
        "check-if-array-is-sorted-and-rotated": ("variable", 0),
        "longest-turbulent-subarray": ("variable", 1),
        "max-consecutive-ones-iii": ("variable", 2),
        "fruit-into-baskets": ("variable", 3),
        "longest-substring-without-duplicates": ("variable", 4),
        "longest-repeating-substring-with-replacement": ("variable", 5),
        "subarray-product-less-than-k": ("variable", 6),
        "binary-subarrays-with-sum": ("variable", 7),
        "permutation-string": ("freq_window", 0),
        "subarrays-with-k-different-integers": ("freq_window", 1),
        "minimum-size-subarray-sum": ("min_window", 0),
        "minimum-window-with-characters": ("min_window", 1),
        "longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit": ("deque", 0),
        "sliding-window-maximum": ("deque", 1),
    },
    "binary-search": {
        "binary-search": ("basic", 0),
        "guess-number-higher-or-lower": ("basic", 1),
        "search-insert-position": ("bound", 0),
        "sqrtx": ("basic", 2),
        "valid-perfect-square": ("basic", 3),
        "find-first-and-last-position-of-element-in-sorted-array": ("bound", 1),
        "find-peak-element": ("bound", 2),
        "single-element-in-a-sorted-array": ("bound", 3),
        "find-minimum-in-rotated-sorted-array": ("rotated", 0),
        "find-target-in-rotated-sorted-array": ("rotated", 1),
        "search-in-rotated-sorted-array-ii": ("rotated", 2),
        "search-2d-matrix": ("bound", 4),
        "eating-bananas": ("answer_space", 0),
        "capacity-to-ship-packages-within-d-days": ("answer_space", 1),
        "frequency-of-the-most-frequent-element": ("answer_space", 2),
        "number-of-subsequences-that-satisfy-the-given-sum-condition": ("answer_space", 3),
        "random-pick-with-weight": ("bound", 5),
        "time-based-key-value-store": ("design_bs", 0),
        "find-in-mountain-array": ("rotated", 3),
        "split-array-largest-sum": ("answer_space", 4),
        "kth-smallest-product-of-two-sorted-arrays": ("answer_space", 5),
    },
    "stack": {
        "implement-queue-using-stacks": ("design", 0),
        "implement-stack-using-queues": ("design", 1),
        "validate-parentheses": ("basic", 0),
        "next-greater-element-i": ("basic", 1),
        "baseball-game": ("basic", 2),
        "minimum-stack": ("design", 0),
        "online-stock-span": ("monotonic", 1),
        "decode-string": ("parsing", 0),
        "simplify-path": ("parsing", 1),
        "basic-calculator-ii": ("parsing", 2),
        "evaluate-reverse-polish-notation": ("parsing", 3),
        "asteroid-collision": ("simulation", 0),
        "car-fleet": ("monotonic", 2),
        "minimum-remove-to-make-valid-parentheses": ("parsing", 4),
        "remove-all-adjacent-duplicates-in-string-ii": ("advanced", 0),
        "design-browser-history": ("design", 1),
        "largest-rectangle-in-histogram": ("monotonic", 3),
        "maximum-frequency-stack": ("advanced", 1),
        "number-of-visible-people-in-a-queue": ("monotonic", 4),
    },
    "linked-list": {
        "reverse-a-linked-list": ("reverse", 0),
        "merge-two-sorted-linked-lists": ("traversal", 0),
        "remove-linked-list-elements": ("traversal", 1),
        "linked-list-cycle-detection": ("fast_slow", 0),
        "non-cyclical-number": ("fast_slow", 1),
        "middle-of-the-linked-list": ("fast_slow", 2),
        "palindrome-linked-list": ("fast_slow", 3),
        "intersection-of-two-linked-lists": ("two_pointer", 0),
        "design-linked-list": ("design", 0),
        "design-circular-queue": ("design", 1),
        "lru-cache": ("design", 2),
        "add-two-numbers": ("traversal", 2),
        "add-two-numbers-ii": ("traversal", 3),
        "insertion-sort-list": ("traversal", 4),
        "remove-node-from-end-of-linked-list": ("two_pointer", 1),
        "reverse-linked-list-ii": ("reverse", 1),
        "rotate-list": ("reverse", 2),
        "reorder-linked-list": ("reverse", 3),
        "maximum-twin-sum-of-a-linked-list": ("reverse", 4),
        "copy-linked-list-with-random-pointer": ("advanced", 0),
        "lowest-common-ancestor-of-a-binary-tree-iii": ("two_pointer", 2),
        "lfu-cache": ("design", 0),
        "merge-k-sorted-linked-lists": ("advanced", 1),
        "reverse-nodes-in-k-group": ("reverse", 5),
    },
    "trees": {
        # Easy — basics then traversals
        "invert-a-binary-tree": ("basics", 0),
        "same-binary-tree": ("basics", 1),
        "depth-of-binary-tree": ("basics", 2),
        "balanced-binary-tree": ("basics", 3),
        "binary-tree-diameter": ("basics", 4),
        "subtree-of-a-binary-tree": ("basics", 5),
        "merge-two-binary-trees": ("basics", 6),
        "path-sum": ("path", 0),
        "range-sum-of-bst": ("bst", 0),
        "binary-tree-preorder-traversal": ("traversal", 0),
        "binary-tree-inorder-traversal": ("traversal", 1),
        "binary-tree-postorder-traversal": ("traversal", 2),
        "n-ary-tree-postorder-traversal": ("traversal", 3),
        # Medium — design/construct, BFS, BST, path
        "binary-search-tree-iterator": ("design", 0),
        "level-order-traversal-of-binary-tree": ("bfs", 0),
        "binary-tree-right-side-view": ("bfs", 1),
        "binary-tree-zigzag-level-order-traversal": ("bfs", 2),
        "check-completeness-of-a-binary-tree": ("bfs", 3),
        "populating-next-right-pointers-in-each-node": ("bfs", 4),
        "binary-tree-from-preorder-and-inorder-traversal": ("construct", 0),
        "construct-binary-tree-from-inorder-and-postorder-traversal": ("construct", 1),
        "construct-quad-tree": ("construct", 2),
        "insert-into-a-binary-search-tree": ("bst", 1),
        "delete-node-in-a-bst": ("bst", 2),
        "valid-binary-search-tree": ("bst", 3),
        "kth-smallest-integer-in-bst": ("bst", 4),
        "lowest-common-ancestor-in-binary-search-tree": ("bst", 5),
        "convert-bst-to-greater-tree": ("bst", 6),
        "recover-binary-search-tree": ("bst", 7),
        "count-good-nodes-in-binary-tree": ("path", 1),
        "sum-root-to-leaf-numbers": ("path", 2),
        "lowest-common-ancestor-of-a-binary-tree": ("path", 3),
        "delete-leaves-with-a-given-value": ("path", 4),
        # Hard
        "serialize-and-deserialize-binary-tree": ("design", 0),
        "binary-tree-maximum-path-sum": ("path", 5),
    },
}

LATER_PATTERN_CUES: list[tuple[str, list[str]]] = [
    ("two-pointers", ["two pointer", "three pointer"]),
    ("sliding-window", ["sliding window", "monotonic queue"]),
    ("binary-search", ["binary search"]),
    ("stack", ["monotonic stack", " stack"]),
    ("linked-list", ["linked list", "fast and slow"]),
    ("trees", ["binary tree", "bst", "inorder", "preorder", "postorder"]),
    ("tries", ["trie"]),
    ("heap", ["heap", "priority queue", "bucket sort"]),
    ("backtracking", ["backtrack"]),
    ("graphs", ["union find", "topolog", "bfs", "dfs", "graph"]),
    ("advanced-graphs", ["dijkstra", "bellman", "kruskal", "prim"]),
    ("greedy", ["greedy"]),
    ("intervals", ["interval", "line sweep"]),
    ("dp-1d", ["dynamic programming", " memo", "kadane"]),
    ("dp-2d", ["2-d dynamic", "2d dynamic", "two-dimensional"]),
    ("bit-manipulation", ["bitmask", "bit manipulation", "bitwise"]),
    ("math-geometry", ["geometry", "combinatorics", "sieve"]),
]


# Canonical "implement this structure/technique" problems, by pattern.
CANONICAL_DESIGN: dict[str, list[str]] = {
    "hashing": ["design-hashset", "design-hashmap"],
    "sliding-window": ["sliding-window-maximum"],
    "binary-search": ["binary-search", "time-based-key-value-store"],
    "tries": ["implement-prefix-tree", "implement-trie-prefix-tree"],
    "heap": ["kth-largest-element-in-a-stream"],
    "stack": [
        "implement-queue-using-stacks",
        "implement-stack-using-queues",
        "minimum-stack",
    ],
    "linked-list": [
        "reverse-a-linked-list",
        "design-linked-list",
        "design-circular-queue",
        "lru-cache",
        "lfu-cache",
    ],
    "trees": [
        "invert-a-binary-tree",
        "binary-search-tree-iterator",
        "serialize-and-deserialize-binary-tree",
    ],
}

# Construction problems that float to the front of whatever difficulty they have.
DESIGN_SLUGS: set[str] = {
    "lru-cache",
    "lfu-cache",
    "insert-delete-getrandom-o1",
    "insert-delete-getrandom-o1-duplicates-allowed",
    "design-twitter",
    "design-twitter-feed",
    "time-based-key-value-store",
    "snapshot-array",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def load_overrides() -> dict[str, dict]:
    if not OVERRIDES_PATH.exists():
        return {}
    raw = load_json(OVERRIDES_PATH)
    return raw if isinstance(raw, dict) else {}


def pattern_order() -> list[str]:
    return load_json(DATA / "patternOrder.json")


def pattern_rank(slug: str) -> int:
    order = pattern_order()
    try:
        return order.index(slug)
    except ValueError:
        return 999


def load_json_maybe(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def is_live_on_neetcode(slug: str) -> bool:
    """True when NeetCode metadata exists (API data !== null). Uses local cache."""
    cached = load_json_maybe(CACHE / f"{slug}.json")
    # Missing file or JSON literal `null` (dead NeetCode page).
    if cached is None:
        return False
    if not isinstance(cached, dict):
        return False
    if "data" in cached:
        return cached["data"] is not None
    return bool(cached.get("id") or cached.get("name"))


def is_excluded(entry: dict) -> bool:
    if entry.get("pro") is True:
        return True
    if entry.get("pattern") == "JavaScript":
        return True
    return False


def _meta(slug: str) -> dict:
    path = CACHE / f"{slug}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return data if isinstance(data, dict) else {}


def _compact(slug: str, compact_by: dict) -> dict:
    return compact_by.get(slug) or {}


def approach_titles(compact: dict) -> list[str]:
    titles: list[str] = []
    for a in compact.get("optimalApproaches") or []:
        titles.append(a if isinstance(a, str) else (a.get("title") or ""))
    return titles


def requires_hashing(
    slug: str,
    meta: dict,
    compact: dict,
    *,
    as_main: bool = True,
    overrides: dict | None = None,
) -> bool:
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "hashing":
        return True
    if ov.get("keep_in") and "hashing" in ov["keep_in"]:
        return True
    if ov.get("keep_in") and "hashing" not in ov["keep_in"]:
        return False

    if slug.startswith("design-hash") or "-hash" in slug:
        return True

    titles = approach_titles(compact)
    title_blob = "\n".join(titles)
    if HASH_TITLE_RE.search(title_blob):
        return True
    if re.search(r"negative marking|index marking|marking", title_blob, re.I):
        return True

    topics = [t.lower() for t in (meta.get("topics") or [])]
    if "hash table" in topics:
        later_topics = (
            "sliding window",
            "two pointer",
            "binary search",
            "dynamic programming",
            "backtracking",
            "breadth-first search",
            "depth-first search",
        )
        blob = title_blob.lower()
        if not any(t in blob for t in later_topics):
            return True

    sols = meta.get("solutions") or {}
    code = "\n".join(
        [
            sols.get("python") or "",
            sols.get("java") or "",
            sols.get("cpp") or "",
            sols.get("javascript") or "",
        ]
    )
    if HASH_CODE_RE.search(code):
        if as_main and titles:
            later_cues = (
                "sliding window",
                "two pointer",
                "binary search",
                "backtrack",
                "dynamic programming",
                "heap",
                "bfs",
                "dfs",
            )
            if any(any(c in t.lower() for c in later_cues) for t in titles):
                return False
        return True
    return False


def later_pattern_from_titles(titles: list[str], *, after: str | None = None) -> str | None:
    """If titles name later techniques, return the *latest* matching pattern (later wins)."""
    blob = " ".join(titles).lower()
    min_rank = pattern_rank(after) + 1 if after else 0
    best: str | None = None
    best_rank = -1
    for pattern, cues in LATER_PATTERN_CUES:
        r = pattern_rank(pattern)
        if r < min_rank:
            continue
        if any(c in blob for c in cues) and r > best_rank:
            best = pattern
            best_rank = r
    return best


def hashing_in_title(title: str) -> bool:
    if HASH_TITLE_RE.search(title):
        return True
    if re.search(
        r"negative marking|index marking|counting sort|boolean array|"
        r"\bcounting\b|custom sort|first and last index|first index \(hash",
        title,
        re.I,
    ):
        return True
    return False


def main_approach_is_hashing(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    """True when the first NeetCode optimal approach is hash/map/set/freq based."""
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "hashing":
        return True
    if ov.get("keep_in") and "hashing" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "hashing":
        return False
    if ov.get("drop_from") and "hashing" in ov["drop_from"]:
        return False

    titles = approach_titles(compact)
    if not titles:
        return requires_hashing(slug, meta, compact, overrides=overrides)

    first = titles[0]
    if hashing_in_title(first):
        return True
    if NON_HASHING_MAIN_RE.search(first):
        return False
    if re.search(r"\bprefix sum\b", first, re.I):
        if any(hashing_in_title(t) for t in titles[:2]):
            return True
        if slug in {
            "number-of-sub-arrays-with-odd-sum",
            "make-sum-divisible-by-p",
            "count-vowel-strings-in-ranges",
        }:
            return True
        return False

    for title in titles[:2]:
        if hashing_in_title(title):
            return True
    return False


def main_approach_is_two_pointers(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    """True when the main NeetCode approach is two/three pointers."""
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "two-pointers":
        return True
    if ov.get("keep_in") and "two-pointers" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "two-pointers":
        return False
    if ov.get("drop_from") and "two-pointers" in ov["drop_from"]:
        return False

    titles = approach_titles(compact)
    if not titles:
        return False

    first = titles[0]
    if TWO_POINTER_TITLE_RE.search(first):
        return True
    if NON_TWO_POINTER_MAIN_RE.search(first):
        return False
    for title in titles[:2]:
        if TWO_POINTER_TITLE_RE.search(title):
            return True
    return False


def main_approach_is_sliding_window(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "sliding-window":
        return True
    if ov.get("keep_in") and "sliding-window" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "sliding-window":
        return False
    if ov.get("drop_from") and "sliding-window" in ov["drop_from"]:
        return False

    titles = approach_titles(compact)
    if not titles:
        return False
    first = titles[0]
    if SW_TITLE_RE.search(first):
        return True
    if NON_SW_MAIN_RE.search(first):
        return False
    for title in titles[:2]:
        if SW_TITLE_RE.search(title):
            return True
    return False


def main_approach_is_binary_search(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "binary-search":
        return True
    if ov.get("keep_in") and "binary-search" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "binary-search":
        return False
    if ov.get("drop_from") and "binary-search" in ov["drop_from"]:
        return False

    titles = approach_titles(compact)
    if not titles:
        return False
    first = titles[0]
    if BS_TITLE_RE.search(first):
        return True
    if NON_BS_MAIN_RE.search(first):
        return False
    for title in titles[:2]:
        if BS_TITLE_RE.search(title):
            return True
    return False


def main_approach_is_stack(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "stack":
        return True
    if ov.get("keep_in") and "stack" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "stack":
        return False
    if ov.get("drop_from") and "stack" in ov["drop_from"]:
        return False

    if slug in {"implement-stack-using-queues", "implement-queue-using-stacks"}:
        return True

    titles = approach_titles(compact)
    if not titles:
        return False
    first = titles[0]
    if STACK_TITLE_RE.search(first):
        return True
    if NON_STACK_MAIN_RE.search(first):
        return False
    for title in titles[:2]:
        if STACK_TITLE_RE.search(title):
            return True
    return False


def main_approach_is_linked_list(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "linked-list":
        return True
    if ov.get("keep_in") and "linked-list" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "linked-list":
        return False
    if ov.get("drop_from") and "linked-list" in ov["drop_from"]:
        return False

    if slug in {"non-cyclical-number", "lowest-common-ancestor-of-a-binary-tree-iii"}:
        return True

    if LINKED_LIST_SLUG_RE.search(slug):
        return True

    titles = approach_titles(compact)
    if not titles:
        return False
    first = titles[0]
    if LL_TITLE_RE.search(first):
        return True
    if NON_LL_MAIN_RE.search(first):
        return False
    for title in titles[:2]:
        if LL_TITLE_RE.search(title):
            return True
    return False


def main_approach_is_trees(
    slug: str,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    ov = (overrides or {}).get(slug, {})
    if ov.get("main_pattern") == "trees":
        return True
    if ov.get("keep_in") and "trees" in ov["keep_in"]:
        return True
    if ov.get("main_pattern") and ov["main_pattern"] != "trees":
        return False
    if ov.get("drop_from") and "trees" in ov["drop_from"]:
        return False

    if TREES_SLUG_RE.search(slug):
        return True

    titles = approach_titles(compact)
    if not titles:
        return False
    first = titles[0]
    if NON_TREES_MAIN_RE.search(first):
        return False
    if TREES_TITLE_RE.search(first):
        return True
    for title in titles[:2]:
        if TREES_TITLE_RE.search(title):
            return True
    return False


def primary_patterns(
    slug: str,
    entry: dict,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> list[str]:
    ov = (overrides or {}).get(slug, {})
    if "patterns" in ov:
        return list(ov["patterns"])
    if ov.get("main_pattern"):
        return [ov["main_pattern"]]

    titles = approach_titles(compact)
    blob = " ".join(titles).lower()

    if main_approach_is_hashing(slug, meta, compact, overrides):
        return ["hashing"]

    if main_approach_is_two_pointers(slug, meta, compact, overrides):
        return ["two-pointers"]

    if main_approach_is_sliding_window(slug, meta, compact, overrides):
        return ["sliding-window"]

    if main_approach_is_binary_search(slug, meta, compact, overrides):
        return ["binary-search"]

    if main_approach_is_stack(slug, meta, compact, overrides):
        return ["stack"]

    if main_approach_is_linked_list(slug, meta, compact, overrides):
        return ["linked-list"]

    if main_approach_is_trees(slug, meta, compact, overrides):
        return ["trees"]

    later = later_pattern_from_titles(titles)
    if later:
        return [later]

    topics = [t.lower() for t in (meta.get("topics") or [])]
    if "trie" in topics or "prefix tree" in blob:
        return ["tries"]
    if "backtracking" in topics or "recursion" in topics:
        if re.search(r"subset|combination|permutation", slug):
            return ["backtracking"]
    if "greedy" in topics and "array" in topics:
        pass

    return ["arrays"]


def belongs_in_pattern(
    pattern: str,
    slug: str,
    entry: dict,
    meta: dict,
    compact: dict,
    overrides: dict | None = None,
) -> bool:
    if is_excluded(entry):
        return False
    if not is_live_on_neetcode(slug):
        return False

    ov = (overrides or {}).get(slug, {})
    if ov.get("keep_in") is not None:
        return pattern in ov["keep_in"]
    if ov.get("drop_from") and pattern in ov["drop_from"]:
        return False

    patterns = primary_patterns(slug, entry, meta, compact, overrides)

    if pattern == "arrays":
        return patterns == ["arrays"]

    if pattern == "hashing":
        if not main_approach_is_hashing(slug, meta, compact, overrides):
            return False
        titles = approach_titles(compact)
        blob = " ".join(titles).lower()
        if "sliding window" in blob and requires_hashing(slug, meta, compact):
            return False
        return True

    if pattern == "two-pointers":
        return main_approach_is_two_pointers(slug, meta, compact, overrides)

    if pattern == "sliding-window":
        return main_approach_is_sliding_window(slug, meta, compact, overrides)

    if pattern == "binary-search":
        return main_approach_is_binary_search(slug, meta, compact, overrides)

    if pattern == "stack":
        return main_approach_is_stack(slug, meta, compact, overrides)

    if pattern == "linked-list":
        return main_approach_is_linked_list(slug, meta, compact, overrides)

    if pattern == "trees":
        return main_approach_is_trees(slug, meta, compact, overrides)

    # Generic: belongs if pattern is in primary list and not superseded by earlier audit
    return pattern in patterns


def infer_binary_search_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("binary-search", {}):
        return PEDAGOGY["binary-search"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if "time-based" in slug or "design" in titles:
        return ("design_bs", 50)
    if "rotated" in titles or "mountain" in titles or "rotated" in slug:
        return ("rotated", 50)
    if "capacity" in slug or "banana" in slug or "ship" in slug or "split" in slug:
        return ("answer_space", 50)
    if "bound" in titles or "first" in titles or "last" in titles or "peak" in titles:
        return ("bound", 50)
    return ("basic", 50)


def infer_linked_list_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("linked-list", {}):
        return PEDAGOGY["linked-list"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if slug.startswith("design-") or slug in {"lru-cache", "lfu-cache"}:
        return ("design", 50)
    if "reverse" in titles or "reverse" in slug:
        return ("reverse", 50)
    if "fast" in titles and "slow" in titles:
        return ("fast_slow", 50)
    if "two pointer" in titles:
        return ("two_pointer", 50)
    if "random" in slug or "merge-k" in slug:
        return ("advanced", 50)
    return ("traversal", 50)


def infer_trees_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("trees", {}):
        return PEDAGOGY["trees"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if "serialize" in slug or "iterator" in slug:
        return ("design", 50)
    if "construct" in slug or "from-preorder" in slug or "from-inorder" in slug:
        return ("construct", 50)
    if "bst" in slug or "binary-search-tree" in slug:
        return ("bst", 50)
    if "breadth" in titles or "level" in slug or "zigzag" in slug or "right-side" in slug:
        return ("bfs", 50)
    if "path" in slug or "lca" in slug or "ancestor" in slug:
        return ("path", 50)
    if "traversal" in slug or "inorder" in slug or "preorder" in slug or "postorder" in slug:
        return ("traversal", 50)
    return ("basics", 50)


def infer_stack_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("stack", {}):
        return PEDAGOGY["stack"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if slug.startswith("implement-") or slug.startswith("design-") or "design" in titles:
        return ("design", 50)
    if "monotonic" in titles or "greater element" in slug or "stock span" in slug:
        return ("monotonic", 50)
    if "calculator" in slug or "decode" in slug or "polish" in slug or "parentheses" in slug:
        return ("parsing", 50)
    if "collision" in slug or "fleet" in slug:
        return ("simulation", 50)
    if "histogram" in slug or "frequency stack" in slug or "duplicate" in slug:
        return ("advanced", 50)
    return ("basic", 50)


def infer_sliding_window_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("sliding-window", {}):
        return PEDAGOGY["sliding-window"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if "deque" in titles or "monotonic" in titles:
        return ("deque", 50)
    if "minimum" in titles and "window" in titles:
        return ("min_window", 50)
    if "permutation" in titles or "anagram" in titles or "character" in titles:
        return ("freq_window", 50)
    if "size k" in titles or "fixed" in titles:
        return ("fixed_k", 50)
    return ("variable", 50)


def infer_two_pointers_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("two-pointers", {}):
        return PEDAGOGY["two-pointers"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if "three pointer" in titles or "partition" in titles:
        return ("partition", 50)
    if "palindrom" in titles or "expand" in titles:
        return ("expand_center", 50)
    if "merge" in titles:
        return ("merge", 50)
    if "linked" in titles:
        return ("linked_list", 50)
    if "greedy" in titles or "boat" in titles or "cookie" in titles:
        return ("greedy_pair", 50)
    if "remove" in titles or "move" in titles or "subsequence" in titles:
        return ("same_direction", 50)
    return ("opposite_ends", 50)


def infer_hashing_family(slug: str, compact: dict) -> tuple[str, int]:
    if slug in PEDAGOGY.get("hashing", {}):
        return PEDAGOGY["hashing"][slug]
    titles = " ".join(approach_titles(compact)).lower()
    if "design" in titles or slug.startswith("design-hash"):
        return ("design_map", 50)
    if "rolling hash" in titles or ("prefix" in titles and "hash" in titles):
        return ("prefix_hash", 50)
    if "counting sort" in titles or "relative sort" in titles:
        return ("counting_sort", 50)
    if "negative marking" in titles or "index marking" in titles:
        return ("index_marking", 50)
    if "frequency" in titles or "counter" in titles or "anagram" in titles:
        return ("freq_count", 50)
    if "hash set" in titles or "duplicate" in titles or "intersection" in titles:
        return ("set_membership", 50)
    return ("map_lookup", 50)


def technique_family(pattern: str, slug: str, compact: dict | None = None) -> str:
    if slug in PEDAGOGY.get(pattern, {}):
        return PEDAGOGY[pattern][slug][0]
    if pattern == "hashing" and compact is not None:
        return infer_hashing_family(slug, compact)[0]
    if pattern == "two-pointers" and compact is not None:
        return infer_two_pointers_family(slug, compact)[0]
    if pattern == "sliding-window" and compact is not None:
        return infer_sliding_window_family(slug, compact)[0]
    if pattern == "binary-search" and compact is not None:
        return infer_binary_search_family(slug, compact)[0]
    if pattern == "stack" and compact is not None:
        return infer_stack_family(slug, compact)[0]
    if pattern == "linked-list" and compact is not None:
        return infer_linked_list_family(slug, compact)[0]
    if pattern == "trees" and compact is not None:
        return infer_trees_family(slug, compact)[0]
    return "scan"


def within_family_rank(pattern: str, slug: str, compact: dict | None = None) -> int:
    if slug in PEDAGOGY.get(pattern, {}):
        return PEDAGOGY[pattern][slug][1]
    if pattern == "hashing" and compact is not None:
        return infer_hashing_family(slug, compact)[1]
    if pattern == "two-pointers" and compact is not None:
        return infer_two_pointers_family(slug, compact)[1]
    if pattern == "sliding-window" and compact is not None:
        return infer_sliding_window_family(slug, compact)[1]
    if pattern == "binary-search" and compact is not None:
        return infer_binary_search_family(slug, compact)[1]
    if pattern == "stack" and compact is not None:
        return infer_stack_family(slug, compact)[1]
    if pattern == "linked-list" and compact is not None:
        return infer_linked_list_family(slug, compact)[1]
    if pattern == "trees" and compact is not None:
        return infer_trees_family(slug, compact)[1]
    return 999


def is_design_problem(
    pattern: str,
    slug: str,
    compact: dict | None = None,
    overrides: dict | None = None,
) -> bool:
    """True if this problem constructs the DS / canonical technique for P."""
    ov = (overrides or {}).get(slug, {})
    if ov.get("design") is True:
        return True
    if ov.get("design") is False:
        return False
    if slug in CANONICAL_DESIGN.get(pattern, []):
        return True
    if slug in DESIGN_SLUGS:
        return True
    if slug.startswith("design-") or slug.startswith("implement-"):
        return True
    family = technique_family(pattern, slug, compact)
    return family.startswith("design")


def design_rank(pattern: str, slug: str) -> int:
    """Among design problems in a band: HashSet before HashMap, etc."""
    leaders = CANONICAL_DESIGN.get(pattern, [])
    if slug in leaders:
        return leaders.index(slug)
    return 50 + (0 if slug.startswith("design-") else 10)


def sort_key_for_pattern(
    pattern: str,
    p: dict,
    compact_by: dict,
    desired_index: dict,
    overrides: dict | None = None,
) -> tuple:
    d = DIFF_RANK.get(p["difficulty"], 9)
    if pattern not in p["patterns"]:
        return (d, 1, 0, 0, 0, p["name"])
    fam = FAMILY_RANK.get(pattern, {})
    slug = p["slug"]
    compact = compact_by.get(slug) or {}
    design = is_design_problem(pattern, slug, compact, overrides)
    return (
        d,
        0 if design else 1,
        design_rank(pattern, slug) if design else 99,
        fam.get(technique_family(pattern, slug, compact), 99),
        within_family_rank(pattern, slug, compact),
        desired_index.get(slug, 10_000),
        p["name"],
    )


def audit_pattern(pattern: str) -> dict:
    all_items = {p["slug"]: p for p in load_json(DATA / "neetcode-all.json")}
    compact_by = {
        p["slug"]: p for p in load_json(DATA / "neetcode-all-true-patterns.compact.json")
    }
    curriculum = load_json(DATA / "curriculum.json")
    overrides = load_overrides()

    current = [p for p in curriculum if pattern in p["patterns"]]
    rows: list[dict] = []
    moves: dict[str, list[str]] = {}
    keep: list[dict] = []
    needs_review: list[dict] = []

    for i, p in enumerate(current):
        slug = p["slug"]
        entry = all_items.get(slug, {})
        meta = _meta(slug)
        compact = _compact(slug, compact_by)

        excl = is_excluded(entry)
        live = is_live_on_neetcode(slug)
        keep_pat = belongs_in_pattern(pattern, slug, entry, meta, compact, overrides)
        patterns = primary_patterns(slug, entry, meta, compact, overrides)
        family = technique_family(pattern, slug, compact) if keep_pat else None
        design = (
            is_design_problem(pattern, slug, compact, overrides) if keep_pat else False
        )

        confidence = "high"
        notes = ""
        if not compact.get("optimalApproaches") and not overrides.get(slug):
            confidence = "medium"
            notes = "no optimal approaches in compact data"

        if excl:
            verdict = "REMOVE"
            target: list[str] = []
        elif not live:
            verdict = "REMOVE"
            target = []
            notes = "dead NeetCode link"
        elif keep_pat:
            verdict = "KEEP"
            target = [pattern]
            keep.append(p)
        else:
            verdict = f"MOVE:{','.join(patterns)}"
            target = patterns
            moves[slug] = patterns
            if confidence == "medium":
                needs_review.append(
                    {
                        "slug": slug,
                        "name": p["name"],
                        "from_pattern": pattern,
                        "target_patterns": patterns,
                        "reason": notes or verdict,
                        "confidence": confidence,
                    }
                )

        rows.append(
            {
                "index": i,
                "slug": slug,
                "name": p["name"],
                "difficulty": p["difficulty"],
                "current_patterns": p["patterns"],
                "verdict": verdict,
                "target_patterns": target,
                "technique_family": family,
                "is_design": design,
                "within_family_rank": within_family_rank(pattern, slug, compact)
                if keep_pat
                else None,
                "live_on_neetcode": live,
                "hashing": requires_hashing(slug, meta, compact, overrides=overrides),
                "status": compact.get("status"),
                "optimal_approaches": compact.get("optimalApproaches") or [],
                "confidence": confidence,
                "notes": notes,
            }
        )

    ordered = sorted(
        keep,
        key=lambda x: sort_key_for_pattern(
            pattern, x, compact_by, {}, overrides
        ),
    )
    desired_slugs = [p["slug"] for p in ordered]
    current_keep_slugs = [p["slug"] for p in keep]

    for row in rows:
        if row["verdict"] != "KEEP":
            row["order_verdict"] = "N/A"
            continue
        cur_pos = current_keep_slugs.index(row["slug"])
        new_pos = desired_slugs.index(row["slug"])
        if cur_pos == new_pos:
            row["order_verdict"] = "ORDER_OK"
        else:
            neighbor = desired_slugs[new_pos - 1] if new_pos > 0 else "(start)"
            row["order_verdict"] = f"ORDER_WRONG: should be at {new_pos} after {neighbor}"

    report = {
        "pattern": pattern,
        "before": len(current),
        "after": len(keep),
        "moves": moves,
        "desired_order": desired_slugs,
        "needs_review": needs_review,
        "rows": rows,
    }
    out = DATA / f"{pattern}-audit-report.json"
    save_json(out, report)
    return report


def apply_pattern_fixes(pattern: str, report: dict) -> None:
    curriculum = load_json(DATA / "curriculum.json")
    moves: dict[str, list[str]] = report["moves"]
    desired: list[str] = report["desired_order"]
    desired_index = {s: i for i, s in enumerate(desired)}
    keep_slugs = {r["slug"] for r in report["rows"] if r["verdict"] == "KEEP"}

    to_remove = {
        r["slug"]
        for r in report["rows"]
        if r["verdict"] == "REMOVE"
    }

    untagged_path = DATA / "untagged.json"
    untagged: list[dict] = []
    if untagged_path.exists():
        raw = load_json(untagged_path)
        untagged = raw if isinstance(raw, list) else []
    untagged_slugs = {x["slug"] for x in untagged}

    new_curriculum: list[dict] = []
    for p in curriculum:
        if p["slug"] in to_remove:
            continue
        slug = p["slug"]
        if slug in moves:
            new_patterns = list(p["patterns"])
            if pattern in new_patterns:
                new_patterns = [x for x in new_patterns if x != pattern]
            for mp in moves[slug]:
                if mp and mp not in new_patterns:
                    new_patterns.append(mp)
            p["patterns"] = new_patterns
            if moves[slug] == [] and slug not in untagged_slugs:
                untagged.append(
                    {
                        "slug": slug,
                        "name": p["name"],
                        "difficulty": p["difficulty"],
                        "reason": f"Moved out of {pattern} — deferred until untagged pass",
                    }
                )
                untagged_slugs.add(slug)
        elif slug in keep_slugs:
            p["patterns"] = [pattern]
        new_curriculum.append(p)

    # Reorder only problems tagged with P; leave every other row in place.
    keepers = [p for p in new_curriculum if pattern in p["patterns"]]
    keepers.sort(key=lambda p: desired_index.get(p["slug"], 10_000))
    ki = 0
    rebuilt: list[dict] = []
    for p in new_curriculum:
        if pattern in p["patterns"]:
            rebuilt.append(keepers[ki])
            ki += 1
        else:
            rebuilt.append(p)

    save_json(DATA / "curriculum.json", rebuilt)
    save_json(untagged_path, untagged)

    # Merge needs_review
    existing: list[dict] = []
    if NEEDS_REVIEW_PATH.exists():
        raw = load_json(NEEDS_REVIEW_PATH)
        existing = raw if isinstance(raw, list) else []
    seen = {(x["slug"], x.get("from_pattern")) for x in existing}
    for item in report.get("needs_review") or []:
        key = (item["slug"], item.get("from_pattern"))
        if key not in seen:
            existing.append(item)
            seen.add(key)
    save_json(NEEDS_REVIEW_PATH, existing)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a curriculum pattern list")
    parser.add_argument(
        "--pattern",
        default="arrays",
        help="Pattern slug from patternOrder.json (default: arrays)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply MOVE/REMOVE/reorder to curriculum.json",
    )
    args = parser.parse_args()

    report = audit_pattern(args.pattern)
    out = DATA / f"{args.pattern}-audit-report.json"
    print(f"Wrote {out}")
    print(f"{args.pattern}_before={report['before']} {args.pattern}_after={report['after']}")
    dead = sum(1 for r in report["rows"] if not r.get("live_on_neetcode", True))
    print(f"dead_links_in_list={dead}")
    if report["moves"]:
        print("moves:", report["moves"])
    print("desired_order:")
    for i, s in enumerate(report["desired_order"]):
        print(f"  {i:02d} {s}")

    if args.apply:
        apply_pattern_fixes(args.pattern, report)
        print("Applied fixes to data/curriculum.json")


if __name__ == "__main__":
    main()
