export type RunStatus = "queued" | "running" | "completed" | "partial" | "failed";

export type SubmitAnalysisRunResponse = {
  result_version: string;
  run_id: string;
  script_id: string;
  revision_id: string;
  status: RunStatus;
  failure_message: string | null;
  reused_from_run_id: string | null;
};

export type EvidenceSpan = {
  start_offset: number;
  end_offset: number;
  text: string;
};

export type SummaryPayload = {
  text: string;
  evidence_spans: EvidenceSpan[];
};

export type EmotionArcPoint = {
  beat_index: number;
  emotion: string;
  valence: number;
  arousal: number;
};

export type EmotionPayload = {
  dominant_emotions: string[];
  valence: number;
  arousal: number;
  emotional_arc: EmotionArcPoint[];
  evidence_spans: EvidenceSpan[];
};

export type EngagementPayload = {
  overall_score: number;
  factors: Record<string, number>;
  rationale: string;
};

export type RecommendationPayload = {
  category: string;
  suggestion: string;
  rationale: string;
};

export type CliffhangerPayload = {
  moment_text: string;
  why_it_works: string;
  evidence_spans: EvidenceSpan[];
};

export type AnalysisWarningPayload = {
  code: string;
  message: string;
  component: string;
};

export type NormalizationWarningPayload = {
  code: string;
  message: string;
};

export type AnalysisRunDetailResponse = {
  result_version: string;
  run_id: string;
  script_id: string;
  revision_id: string;
  status: RunStatus;
  failure_message: string | null;
  reused_from_run_id: string | null;
  normalized_candidate_run_id: string | null;
  normalized_script: {
    scenes: Array<{
      scene_index: number;
      heading: string;
      content: string;
      start_offset: number;
      end_offset: number;
    }>;
    dialogue_blocks: Array<{
      scene_index: number;
      speaker: string;
      line: string;
      start_offset: number;
      end_offset: number;
    }>;
    warnings: NormalizationWarningPayload[];
  } | null;
  summary: SummaryPayload | null;
  emotion: EmotionPayload | null;
  engagement: EngagementPayload | null;
  recommendations: RecommendationPayload[];
  cliffhanger: CliffhangerPayload | null;
  warnings: AnalysisWarningPayload[];
};

export type RunHistoryEntry = {
  run_id: string;
  revision_id: string;
  status: RunStatus;
  created_at: string;
};

export type RunHistoryResponse = {
  result_version: string;
  script_id: string;
  runs: RunHistoryEntry[];
};

export type RunComparisonResponse = {
  result_version: string;
  script_id: string;
  base_run_id: string;
  target_run_id: string;
  engagement_delta: {
    overall_delta: number;
    factor_deltas: Record<string, number>;
  };
  changed_recommendations: string[];
  changed_evidence: string[];
  revision_lineage: {
    base_revision_id: string;
    target_revision_id: string;
  };
};
