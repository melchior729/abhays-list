# Abhay's List

A personal **NeetCode pattern tracker** — a curated, pedagogically ordered problem list grouped by DSA pattern, with solve progress synced from a local [neetcode-submissions](https://github.com/melchior729/neetcode-submissions) GitHub repo (not from a NeetCode account login).

Built with Next.js and deployed on Vercel.

## What it does

NeetCode's built-in lists (150, All, Roadmap) are useful but not tailored to a pattern-first study path. This app replaces them with a **hand-audited curriculum** of **439 live NeetCode problems** across **19 patterns**, ordered for learning — easy → medium → hard within each list, with construction/design problems leading each difficulty band before problems that use the structure.

Solve progress is derived from folder names in [`neetcode-submissions`](https://github.com/melchior729/neetcode-submissions): each solved problem is a directory under `Data Structures & Algorithms/<slug>/`. The tracker reads that clone locally (or via CI) and marks problems done in the UI.

### UI

- **Pattern rail** — all 19 patterns in learning order, with per-pattern solved/total counts and completion status.
- **Pattern detail** — searchable problem list with difficulty filter, Open/Done sort, and direct links to NeetCode problem pages.
- **Progress bars** — overall and per-pattern breakdown by easy / medium / hard.
- **Mobile layout** — collapsible rail; back navigation on small screens.
- **Settings** — quick links to the submissions repo and NeetCode practice.
- **Demo mode** — append `?demo=all` to mark every curriculum problem as solved (useful for UI preview).

Pattern URLs like `/pattern/hashing` redirect to `/?p=hashing`.

## Goals

1. **Pattern-first progression** — work through patterns top to bottom (`arrays` → … → `math-geometry`), not a flat difficulty-sorted grind.
2. **Curated, not exhaustive** — exclude NeetCode Pro, JavaScript-only, and dead problem links; keep only problems with a live NeetCode page.
3. **Design-before-use** — implement-the-structure problems (e.g. Design HashSet, Binary Search, LRU Cache) lead their difficulty band before problems that assume the structure exists.
4. **Git-backed progress** — solved state lives in version-controlled submission folders, syncable to production automatically.
5. **Auditable curriculum** — each pattern list is maintained with explicit audit rules and Python tooling, not ad-hoc edits.

## Learning model

Within each pattern list:

1. **Difficulty bands** — easy, then medium, then hard.
2. **Design-before-use** — construction / implement-X problems lead that band (e.g. Design HashMap before Two Sum-style hashing usage; Binary Search before search-on-answer problems).
3. **Technique families** — related techniques grouped and ordered (e.g. two-pointers: opposite ends → same direction → merge → partition).
4. **Multi-list tagging** — a problem can appear in multiple pattern lists when the approaches are fundamentally different; supporting skills stay under the later/main pattern.

Full audit rules: [`data/pattern-audit-rules.md`](data/pattern-audit-rules.md).

### Patterns (learning order)

| # | Pattern | Problems |
|---|---------|----------|
| 01 | Arrays | 35 |
| 02 | Hashing | 57 |
| 03 | Two Pointers | 26 |
| 04 | Sliding Window | 19 |
| 05 | Binary Search | 21 |
| 06 | Stack | 20 |
| 07 | Linked List | 25 |
| 08 | Trees | 36 |
| 09 | Tries | 3 |
| 10 | Heap | 11 |
| 11 | Backtracking | 18 |
| 12 | Graphs | 31 |
| 13 | Advanced Graphs | 8 |
| 14 | Greedy | 30 |
| 15 | Intervals | 10 |
| 16 | 1D Dynamic Programming | 26 |
| 17 | 2D Dynamic Programming | 23 |
| 18 | Bit Manipulation | 14 |
| 19 | Math & Geometry | 26 |

All 19 pattern lists are **complete** (audited 2026-08-25). Counts are live curriculum rows per pattern (some problems appear in more than one list). Status details: [`data/pattern-status.json`](data/pattern-status.json).

Curriculum difficulty split: **147 easy · 243 medium · 49 hard**.

## Tech stack

- **Next.js 16** (App Router, static generation)
- **React 19** + **TypeScript**
- **Tailwind CSS 4**
- **Node 22** in CI

## Getting started

```bash
git clone https://github.com/melchior729/abhays-list.git
cd abhays-list
npm install

# Clone submissions repo alongside (or set NEETCODE_SUBMISSIONS_DIR)
git clone https://github.com/melchior729/neetcode-submissions.git ../neetcode-submissions

just update        # refresh solved set → data/generated.json
npm run dev        # http://localhost:3000
npm run build      # production build
```

After `just update`, commit `data/generated.json` if you want Vercel/production to show the latest progress.

### Environment

| Variable | Purpose |
|----------|---------|
| `NEETCODE_SUBMISSIONS_DIR` | Path to local `neetcode-submissions` clone. Defaults to `~/code/neetcode-submissions`, then `../neetcode-submissions`. |

## Project structure

```
abhays-list/
├── src/
│   ├── app/                  # Next.js pages (home, pattern redirects)
│   ├── components/           # TrackerShell, PatternDetailClient, SearchBar, …
│   └── lib/                  # data loading, progress math, pattern helpers
├── data/
│   ├── curriculum.json       # Master problem list (hand-curated)
│   ├── patternOrder.json     # Pattern learning order
│   ├── generated.json        # Solved slugs + git dates (auto-generated)
│   ├── pattern-status.json   # Audit completion per pattern
│   ├── pattern-audit-rules.md
│   ├── neetcode-meta-cache/  # Cached NeetCode API metadata for audits
│   └── *-audit-report.json  # Per-pattern audit outputs
├── scripts/
│   ├── generate-data.ts      # Scan submissions → generated.json
│   ├── audit-pattern-list.py # Curriculum audit + optional --apply
│   └── retag-patterns.py     # Bulk pattern retagging
├── .github/workflows/
│   └── sync-submissions.yml  # Auto-sync on submissions push
└── justfile                  # `just update`, `just copy`
```

## Data files

| File | Role |
|------|------|
| `data/patternOrder.json` | Learning order for pattern cards |
| `data/curriculum.json` | Problems (slug, patterns[], difficulty, NeetCode URL) — one row per problem |
| `data/generated.json` | Solved slugs + git commit dates — refreshed by `just update`; do not hand-edit |
| `data/pattern-audit-rules.md` | Curriculum audit rules and pattern completion status |
| `data/pattern-status.json` | Which pattern lists are complete, with notes |
| `data/pattern-overrides.json` | Manual audit overrides |
| `data/dead-neetcode-links.json` | Removed slugs with no live NeetCode problem page |
| `data/needs-review.json` | Problems flagged NEEDS_REVIEW during audit |
| `data/neetcode-all.json` | Full NeetCode All list (reference; not used by the tracker UI) |

## Curriculum maintenance

Audit a pattern list (dry run):

```bash
python scripts/audit-pattern-list.py --pattern hashing
```

Apply audit changes to `curriculum.json`:

```bash
python scripts/audit-pattern-list.py --pattern hashing --apply
```

Global prerequisites on every audit:

- Remove NeetCode Pro and JavaScript-only problems
- Remove slugs with no live NeetCode page (`isLiveOnNeetCode`)

## Auto-sync from GitHub

Pushes to [`neetcode-submissions`](https://github.com/melchior729/neetcode-submissions) trigger a workflow that calls `repository_dispatch` on this repo. The [`sync-submissions`](.github/workflows/sync-submissions.yml) workflow then:

1. Checks out the latest `neetcode-submissions`
2. Runs `npm run generate` → updates `data/generated.json`
3. Commits and pushes to `main` (if anything changed)

Vercel redeploys on that push automatically.

**One-time setup:** create a fine-grained PAT (or classic token) with `repo` scope on `abhays-list`, add it as **`ABHAYS_LIST_PAT`** in the `neetcode-submissions` repo secrets ([Settings → Secrets → Actions](https://github.com/melchior729/neetcode-submissions/settings/secrets/actions)).

Manual sync: **Actions → Sync NeetCode submissions → Run workflow** on this repo.

## Deployment

Production uses the committed `data/generated.json`. Options:

1. Run `just update` locally, commit, and push — Vercel rebuilds.
2. Rely on the GitHub Action above when submissions are pushed.
3. Wire a Vercel deploy hook from `neetcode-submissions` after bulk sync.

## Related repos

- [**neetcode-submissions**](https://github.com/melchior729/neetcode-submissions) — solved-problem folders; source of truth for progress
- [**abhays-list**](https://github.com/melchior729/abhays-list) — this tracker (curriculum + UI)
