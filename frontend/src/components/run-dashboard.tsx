"use client";

import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { ScoreRing } from "@/components/score-ring";
import { StatusBadge } from "@/components/status-badge";
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
      <ul className="evidence-list">
        {items.map((item, index) => (
          <li key={`${title}-${index}`} className="evidence-chip">
            {item.text}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function RunDashboard({ runId }: Props) {
  const runQuery = useRunDetail(runId);

  if (runQuery.isLoading) {
    return (
      <section className="dashboard">
        <article className="panel">
          <EmptyState
            title="Loading run details..."
            description="Pulling the latest agent outputs, evidence spans, and scoring factors."
            tone="neutral"
          />
        </article>
      </section>
    );
  }

  if (runQuery.isError || !runQuery.data) {
    return (
      <section className="dashboard">
        <article className="panel">
          <EmptyState
            title="Unable to load run details"
            description="The run could not be retrieved right now. Refresh and try again."
            tone="danger"
          />
        </article>
      </section>
    );
  }

  const run = runQuery.data;
  const normalizationWarnings = run.normalized_script?.warnings ?? [];
  const factorEntries = Object.entries(run.engagement?.factors ?? {});
  const topFactors = factorEntries.slice(0, 4);
  const hasReuseMetadata =
    run.reused_from_run_id !== null || run.normalized_candidate_run_id !== null;

  return (
    <section className="dashboard">
      <header className="panel panel--hero dashboard-hero">
        <div>
          <p className="eyebrow">Run dashboard</p>
          <h1>Analysis run {run.run_id}</h1>
          <p className="hero-lede">
            A full creative-health snapshot across summary, emotion, engagement,
            recommendations, and revision-readiness.
          </p>
          <div className="meta-row">
            <StatusBadge status={run.status} />
            <span className="meta-chip">
              Script <code>{run.script_id}</code>
            </span>
            <span className="meta-chip">
              Revision <code>{run.revision_id}</code>
            </span>
          </div>
        </div>
        <div className="run-links">
          <Link href={`/?script_id=${run.script_id}`}>Analyze next revision</Link>
          <Link href={`/scripts/${run.script_id}/history`}>Open run history</Link>
          <Link href={`/scripts/${run.script_id}/compare`}>Open compare view</Link>
        </div>
      </header>

      {hasReuseMetadata ? (
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Reuse provenance</p>
              <h2>Execution context</h2>
            </div>
          </div>
          <div className="recommendation-list">
            {run.reused_from_run_id ? (
              <article className="recommendation-card">
                <span className="recommendation-card__tag">Exact reuse</span>
                <strong>Reused from prior run</strong>
                <p>
                  This run resolved against an existing exact-match execution and
                  inherited its completed artifact set.
                </p>
                <Link href={`/runs/${run.reused_from_run_id}`}>Open source run</Link>
              </article>
            ) : null}
            {run.normalized_candidate_run_id ? (
              <article className="recommendation-card">
                <span className="recommendation-card__tag">Near match</span>
                <strong>Structurally similar prior run</strong>
                <p>
                  A normalized-content match was detected, but this run was still
                  recomputed to preserve exact evidence alignment.
                </p>
                <Link href={`/runs/${run.normalized_candidate_run_id}`}>
                  Open candidate run
                </Link>
              </article>
            ) : null}
          </div>
        </section>
      ) : null}

      {run.failure_message ? (
        <article className="panel warning-panel">
          <h2>Failure</h2>
          <p>{run.failure_message}</p>
        </article>
      ) : null}

      <section className="metrics-grid">
        <ScoreRing
          label="Engagement"
          value={run.engagement?.overall_score ?? 0}
          caption={run.engagement?.rationale ?? "Waiting for engagement output."}
          tone="amber"
          size="large"
          valueText={run.engagement ? formatScore(run.engagement.overall_score) : "--"}
        />
        <ScoreRing
          label="Valence"
          value={run.emotion?.valence ?? 0}
          max={1}
          caption={
            run.emotion
              ? `Dominant: ${run.emotion.dominant_emotions.join(", ")}`
              : "Waiting for emotion output."
          }
          tone="cyan"
          size="medium"
          valueText={run.emotion ? formatScore(run.emotion.valence) : "--"}
        />
        <ScoreRing
          label="Arousal"
          value={run.emotion?.arousal ?? 0}
          max={1}
          caption="Intensity of the emotional curve"
          tone="rose"
          size="medium"
          valueText={run.emotion ? formatScore(run.emotion.arousal) : "--"}
        />
        <ScoreRing
          label="Warnings"
          value={run.warnings.length + normalizationWarnings.length}
          max={6}
          caption="Operational or extraction caveats"
          tone="lime"
          size="medium"
          valueText={String(run.warnings.length + normalizationWarnings.length)}
        />
      </section>

      {topFactors.length > 0 ? (
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Engagement factors</p>
              <h2>Score profile</h2>
            </div>
          </div>
          <div className="factor-ring-grid">
            {topFactors.map(([name, value], index) => (
              <ScoreRing
                key={name}
                label={name}
                value={value}
                caption="Factor strength"
                tone={index % 3 === 0 ? "amber" : index % 3 === 1 ? "cyan" : "rose"}
                valueText={formatScore(value)}
              />
            ))}
          </div>
        </section>
      ) : null}

      {run.summary ? (
        <article className="panel">
          <h2>Summary</h2>
          <p className="narrative-copy">{run.summary.text}</p>
          <EvidenceList
            title="Summary evidence"
            items={run.summary.evidence_spans}
          />
        </article>
      ) : null}

      {run.emotion ? (
        <article className="panel">
          <h2>Emotion</h2>
          <div className="emotion-summary">
            <p>Dominant emotions: {run.emotion.dominant_emotions.join(", ")}</p>
            <p>
              Valence {formatScore(run.emotion.valence)} · Arousal{" "}
              {formatScore(run.emotion.arousal)}
            </p>
          </div>
          <div className="arc-list">
            {run.emotion.emotional_arc.map((point) => (
              <div key={`${point.beat_index}-${point.emotion}`} className="arc-item">
                <div className="arc-item__meta">
                  <strong>Beat {point.beat_index}</strong>
                  <span>{point.emotion}</span>
                </div>
                <div className="arc-bar">
                  <div
                    className="arc-bar__fill"
                    style={{
                      width: formatPercent(Math.max(0, point.valence)),
                    }}
                  />
                </div>
                <span className="arc-item__value">
                  {formatPercent(Math.max(0, point.valence))}
                </span>
              </div>
            ))}
          </div>
          <p className="subtle">
            Valence {formatScore(run.emotion.valence)} · Arousal{" "}
            {formatScore(run.emotion.arousal)}
          </p>
          <EvidenceList
            title="Emotion evidence"
            items={run.emotion.evidence_spans}
          />
        </article>
      ) : null}

      {run.engagement ? (
        <article className="panel">
          <h2>Engagement</h2>
          <p className="narrative-copy">
            Overall score <strong>{formatScore(run.engagement.overall_score)}</strong>
          </p>
          <p>{run.engagement.rationale}</p>
          <div className="factor-grid">
            {Object.entries(run.engagement.factors).map(([name, value]) => (
              <div key={name} className="factor-card">
                <p>{name}</p>
                <strong>{formatScore(value)}</strong>
                <div className="factor-bar">
                  <div
                    className="factor-bar__fill"
                    style={{ width: `${Math.max(0, Math.min(100, value * 10))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>
      ) : null}

      {run.recommendations.length > 0 ? (
        <article className="panel">
          <h2>Recommendations</h2>
          <ul className="recommendation-list">
            {run.recommendations.map((item) => (
              <li key={`${item.category}-${item.suggestion}`} className="recommendation-card">
                <span className="recommendation-card__tag">{item.category}</span>
                <strong>{item.suggestion}</strong>
                <p>{item.rationale}</p>
              </li>
            ))}
          </ul>
        </article>
      ) : null}

      {run.cliffhanger ? (
        <article className="panel panel--spotlight">
          <h2>Cliffhanger</h2>
          <p className="spotlight-quote">{run.cliffhanger.moment_text}</p>
          <p>{run.cliffhanger.why_it_works}</p>
          <EvidenceList
            title="Cliffhanger evidence"
            items={run.cliffhanger.evidence_spans}
          />
        </article>
      ) : null}

      {run.warnings.length > 0 || normalizationWarnings.length > 0 ? (
        <article className="panel warning-panel">
          <h2>Warnings</h2>
          <ul className="warning-list">
            {run.warnings.map((warning) => (
              <li key={`${warning.component}-${warning.code}`} className="warning-item">
                {warning.component}: {warning.message}
              </li>
            ))}
            {normalizationWarnings.map((warning) => (
              <li key={`normalization-${warning.code}`} className="warning-item">
                {warning.message}
              </li>
            ))}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
