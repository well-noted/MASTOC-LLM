# Run Index

Each folder also has a `label` and `description` field written into its `run_meta.json`.

---

## Completed experiments

| Label | Folder | Ticks | Key result |
|---|---|---|---|
| `full-gabm_default` | `20260515_233233_full-gabm` | 120 | 13/13/13 by tick 22, pool 99.4%, inst. score 10/10 |
| `hybrid_1llm` | `20260516_005208_hybrid` | 54 | Collapse tick ~35, LLM powerless alone |
| `hybrid_2llm` | `20260516_011536_hybrid` | 60 | Coalition formed, collapse delayed 35→58 (+66%) |
| `full-gabm_low-cooperation` | `20260516_071509_full-gabm` | 119 | 20/20/20 by tick 16, pool 97.5% — cooperation robust to framing |
| `full-gabm_low-fairness` | `20260516_075015_full-gabm` | 120 | 28/28/28 by tick 107, pool 86.7%, repeated defections |
| `full-gabm_llama3b_normal` | `20260516_083148_full-gabm` | 28 | Pool stable at 99.4%, herds oscillated without converging; message-action disconnect; no institution formation |
| `full-gabm_llama3b_scarce` | `20260516_085639_full-gabm` | 51 | initial-grassland=48; pool 48%→99% by tick 17; herds oscillated without convergence throughout [A0: 4–17, A1: 7–16, A2: 20–25]; no institutional depth |
| `full-gabm_scarce_default-fairness` | `20260516_093606_full-gabm` | 50 | initial-grassland=49; pool 49%→99% by tick 10; converged [11,12,13] by tick 30 — fastest recovery observed |
| `full-gabm_scarce_low-coop-low-fairness` | `20260516_094859_full-gabm` | 50 | initial-grassland=50, coop=0.3, fairness=0; pool 50%→99% by tick 20; converged [12,14,16] by tick 30 |

## Preliminary / unconfirmed

| Label | Folder | Notes |
|---|---|---|
| `hybrid_test_unconfirmed` | `20260516_011105_hybrid` | Hybrid, collapsed tick ~30, params not logged (old bridge) |

---

## To delete (empty/aborted runs)

Delete these folders manually — they contain only empty CSVs:

```
20260516_000107_full-gabm
20260516_004241_hybrid
20260516_004305_hybrid
20260516_005040_hybrid
20260516_005144_hybrid
20260516_065823_full-gabm
20260516_070007_full-gabm   ← Google Gemini, rate-limited after 2 ticks
20260516_070544_full-gabm
20260516_070850_full-gabm
20260516_071220_full-gabm
20260516_083028_full-gabm
```
