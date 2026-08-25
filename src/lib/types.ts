export type Difficulty = "easy" | "medium" | "hard";

export interface CurriculumProblem {
  slug: string;
  name: string;
  pattern: string;
  difficulty: Difficulty;
  neetcodeUrl: string;
}

export interface PatternProgress {
  pattern: string;
  total: number;
  solved: number;
  byDifficulty: Record<Difficulty, { total: number; solved: number }>;
  isComplete: boolean;
}

export interface GeneratedData {
  solvedSlugs: string[];
  lastSolvedMap: Record<string, string>; // pattern -> difficulty of last solved
  gitDates: Record<string, string>; // slug -> last commit date
}
