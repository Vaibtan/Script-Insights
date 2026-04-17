import { AnalysisComposer } from "@/components/analysis-composer";

type Props = {
  searchParams: Promise<{ script_id?: string }>;
};

export default async function HomePage({ searchParams }: Props) {
  const query = await searchParams;

  return (
    <main className="page-shell">
      <AnalysisComposer initialScriptId={query.script_id} />
    </main>
  );
}
