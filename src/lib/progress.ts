import type { CurriculumProblem, Difficulty, PatternProgress } from "./types";

export function computeProgress(
  curriculum: CurriculumProblem[],
  solvedSet: Set<string>,
  gitDates: Record<string, string> = {}
): {
  total: number;
  solved: number;
  byPattern: Map<string, PatternProgress>;
  lastSolvedDifficultyByPattern: Map<string, Difficulty>;
  playTargetByPattern: Map<string, string | null>;
} {
  const total = curriculum.length;
  const solved = curriculum.filter(p => solvedSet.has(p.slug)).length;

  const byPattern = new Map<string, PatternProgress>();
  const lastSolvedDifficultyByPattern = new Map<string, Difficulty>();
  const playTargetByPattern = new Map<string, string | null>();

  // group by pattern
  const groups = new Map<string, CurriculumProblem[]>();
  for (const p of curriculum) {
    if (!groups.has(p.pattern)) groups.set(p.pattern, []);
    groups.get(p.pattern)!.push(p);
  }

  for (const [pattern, problems] of groups) {
    const prog: PatternProgress = {
      pattern,
      total: problems.length,
      solved: problems.filter(p => solvedSet.has(p.slug)).length,
      byDifficulty: {
        easy: { total: 0, solved: 0 },
        medium: { total: 0, solved: 0 },
        hard: { total: 0, solved: 0 },
      },
      isComplete: false,
    };
    for (const d of ["easy", "medium", "hard"] as Difficulty[]) {
      const ofDiff = problems.filter(p => p.difficulty === d);
      prog.byDifficulty[d].total = ofDiff.length;
      prog.byDifficulty[d].solved = ofDiff.filter(p => solvedSet.has(p.slug)).length;
    }
    prog.isComplete = prog.solved === prog.total && prog.total > 0;
    byPattern.set(pattern, prog);

    // last solved difficulty in this pattern (by git date, fallback to last in curriculum order that is solved)
    const solvedInPattern = problems.filter(p => solvedSet.has(p.slug));
    if (solvedInPattern.length > 0) {
      // sort by date desc if available, else by original order
      solvedInPattern.sort((a, b) => {
        const da = gitDates[a.slug] || "";
        const db = gitDates[b.slug] || "";
        if (da && db) return db.localeCompare(da);
        return 0;
      });
      lastSolvedDifficultyByPattern.set(pattern, solvedInPattern[0].difficulty);
    }

    // play target
    const unsolved = problems.filter(p => !solvedSet.has(p.slug));
    if (unsolved.length === 0) {
      playTargetByPattern.set(pattern, null);
    } else {
      const lastDiff = lastSolvedDifficultyByPattern.get(pattern);
      if (lastDiff) {
        const candidate = unsolved.find(p => p.difficulty === lastDiff);
        playTargetByPattern.set(pattern, candidate ? candidate.slug : unsolved[0].slug);
      } else {
        playTargetByPattern.set(pattern, unsolved[0].slug);
      }
    }
  }

  return { total, solved, byPattern, lastSolvedDifficultyByPattern, playTargetByPattern };
}
