import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HistoryDashboard } from "@/components/history-dashboard";
import { renderWithProviders } from "./render";

describe("history dashboard", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows run history and refetches when status filter changes", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            result_version: "v1",
            script_id: "22222222-2222-4222-8222-222222222222",
            runs: [
              {
                run_id: "r-2",
                revision_id: "rev-2",
                status: "completed",
                created_at: "2026-01-01T12:00:00+00:00",
              },
              {
                run_id: "r-1",
                revision_id: "rev-1",
                status: "partial",
                created_at: "2026-01-01T11:00:00+00:00",
              },
            ],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      );

    renderWithProviders(
      <HistoryDashboard scriptId="22222222-2222-4222-8222-222222222222" />,
    );

    expect(await screen.findByText("r-2")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Open" })[0]).toHaveAttribute(
      "href",
      "/runs/r-2",
    );

    await userEvent.selectOptions(screen.getByLabelText("Status"), "partial");

    await waitFor(() => {
      const urls = fetchMock.mock.calls.map((call) => String(call[0]));
      expect(urls.some((url) => url.includes("status=partial"))).toBe(true);
    });
  });
});
