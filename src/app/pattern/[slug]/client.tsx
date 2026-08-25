"use client";
import { useMemo, useState } from "react";
import type { CurriculumProblem } from "@/lib/types";
import { SearchBar } from "@/components/SearchBar";

export function PatternDetailClient({ problems, solvedSlugs }: { problems: CurriculumProblem[]; solvedSlugs: string[] }) {
  const solved = useMemo(() => new Set(solvedSlugs), [solvedSlugs]);
  const [q, setQ] = useState("");
  const [diff, setDiff] = useState("all");

  const filtered = useMemo(() => {
    return problems.filter(p => {
      if (diff !== "all" && p.difficulty !== diff) return false;
      if (q && !p.name.toLowerCase().includes(q.toLowerCase()) && !p.slug.toLowerCase().includes(q.toLowerCase())) return false;
      return true;
    });
  }, [problems, q, diff]);

  return (
    <div className="flex flex-col gap-4">
      <SearchBar value={q} onChange={setQ} difficulty={diff} onDifficulty={setDiff} />
      <div className="overflow-hidden rounded-2xl border border-zinc-800">
        {filtered.length === 0 ? (
          <div className="p-8 text-center text-sm text-zinc-500">No matches</div>
        ) : (
          <ul className="divide-y divide-zinc-800">
            {filtered.map(p => {
              const isDone = solved.has(p.slug);
              return (
                <li key={p.slug} className="flex items-center justify-between gap-3 bg-zinc-900/30 px-4 py-3 hover:bg-zinc-900">
                  <div className="min-w-0 flex items-center gap-3">
                    <span className={`flex h-6 w-6 items-center justify-center rounded-full border text-xs ${isDone ? "border-emerald-500 bg-emerald-500 text-black" : "border-zinc-700 text-zinc-500"}`}>{isDone ? "✓" : "○"}</span>
                    <div className="min-w-0">
                      <a href={p.neetcodeUrl} target="_blank" rel="noopener noreferrer" className="truncate text-sm font-medium text-zinc-100 hover:underline">
                        {p.name}
                      </a>
                      <div className="text-xs text-zinc-500">{p.slug} · <span className={`capitalize ${p.difficulty === "easy" ? "text-emerald-400" : p.difficulty === "medium" ? "text-amber-400" : "text-red-400"}`}>{p.difficulty}</span></div>
                    </div>
                  </div>
                  <a href={p.neetcodeUrl} target="_blank" rel="noopener noreferrer" className="shrink-0 rounded-full border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:bg-zinc-700">
                    Open ↗
                  </a>
                </li>
              );
            })}
          </ul>
        )}
      </div>
      <div className="text-xs text-zinc-600">{filtered.length} / {problems.length} shown • clicking opens NeetCode externally (no in-app code)</div>
    </div>
  );
}
