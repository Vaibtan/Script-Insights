"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

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

  return (
    <div className="surface">
      <div className="composer-header">
        <p className="eyebrow">Multi-agent script evaluation</p>
        <h1>Script Insights Workspace</h1>
        <p className="subtle">
          Submit script text or upload a PDF to run summary, emotion, engagement, recommendation, and cliffhanger agents.
        </p>
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

      <form onSubmit={handleSubmit} className="composer-form">
        <label htmlFor="title-input">Title (optional)</label>
        <input
          id="title-input"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="The Last Message"
          autoComplete="off"
        />

        <label htmlFor="script-id-input">Existing script ID (optional)</label>
        <input
          id="script-id-input"
          value={scriptId}
          onChange={(event) => setScriptId(event.target.value)}
          placeholder="Reuse an existing script lineage"
          autoComplete="off"
        />

        {mode === "text" ? (
          <>
            <label htmlFor="script-input">Script text</label>
            <textarea
              id="script-input"
              rows={10}
              value={scriptText}
              onChange={(event) => setScriptText(event.target.value)}
              placeholder="Scene: ..."
            />
          </>
        ) : (
          <>
            <label htmlFor="pdf-input">PDF file</label>
            <input
              id="pdf-input"
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </>
        )}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting..." : submitLabel}
        </button>
      </form>

      {formError ? <p className="error">{formError}</p> : null}
      {submitRun.error ? (
        <p className="error">{submitRun.error.message}</p>
      ) : null}

      {lastRun ? (
        <div className="run-state" data-testid="submitted-run">
          <p className="run-title">
            {isPendingRun(lastRun.status) ? "Run queued" : "Run accepted"}
          </p>
          <p>
            Run ID: <code>{lastRun.run_id}</code>
          </p>
          <p>
            Status: <strong>{lastRun.status}</strong>
          </p>
          <div className="run-links">
            <Link href={`/runs/${lastRun.run_id}`}>Open run dashboard</Link>
            <Link href={`/scripts/${lastRun.script_id}/history`}>View run history</Link>
            <Link href={`/scripts/${lastRun.script_id}/compare`}>Compare revisions</Link>
          </div>
        </div>
      ) : null}
    </div>
  );
}
