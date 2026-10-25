# Preprint clarifications

These notes accompany the October 2026 [preprint materials](paper/updated-CLQ.zip). They describe the method used for the released observations and clarify numerical presentation. The bundled manuscript incorporates these clarifications as of October 25, 2026. Research code, frozen inputs and experimental records are unchanged; no new model evaluation was performed for this manuscript update.

## Experiment locations

The [README experiment table](README.md#replaying-a-round), [PUBLIC_SCOPE.json](PUBLIC_SCOPE.json), and the paper references in each round's DESIGN and RESULTS files use the current manuscript numbering: query rescue in Section 4, crossed swaps in Section 5, the converse test in Section 5.1, and freezes and matched controls in Section 6. Native accuracy is in Appendix C, Table 7. Natural QA and format/scale boundaries remain in Sections 7 and 8.

## Donor rules and positional alignment

### Synthetic query rescue

Shuffled donors are drawn from other targets with the same prompt token length. The donor's late query is supplied at the corresponding layer, head and final prompt position. The primary setting uses donor loop 3 and recipient loop 1; the patch supplies a layer-indexed collection of queries throughout the recipient stack.

### Natural-QA rescue

The initial rescue, the 1.4B boundary experiment, and the fresh replication use seeded permutations of the target set with no item assigned to itself. These permutations are not restricted to equal prompt lengths. The late-layer band control also uses stored and independently seeded donor maps without length matching.

For each transferred query, the implementation aligns the donor's post-RoPE query to the recipient's final prompt position. If the prompt token lengths are `L_recipient` and `L_donor`, it applies the rotary offset `delta = L_recipient - L_donor` before patching. The same-item arm has zero offset. This alignment is performed separately for the cached query at each layer and head.

The manuscript now explicitly distinguishes the same-length synthetic query-rescue control from the different-length, position-aligned natural-QA control described here.

The relevant implementations are [natural_scoring.py](lib/natural_scoring.py), [nl_ouro14_boundary.py](lib/nl_ouro14_boundary.py), [nl_fresh_replication.py](lib/nl_fresh_replication.py), [nl_band_control.py](lib/nl_band_control.py), and the [rotary alignment helper](lib/rotary.py).

Natural-QA crossed swaps use the donor and unrelated-item pairings stored in the frozen inputs, with the same rotary position-alignment operation; see [nl_crossover.py](lib/nl_crossover.py). Their reported null redirection conclusion is unchanged.

## Numerical display and interval annotations

### Table 5: matched-size key control in Ouro-1.4B

The earlier manuscript displayed the retained loop gain for `C_K` as `0.97`; the current archive corrects this display to `0.96`. The saved observations give 233/400 correct at native loop 1, 375/400 at native loop 3, and 370/400 at loop 3 under `C_K`. Thus:

```text
rho_CK = (370 - 233) / (375 - 233) = 137 / 142 = 0.9647887324...
```

The current manuscript displays **0.96** and the matched-control range **0.96–1.04**. The stored summary value is approximately `0.9647887297` because its denominator includes a numerical epsilon. This presentation correction does not change the underlying observations or the conclusion that the matched-size controls largely retain the loop gain.

### Table 6: fresh-replication intervals

Both fresh-replication contrasts, all layers (`R1`) and last-quarter layers (`R2`), use Bonferroni correction over two primary tests. Their paired bootstrap intervals use 20,000 resamples and quantiles `0.0125` and `0.9875`. The table retains these corrected intervals for both replication rows; its caption now explicitly identifies both replication rows as Bonferroni-corrected. The initial all-layer and last-quarter rescue rows use their reported uncorrected 95% intervals. See [nl_fresh_replication.py](lib/nl_fresh_replication.py).

## Verification scope

CPU record checks and statistical recomputation have passed for the 21 released rounds. They check saved observations and analyses; they do not constitute new model inference. A complete rerun of this release in a clean GPU environment has not been verified.

The release supports replaying the shipped frozen inputs with the published inference runners. The historical campaigns that generated all inputs are not included. Follow the [installation and replay instructions](README.md#setup), preserve the shipped outputs with the reset helper, and compare newly generated observations with the saved results.
