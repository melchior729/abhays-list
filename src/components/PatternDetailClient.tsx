"use client";

import { useMemo, useState } from "react";
import type { CurriculumProblem, Difficulty } from "@/lib/types";
import { SearchBar, type StatusSort } from "@/components/SearchBar";
import { DiffSolvedBar } from "@/components/DiffSolvedBar";

type DiffCounts = { easy: number; medium: number; hard: number };

function countByDifficulty(
  problems: CurriculumProblem[],
  solved: Set<string> | null,
): DiffCounts {
  const counts: DiffCounts = { easy: 0, medium: 0, hard: 0 };
  for (const p of problems) {
    if (solved && !solved.has(p.slug)) continue;
    counts[p.difficulty]++;
  }
  return counts;
}

export function PatternDetailClient({
  problems,
  solvedSlugs,
  title,
  onBack,
}: {
  problems: CurriculumProblem[];
  solvedSlugs: string[];
  title: string;
  onBack?: () => void;
}) {
  const solved = useMemo(() => new Set(solvedSlugs), [solvedSlugs]);
  const [q, setQ] = useState("");
  const [diff, setDiff] = useState("all");
  const [statusSort, setStatusSort] = useState<StatusSort>("open");

  const totals = useMemo(() => countByDifficulty(problems, null), [problems]);
  const solvedCounts = useMemo(
    () => countByDifficulty(problems, solved),
    [problems, solved],
  );

  const { displaySolved, displayTotal, barCounts, barTotal } = useMemo(() => {
    if (diff === "all") {
      return {
        displaySolved:
          solvedCounts.easy + solvedCounts.medium + solvedCounts.hard,
        displayTotal: problems.length,
        barCounts: solvedCounts,
        barTotal: problems.length,
      };
    }
    const d = diff as Difficulty;
    const empty: DiffCounts = { easy: 0, medium: 0, hard: 0 };
    return {
      displaySolved: solvedCounts[d],
      displayTotal: totals[d],
      barCounts: { ...empty, [d]: solvedCounts[d] },
      barTotal: totals[d],
    };
  }, [diff, problems.length, solvedCounts, totals]);

  const curriculumIndex = useMemo(
    () => new Map(problems.map((p, i) => [p.slug, i])),
    [problems],
  );

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    const matched = problems.filter((p) => {
      if (diff !== "all" && p.difficulty !== diff) return false;
      if (!query) return true;
      return (
        p.name.toLowerCase().includes(query) ||
        p.slug.toLowerCase().includes(query)
      );
    });

    const pos = curriculumIndex;

    return [...matched].sort((a, b) => {
      if (statusSort === "path") {
        return (pos.get(a.slug) ?? 0) - (pos.get(b.slug) ?? 0);
      }
      const statusRank = (slug: string) => {
        const done = solved.has(slug);
        if (statusSort === "open") return done ? 1 : 0;
        return done ? 0 : 1;
      };
      const statusCmp = statusRank(a.slug) - statusRank(b.slug);
      if (statusCmp !== 0) return statusCmp;
      return (pos.get(a.slug) ?? 0) - (pos.get(b.slug) ?? 0);
    });
  }, [problems, q, diff, statusSort, solved, curriculumIndex]);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="shrink-0 bg-transparent px-5 pt-5 pb-2 sm:px-8 sm:pt-6">
        {onBack ? (
          <button
            type="button"
            className="mb-3 font-mono text-[11px] tracking-wider text-[var(--text-faint)] uppercase md:hidden"
            onClick={onBack}
          >
            ← Patterns
          </button>
        ) : null}

        <div className="grid grid-cols-[minmax(0,max-content)_minmax(0,1fr)_auto] items-center gap-x-4 gap-y-2 sm:gap-x-6 sm:gap-y-2.5">
          <h2 className="m-0 min-w-0 max-w-[40vw] truncate py-0.5 text-2xl font-semibold leading-tight text-[var(--text)] sm:max-w-[14rem] sm:text-3xl lg:max-w-[18rem]">
            {title}
          </h2>
          <div className="flex min-w-0 items-center self-center">
            <DiffSolvedBar
              key={`${title}-${diff}`}
              barKey={`${title}-${diff}`}
              counts={barCounts}
              total={barTotal}
            />
          </div>
          <p className="m-0 flex shrink-0 items-baseline justify-self-end gap-0 leading-none">
            <span className="text-3xl font-semibold tabular-nums text-[var(--text)] sm:text-4xl">
              {displaySolved}
            </span>
            <span className="text-lg tabular-nums text-[var(--text-faint)] sm:text-xl">
              /{displayTotal}
            </span>
          </p>
          <SearchBar
            value={q}
            onChange={setQ}
            difficulty={diff}
            onDifficulty={setDiff}
            statusSort={statusSort}
            onStatusSort={setStatusSort}
          />
        </div>
      </div>

      <div className="pane-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain bg-[var(--bg-main)] px-5 pb-6 sm:px-8">
        {filtered.length === 0 ? (
          <p className="py-16 text-center text-sm text-[var(--text-faint)]">
            Nothing matches.
          </p>
        ) : (
          <ul className="flex flex-col gap-1">
            {filtered.map((p, i) => {
              const isDone = solved.has(p.slug);
              return (
                <li key={p.slug}>
                  <a
                    href={p.neetcodeUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center gap-4 px-3 py-4 transition-colors hover:bg-[var(--bg-hover)]"
                  >
                    <span
                      className={`flex h-[2.375rem] w-12 shrink-0 items-center justify-end font-mono text-[34px] leading-none tabular-nums ${
                        isDone
                          ? "text-[var(--accent)]"
                          : "text-[var(--text-faint)]"
                      }`}
                    >
                      {isDone ? (
                        <span
                          className="inline-block animate-mark text-[34px]"
                          aria-label="Done"
                        >
                          ✓
                        </span>
                      ) : (
                        String(
                          statusSort === "path"
                            ? (curriculumIndex.get(p.slug) ?? i)
                            : i,
                        ).padStart(2, "0")
                      )}
                    </span>

                    <span className="min-w-0 flex-1">
                      <span
                        className={`block truncate text-[15px] font-medium tracking-tight transition-colors group-hover:text-[var(--accent)] ${
                          isDone
                            ? "text-[var(--text-muted)]"
                            : "text-[var(--text)]"
                        }`}
                      >
                        {p.name}
                      </span>
                      <span className="mt-0.5 block truncate font-mono text-[11px] capitalize text-[var(--text-faint)]">
                        {p.difficulty}
                      </span>
                    </span>

                    <span
                      className={`play-btn-${p.difficulty} hidden h-8 w-8 shrink-0 items-center justify-center rounded-full text-[var(--text-faint)] transition-colors sm:inline-flex`}
                      aria-hidden="true"
                    >
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 16 16"
                        fill="currentColor"
                      >
                        <path d="M4.5 2.8v10.4c0 .5.55.8.97.55l8.1-5.2a.65.65 0 0 0 0-1.1l-8.1-5.2a.65.65 0 0 0-.97.55Z" />
                      </svg>
                    </span>
                  </a>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
