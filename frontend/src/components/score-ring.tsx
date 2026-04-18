"use client";

import { CSSProperties } from "react";

type Tone = "cyan" | "amber" | "rose" | "lime";
type Size = "small" | "medium" | "large";

type Props = {
  label: string;
  value: number;
  max?: number;
  caption?: string;
  tone?: Tone;
  size?: Size;
  valueText?: string;
};

const TONE_BY_NAME: Record<Tone, string> = {
  cyan: "var(--tone-cyan)",
  amber: "var(--tone-amber)",
  rose: "var(--tone-rose)",
  lime: "var(--tone-lime)",
};

export function ScoreRing({
  label,
  value,
  max = 10,
  caption,
  tone = "cyan",
  size = "medium",
  valueText,
}: Props) {
  const safeValue = Number.isFinite(value) ? Math.max(0, value) : 0;
  const progress = Math.max(0, Math.min(1, safeValue / max));
  const offset = 100 - progress * 100;
  const style = {
    "--ring-progress": `${progress}`,
    "--ring-accent": TONE_BY_NAME[tone],
    "--ring-offset": `${offset}`,
  } as CSSProperties;

  return (
    <article
      className={`score-ring score-ring--${size}`}
      style={style}
      aria-label={`${label}: ${valueText ?? safeValue.toFixed(1)}`}
    >
      <div className="score-ring__visual" aria-hidden="true">
        <svg viewBox="0 0 120 120" className="score-ring__svg">
          <circle className="score-ring__track" cx="60" cy="60" r="44" />
          <circle
            className="score-ring__progress"
            cx="60"
            cy="60"
            r="44"
            pathLength="100"
            strokeDasharray="100"
          />
        </svg>
        <div className="score-ring__core">
          <span className="score-ring__value">{valueText ?? safeValue.toFixed(1)}</span>
          <span className="score-ring__label">{label}</span>
        </div>
      </div>
      {caption ? <p className="score-ring__caption">{caption}</p> : null}
    </article>
  );
}
