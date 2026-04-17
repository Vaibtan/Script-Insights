import { HistoryDashboard } from "@/components/history-dashboard";

type Props = {
  params: Promise<{ scriptId: string }>;
  searchParams: Promise<{
    revision_id?: string;
    status?: "queued" | "running" | "completed" | "partial" | "failed";
  }>;
};

export default async function ScriptHistoryPage({ params, searchParams }: Props) {
  const { scriptId } = await params;
  const query = await searchParams;

  return (
    <main className="page-shell">
      <HistoryDashboard
        scriptId={scriptId}
        initialRevisionId={query.revision_id}
        initialStatus={query.status}
      />
    </main>
  );
}
