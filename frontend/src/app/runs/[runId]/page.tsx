import { RunDashboard } from "@/components/run-dashboard";

type Props = {
  params: Promise<{ runId: string }>;
};

export default async function RunPage({ params }: Props) {
  const { runId } = await params;
  return (
    <main className="page-shell">
      <RunDashboard runId={runId} />
    </main>
  );
}
