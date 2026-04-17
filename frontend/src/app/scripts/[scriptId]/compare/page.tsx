import { CompareView } from "@/components/compare-view";

type Props = {
  params: Promise<{ scriptId: string }>;
  searchParams: Promise<{
    base_run_id?: string;
    target_run_id?: string;
  }>;
};

export default async function ScriptComparePage({ params, searchParams }: Props) {
  const { scriptId } = await params;
  const query = await searchParams;

  return (
    <main className="page-shell">
      <CompareView
        scriptId={scriptId}
        initialBaseRunId={query.base_run_id}
        initialTargetRunId={query.target_run_id}
      />
    </main>
  );
}
