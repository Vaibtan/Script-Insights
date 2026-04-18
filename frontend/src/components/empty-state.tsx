"use client";

import { ReactNode } from "react";

type EmptyStateTone = "neutral" | "warm" | "danger";

type Props = {
  title: string;
  description: string;
  action?: ReactNode;
  tone?: EmptyStateTone;
};

export function EmptyState({
  title,
  description,
  action,
  tone = "neutral",
}: Props) {
  return (
    <div className={`empty-state empty-state--${tone}`}>
      <div className="empty-state__glyph" aria-hidden="true" />
      <div className="empty-state__copy">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      {action ? <div className="empty-state__action">{action}</div> : null}
    </div>
  );
}
