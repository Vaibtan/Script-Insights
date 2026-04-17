"use client";

import Link from "next/link";

import { useRunDetail } from "@/hooks/use-analysis-api";
import { formatPercent, formatScore } from "@/lib/formatting";

type Props = {
  runId: string;
};

function EvidenceList({
  title,
  items,
}: {
  title: string;
  items: Array<{ text: string }>;
}) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className="evidence-block">
      <p className="evidence-title">{title}</p>
      <ul>
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>{item.text}</li>
        ))}
      </ul>
    </div>
  );
}

export function RunDashboard({ runId }: Props) {
  const runQuery = useRunDetail(runId);

  if (runQuery.isLoading) {
    return <p>Loading run details...</p>;
  }

  if (runQuery.isError || !runQuery.data) {
    return <p role="alert">Unable to load run details.</p>;
  }

  const run = runQuery.data;
  const normalizationWarnings = run.normalized_script?.warnings ?? [];

  return (
    <section className="dashboard">
      <header className="surface">
        <p className="eyebrow">Run dashboard</p>
        <h1>Analysis run {run.run_id}</h1>
        <p className="subtle">
          Status <strong>{run.status}</strong> · Script <code>{run.script_id}</code>
        </p>
        <div className="run-links">
          <Link href={`/?script_id=${run.script_id}`}>Analyze next revision</Link>
          <Link href={`/scripts/${run.script_id}/history`}>Open run history</Link>
          <Link href={`/scripts/${run.script_id}/compare`}>Open compare view</Link>
        </div>
      </header>

      {run.failure_message ? (
        <article className="surface">
          <h2>Failure</h2>
          <p>{run.failure_message}</p>
        </article>
      ) : null}

      {run.summary ? (
        <article className="surface">
          <h2>Summary</h2>
          <p>{run.summary.text}</p>
          <EvidenceList
            title="Summary evidence"
            items={run.summary.evidence_spans}
          />
        </article>
      ) : null}

      {run.emotion ? (
        <article className="surface">
          <h2>Emotion</h2>
          <p>Dominant emotions: {run.emotion.dominant_emotions.join(", ")}</p>
          <p>
            Valence {formatScore(run.emotion.valence)} · Arousal{" "}
            {formatScore(run.emotion.arousal)}
          </p>
          <ul>
            {run.emotion.emotional_arc.map((point) => (
              <li key={`${point.beat_index}-${point.emotion}`}>
                Beat {point.beat_index}: {point.emotion} (
                {formatPercent(Math.max(0, point.valence))})
              </li>
            ))}
          </ul>
          <EvidenceList
            title="Emotion evidence"
            items={run.emotion.evidence_spans}
          />
        </article>
      ) : null}

      {run.engagement ? (
        <article className="surface">
          <h2>Engagement</h2>
          <p>
            Overall score <strong>{formatScore(run.engagement.overall_score)}</strong>
          </p>
          <p>{run.engagement.rationale}</p>
          <div className="factor-grid">
            {Object.entries(run.engagement.factors).map(([name, value]) => (
              <div key={name} className="factor-card">
                <p>{name}</p>
                <strong>{formatScore(value)}</strong>
              </div>
            ))}
          </div>
        </article>
      ) : null}

      {run.recommendations.length > 0 ? (
        <article className="surface">
          <h2>Recommendations</h2>
          <ul>
            {run.recommendations.map((item) => (
              <li key={`${item.category}-${item.suggestion}`}>
                <strong>{item.category}:</strong> {item.suggestion} ({item.rationale})
              </li>
            ))}
          </ul>
        </article>
      ) : null}

      {run.cliffhanger ? (
        <article className="surface">
          <h2>Cliffhanger</h2>
          <p>{run.cliffhanger.moment_text}</p>
          <p>{run.cliffhanger.why_it_works}</p>
          <EvidenceList
            title="Cliffhanger evidence"
            items={run.cliffhanger.evidence_spans}
          />
        </article>
      ) : null}

      {run.warnings.length > 0 || normalizationWarnings.length > 0 ? (
        <article className="surface warning-surface">
          <h2>Warnings</h2>
          <ul>
            {run.warnings.map((warning) => (
              <li key={`${warning.component}-${warning.code}`}>
                {warning.component}: {warning.message}
              </li>
            ))}
            {normalizationWarnings.map((warning) => (
              <li key={`normalization-${warning.code}`}>{warning.message}</li>
            ))}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
