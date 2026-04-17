import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AnalysisComposer } from "@/components/analysis-composer";
import { RunDashboard } from "@/components/run-dashboard";
import { SubmitAnalysisRunResponse } from "@/lib/api-types";
import { renderWithProviders } from "./render";

function UploadFlowHarness() {
  const [runId, setRunId] = useState<string | null>(null);

  return (
    <>
      <AnalysisComposer
        initialScriptId="55555555-5555-4555-8555-555555555555"
        onRunSubmitted={(run: SubmitAnalysisRunResponse) => setRunId(run.run_id)}
      />
      {runId ? <RunDashboard runId={runId} /> : null}
    </>
  );
}

describe("pdf upload flow", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("uploads a PDF and surfaces extraction warnings in results", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(
      async (input: URL | RequestInfo, init?: RequestInit) => {
        const url = typeof input === "string" ? input : input.toString();
        if (url.endsWith("/api/v1/analysis/runs/upload")) {
          expect(init?.method).toBe("POST");
          expect(init?.body).toBeInstanceOf(FormData);
          expect((init?.body as FormData).get("script_id")).toBe(
            "55555555-5555-4555-8555-555555555555",
          );
          return new Response(
            JSON.stringify({
              result_version: "v1",
              run_id: "44444444-4444-4444-8444-444444444444",
              script_id: "55555555-5555-4555-8555-555555555555",
              revision_id: "66666666-6666-4666-8666-666666666666",
              status: "queued",
              failure_message: null,
            }),
            { status: 202, headers: { "Content-Type": "application/json" } },
          );
        }

        if (url.endsWith("/api/v1/analysis/runs/44444444-4444-4444-8444-444444444444")) {
          return new Response(
            JSON.stringify({
              result_version: "v1",
              run_id: "44444444-4444-4444-8444-444444444444",
              script_id: "55555555-5555-4555-8555-555555555555",
              revision_id: "66666666-6666-4666-8666-666666666666",
              status: "completed",
              failure_message: null,
              normalized_script: {
                scenes: [],
                dialogue_blocks: [],
                warnings: [
                  {
                    code: "extraction_noise",
                    message: "PDF extraction dropped some punctuation.",
                  },
                ],
              },
              summary: {
                text: "A hidden truth resets a broken relationship.",
                evidence_spans: [],
              },
              emotion: null,
              engagement: null,
              recommendations: [],
              cliffhanger: null,
              warnings: [],
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        return new Response(
          JSON.stringify({ detail: `Unhandled request: ${url}` }),
          { status: 500, headers: { "Content-Type": "application/json" } },
        );
      },
    );

    renderWithProviders(<UploadFlowHarness />);

    await userEvent.click(screen.getByRole("button", { name: /upload pdf/i }));
    const fileInput = screen.getByLabelText("PDF file");
    const file = new File(["dummy content"], "script.pdf", {
      type: "application/pdf",
    });
    await userEvent.upload(fileInput, file);

    await userEvent.click(
      screen.getByRole("button", { name: /start analysis from pdf/i }),
    );

    expect(await screen.findByText(/PDF extraction dropped some punctuation/i)).toBeInTheDocument();
  });
});
