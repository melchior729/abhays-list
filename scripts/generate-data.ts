import fs from "fs";
import path from "path";
import { execSync } from "child_process";
import type { GeneratedData } from "../src/lib/types";

const DSA_DIR = "Data Structures & Algorithms";

const LOCAL_CANDIDATES = [
  process.env.NEETCODE_SUBMISSIONS_DIR,
  "/home/abhay/code/neetcode-submissions",
  path.join(process.cwd(), "..", "neetcode-submissions"),
  path.join(process.cwd(), "neetcode-submissions"),
].filter((p): p is string => Boolean(p));

function writeGenerated(data: GeneratedData, source: string) {
  fs.mkdirSync("data", { recursive: true });
  fs.writeFileSync("data/generated.json", JSON.stringify(data, null, 2) + "\n");
  console.log(
    `Generated data/generated.json from ${source} with ${data.solvedSlugs.length} solved`,
  );
}

function scanLocal(base: string): GeneratedData {
  const dir = path.join(base, DSA_DIR);
  const slugs = fs
    .readdirSync(dir)
    .filter((f) => fs.statSync(path.join(dir, f)).isDirectory())
    .sort();

  const gitDates: Record<string, string> = {};
  try {
    const log = execSync(
      `git -C "${base}" log --pretty=format:"%ad %s" --date=short --name-only`,
      { encoding: "utf8" },
    );
    for (const line of log.split("\n")) {
      const fileMatch = line.match(/Data Structures & Algorithms\/(.+?)\//);
      if (!fileMatch || gitDates[fileMatch[1]]) continue;
      const dateMatch = line.match(/^(\d{4}-\d{2}-\d{2})/);
      if (dateMatch) gitDates[fileMatch[1]] = dateMatch[1];
    }
  } catch {
    // git dates are optional
  }

  return { solvedSlugs: slugs, gitDates };
}

function findLocalClone(): string | null {
  for (const base of LOCAL_CANDIDATES) {
    if (fs.existsSync(path.join(base, DSA_DIR))) return base;
  }
  return null;
}

function main() {
  const local = findLocalClone();
  if (!local) {
    console.error(
      "No local neetcode-submissions clone found.\n" +
        "Expected a directory containing:\n" +
        `  Data Structures & Algorithms/\n\n` +
        "Set NEETCODE_SUBMISSIONS_DIR or clone to one of:\n" +
        LOCAL_CANDIDATES.map((p) => `  ${p}`).join("\n"),
    );
    process.exit(1);
  }

  writeGenerated(scanLocal(local), `LOCAL (${local})`);
}

main();
