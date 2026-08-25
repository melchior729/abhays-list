# Pattern curriculum audit rules

Global prerequisites (run before any pattern audit):

1. **REMOVE** if `pro === true` or NeetCode bucket is `JavaScript`
2. **REMOVE** if `isLiveOnNeetCode(slug)` is false (metadata API returns `data: null`)

Pattern order: see `data/patternOrder.json`.

```text
arrays → hashing → two-pointers → sliding-window → binary-search →
stack → linked-list → trees → tries → heap → backtracking → graphs →
advanced-graphs → greedy → intervals → dp-1d → dp-2d → bit-manipulation → math-geometry
```

## Status

| Pattern | Status | Count |
|---------|--------|-------|
| arrays | **complete** | 34 live problems |
| hashing | **complete** | 53 live problems |
| two-pointers | **complete** | 26 live problems |
| sliding-window | **complete** | 19 live problems |
| binary-search | **complete** | 21 live problems |
| stack | **complete** | 20 live problems |
| linked-list | **complete** | 25 live problems |
| trees | **complete** | 35 live problems |
| tries | **complete** | 3 live problems |
| heap | **complete** | 11 live problems |
| backtracking | **complete** | 18 live problems |
| graphs | **complete** | 31 live problems |
| advanced-graphs | **complete** | 8 live problems |
| greedy | **complete** | 27 live problems |
| intervals | **complete** | 9 live problems |
| dp-1d | **complete** | 27 live problems |
| dp-2d | **complete** | 22 live problems |
| bit-manipulation | **complete** | 18 live problems |
| math-geometry | **complete** | 29 live problems |

## Membership cases

| Case | Action |
|------|--------|
| REMOVE | Delete from curriculum |
| KEEP | Ensure pattern tag present |
| ADD_ALTERNATE | Add pattern tag (multi-list OK) |
| DROP_SUPPORT | Remove tag; ensure later main pattern is tagged |
| MOVE | Remove tag; retag to later/main pattern(s) |
| NEEDS_REVIEW | Keep tags; append to `data/needs-review.json` |

## Learning model

1. User progresses patterns top → bottom.
2. Within each list: easy → medium → hard; within band, easiest technique first.
3. **Design-before-use:** construction / implement-X problems lead that difficulty band, before any problem that uses the structure. Applies at pattern level (Design HashSet/Map before hashing usage; Binary Search before binary-search usage) and inside a band (LRU Cache before Medium problems that need an LRU).
4. Multi-list when approaches are fundamentally different.
5. Supporting skills list under the **later/main** pattern, not the helper pattern.

## Arrays-specific (complete)

- Pure array iteration / prefix / suffix / simulation only.
- No hash map/set as main approach.
- No later-pattern requirement (two-pointers, sliding-window, etc.).
- Hashing + array → **hashing only**, not arrays.

## Hashing-specific

- Main approach uses map / set / freq table (incl. fixed-size count arrays).
- Freq map inside sliding window → **sliding-window**, not hashing (supporting role).

## Two-pointers-specific

- Main approach is two/three pointers (opposite ends, same-direction write, merge, partition, expand-center).
- Stack / heap / BFS / binary-search as main → those patterns, not two-pointers.
- Linked-list two-pointer classics (remove nth from end) → **linked-list**.
- Families: opposite_ends → same_direction → merge → partition → expand_center → greedy_pair
- Linked-list two-pointer problems (`remove-nth-from-end`, intersection) → **linked-list**.

## Sliding-window-specific

- Main approach is a window (fixed-k, variable, freq map in a window, min covering window, or monotonic deque).
- BFS / DP-as-main → those later patterns, not sliding-window.
- Families: fixed_k → variable → freq_window → min_window → deque.
- `sliding-window-maximum` is the design/deque lead-in for Hard.

## Binary-search-specific

- Main approach is binary search (on index, rotated array, or answer space).
- DP / Dijkstra / interval-greedy as main → those later patterns.
- Families: basic → bound → rotated → answer_space (design leads each difficulty band).
- Easy lead: **Binary Search**. Medium design lead: **Time Based Key-Value Store**.

## Ordering

```text
difficulty → design-before-use → techniqueFamily[P] → withinFamilyRank[P] → name
```

`isDesignProblem` (see `scripts/audit-pattern-list.py`): override `"design": true`, slugs `design-*` / `implement-*`, plus canonical implementers per pattern (`data/pattern-overrides.json` or `CANONICAL_DESIGN` in the script).

Run: `python scripts/audit-pattern-list.py --pattern <slug> [--apply]`
