import fs from "fs";
import path from "path";
import type { CurriculumProblem, GeneratedData } from "./types";

const dataDir = (...parts: string[]) => path.join(process.cwd(), "data", ...parts);

function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(dataDir(file), "utf8")) as T;
}

export function loadCurriculum(): CurriculumProblem[] {
  return readJson("curriculum.json");
}

export function loadPatternOrder(): string[] {
  return readJson("patternOrder.json");
}

export function loadGenerated(): GeneratedData {
  try {
    return readJson("generated.json");
  } catch {
    return { solvedSlugs: [], gitDates: {} };
  }
}

export function loadAppData() {
  const curriculum = loadCurriculum();
  const order = loadPatternOrder();
  const generated = loadGenerated();
  const solved = new Set(generated.solvedSlugs);
  return { curriculum, order, solved, dates: generated.gitDates };
}
