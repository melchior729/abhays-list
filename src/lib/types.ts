export type Difficulty = "easy" | "medium" | "hard";

export interface CurriculumProblem {
  slug: string;
  name: string;
  /** One or more pattern slugs this problem belongs to. */
  patterns: string[];
  difficulty: Difficulty;
  neetcodeUrl: string;
}

export interface PatternProgress {
  pattern: string;
  total: number;
  solved: number;
  isComplete: boolean;
}

export interface GeneratedData {
  solvedSlugs: string[];
  gitDates: Record<string, string>;
}
