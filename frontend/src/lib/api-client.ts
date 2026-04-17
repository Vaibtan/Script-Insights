import {
  AnalysisRunDetailResponse,
  RunComparisonResponse,
  RunHistoryResponse,
  RunStatus,
  SubmitAnalysisRunResponse,
} from "@/lib/api-types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

const API_PREFIX = "/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly statusCode: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type SubmitTextInput = {
  title?: string;
  scriptText: string;
  scriptId?: string;
};

type HistoryFilters = {
  revisionId?: string;
  status?: RunStatus;
};

function buildUrl(path: string): string {
  return `${API_BASE_URL}${API_PREFIX}${path}`;
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: "Unexpected API error." }));
    const message =
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof body.detail === "string"
        ? body.detail
        : "Unexpected API error.";
    throw new ApiError(message, response.status);
  }
  return (await response.json()) as T;
}

export async function submitTextRun(
  input: SubmitTextInput,
): Promise<SubmitAnalysisRunResponse> {
  const response = await fetch(buildUrl("/analysis/runs"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: input.title,
      script_text: input.scriptText,
      script_id: input.scriptId,
    }),
  });
  return parseJson<SubmitAnalysisRunResponse>(response);
}

export async function submitPdfRun(input: {
  title?: string;
  file: File;
  scriptId?: string;
}): Promise<SubmitAnalysisRunResponse> {
  const formData = new FormData();
  formData.set("file", input.file);
  if (input.title?.trim()) {
    formData.set("title", input.title.trim());
  }
  if (input.scriptId?.trim()) {
    formData.set("script_id", input.scriptId.trim());
  }

  const response = await fetch(buildUrl("/analysis/runs/upload"), {
    method: "POST",
    body: formData,
  });
  return parseJson<SubmitAnalysisRunResponse>(response);
}

export async function getRunDetail(
  runId: string,
): Promise<AnalysisRunDetailResponse> {
  const response = await fetch(buildUrl(`/analysis/runs/${runId}`));
  return parseJson<AnalysisRunDetailResponse>(response);
}

export async function getRunHistory(
  scriptId: string,
  filters: HistoryFilters,
): Promise<RunHistoryResponse> {
  const query = new URLSearchParams();
  if (filters.revisionId?.trim()) {
    query.set("revision_id", filters.revisionId.trim());
  }
  if (filters.status) {
    query.set("status", filters.status);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  const response = await fetch(buildUrl(`/scripts/${scriptId}/runs${suffix}`));
  return parseJson<RunHistoryResponse>(response);
}

export async function getRunComparison(input: {
  scriptId: string;
  baseRunId: string;
  targetRunId: string;
}): Promise<RunComparisonResponse> {
  const query = new URLSearchParams({
    base_run_id: input.baseRunId,
    target_run_id: input.targetRunId,
  });
  const response = await fetch(
    buildUrl(`/scripts/${input.scriptId}/compare?${query.toString()}`),
  );
  return parseJson<RunComparisonResponse>(response);
}

export function isPendingRun(status: RunStatus): boolean {
  return status === "queued" || status === "running";
}
