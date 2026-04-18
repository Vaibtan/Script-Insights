"use client";

import { RunStatus } from "@/lib/api-types";

type Props = {
  status: RunStatus;
};

export function StatusBadge({ status }: Props) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      <span className="status-badge__dot" aria-hidden="true" />
      {status}
    </span>
  );
}
