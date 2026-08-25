import fs from "fs";
import path from "path";
import Link from "next/link";
import type { CurriculumProblem } from "@/lib/types";
import { PatternDetailClient } from "./client";

export const dynamic = "force-static";

export async function generateStaticParams() {
  const order = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/patternOrder.json"), "utf8")) as string[];
  return order.map(slug => ({ slug }));
}

function loadData(slug: string) {
  const curriculum = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/curriculum.json"), "utf8")) as CurriculumProblem[];
  const gen = (() => {
    try {
      return JSON.parse(fs.readFileSync(path.join(process.cwd(), "data/generated.json"), "utf8")) as { solvedSlugs: string[] };
    } catch { return { solvedSlugs: [] as string[] }; }
  })();
  const solved = new Set(gen.solvedSlugs);
  const problems = curriculum.filter(p => p.pattern === slug);
  return { problems, solved };
}

export default async function PatternPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { problems, solved } = loadData(slug);
  const title = slug.replace(/-/g, " ");

  if (problems.length === 0) {
    return (
      <div className="mx-auto w-full max-w-3xl px-5 py-10">
        <Link href="/" className="text-sm text-zinc-400 hover:text-zinc-200">← Back</Link>
        <h1 className="mt-4 text-2xl font-bold capitalize">{title}</h1>
        <p className="mt-2 text-sm text-zinc-500">No problems in this pattern yet. Edit <code className="rounded bg-zinc-800 px-1">data/curriculum.json</code> to assign problems.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-8">
      <Link href="/" className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800">
        ← Back to Home
      </Link>
      <h1 className="mt-6 text-3xl font-bold capitalize tracking-tight">{title}</h1>
      <p className="mt-1 text-sm text-zinc-500">{problems.filter(p => solved.has(p.slug)).length} / {problems.length} completed</p>

      <div className="mt-6">
        <PatternDetailClient problems={problems} solvedSlugs={Array.from(solved)} />
      </div>
    </div>
  );
}
