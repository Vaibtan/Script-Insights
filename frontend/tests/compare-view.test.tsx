import { screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CompareView } from "@/components/compare-view";
import { renderWithProviders } from "./render";

describe("compare view", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders run deltas and changed recommendations", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(
      async (input: URL | RequestInfo) => {
        const url = String(input);
        if (url.includes("/api/v1/scripts/script-123/runs")) {
          return new Response(
            JSON.stringify({
              result_version: "v1",
              script_id: "script-123",
              runs: [
                {
                  run_id: "target-run",
                  revision_id: "rev-b",
                  status: "completed",
                  created_at: "2026-01-01T12:00:00+00:00",
                },
                {
                  run_id: "base-run",
                  revision_id: "rev-a",
                  status: "completed",
                  created_at: "2026-01-01T11:00:00+00:00",
                },
              ],
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        if (url.includes("/api/v1/scripts/script-123/compare")) {
          return new Response(
            JSON.stringify({
              result_version: "v1",
              script_id: "script-123",
              base_run_id: "base-run",
              target_run_id: "target-run",
              engagement_delta: {
                overall_delta: 1.4,
                factor_deltas: {
                  hook: 1.2,
                  conflict: 1.6,
                },
              },
              changed_recommendations: [
                "Dialogue: tighten the exchange leading to the reveal.",
              ],
              changed_evidence: ["Line 12-18 now carries the new reveal"],
              revision_lineage: {
                base_revision_id: "rev-a",
                target_revision_id: "rev-b",
              },
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        return new Response(
          JSON.stringify({ detail: `Unhandled request ${url}` }),
          { status: 500, headers: { "Content-Type": "application/json" } },
        );
      },
    );

    renderWithProviders(
      <CompareView
        scriptId="script-123"
        initialBaseRunId="base-run"
        initialTargetRunId="target-run"
      />,
    );

    expect(await screen.findByText(/Overall engagement delta/i)).toBeInTheDocument();
    expect(screen.getByText(/Dialogue: tighten the exchange/i)).toBeInTheDocument();
    expect(screen.getByText(/Line 12-18 now carries the new reveal/i)).toBeInTheDocument();
  });
});
