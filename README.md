# Abhay's List

NeetCode pattern tracker. Progress comes from a local [`neetcode-submissions`](https://github.com/melchior729/neetcode-submissions) clone synced from NeetCode.

## Commands

```bash
npm install
just update        # refresh solved set from local clone → data/generated.json
npm run dev
npm run build
```

After `just update`, commit `data/generated.json` if you want Vercel/production to show the latest progress.

## Data

| File | Role |
|------|------|
| `data/patternOrder.json` | Learning order for pattern cards |
| `data/curriculum.json` | Problems (slug, patterns[], difficulty, NeetCode URL) — one row per problem |
| `data/generated.json` | Solved slugs + git dates — refreshed by `just update`, don't hand-edit |
| `data/pattern-audit-rules.md` | Curriculum audit rules and pattern completion status |
| `data/pattern-status.json` | Which pattern lists are complete |
| `data/dead-neetcode-links.json` | Removed slugs with no live NeetCode problem page |

Curriculum excludes Pro, JavaScript-only, and dead NeetCode links. Pattern lists are easy → medium → hard; **design/construction problems lead each difficulty band** (design-before-use). Audit with:

```bash
python scripts/audit-pattern-list.py --pattern hashing --apply
```

Local clone is read from `NEETCODE_SUBMISSIONS_DIR`, or defaults to `~/code/neetcode-submissions`.

## Vercel

Production uses the committed `data/generated.json`. Run `just update` locally, commit, and deploy — or wire a deploy hook from `neetcode-submissions` after bulk sync.
