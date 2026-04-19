"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { ScoreRing } from "@/components/score-ring";
import { isPendingRun } from "@/lib/api-client";
import { SubmitAnalysisRunResponse } from "@/lib/api-types";
import { useSubmitAnalysisRun } from "@/hooks/use-analysis-api";

type Mode = "text" | "pdf";

type Props = {
  onRunSubmitted?: (run: SubmitAnalysisRunResponse) => void;
  initialScriptId?: string;
};

export function AnalysisComposer({ onRunSubmitted, initialScriptId = "" }: Props) {
  const submitRun = useSubmitAnalysisRun();
  const [mode, setMode] = useState<Mode>("text");
  const [title, setTitle] = useState("");
  const [scriptId, setScriptId] = useState(initialScriptId);
  const [scriptText, setScriptText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [lastRun, setLastRun] = useState<SubmitAnalysisRunResponse | null>(null);

  const submitLabel =
    mode === "text" ? "Start analysis from text" : "Start analysis from PDF";

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    setLastRun(null);

    if (mode === "text") {
      if (!scriptText.trim()) {
        setFormError("Script text is required.");
        return;
      }
      submitRun.mutate(
        {
          mode: "text",
          title: title.trim() || undefined,
          scriptId: scriptId.trim() || undefined,
          scriptText: scriptText.trim(),
        },
        {
          onSuccess: (result) => {
            setLastRun(result);
            onRunSubmitted?.(result);
          },
        },
      );
      return;
    }

    if (!file) {
      setFormError("Choose a PDF file before submitting.");
      return;
    }

    submitRun.mutate(
      {
        mode: "pdf",
        title: title.trim() || undefined,
        scriptId: scriptId.trim() || undefined,
        file,
      },
      {
        onSuccess: (result) => {
          setLastRun(result);
          onRunSubmitted?.(result);
        },
      },
    );
  };

  const isSubmitting = submitRun.isPending;
  const isReuseAttached =
    lastRun !== null &&
    lastRun.reused_from_run_id !== null &&
    isPendingRun(lastRun.status);
  const isCompletedReuse =
    lastRun !== null &&
    lastRun.reused_from_run_id !== null &&
    !isPendingRun(lastRun.status);

  return (
    <section className="workspace-shell">
      <div className="workspace-hero panel panel--hero">
        <div className="hero-copy">
          <p className="eyebrow">Creative signal lab</p>
          <h1>Script Insights Workspace</h1>
          <p className="hero-lede">
            Review drafts like an editorial control room: ingest text or PDF,
            score the script across multiple agents, and track how each revision
            sharpens the audience hook.
          </p>
          <div className="hero-pill-row">
            <span className="hero-pill">summary</span>
            <span className="hero-pill">emotion arc</span>
            <span className="hero-pill">engagement factors</span>
            <span className="hero-pill">revision compare</span>
          </div>
          <div className="hero-note">
            {scriptId ? (
              <p>
                Revision mode is active for <code>{scriptId}</code>.
              </p>
            ) : (
              <p>Start a new script lineage or continue an existing revision stream.</p>
            )}
          </div>
        </div>

        <div className="hero-metrics">
          <ScoreRing
            label="Hook"
            value={8.6}
            caption="Cold-open urgency"
            tone="amber"
            valueText="8.6"
          />
          <ScoreRing
            label="Tension"
            value={7.8}
            caption="Escalation pressure"
            tone="cyan"
            valueText="7.8"
          />
          <ScoreRing
            label="Payoff"
            value={7.2}
            caption="Reveal satisfaction"
            tone="rose"
            valueText="7.2"
          />
        </div>
      </div>

      <div className="workspace-grid">
        <div className="panel panel--form">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Submission console</p>
              <h2>Launch a run</h2>
            </div>
            <div className="mode-toggle" role="tablist" aria-label="submission mode">
              <button
                type="button"
                className={mode === "text" ? "active" : ""}
                onClick={() => setMode("text")}
              >
                Paste text
              </button>
              <button
                type="button"
                className={mode === "pdf" ? "active" : ""}
                onClick={() => setMode("pdf")}
              >
                Upload PDF
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="composer-form">
            <div className="field-grid">
              <div className="field-group">
                <label htmlFor="title-input">Title (optional)</label>
                <input
                  id="title-input"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="The Last Message"
                  autoComplete="off"
                />
              </div>

              <div className="field-group">
                <label htmlFor="script-id-input">Existing script ID (optional)</label>
                <input
                  id="script-id-input"
                  value={scriptId}
                  onChange={(event) => setScriptId(event.target.value)}
                  placeholder="Reuse an existing script lineage"
                  autoComplete="off"
                />
              </div>
            </div>

            {mode === "text" ? (
              <div className="field-group">
                <label htmlFor="script-input">Script text</label>
                <textarea
                  id="script-input"
                  rows={12}
                  value={scriptText}
                  onChange={(event) => setScriptText(event.target.value)}
                  placeholder="Scene: Rain hammers the windshield. Riya reads the final message..."
                />
              </div>
            ) : (
              <div className="field-group">
                <label htmlFor="pdf-input">PDF file</label>
                <input
                  id="pdf-input"
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                />
                <p className="field-note">
                  Upload screenplay drafts directly. Extraction warnings remain visible in results.
                </p>
              </div>
            )}

            <button type="submit" className="primary-button" disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : submitLabel}
            </button>
          </form>

          {formError ? <p className="error">{formError}</p> : null}
          {submitRun.error ? <p className="error">{submitRun.error.message}</p> : null}

          {lastRun ? (
            <div className="run-state panel panel--success" data-testid="submitted-run">
              <div className="run-state__header">
              <p className="run-title">
                  {isPendingRun(lastRun.status) ? "Run queued" : "Run accepted"}
                </p>
                <span className="run-state__status">{lastRun.status}</span>
              </div>
              <p>
                Run ID: <code>{lastRun.run_id}</code>
              </p>
              {isReuseAttached ? (
                <p className="field-note">
                  Attached to an active exact-match run:{" "}
                  <code>{lastRun.reused_from_run_id}</code>
                </p>
              ) : null}
              {isCompletedReuse ? (
                <p className="field-note">
                  Reused completed analysis artifacts from{" "}
                  <code>{lastRun.reused_from_run_id}</code>.
                </p>
              ) : null}
              <div className="run-links">
                <Link href={`/runs/${lastRun.run_id}`}>Open run dashboard</Link>
                <Link href={`/scripts/${lastRun.script_id}/history`}>View run history</Link>
                <Link href={`/scripts/${lastRun.script_id}/compare`}>Compare revisions</Link>
              </div>
            </div>
          ) : null}
        </div>

        <aside className="panel panel--sidebar">
          <p className="eyebrow">What the system surfaces</p>
          <h2>Signal cards, not raw logs</h2>
          <div className="insight-stack">
            <article className="insight-card">
              <span className="insight-card__tag">Narrative fit</span>
              <h3>Summary + cliffhanger</h3>
              <p>
                See the high-order story shape, the strongest reveal, and the cited
                lines that justify the call.
              </p>
            </article>
            <article className="insight-card">
              <span className="insight-card__tag">Audience energy</span>
              <h3>Emotion + engagement</h3>
              <p>
                Track hook, tension, stakes, payoff, and emotional momentum as
                visual scores instead of dense JSON.
              </p>
            </article>
            <article className="insight-card">
              <span className="insight-card__tag">Revision intelligence</span>
              <h3>History + compare</h3>
              <p>
                Navigate past runs, compare revisions, and keep improving the same
                script lineage.
              </p>
            </article>
          </div>
        </aside>
      </div>
    </section>
  );
}
