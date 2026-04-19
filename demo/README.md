# Demo Test Cases

These fixtures are meant for quick local testing through the UI or API.

How to use them:

- paste any `.txt` fixture into the home page
- or upload `sample_script.pdf` to exercise the PDF ingestion path
- use repeated submissions on the same script text to observe exact fingerprint reuse
- submit edited variants under the same `script_id` to inspect history and compare views

Suggested cases:

- `fixtures/sample_script.txt`
  Baseline reveal scene with a strong emotional turn.
- `fixtures/escalation_chain.txt`
  Multi-beat escalation with rising stakes and a strong cliffhanger.
- `fixtures/quiet_confession.txt`
  Low-intensity, dialogue-heavy scene useful for checking pacing and emotional-impact recommendations.
- `fixtures/ensemble_heist.txt`
  Ensemble conflict scene with multiple speakers and operational tension.
- `fixtures/noisy_format_scene.txt`
  Deliberately messy formatting to exercise normalization robustness.
- `fixtures/revision_compare_v1.txt` and `fixtures/revision_compare_v2.txt`
  Paired revision fixtures for testing run history and compare deltas under the same `script_id`.

Suggested local flows:

1. Submit `sample_script.txt` and inspect the baseline dashboard.
2. Submit `quiet_confession.txt` and compare its engagement profile to a higher-tension scene.
3. Submit `noisy_format_scene.txt` and confirm normalization still produces a usable result.
4. Submit `revision_compare_v1.txt`, then resubmit `revision_compare_v2.txt` using the same `script_id` to test history and compare.
5. Submit the same fixture twice unchanged and confirm duplicate execution reuse metadata appears.
