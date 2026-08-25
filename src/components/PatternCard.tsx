"use client";
import Link from "next/link";
import type { CurriculumProblem } from "@/lib/types";

function Bar({ label, solved, total }: { label: string; solved: number; total: number }) {
  const pct = total === 0 ? 0 : Math.round((solved / total) * 100);
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs uppercase tracking-wider text-zinc-400">
        <span>{label}</span>
        <span className="text-zinc-300">{solved}/{total}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-zinc-800 overflow-hidden">
        <div className="h-full bg-zinc-100 transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function PatternCard({
  pattern,
  problems,
  solvedSet,
  playTarget,
  isComplete,
}: {
  pattern: string;
  problems: CurriculumProblem[];
  solvedSet: Set<string>;
  playTarget: string | null;
  isComplete: boolean;
}) {
  const title = pattern.replace(/-/g, " ");
  const targetProblem = playTarget ? problems.find(p => p.slug === playTarget) : null;

  return (
    <div
      className={`relative flex flex-col rounded-2xl border p-5 transition ${
        isComplete
          ? "border-amber-400/50 bg-gradient-to-br from-amber-400 via-yellow-500 to-amber-700 text-black"
          : "border-zinc-800 bg-zinc-900/60 backdrop-blur hover:border-zinc-700"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <Link href={`/pattern/${pattern}`} className={`text-sm font-semibold capitalize tracking-tight hover:underline ${isComplete ? "text-black" : "text-zinc-100"}`}>
          {title}
        </Link>
        {isComplete && <span className="rounded-full bg-black px-2 py-0.5 text-xs font-bold text-amber-400">✓ 100%</span>}
      </div>

      <div className={`mt-1 text-xs ${isComplete ? "text-black/70" : "text-zinc-400"}`}>
        {problems.filter(p => solvedSet.has(p.slug)).length} / {problems.length} completed
      </div>

      <div className="mt-4 flex flex-col gap-2.5">
        {(["easy", "medium", "hard"] as const).map(d => {
          const ofDiff = problems.filter(p => p.difficulty === d);
          const solved = ofDiff.filter(p => solvedSet.has(p.slug)).length;
          if (ofDiff.length === 0) return null;
          return <Bar key={d} label={d} solved={solved} total={ofDiff.length} />;
        })}
      </div>

      <div className="mt-5 flex gap-2">
        <Link
          href={`/pattern/${pattern}`}
          className={`flex-1 rounded-full px-4 py-2 text-center text-sm font-medium transition ${isComplete ? "bg-black text-amber-400 hover:bg-zinc-900" : "bg-zinc-100 text-black hover:bg-white"}`}
        >
          View
        </Link>
        {targetProblem ? (
          <a
            href={targetProblem.neetcodeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center justify-center rounded-full px-4 py-2 text-sm font-bold transition ${isComplete ? "bg-black/10 text-black border border-black/20 hover:bg-black/20" : "bg-zinc-800 text-white hover:bg-zinc-700 border border-zinc-700"}`}
            title={`Next: ${targetProblem.name}`}
          >
            ▶
          </a>
        ) : (
          <span className={`flex items-center justify-center rounded-full px-4 py-2 text-sm font-bold ${isComplete ? "bg-black/10 text-black/50 border border-black/10" : "bg-zinc-800 text-zinc-500 border border-zinc-800"}`} title="Complete!">
            ✓
          </span>
        )}
      </div>
      {targetProblem && !isComplete && (
        <div className="mt-2 text-xs text-zinc-500 truncate">Next: {targetProblem.name} · {targetProblem.difficulty}</div>
      )}
    </div>
  );
}
