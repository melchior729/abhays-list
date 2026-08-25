import { redirect } from "next/navigation";
import { loadPatternOrder } from "@/lib/data";

export const dynamic = "force-static";

export async function generateStaticParams() {
  return loadPatternOrder().map((slug) => ({ slug }));
}

export default async function PatternPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  redirect(`/?p=${encodeURIComponent(slug)}`);
}
