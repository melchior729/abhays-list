"use client";

export type StatusSort = "open" | "done";

const STATUS_OPTIONS: { id: StatusSort; label: string }[] = [
  { id: "open", label: "Open" },
  { id: "done", label: "Done" },
];

const DIFFS = ["all", "easy", "medium", "hard"] as const;

export function SearchBar({
  value,
  onChange,
  difficulty,
  onDifficulty,
  statusSort,
  onStatusSort,
}: {
  value: string;
  onChange: (v: string) => void;
  difficulty: string;
  onDifficulty: (v: string) => void;
  statusSort: StatusSort;
  onStatusSort: (v: StatusSort) => void;
}) {
  return (
    <>
      <div className="col-span-2 flex min-w-0 flex-wrap items-center gap-0.5">
        <div
          className="flex gap-0.5"
          role="group"
          aria-label="Sort by completion"
        >
          {STATUS_OPTIONS.map(({ id, label }) => {
            const on = statusSort === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => onStatusSort(id)}
                className={`rounded-full px-3 py-1.5 text-xs font-medium tracking-wide transition-colors ${
                  on
                    ? "bg-[var(--bg-active)] text-[var(--text)]"
                    : "text-[var(--text-faint)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-muted)]"
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        <div
          className="flex gap-0.5"
          role="group"
          aria-label="Difficulty filter"
        >
          {DIFFS.map((d) => {
            const on = difficulty === d;
            return (
              <button
                key={d}
                type="button"
                onClick={() => onDifficulty(d)}
                className={`rounded-full px-2.5 py-1 text-[11px] tracking-wide capitalize transition-colors ${
                  on
                    ? d === "easy"
                      ? "bg-[var(--bg-active)] text-[var(--easy)]"
                      : d === "medium"
                        ? "bg-[var(--bg-active)] text-[var(--medium)]"
                        : d === "hard"
                          ? "bg-[var(--bg-active)] text-[var(--hard)]"
                          : "bg-[var(--bg-active)] text-[var(--text)]"
                    : "text-[var(--text-faint)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-muted)]"
                }`}
              >
                {d === "all" ? "All" : d[0].toUpperCase() + d.slice(1)}
              </button>
            );
          })}
        </div>
      </div>

      <label className="group relative block w-[min(100%,14rem)] justify-self-stretch sm:w-auto sm:min-w-[10rem] sm:max-w-[14rem] sm:justify-self-end">
        <span className="sr-only">Search problems</span>
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Search"
          className="w-full border-0 bg-[var(--bg-elevated)] px-3 py-1.5 pr-8 text-xs text-[var(--text)] placeholder:text-[var(--text-faint)] outline-none transition-colors focus:bg-[var(--bg-active)]"
        />
        <svg
          className="pointer-events-none absolute top-1/2 right-2.5 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-faint)] transition-colors group-focus-within:text-[var(--accent)]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-3-3" strokeLinecap="round" />
        </svg>
      </label>
    </>
  );
}
