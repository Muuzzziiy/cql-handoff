# Preprint protocol view: 2026-10-12-ouro26-natural-rescue-fc-powered

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

The frozen 1,105-item natural QA set, candidate ranking, target screen, same-item query, shuffled donor and same-loop donor. Gold answer is candidate zero; candidates use length-normalized log-likelihood.

This is release documentation for a disclosed subset of a completed experiment. It was prepared after the original experiment and is not a new preregistration. Frozen inputs, inference seeds, model specifications, donor rules and retained per-item observations are supplied with the records. Statistical corrections retain their original factors. No new model evaluation was performed to prepare this release.

Replay from `INPUTS.json` (or `FRESH_INPUTS.json` where the runner uses it) and `CONFIG.json`. Item sets and donor ordering are fixed; do not regenerate inputs from a new sample. Each runner refuses to overwrite existing run outputs. Use `scripts/reset_round.py 2026-10-12-ouro26-natural-rescue-fc-powered` to preserve shipped results before replay.

Run: `python -m lib.ouro_natural_rescue_fc2 run`.

Analysis: `python -m lib.ouro_natural_rescue_fc2 analyze`. Independent CPU check: `python -m lib.ouro_natural_rescue_fc2_check`.

`SUMMARY.json` contains the retained contrasts, their original units, intervals and gate outcomes. `INDEPENDENT_CHECK.json` describes the checks that were actually executed on the released records. The release repository does not provide the original chronological Git objects, so the original design-before-results chronology cannot be verified from its initial release commit.
