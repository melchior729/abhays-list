# Abhay's List — NeetCode Progress Tracker

Black-theme, mobile-friendly tracker for curated NeetCode patterns. Hosted on Vercel, data from `melchior729/neetcode-submissions`.

## Features
- **Home `/`**: Header `X / TOTAL`, grid of pattern boxes in fixed learning order (`data/patternOrder.json`), per-difficulty progress bars (easy/medium/hard), **Play ▶** jumps to next unsolved at same difficulty as last solve (fallback to next unsolved), gold styling when 100%.
- **Pattern `/pattern/[slug]`**: Back to home, lists ALL problems in category, search/filter (text + difficulty), clicking opens NeetCode externally (no in-app code).
- **Design**: Black background, responsive 1→2→3 columns.
- **Data**: `data/curriculum.json` is source of truth (pattern assignment + difficulty + neetcodeUrl). `data/generated.json` is derived solved set from GitHub submissions.

## Data Files (you own)
- `data/patternOrder.json` — fixed learning order
- `data/curriculum.json` — 130 entries (120 solved + 10 unsolved placeholders). Edit to set your full list. Each entry:
  ```json
  { "slug": "two-integer-sum", "name": "Two Integer Sum", "pattern": "arrays-hashing", "difficulty": "easy", "neetcodeUrl": "https://neetcode.io/problems/two-sum" }
  ```
- `data/slugMap.json` — repo kebab → NeetCode slug overrides
- `data/generated.json` — auto-generated, do not hand-edit (run `npm run generate`)

## Local Dev
```bash
npm install
npm run generate   # scans /home/abhay/code/neetcode-submissions or GitHub API
npm run dev        # http://localhost:3000
npm run build      # generates + builds
```

## Wireable for Vercel (not yet connected — per your request)
The site is **pre-wired** but not yet connected:

1. **GitHub source of truth**: `melchior729/neetcode-submissions` (NeetCode GitHub Sync pushes on every solve)
2. **Build-time fetch**: `scripts/generate-data.ts` tries local clone → falls back to `GitHub API` with `GITHUB_TOKEN` env. On Vercel where local clone doesn't exist, it will use API.
3. **To connect (when you're ready to watch)**:
   ```bash
   vercel --prod                # link to melchior729/abhays-list
   # add env GITHUB_TOKEN (gh pat with repo scope) in Vercel dashboard
   # add deploy hook: Vercel Settings → Git Hooks → Deploy Hook URL
   # in neetcode-submissions repo: .github/workflows/deploy-hook.yml
   # on: push
   # jobs: { trigger: { runs-on: ubuntu-latest, steps: [{ run: curl -X POST $VERCEL_DEPLOY_HOOK }] } }
   ```
   Every NeetCode push then auto-rebuilds this site in ~60s.

## Editing Your List
- Change pattern order: edit `data/patternOrder.json`
- Re-assign problem to different pattern or change difficulty: edit `data/curriculum.json` `pattern` / `difficulty` fields
- Add new problem: append entry to `curriculum.json` (TOTAL increments automatically)
- Regenerate solved: `npm run generate` after pushing to submissions, or rely on Vercel hook
