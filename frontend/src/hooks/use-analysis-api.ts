"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  getRunComparison,
  getRunDetail,
  getRunHistory,
  isPendingRun,
  submitPdfRun,
  submitTextRun,
} from "@/lib/api-client";
import { RunStatus, SubmitAnalysisRunResponse } from "@/lib/api-types";

type SubmitInput =
  | {
      mode: "text";
      title?: string;
      scriptText: string;
      scriptId?: string;
    }
  | {
      mode: "pdf";
      title?: string;
      file: File;
      scriptId?: string;
    };

export function useSubmitAnalysisRun() {
  return useMutation<SubmitAnalysisRunResponse, Error, SubmitInput>({
    mutationFn: async (input) => {
      if (input.mode === "pdf") {
        return submitPdfRun({
          title: input.title,
          file: input.file,
          scriptId: input.scriptId,
        });
      }

      return submitTextRun({
        title: input.title,
        scriptText: input.scriptText,
        scriptId: input.scriptId,
      });
    },
  });
}

export function useRunDetail(runId: string) {
  return useQuery({
    queryKey: ["run-detail", runId],
    queryFn: () => getRunDetail(runId),
    enabled: runId.length > 0,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || isPendingRun(status)) {
        return 1_500;
      }
      return false;
    },
  });
}

export function useRunHistory(
  scriptId: string,
  filters: { revisionId?: string; status?: RunStatus },
) {
  return useQuery({
    queryKey: ["run-history", scriptId, filters.revisionId ?? "", filters.status ?? ""],
    queryFn: () => getRunHistory(scriptId, filters),
    enabled: scriptId.length > 0,
  });
}

export function useRunComparison(input: {
  scriptId: string;
  baseRunId: string;
  targetRunId: string;
}) {
  return useQuery({
    queryKey: ["run-compare", input.scriptId, input.baseRunId, input.targetRunId],
    queryFn: () =>
      getRunComparison({
        scriptId: input.scriptId,
        baseRunId: input.baseRunId,
        targetRunId: input.targetRunId,
      }),
    enabled:
      input.scriptId.length > 0 &&
      input.baseRunId.length > 0 &&
      input.targetRunId.length > 0,
  });
}
