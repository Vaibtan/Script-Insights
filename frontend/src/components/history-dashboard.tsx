"use client";

import Link from "next/link";
import { useState } from "react";

import { useRunHistory } from "@/hooks/use-analysis-api";
import { formatDateTime } from "@/lib/formatting";

type Props = {
  scriptId: string;
  initialRevisionId?: string;
  initialStatus?: "queued" | "running" | "completed" | "partial" | "failed";
};

export function HistoryDashboard({
  scriptId,
  initialRevisionId = "",
  initialStatus,
}: Props) {
  const [revisionId, setRevisionId] = useState(initialRevisionId);
  const [status, setStatus] = useState<
    "queued" | "running" | "completed" | "partial" | "failed" | ""
  >(initialStatus ?? "");

  const historyQuery = useRunHistory(scriptId, {
    revisionId: revisionId || undefined,
    status: status || undefined,
  });

  return (
    <section className="dashboard">
      <header className="surface">
        <p className="eyebrow">Run history</p>
        <h1>Script {scriptId}</h1>
        <div className="run-links">
          <Link href={`/?script_id=${scriptId}`}>Analyze next revision</Link>
          <Link href={`/scripts/${scriptId}/compare`}>Open compare view</Link>
        </div>
      </header>

      <article className="surface">
        <h2>Filters</h2>
        <label htmlFor="revision-filter">Revision ID</label>
        <input
          id="revision-filter"
          value={revisionId}
          onChange={(event) => setRevisionId(event.target.value)}
          placeholder="Optional revision UUID"
        />

        <label htmlFor="status-filter">Status</label>
        <select
          id="status-filter"
          value={status}
          onChange={(event) => setStatus(event.target.value as typeof status)}
        >
          <option value="">All statuses</option>
          <option value="queued">Queued</option>
          <option value="running">Running</option>
          <option value="completed">Completed</option>
          <option value="partial">Partial</option>
          <option value="failed">Failed</option>
        </select>
      </article>

      <article className="surface">
        <h2>Runs</h2>
        {historyQuery.isLoading ? <p>Loading history...</p> : null}
        {historyQuery.isError ? <p role="alert">Unable to load history.</p> : null}
        {historyQuery.data ? (
          <table className="history-table">
            <thead>
              <tr>
                <th>Run</th>
                <th>Revision</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {historyQuery.data.runs.map((run) => (
                <tr key={run.run_id}>
                  <td>{run.run_id}</td>
                  <td>{run.revision_id}</td>
                  <td>{run.status}</td>
                  <td>{formatDateTime(run.created_at)}</td>
                  <td>
                    <Link href={`/runs/${run.run_id}`}>Open</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </article>
    </section>
  );
}
