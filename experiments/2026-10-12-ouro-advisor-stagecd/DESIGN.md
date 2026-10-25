# Preprint protocol view: 2026-10-12-ouro-advisor-stagecd

Paper: section 3–4, 6; Tables 2, 5, 7 of [paper materials archive](../../paper/updated-CLQ.zip).

Native one-hop/two-hop gate; Q, K and V freezes with matched-size controls; same-example and shuffled late-query rescue at loop 1 and loop 2. Original bootstrap seed and Bonferroni-4 rescue intervals are retained.

This is release documentation for a disclosed subset of a completed experiment. It was prepared after the original experiment and is not a new preregistration. Frozen inputs, inference seeds, model specifications, donor rules and retained per-item observations are supplied with the records. Statistical corrections retain their original factors. No new model evaluation was performed to prepare this release.

Replay from `INPUTS.json` (or `FRESH_INPUTS.json` where the runner uses it) and `CONFIG.json`. Item sets and donor ordering are fixed; do not regenerate inputs from a new sample. Each runner refuses to overwrite existing run outputs. Use `scripts/reset_round.py 2026-10-12-ouro-advisor-stagecd` to preserve shipped results before replay.

Run: `python -m lib.ouro_advisor_stagecd run` with `--model ouro14` and `--model ouro26` in separate processes.

Analysis: `python -m lib.ouro_advisor_stagecd analyze`. Independent CPU check: `python -m lib.ouro_advisor_stagecd_check`.

`SUMMARY.json` contains the retained contrasts, their original units, intervals and gate outcomes. `INDEPENDENT_CHECK.json` describes the checks that were actually executed on the released records. The release repository does not provide the original chronological Git objects, so the original design-before-results chronology cannot be verified from its initial release commit.
