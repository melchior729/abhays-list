import fs from "fs";
import path from "path";

type Generated = { solvedSlugs: string[]; gitDates: Record<string,string> };

function scanLocal(): { slugs: string[]; dates: Record<string,string> } | null {
  const candidates = [
    "/home/abhay/code/neetcode-submissions",
    path.join(process.cwd(), "..", "neetcode-submissions"),
    path.join(process.cwd(), "neetcode-submissions"),
  ];
  for (const base of candidates) {
    const dir = path.join(base, "Data Structures & Algorithms");
    if (!fs.existsSync(dir)) continue;
    const slugs = fs.readdirSync(dir).filter(f => fs.statSync(path.join(dir,f)).isDirectory()).sort();
    const dates: Record<string,string> = {};
    try {
      const { execSync } = require("child_process");
      const log = execSync(`git -C "${base}" log --pretty=format:"%ad %s" --date=short --name-only`, {encoding:"utf8"});
      for (const line of log.split("\n")) {
        const m = line.match(/Data Structures & Algorithms\/(.+?)\//);
        if (m && !dates[m[1]]) {
          const d = line.match(/^(\d{4}-\d{2}-\d{2})/);
          if (d) dates[m[1]] = d[1];
        }
      }
    } catch {}
    return { slugs, dates };
  }
  return null;
}

async function fetchViaGitHub(): Promise<{ slugs: string[]; dates: Record<string,string> } | null> {
  const token = process.env.GITHUB_TOKEN;
  const owner = "melchior729";
  const repo = "neetcode-submissions";
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent("Data Structures & Algorithms")}`;
  const headers: Record<string,string> = { Accept: "application/vnd.github.v3+json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  try {
    const res = await fetch(url, { headers });
    if (!res.ok) {
      console.warn(`GitHub API ${res.status} — skipping`);
      return null;
    }
    const data = await res.json() as Array<{ name:string; type:string }>;
    const slugs = data.filter(d => d.type === "dir").map(d => d.name).sort();
    return { slugs, dates: {} };
  } catch (e) {
    console.warn("GitHub fetch failed", e);
    return null;
  }
}

async function main() {
  // 1. local (dev)
  const local = scanLocal();
  if (local) {
    const out: Generated = { solvedSlugs: local.slugs, gitDates: local.dates };
    fs.mkdirSync("data", {recursive:true});
    fs.writeFileSync("data/generated.json", JSON.stringify(out, null, 2));
    console.log(`Generated data/generated.json from LOCAL with ${local.slugs.length} solved`);
    return;
  }
  // 2. GitHub API (Vercel prod / wireable)
  const remote = await fetchViaGitHub();
  if (remote) {
    const out: Generated = { solvedSlugs: remote.slugs, gitDates: remote.dates };
    fs.mkdirSync("data", {recursive:true});
    fs.writeFileSync("data/generated.json", JSON.stringify(out, null, 2));
    console.log(`Generated data/generated.json from GITHUB API with ${remote.slugs.length} solved`);
    return;
  }
  // 3. fallback empty (keeps build from failing)
  const out: Generated = { solvedSlugs: [], gitDates: {} };
  fs.mkdirSync("data", {recursive:true});
  fs.writeFileSync("data/generated.json", JSON.stringify(out, null, 2));
  console.log("Generated empty data/generated.json (no source found)");
}

main();
