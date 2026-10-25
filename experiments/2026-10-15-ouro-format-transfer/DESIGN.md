# Preprint protocol view: 2026-10-15-ouro-format-transfer

Paper: section 8 of [paper materials archive](../../paper/updated-CLQ.zip).

Gate and all-head rescue for lockers, rooms, cars and story formats. Donor prompts have the same token length.

This is release documentation for a disclosed subset of a completed experiment. It was prepared after the original experiment and is not a new preregistration. Frozen inputs, inference seeds, model specifications, donor rules and retained per-item observations are supplied with the records. Statistical corrections retain their original factors. No new model evaluation was performed to prepare this release.

Replay from `INPUTS.json` (or `FRESH_INPUTS.json` where the runner uses it) and `CONFIG.json`. Item sets and donor ordering are fixed; do not regenerate inputs from a new sample. Each runner refuses to overwrite existing run outputs. Use `scripts/reset_round.py 2026-10-15-ouro-format-transfer` to preserve shipped results before replay.

Run: `python -m lib.ouro_format_transfer run` with `--model ouro14` and `--model ouro26` in separate processes.

Analysis: `python -m lib.ouro_format_transfer analyze`. Independent CPU check: `python -m lib.ouro_format_transfer_check`.

`SUMMARY.json` contains the retained contrasts, their original units, intervals and gate outcomes. `INDEPENDENT_CHECK.json` describes the checks that were actually executed on the released records. The release repository does not provide the original chronological Git objects, so the original design-before-results chronology cannot be verified from its initial release commit.
