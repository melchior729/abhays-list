type DiffCounts = { easy: number; medium: number; hard: number };

export function DiffSolvedBar({
  counts,
  total,
  barKey,
}: {
  counts: DiffCounts;
  total: number;
  barKey?: string;
}) {
  const segments = (
    [
      ["easy", counts.easy, "var(--easy)"],
      ["medium", counts.medium, "var(--medium)"],
      ["hard", counts.hard, "var(--hard)"],
    ] as const
  ).filter(([, n]) => n > 0);

  return (
    <div className="h-[3px] w-full overflow-hidden rounded-full bg-[var(--border)]">
      <div key={barKey} className="animate-bar flex h-full w-full">
        {total > 0 &&
          segments.map(([id, n, color]) => (
            <div
              key={id}
              className="h-full min-w-px"
              style={{
                width: `${(n / total) * 100}%`,
                backgroundColor: color,
              }}
            />
          ))}
      </div>
    </div>
  );
}
