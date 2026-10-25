# Preprint protocol view: 2026-10-17-nl-band-control

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

All heads in the last quarter of Ouro-2.6B layers, with the original shuffled donor and an independent donor map. Keep the strong shuffled-donor baseline.

This is release documentation for a disclosed subset of a completed experiment. It was prepared after the original experiment and is not a new preregistration. Frozen inputs, inference seeds, model specifications, donor rules and retained per-item observations are supplied with the records. Statistical corrections retain their original factors. No new model evaluation was performed to prepare this release.

Replay from `INPUTS.json` (or `FRESH_INPUTS.json` where the runner uses it) and `CONFIG.json`. Item sets and donor ordering are fixed; do not regenerate inputs from a new sample. Each runner refuses to overwrite existing run outputs. Use `scripts/reset_round.py 2026-10-17-nl-band-control` to preserve shipped results before replay.

Run: `python -m lib.nl_band_control run`.

Analysis: `python -m lib.nl_band_control analyze`. Independent CPU check: `python -m lib.nl_band_control_check`.

`SUMMARY.json` contains the retained contrasts, their original units, intervals and gate outcomes. `INDEPENDENT_CHECK.json` describes the checks that were actually executed on the released records. The release repository does not provide the original chronological Git objects, so the original design-before-results chronology cannot be verified from its initial release commit.
