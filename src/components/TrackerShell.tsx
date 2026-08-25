"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import type { CurriculumProblem, PatternProgress } from "@/lib/types";
import { formatPatternName } from "@/lib/patterns";
import { PatternDetailClient } from "@/components/PatternDetailClient";
import { DiffSolvedBar } from "@/components/DiffSolvedBar";

type PatternMeta = {
  slug: string;
  problems: CurriculumProblem[];
  progress: PatternProgress | null;
  playTarget: string | null;
};

type DiffCounts = { easy: number; medium: number; hard: number };

export function TrackerShell({
  order,
  byPatternProblems,
  byPattern,
  playTargetByPattern,
  solvedSlugs,
  total,
  solvedCount,
}: {
  order: string[];
  byPatternProblems: Record<string, CurriculumProblem[]>;
  byPattern: Record<string, PatternProgress>;
  playTargetByPattern: Record<string, string | null>;
  solvedSlugs: string[];
  total: number;
  solvedCount: number;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const demoAll = searchParams.get("demo") === "all";

  const allSlugs = useMemo(() => {
    const seen = new Set<string>();
    const out: string[] = [];
    for (const problems of Object.values(byPatternProblems)) {
      for (const p of problems) {
        if (seen.has(p.slug)) continue;
        seen.add(p.slug);
        out.push(p.slug);
      }
    }
    return out;
  }, [byPatternProblems]);

  const effectiveSolvedSlugs = demoAll ? allSlugs : solvedSlugs;
  const effectiveSolvedCount = demoAll ? total : solvedCount;
  const pct =
    total === 0 ? 0 : Math.round((effectiveSolvedCount / total) * 100);

  const solvedSet = useMemo(
    () => new Set(effectiveSolvedSlugs),
    [effectiveSolvedSlugs],
  );

  const overallDiff = useMemo(() => {
    const seen = new Set<string>();
    const counts: DiffCounts = { easy: 0, medium: 0, hard: 0 };
    for (const problems of Object.values(byPatternProblems)) {
      for (const p of problems) {
        if (!solvedSet.has(p.slug) || seen.has(p.slug)) continue;
        seen.add(p.slug);
        counts[p.difficulty]++;
      }
    }
    return counts;
  }, [byPatternProblems, solvedSet]);

  const patterns: PatternMeta[] = useMemo(
    () =>
      order.map((slug) => {
        const problems = byPatternProblems[slug] ?? [];
        const progress = demoAll
          ? {
              pattern: slug,
              solved: problems.length,
              total: problems.length,
              isComplete: problems.length > 0,
            }
          : (byPattern[slug] ?? null);
        return {
          slug,
          problems,
          progress,
          playTarget: playTargetByPattern[slug] ?? null,
        };
      }),
    [order, byPatternProblems, byPattern, playTargetByPattern, demoAll],
  );

  const selectable = useMemo(
    () => patterns.filter((p) => p.problems.length > 0),
    [patterns],
  );
  const paramSlug = searchParams.get("p");

  const initialSlug = useMemo(() => {
    if (paramSlug && selectable.some((p) => p.slug === paramSlug)) {
      return paramSlug;
    }
    return selectable[0]?.slug ?? null;
  }, [paramSlug, selectable]);

  const [active, setActive] = useState<string | null>(initialSlug);
  const [mobileShowDetail, setMobileShowDetail] = useState(false);
  const [railOpen, setRailOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    setActive(initialSlug);
  }, [initialSlug]);

  useEffect(() => {
    try {
      if (localStorage.getItem("al-rail-open") === "0") setRailOpen(false);
    } catch {
      /* ignore */
    }
  }, []);

  const toggleRail = useCallback(() => {
    setRailOpen((open) => {
      const next = !open;
      try {
        localStorage.setItem("al-rail-open", next ? "1" : "0");
      } catch {
        /* ignore */
      }
      return next;
    });
  }, []);

  useEffect(() => {
    if (!settingsOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSettingsOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [settingsOpen]);

  const selectPattern = useCallback(
    (slug: string) => {
      setActive(slug);
      setMobileShowDetail(true);
      const params = new URLSearchParams(searchParams.toString());
      params.set("p", slug);
      router.replace(`/?${params.toString()}`, { scroll: false });
    },
    [router, searchParams],
  );

  const activeMeta = patterns.find((p) => p.slug === active) ?? null;

  return (
    <div className="app-seam-glow flex h-dvh min-h-0 flex-col bg-[var(--bg)]">
      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        {/* —— Pattern rail —— */}
        <aside
          className={`rail-pane relative flex shrink-0 flex-col overflow-hidden bg-transparent ${
            mobileShowDetail ? "hidden md:flex" : "flex"
          }`}
          data-open={railOpen ? "true" : "false"}
        >
          <div className="rail-pane-inner flex h-full w-full flex-col md:w-[17.5rem] lg:w-[19rem]">
          <div className="shrink-0 px-5 pt-6 pb-5">
            <div className="flex items-baseline justify-between gap-3">
              <p className="tabular-nums text-2xl font-semibold leading-none text-[var(--text)]">
                {effectiveSolvedCount}
                <span className="text-[var(--text-faint)]">/{total}</span>
              </p>
              <p className="tabular-nums text-2xl font-semibold leading-none text-[var(--text)]">
                {pct}%
              </p>
            </div>
            <div className="mt-2.5">
              <DiffSolvedBar counts={overallDiff} total={total} />
            </div>
          </div>

          <nav
            className="scrollbar-hide min-h-0 flex-1 overflow-y-auto overscroll-contain px-2 py-3"
            aria-label="Patterns"
          >
            <ul>
              {patterns.map((p, i) => {
                const empty = p.problems.length === 0;
                const selected = p.slug === active;
                const solved = p.progress?.solved ?? 0;
                const totalP = p.progress?.total ?? p.problems.length;
                const done = p.progress?.isComplete ?? false;
                const n = String(i + 1).padStart(2, "0");

                return (
                  <li key={p.slug}>
                    <button
                      type="button"
                      disabled={empty}
                      onClick={() => selectPattern(p.slug)}
                      className={`group relative flex w-full items-baseline gap-3 px-3 py-2.5 text-left transition-colors ${
                        empty
                          ? "cursor-not-allowed opacity-30"
                          : selected
                            ? "bg-[var(--bg-active)]"
                            : "hover:bg-[var(--bg-hover)]"
                      }`}
                    >
                      {selected && (
                        <span
                          className="absolute top-2 bottom-2 left-0 w-[2px] rounded-full bg-[var(--accent)]"
                          aria-hidden="true"
                        />
                      )}
                      <span
                        className={`w-5 shrink-0 text-[10px] tabular-nums ${
                          selected
                            ? "text-[var(--accent)]"
                            : "text-[var(--text-faint)]"
                        }`}
                      >
                        {n}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span
                          className={`block truncate text-[13px] font-medium ${
                            selected
                              ? "text-[var(--text)]"
                              : done
                                ? "text-[var(--text-muted)]"
                                : "text-[var(--text)]"
                          }`}
                        >
                          {formatPatternName(p.slug)}
                        </span>
                        <span className="mt-0.5 block text-[10px] tabular-nums text-[var(--text-faint)]">
                          {empty
                            ? "—"
                            : done
                              ? "complete"
                              : `${solved} / ${totalP}`}
                        </span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="flex shrink-0 items-center justify-between gap-3 px-5 py-3.5">
            <button
              type="button"
              onClick={() => setSettingsOpen(true)}
              className="flex h-7 w-7 items-center justify-center rounded-full text-[var(--text-faint)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
              aria-label="Settings"
            >
              <svg
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
            </button>
            <button
              type="button"
              onClick={toggleRail}
              className="hidden h-8 w-8 items-center justify-center rounded-full text-[var(--text-faint)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text)] md:inline-flex"
              aria-label="Hide pattern list"
            >
              &lt;
            </button>
          </div>
          </div>
        </aside>

        {/* —— Detail —— */}
        <main
          className={`relative min-h-0 min-w-0 flex-1 flex-col ${
            mobileShowDetail ? "flex" : "hidden md:flex"
          }`}
        >
          {activeMeta && activeMeta.problems.length > 0 ? (
            <PatternDetailClient
              key={activeMeta.slug}
              problems={activeMeta.problems}
              solvedSlugs={effectiveSolvedSlugs}
              title={formatPatternName(activeMeta.slug)}
              onBack={() => setMobileShowDetail(false)}
            />
          ) : (
            <div className="flex flex-1 flex-col items-center justify-center gap-2 bg-[var(--bg-main)] p-8">
              <p className="text-lg text-[var(--text-muted)]">
                Choose a pattern
              </p>
              <p className="font-mono text-[11px] tracking-wider text-[var(--text-faint)] uppercase">
                from the list
              </p>
            </div>
          )}
        </main>

        {!railOpen && (
          <button
            type="button"
            onClick={toggleRail}
            className="animate-fade fixed bottom-5 left-5 z-40 hidden h-11 w-11 items-center justify-center rounded-full bg-[var(--bg-elevated)] text-[var(--text-muted)] transition-[transform,background-color,color] hover:bg-[var(--bg-hover)] hover:text-[var(--text)] active:scale-95 md:flex"
            aria-label="Show pattern list"
          >
            &gt;
          </button>
        )}
      </div>

      {settingsOpen ? (
        <div
          className="animate-fade fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={() => setSettingsOpen(false)}
          role="presentation"
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="settings-title"
            className="animate-rise relative w-full max-w-sm rounded-2xl bg-[var(--bg-main)] p-6 shadow-none"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setSettingsOpen(false)}
              className="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full text-[var(--text-faint)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
              aria-label="Close settings"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <path d="M3 3l8 8M11 3L3 11" />
              </svg>
            </button>

            <h2
              id="settings-title"
              className="m-0 pr-8 text-lg font-semibold tracking-tight text-[var(--text)]"
            >
              Settings
            </h2>

            <div className="mt-6 flex flex-col gap-1">
              <a
                className="flex items-center justify-between px-3 py-3 text-[13px] font-medium text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
                href="https://github.com/melchior729/neetcode-submissions"
                target="_blank"
                rel="noreferrer"
              >
                <span>Submissions</span>
                <span className="text-[var(--text-faint)]" aria-hidden="true">
                  ↗
                </span>
              </a>
              <a
                className="flex items-center justify-between px-3 py-3 text-[13px] font-medium text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
                href="https://neetcode.io/practice"
                target="_blank"
                rel="noreferrer"
              >
                <span>Clear history</span>
                <span className="text-[var(--text-faint)]" aria-hidden="true">
                  ↗
                </span>
              </a>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
