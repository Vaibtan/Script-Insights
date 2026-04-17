import { screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RunDashboard } from "@/components/run-dashboard";
import { renderWithProviders } from "./render";

describe("run dashboard", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders summary, engagement, emotion, recommendations, cliffhanger, and warnings", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          result_version: "v1",
          run_id: "11111111-1111-4111-8111-111111111111",
          script_id: "22222222-2222-4222-8222-222222222222",
          revision_id: "33333333-3333-4333-8333-333333333333",
          status: "completed",
          failure_message: null,
          normalized_script: {
            scenes: [],
            dialogue_blocks: [],
            warnings: [{ code: "pdf_noise", message: "Minor extraction noise." }],
          },
          summary: {
            text: "Riya reconnects with Arjun after learning a hidden truth.",
            evidence_spans: [
              {
                start_offset: 0,
                end_offset: 24,
                text: "Riya receives the message.",
              },
            ],
          },
          emotion: {
            dominant_emotions: ["regret", "relief"],
            valence: 0.6,
            arousal: 0.7,
            emotional_arc: [
              { beat_index: 1, emotion: "regret", valence: 0.4, arousal: 0.8 },
            ],
            evidence_spans: [
              {
                start_offset: 25,
                end_offset: 54,
                text: "Arjun admits he learned the truth.",
              },
            ],
          },
          engagement: {
            overall_score: 7.9,
            factors: {
              hook: 8.2,
              conflict: 7.8,
              tension: 8.1,
              pacing: 7.5,
              stakes: 7.6,
              payoff: 7.4,
            },
            rationale: "The opening reveals unresolved history quickly.",
          },
          recommendations: [
            {
              category: "pacing",
              suggestion: "Tighten transition beats in the midpoint.",
              rationale: "Maintains tension between reveal moments.",
            },
          ],
          cliffhanger: {
            moment_text: "The accident wasn't your fault.",
            why_it_works: "Reframes the core relationship conflict.",
            evidence_spans: [
              {
                start_offset: 55,
                end_offset: 85,
                text: "The accident wasn't your fault.",
              },
            ],
          },
          warnings: [
            {
              code: "low_confidence",
              message: "Emotion confidence is moderate.",
              component: "emotion",
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    renderWithProviders(<RunDashboard runId="11111111-1111-4111-8111-111111111111" />);

    expect(await screen.findByText(/Riya reconnects with Arjun/i)).toBeInTheDocument();
    expect(screen.getByText(/overall score/i)).toBeInTheDocument();
    expect(screen.getByText(/Dominant emotions:/i)).toBeInTheDocument();
    expect(screen.getByText(/Tighten transition beats/i)).toBeInTheDocument();
    expect(screen.getAllByText(/The accident wasn't your fault/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Minor extraction noise/i)).toBeInTheDocument();
    expect(screen.getByText(/Emotion confidence is moderate/i)).toBeInTheDocument();
    expect(screen.getByText(/Riya receives the message/i)).toBeInTheDocument();
    expect(screen.getByText(/Arjun admits he learned the truth/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /analyze next revision/i })).toHaveAttribute(
      "href",
      "/?script_id=22222222-2222-4222-8222-222222222222",
    );
  });
});
