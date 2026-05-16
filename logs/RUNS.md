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

## Preliminary / unconfirmed

| Label | Folder | Notes |
|---|---|---|
| `hybrid_test_unconfirmed` | `20260516_011105_hybrid` | Hybrid, collapsed tick ~30, params not logged (old bridge) |
| `full-gabm_llama3b_preliminary` | `20260516_083148_full-gabm` | 4 ticks only — Llama 3.2 3B test |

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
