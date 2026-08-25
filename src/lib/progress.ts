import type { CurriculumProblem, Difficulty, PatternProgress } from "./types";
import { groupByPattern } from "./patterns";

export function computeProgress(
  curriculum: CurriculumProblem[],
  solvedSet: Set<string>,
  gitDates: Record<string, string> = {},
): {
  total: number;
  solved: number;
  byPattern: Map<string, PatternProgress>;
  playTargetByPattern: Map<string, string | null>;
} {
  const groups = groupByPattern(curriculum);

  const byPattern = new Map<string, PatternProgress>();
  const playTargetByPattern = new Map<string, string | null>();

  for (const [pattern, problems] of groups) {
    const solvedCount = problems.filter((p) => solvedSet.has(p.slug)).length;
    byPattern.set(pattern, {
      pattern,
      total: problems.length,
      solved: solvedCount,
      isComplete: problems.length > 0 && solvedCount === problems.length,
    });

    const unsolved = problems.filter((p) => !solvedSet.has(p.slug));
    if (unsolved.length === 0) {
      playTargetByPattern.set(pattern, null);
      continue;
    }

    const lastDiff = lastSolvedDifficulty(problems, solvedSet, gitDates);
    const sameDiff = lastDiff
      ? unsolved.find((p) => p.difficulty === lastDiff)
      : undefined;
    playTargetByPattern.set(pattern, (sameDiff ?? unsolved[0]).slug);
  }

  return {
    total: curriculum.length,
    solved: curriculum.filter((p) => solvedSet.has(p.slug)).length,
    byPattern,
    playTargetByPattern,
  };
}

function lastSolvedDifficulty(
  problems: CurriculumProblem[],
  solvedSet: Set<string>,
  gitDates: Record<string, string>,
): Difficulty | undefined {
  const solved = problems.filter((p) => solvedSet.has(p.slug));
  if (solved.length === 0) return undefined;

  solved.sort((a, b) => {
    const da = gitDates[a.slug] ?? "";
    const db = gitDates[b.slug] ?? "";
    if (da && db) return db.localeCompare(da);
    return 0;
  });

  return solved[0].difficulty;
}
