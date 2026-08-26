import { loadCurriculum, loadGenerated, loadPatternOrder } from "../src/lib/data";
import {
  belongsToPattern,
  formatPatternName,
} from "../src/lib/patterns";

const curriculum = loadCurriculum();
const order = loadPatternOrder();
const { solvedSlugs } = loadGenerated();
const solved = new Set(solvedSlugs);

const lines: string[] = [];

for (const pattern of order) {
  const problems = curriculum.filter((p) => belongsToPattern(p, pattern));
  if (problems.length === 0) continue;

  if (lines.length > 0) lines.push("");
  lines.push(formatPatternName(pattern));
  lines.push("");

  for (let i = 0; i < problems.length; i++) {
    const p = problems[i]!;
    const isDone = solved.has(p.slug);
    const prefix = isDone ? "✓" : String(i).padStart(2, "0");
    lines.push(`${prefix} ${p.name} (${p.difficulty})`);
  }
}

process.stdout.write(lines.join("\n") + "\n");
