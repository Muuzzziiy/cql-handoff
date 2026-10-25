# Preprint protocol view: 2026-10-12-ouro-rescue-audit

Paper: section 4 of [paper materials archive](../../paper/updated-CLQ.zip).

Saved operand-isolation diagnostics and the replication on 300 new Ouro-2.6B scenes. Final-position query patches keep all other positions unchanged. The archived factor controls use the original same-scene inputs.

This is release documentation for a disclosed subset of a completed experiment. It was prepared after the original experiment and is not a new preregistration. Frozen inputs, inference seeds, model specifications, donor rules and retained per-item observations are supplied with the records. Statistical corrections retain their original factors. No new model evaluation was performed to prepare this release.

Replay from `INPUTS.json` (or `FRESH_INPUTS.json` where the runner uses it) and `CONFIG.json`. Item sets and donor ordering are fixed; do not regenerate inputs from a new sample. Each runner refuses to overwrite existing run outputs. Use `scripts/reset_round.py 2026-10-12-ouro-rescue-audit` to preserve shipped results before replay.

Run: `python -m lib.ouro_rescue_audit run` with `--model ouro14` and `--model ouro26` in separate processes.

Analysis: `python -m lib.ouro_rescue_audit analyze`. Independent CPU check: `python -m lib.ouro_rescue_audit_check`.

`SUMMARY.json` contains the retained contrasts, their original units, intervals and gate outcomes. `INDEPENDENT_CHECK.json` describes the checks that were actually executed on the released records. The release repository does not provide the original chronological Git objects, so the original design-before-results chronology cannot be verified from its initial release commit.
