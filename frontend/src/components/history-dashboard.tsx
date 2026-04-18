"use client";

import Link from "next/link";
import { useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { StatusBadge } from "@/components/status-badge";
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
  const runs = historyQuery.data?.runs ?? [];
  const completedRuns = runs.filter((run) => run.status === "completed").length;
  const partialRuns = runs.filter((run) => run.status === "partial").length;

  return (
    <section className="dashboard">
      <header className="panel panel--hero dashboard-hero">
        <div>
          <p className="eyebrow">Run history</p>
          <h1>Script {scriptId}</h1>
          <p className="hero-lede">
            Review how this script lineage evolved across successive runs and
            filter down to the exact revision slice you need.
          </p>
        </div>
        <div className="run-links">
          <Link href={`/?script_id=${scriptId}`}>Analyze next revision</Link>
          <Link href={`/scripts/${scriptId}/compare`}>Open compare view</Link>
        </div>
      </header>

      <section className="history-metrics">
        <article className="panel history-metric-card">
          <span className="history-metric-card__label">Total runs</span>
          <strong>{runs.length}</strong>
        </article>
        <article className="panel history-metric-card">
          <span className="history-metric-card__label">Completed</span>
          <strong>{completedRuns}</strong>
        </article>
        <article className="panel history-metric-card">
          <span className="history-metric-card__label">Partial</span>
          <strong>{partialRuns}</strong>
        </article>
      </section>

      <article className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Filters</p>
            <h2>Focus the run list</h2>
          </div>
        </div>
        <div className="field-grid">
          <div className="field-group">
            <label htmlFor="revision-filter">Revision ID</label>
            <input
              id="revision-filter"
              value={revisionId}
              onChange={(event) => setRevisionId(event.target.value)}
              placeholder="Optional revision UUID"
            />
          </div>

          <div className="field-group">
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
          </div>
        </div>
      </article>

      <article className="panel">
        <h2>Runs</h2>
        {historyQuery.isLoading ? (
          <EmptyState
            title="Loading history..."
            description="Gathering the run timeline for this script lineage."
            tone="neutral"
          />
        ) : null}
        {historyQuery.isError ? (
          <EmptyState
            title="Unable to load history"
            description="The history endpoint failed. Refresh and retry."
            tone="danger"
          />
        ) : null}
        {historyQuery.data && historyQuery.data.runs.length === 0 ? (
          <EmptyState
            title="No runs yet"
            description="Start the first analysis run for this script to build a revision timeline."
            tone="warm"
            action={<Link href={`/?script_id=${scriptId}`}>Launch first run</Link>}
          />
        ) : null}
        {historyQuery.data ? (
          <div className="history-card-list">
            {historyQuery.data.runs.map((run) => (
              <article key={run.run_id} className="history-run-card">
                <div className="history-run-card__top">
                  <div>
                    <p className="history-run-card__eyebrow">Run</p>
                    <h3>{run.run_id}</h3>
                  </div>
                  <StatusBadge status={run.status} />
                </div>
                <div className="history-run-card__meta">
                  <span>
                    Revision <code>{run.revision_id}</code>
                  </span>
                  <span>{formatDateTime(run.created_at)}</span>
                </div>
                <div className="run-links">
                  <Link href={`/runs/${run.run_id}`}>Open</Link>
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </article>
    </section>
  );
}
