"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useRunComparison, useRunHistory } from "@/hooks/use-analysis-api";
import { formatScore } from "@/lib/formatting";

type Props = {
  scriptId: string;
  initialBaseRunId?: string;
  initialTargetRunId?: string;
};

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

  return (
    <section className="dashboard">
      <header className="surface">
        <p className="eyebrow">Revision compare</p>
        <h1>Script {scriptId}</h1>
        <div className="run-links">
          <Link href={`/?script_id=${scriptId}`}>Analyze next revision</Link>
          <Link href={`/scripts/${scriptId}/history`}>Open run history</Link>
        </div>
      </header>

      <article className="surface">
        <h2>Run selection</h2>
        <label htmlFor="base-run-select">Base run</label>
        <select
          id="base-run-select"
          value={baseRunId}
          onChange={(event) => setBaseRunId(event.target.value)}
        >
          <option value="">Choose base run</option>
          {historyQuery.data?.runs.map((run) => (
            <option key={`base-${run.run_id}`} value={run.run_id}>
              {run.run_id} ({run.status})
            </option>
          ))}
        </select>

        <label htmlFor="target-run-select">Target run</label>
        <select
          id="target-run-select"
          value={targetRunId}
          onChange={(event) => setTargetRunId(event.target.value)}
        >
          <option value="">Choose target run</option>
          {historyQuery.data?.runs.map((run) => (
            <option key={`target-${run.run_id}`} value={run.run_id}>
              {run.run_id} ({run.status})
            </option>
          ))}
        </select>
      </article>

      <article className="surface">
        <h2>Delta summary</h2>
        {compareQuery.isLoading ? <p>Computing deltas...</p> : null}
        {compareQuery.isError ? <p role="alert">Unable to compare selected runs.</p> : null}
        {compareQuery.data ? (
          <>
            <p>
              Overall engagement delta{" "}
              <strong>{formatScore(compareQuery.data.engagement_delta.overall_delta)}</strong>
            </p>
            <div className="factor-grid">
              {Object.entries(compareQuery.data.engagement_delta.factor_deltas).map(
                ([factor, delta]) => (
                  <div key={factor} className="factor-card">
                    <p>{factor}</p>
                    <strong>{formatScore(delta)}</strong>
                  </div>
                ),
              )}
            </div>

            <h3>Changed recommendations</h3>
            <ul>
              {compareQuery.data.changed_recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>

            <h3>Changed evidence spans</h3>
            <ul>
              {compareQuery.data.changed_evidence.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>

            <div className="run-links">
              <Link href={`/runs/${compareQuery.data.base_run_id}`}>Open base run</Link>
              <Link href={`/runs/${compareQuery.data.target_run_id}`}>Open target run</Link>
            </div>
          </>
        ) : (
          <p>Select two runs to view deltas.</p>
        )}
      </article>
    </section>
  );
}
