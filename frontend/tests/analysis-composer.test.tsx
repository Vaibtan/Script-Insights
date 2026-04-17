import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AnalysisComposer } from "@/components/analysis-composer";
import { renderWithProviders } from "./render";

describe("analysis composer", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("submits pasted text and shows queued run links", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          result_version: "v1",
          run_id: "11111111-1111-4111-8111-111111111111",
          script_id: "22222222-2222-4222-8222-222222222222",
          revision_id: "33333333-3333-4333-8333-333333333333",
          status: "queued",
          failure_message: null,
        }),
        {
          status: 202,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    renderWithProviders(<AnalysisComposer />);

    await userEvent.type(
      screen.getByLabelText("Script text"),
      "Scene: Riya receives a late message.\nRiya: Why now?\nArjun: I learned the truth.",
    );
    await userEvent.click(screen.getByRole("button", { name: /start analysis from text/i }));

    expect(await screen.findByText("Run queued")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open run dashboard/i })).toHaveAttribute(
      "href",
      "/runs/11111111-1111-4111-8111-111111111111",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analysis/runs"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("submits a new revision into an existing script lineage", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          result_version: "v1",
          run_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
          script_id: "22222222-2222-4222-8222-222222222222",
          revision_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
          status: "queued",
          failure_message: null,
        }),
        {
          status: 202,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    renderWithProviders(
      <AnalysisComposer initialScriptId="22222222-2222-4222-8222-222222222222" />,
    );

    await userEvent.type(
      screen.getByLabelText("Script text"),
      "Scene: Revision draft\nRiya: Why now?\nArjun: Because I know the truth.",
    );
    await userEvent.click(screen.getByRole("button", { name: /start analysis from text/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: expect.stringContaining(
          '"script_id":"22222222-2222-4222-8222-222222222222"',
        ),
      }),
    );
  });
});
