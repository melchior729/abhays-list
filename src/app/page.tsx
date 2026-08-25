import fs from "fs";
import path from "path";
import { computeProgress } from "@/lib/progress";
import { PatternCard } from "@/components/PatternCard";
import type { CurriculumProblem } from "@/lib/types";

export const dynamic = "force-static";

function loadData(): { curriculum: CurriculumProblem[]; solved: Set<string>; dates: Record<string,string>; order: string[] } {
  const curriculum = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/curriculum.json"), "utf8")) as CurriculumProblem[];
  const order = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/patternOrder.json"), "utf8")) as string[];
  let solved = new Set<string>();
  let dates: Record<string,string> = {};
  try {
    const gen = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/generated.json"), "utf8")) as { solvedSlugs: string[]; gitDates: Record<string,string> };
    solved = new Set(gen.solvedSlugs);
    dates = gen.gitDates || {};
  } catch {}
  return { curriculum, solved, dates, order };
}

export default function Home() {
  const { curriculum, solved, dates, order } = loadData();
  const { total, solved: solvedCount, byPattern, playTargetByPattern } = computeProgress(curriculum, solved, dates);

  // group problems by pattern for cards
  const byPatternProblems = new Map<string, CurriculumProblem[]>();
  for (const p of curriculum) {
    if (!byPatternProblems.has(p.pattern)) byPatternProblems.set(p.pattern, []);
    byPatternProblems.get(p.pattern)!.push(p);
  }

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-6">
      <header className="flex flex-col gap-4 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Abhay&apos;s List</h1>
          <p className="mt-1 text-sm text-zinc-400">Curated NeetCode — progress from <code className="rounded bg-zinc-800 px-1 py-0.5 text-xs">melchior729/neetcode-submissions</code></p>
        </div>
        <div className="flex flex-col items-start gap-2 sm:items-end">
          <div className="rounded-full bg-zinc-100 px-5 py-2 text-lg font-bold text-black tabular-nums">
            {solvedCount} / {total}
          </div>
          <div className="text-xs text-zinc-500">{total - solvedCount} remaining · {Math.round((solvedCount/total)*100)}% complete</div>
          <div className="h-2 w-48 overflow-hidden rounded-full bg-zinc-800">
            <div className="h-full bg-white transition-all" style={{ width: `${(solvedCount/total)*100}%` }} />
          </div>
          <div className="text-xs text-zinc-600">Wireable: Vercel Deploy Hook on push to neetcode-submissions → auto rebuild</div>
        </div>
      </header>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {order.map(pattern => {
          const problems = byPatternProblems.get(pattern) || [];
          if (problems.length === 0) {
            // still render empty pattern placeholder so order is visible
            return (
              <div key={pattern} className="rounded-2xl border border-dashed border-zinc-800 p-5">
                <div className="text-sm font-semibold capitalize text-zinc-500">{pattern.replace(/-/g, " ")}</div>
                <div className="mt-1 text-xs text-zinc-600">No problems assigned yet — edit <code>data/curriculum.json</code></div>
              </div>
            );
          }
          const prog = byPattern.get(pattern)!;
          return (
            <PatternCard
              key={pattern}
              pattern={pattern}
              problems={problems}
              solvedSet={solved}
              playTarget={playTargetByPattern.get(pattern) ?? null}
              isComplete={prog.isComplete}
            />
          );
        })}
      </div>

      <footer className="mt-10 text-center text-xs text-zinc-600">
        Black theme • Mobile-friendly • No code display • <a className="underline hover:text-zinc-400" href="https://github.com/melchior729/neetcode-submissions" target="_blank" rel="noreferrer">Source repo</a>
      </footer>
    </div>
  );
}
