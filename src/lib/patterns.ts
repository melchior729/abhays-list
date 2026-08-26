import type { CurriculumProblem } from "./types";

const DISPLAY_NAMES: Record<string, string> = {
  arrays: "Arrays",
  hashing: "Hashing",
  stack: "Stacks & Queues",
  "dp-1d": "1D Dynamic",
  "dp-2d": "2D Dynamic",
  "math-geometry": "Math & Geometry",
  "advanced-graphs": "Weighted Graphs",
};

export function formatPatternName(slug: string): string {
  if (DISPLAY_NAMES[slug]) return DISPLAY_NAMES[slug];
  return slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function problemPatterns(p: CurriculumProblem): string[] {
  return p.patterns;
}

export function belongsToPattern(
  p: CurriculumProblem,
  pattern: string,
): boolean {
  return p.patterns.includes(pattern);
}

/** Expand curriculum into pattern → problems (a problem may appear in multiple lists).
 * Preserves curriculum.json order (already difficulty + pedagogical). */
export function groupByPattern(
  curriculum: CurriculumProblem[],
): Map<string, CurriculumProblem[]> {
  const groups = new Map<string, CurriculumProblem[]>();
  for (const p of curriculum) {
    for (const pattern of p.patterns) {
      const list = groups.get(pattern);
      if (list) list.push(p);
      else groups.set(pattern, [p]);
    }
  }
  return groups;
}
