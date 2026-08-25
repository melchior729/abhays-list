import fs from "fs";
import path from "path";

// Wireable for Vercel: uses GITHUB_TOKEN + API in prod, falls back to local fs in dev
const OWNER = "melchior729";
const REPO = "neetcode-submissions";
const BASE = `https://api.github.com/repos/${OWNER}/${REPO}`;

export async function getSolvedSlugs(): Promise<{ slugs: Set<string>; dates: Record<string, string> }> {
  const token = process.env.GITHUB_TOKEN;

  // 1. Try GitHub API if token available (Vercel prod) or env flag
  if (token) {
    try {
      return await fetchViaGitHub(token);
    } catch (e) {
      console.warn("GitHub API failed, falling back to local", e);
    }
  }

  // 2. Try local clone (dev: ~/code/neetcode-submissions or ../neetcode-submissions)
  const localCandidates = [
    "/home/abhay/code/neetcode-submissions",
    path.join(process.cwd(), "..", "neetcode-submissions"),
    path.join(process.cwd(), "neetcode-submissions"),
  ];
  for (const p of localCandidates) {
    if (fs.existsSync(path.join(p, "Data Structures & Algorithms"))) {
      return scanLocal(p);
    }
  }

  // 3. Public API without token (rate limited 60/hr) — last resort
  try {
    return await fetchViaGitHub(undefined);
  } catch {
    return { slugs: new Set(), dates: {} };
  }
}

function scanLocal(base: string) {
  const dir = path.join(base, "Data Structures & Algorithms");
  const slugs = new Set<string>();
  const dates: Record<string, string> = {};

  // use git log for dates if available
  try {
    const { execSync } = require("child_process");
    const log = execSync(`git -C "${base}" log --pretty=format:"%ad %s" --date=short --name-only`, { encoding: "utf8" });
    // parse per file
    const lines = log.split("\n");
    for (const line of lines) {
      const m = line.match(/Data Structures & Algorithms\/(.+?)\//);
      if (m) {
        const slug = m[1];
        slugs.add(slug);
        if (!dates[slug]) {
          const d = line.match(/^(\d{4}-\d{2}-\d{2})/);
          if (d) dates[slug] = d[1];
        }
      }
    }
  } catch {}

  // also ensure dirs without git history still count
  for (const d of fs.readdirSync(dir)) {
    if (fs.statSync(path.join(dir, d)).isDirectory()) slugs.add(d);
  }

  return { slugs, dates };
}

async function fetchViaGitHub(token?: string): Promise<{ slugs: Set<string>; dates: Record<string, string> }> {
  const headers: Record<string, string> = { Accept: "application/vnd.github.v3+json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  // Contents API for top folder (handles spaces via encoding)
  const url = `${BASE}/contents/${encodeURIComponent("Data Structures & Algorithms")}`;
  const res = await fetch(url, { headers, next: { revalidate: 3600 } } as any);
  if (!res.ok) throw new Error(`GitHub contents ${res.status}`);
  const data = (await res.json()) as Array<{ name: string; type: string }>;
  const slugs = new Set(data.filter(d => d.type === "dir").map(d => d.name));

  // optional: fetch commit dates via commits API (lightweight, last commit per file is heavy, so we skip precise per-slug dates in API mode)
  return { slugs, dates: {} };
}

// Build-time generator entrypoint (used by scripts/generate-data.ts)
export function getSolvedSlugsSyncLocal() {
  return scanLocal("/home/abhay/code/neetcode-submissions");
}
