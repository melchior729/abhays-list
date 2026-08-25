"use client";
import { useState } from "react";

export function SearchBar({
  value,
  onChange,
  difficulty,
  onDifficulty,
}: {
  value: string;
  onChange: (v: string) => void;
  difficulty: string;
  onDifficulty: (v: string) => void;
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <input
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder="Search problems..."
          className="w-full rounded-full border border-zinc-800 bg-zinc-900 px-4 py-2.5 pr-10 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-zinc-600 focus:outline-none"
        />
        <span className="pointer-events-none absolute right-3 top-2.5 text-zinc-500">⌕</span>
      </div>
      <div className="flex gap-2">
        {["all", "easy", "medium", "hard"].map(d => (
          <button
            key={d}
            onClick={() => onDifficulty(d)}
            className={`rounded-full px-4 py-2 text-xs font-medium capitalize transition ${difficulty === d ? "bg-zinc-100 text-black" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"}`}
          >
            {d}
          </button>
        ))}
      </div>
    </div>
  );
}
