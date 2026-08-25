import { Suspense } from "react";
import { computeProgress } from "@/lib/progress";
import { loadAppData } from "@/lib/data";
import { groupByPattern } from "@/lib/patterns";
import { TrackerShell } from "@/components/TrackerShell";
import type { CurriculumProblem, PatternProgress } from "@/lib/types";

export const dynamic = "force-static";

export default function Home() {
  const { curriculum, solved, dates, order } = loadAppData();
  const {
    total,
    solved: solvedCount,
    byPattern,
    playTargetByPattern,
  } = computeProgress(curriculum, solved, dates);

  const byPatternProblems = groupByPattern(curriculum);

  const problemsRecord: Record<string, CurriculumProblem[]> = {};
  for (const [k, v] of byPatternProblems) problemsRecord[k] = v;

  const progressRecord: Record<string, PatternProgress> = {};
  for (const [k, v] of byPattern) progressRecord[k] = v;

  const playRecord: Record<string, string | null> = {};
  for (const [k, v] of playTargetByPattern) playRecord[k] = v;

  return (
    <Suspense
      fallback={
        <div className="flex h-dvh items-center justify-center text-sm text-[var(--text-faint)]">
          Loading…
        </div>
      }
    >
      <TrackerShell
        order={order}
        byPatternProblems={problemsRecord}
        byPattern={progressRecord}
        playTargetByPattern={playRecord}
        solvedSlugs={Array.from(solved)}
        total={total}
        solvedCount={solvedCount}
      />
    </Suspense>
  );
}
