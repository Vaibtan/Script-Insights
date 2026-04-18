"use client";

import { CSSProperties } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { ScoreRing } from "@/components/score-ring";
import { useRunComparison, useRunHistory } from "@/hooks/use-analysis-api";
import { formatScore } from "@/lib/formatting";

type Props = {
  scriptId: string;
  initialBaseRunId?: string;
  initialTargetRunId?: string;
};

function formatSignedScore(value: number): string {
  const formatted = formatScore(value);
  return value > 0 ? `+${formatted}` : formatted;
}

export function CompareView({
  scriptId,
  initialBaseRunId = "",
  initialTargetRunId = "",
}: Props) {
  const historyQuery = useRunHistory(scriptId, {});
  const [baseRunId, setBaseRunId] = useState(initialBaseRunId);
  const [targetRunId, setTargetRunId] = useState(initialTargetRunId);

  useEffect(() => {
    if (!historyQuery.data || historyQuery.data.runs.length < 2) {
      return;
    }
    if (!baseRunId) {
      setBaseRunId(historyQuery.data.runs[1]?.run_id ?? "");
    }
    if (!targetRunId) {
      setTargetRunId(historyQuery.data.runs[0]?.run_id ?? "");
    }
  }, [baseRunId, historyQuery.data, targetRunId]);

  const compareQuery = useRunComparison({
    scriptId,
    baseRunId,
    targetRunId,
  });
  const runs = historyQuery.data?.runs ?? [];
  const hasComparableRuns = runs.length >= 2;

  return (
    <section className="dashboard">
      <header className="panel panel--hero dashboard-hero">
        <div>
          <p className="eyebrow">Revision compare</p>
          <h1>Script {scriptId}</h1>
          <p className="hero-lede">
            Compare two runs side by side to see whether the latest revision
            materially improved the audience signal.
          </p>
        </div>
        <div className="run-links">
          <Link href={`/?script_id=${scriptId}`}>Analyze next revision</Link>
          <Link href={`/scripts/${scriptId}/history`}>Open run history</Link>
        </div>
      </header>

      <article className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Run selection</p>
            <h2>Choose revisions to compare</h2>
          </div>
        </div>
        {historyQuery.isLoading ? (
          <EmptyState
            title="Loading runs..."
            description="Pulling available runs for this script."
            tone="neutral"
          />
        ) : null}
        {historyQuery.isError ? (
          <EmptyState
            title="Unable to load runs"
            description="Run selection is temporarily unavailable. Refresh and retry."
            tone="danger"
          />
        ) : null}
        {historyQuery.data && runs.length === 0 ? (
          <EmptyState
            title="No runs to compare yet"
            description="Create at least two runs for this script to unlock revision delta analysis."
            tone="warm"
            action={<Link href={`/?script_id=${scriptId}`}>Analyze first revision</Link>}
          />
        ) : null}
        {historyQuery.data && runs.length === 1 ? (
          <EmptyState
            title="Need one more run"
            description="Only one run exists. Submit another revision to compare changes."
            tone="warm"
            action={<Link href={`/?script_id=${scriptId}`}>Analyze next revision</Link>}
          />
        ) : null}
        {hasComparableRuns ? (
          <div className="field-grid">
            <div className="field-group">
              <label htmlFor="base-run-select">Base run</label>
              <select
                id="base-run-select"
                value={baseRunId}
                onChange={(event) => setBaseRunId(event.target.value)}
              >
                <option value="">Choose base run</option>
                {runs.map((run) => (
                  <option key={`base-${run.run_id}`} value={run.run_id}>
                    {run.run_id} ({run.status})
                  </option>
                ))}
              </select>
            </div>

            <div className="field-group">
              <label htmlFor="target-run-select">Target run</label>
              <select
                id="target-run-select"
                value={targetRunId}
                onChange={(event) => setTargetRunId(event.target.value)}
              >
                <option value="">Choose target run</option>
                {runs.map((run) => (
                  <option key={`target-${run.run_id}`} value={run.run_id}>
                    {run.run_id} ({run.status})
                  </option>
                ))}
              </select>
            </div>
          </div>
        ) : null}
      </article>

      <article className="panel">
        <h2>Delta summary</h2>
        {!hasComparableRuns ? (
          <EmptyState
            title="Delta engine is waiting"
            description="Choose a base and target run after at least two runs are available."
            tone="neutral"
          />
        ) : null}
        {compareQuery.isLoading ? (
          <EmptyState
            title="Computing deltas..."
            description="Comparing engagement changes, recommendation shifts, and evidence drift."
            tone="neutral"
          />
        ) : null}
        {compareQuery.isError ? (
          <EmptyState
            title="Unable to compare selected runs"
            description="The compare request failed. Try another run pair."
            tone="danger"
          />
        ) : null}
        {compareQuery.data && hasComparableRuns ? (
          <>
            <div className="compare-summary-grid">
              <ScoreRing
                label="Delta"
                value={Math.abs(compareQuery.data.engagement_delta.overall_delta)}
                max={3}
                tone={
                  compareQuery.data.engagement_delta.overall_delta >= 0 ? "amber" : "rose"
                }
                valueText={formatSignedScore(compareQuery.data.engagement_delta.overall_delta)}
                caption="Overall engagement delta"
              />
              <div className="compare-lineage">
                <p className="compare-lineage__eyebrow">Revision lineage</p>
                <strong>
                  {compareQuery.data.revision_lineage.base_revision_id} →{" "}
                  {compareQuery.data.revision_lineage.target_revision_id}
                </strong>
                <p>
                  Net movement{" "}
                  <strong>
                    {formatScore(compareQuery.data.engagement_delta.overall_delta)}
                  </strong>
                </p>
                <div className="compare-insight-strip">
                  <span className="compare-insight compare-insight--positive">
                    Improved{" "}
                    {
                      Object.values(compareQuery.data.engagement_delta.factor_deltas).filter(
                        (value) => value > 0,
                      ).length
                    }
                  </span>
                  <span className="compare-insight compare-insight--negative">
                    Dropped{" "}
                    {
                      Object.values(compareQuery.data.engagement_delta.factor_deltas).filter(
                        (value) => value < 0,
                      ).length
                    }
                  </span>
                  <span className="compare-insight compare-insight--neutral">
                    Flat{" "}
                    {
                      Object.values(compareQuery.data.engagement_delta.factor_deltas).filter(
                        (value) => value === 0,
                      ).length
                    }
                  </span>
                </div>
              </div>
            </div>
            <div className="factor-grid factor-grid--compare">
              {Object.entries(compareQuery.data.engagement_delta.factor_deltas).map(
                ([factor, delta]) => {
                  const span = Math.max(4, Math.min(50, Math.abs(delta) * 12));
                  const style = { "--delta-span": `${span}%` } as CSSProperties;
                  const trend =
                    delta > 0 ? "improved" : delta < 0 ? "dropped" : "no shift";
                  return (
                    <div key={factor} className="factor-card factor-card--delta">
                      <div className="factor-card__header">
                        <p>{factor}</p>
                        <span
                          className={`delta-chip ${
                            delta > 0
                              ? "delta-chip--positive"
                              : delta < 0
                                ? "delta-chip--negative"
                                : "delta-chip--neutral"
                          }`}
                        >
                          {formatSignedScore(delta)}
                        </span>
                      </div>
                      <div className="compare-delta-track">
                        <span className="compare-delta-track__zero" />
                        {delta !== 0 ? (
                          <span
                            className={`compare-delta-fill ${
                              delta > 0
                                ? "compare-delta-fill--positive"
                                : "compare-delta-fill--negative"
                            }`}
                            style={style}
                          />
                        ) : null}
                      </div>
                      <p className="factor-card__trend">Trend: {trend}</p>
                    </div>
                  );
                },
              )}
            </div>

            <h3>Changed recommendations</h3>
            {compareQuery.data.changed_recommendations.length > 0 ? (
              <ul className="recommendation-list">
                {compareQuery.data.changed_recommendations.map((item) => (
                  <li key={item} className="recommendation-card">
                    <strong>{item}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                title="No recommendation deltas"
                description="Recommendation guidance stayed stable between these revisions."
                tone="neutral"
              />
            )}

            <h3>Changed evidence spans</h3>
            {compareQuery.data.changed_evidence.length > 0 ? (
              <ul className="evidence-list">
                {compareQuery.data.changed_evidence.map((item) => (
                  <li key={item} className="evidence-chip">
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                title="No evidence drift"
                description="Cited evidence did not materially change between selected runs."
                tone="neutral"
              />
            )}

            <div className="run-links">
              <Link href={`/runs/${compareQuery.data.base_run_id}`}>Open base run</Link>
              <Link href={`/runs/${compareQuery.data.target_run_id}`}>Open target run</Link>
            </div>
          </>
        ) : null}
      </article>
    </section>
  );
}
