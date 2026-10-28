# RFD4 route: design binders with RFD4-Proteina, check them with AlphaFold 3

RFD4 designs the binder's backbone **and** sequence together (no ProteinMPNN). This folder holds the pieces that were used to run it
on the example target 5YXH and check the designs with the local AlphaFold 3 stages of `design_pipeline.py`.

```
task spec (yaml) ─► [rfd4-generate] ─► designs (CIF) ─► rfd4_to_af3_jobs.py ─► design_pipeline.py --stages af3,score_af3 ─► rfd4_af3_report.py
                    optionally with reward-guided search or partial re-noising
```

## What you need
- RFD4 installed (`rfd4-generate`) and its weights (`nvidia/RFD4-Proteina`, pinned in the commands below by revision). The RFD4 venv used here is a
  `--system-site-packages` venv on top of another conda env, so do not delete that env.
- The `af3` conda env, the AF3 parameters and `settings_server_af3.py` (see the main README). AF3 needs a GPU with compute capability 8.0+.
- A Python with `gemmi` and `numpy` for the converter and report (the RFD4 venv has both).

## Steps
1. **Task spec** (`inputs/spec_5YXH.yaml`): the target is kept exactly (`C_CRD` fixes coordinates, `C_SEQ` fixes sequence), hotspots are set, and the binder is an
   expandable segment (`50-80` residues). The input must be a **CIF** with one chain per contiguous target piece (`inputs/5YXH_split.cif`).
2. **Generate:** `rfd4-generate inputs=spec_5YXH.yaml hf_ckpt_path=nvidia/RFD4-Proteina hf_ckpt_revision=a06e2509c7033b010fc43614e9fd840303588502 num_replicates=50 out_dir=runs/batch50 '~metrics' compile_lengths=null`
   (set `CUDA_VISIBLE_DEVICES`; `HF_HUB_OFFLINE=1` after the first download).
3. **Convert:** `python rfd4_to_af3_jobs.py --rfd4_samples runs/batch50/inference_samples --out ~/run_RFD4 --target_seq <the 132-residue target sequence>`.
   It refuses any design whose target changed, and stops if two designs would get the same job name (the sample folder must end in a unique `_<number>`).
4. **AF3 check:** `python design_pipeline.py --settings settings_rfd4_af3_5YXH.py --stages af3,score_af3` (target template + 5 diffusion samples; `--output_dir` points it at another run).
5. **Report:** `python rfd4_af3_report.py --run ~/run_RFD4`.

## Files
| File | What it does |
|---|---|
| `inputs/spec_5YXH.yaml`, `inputs/5YXH_split.cif` | RFD4 task spec and its input CIF for the example target |
| `search/tiny_search.yaml` | Hydra experiment for **reward-guided beam search**: AF3 pLDDT of the designed chain is scored at steps 30 and 60 and the best candidates continue (beam 2, 2 branches) |
| `search/launch_search50.sh`, `search/select_best.py`, `search/rerun_check.sh` | run the search for 50 designs, keep the best-reward candidate of each design, then convert and check it |
| `shim/apptainer`, `shim/patched_worker.py` | lets RFD4's built-in AF3 oracle run **without Apptainer**: a fake `apptainer` that starts RFD4's AF3 worker with the `af3` conda env (see "The oracle shim") |
| `partial/spec_partial.yaml`, `partial/run_partial.sh` | **partial re-noising**: start from a finished design, add noise to the binder only (`generation.args.partial_trajectory_fraction_steps`), and denoise again to get neighbours |
| `partial/chain_partial.sh`, `partial/combine.py`, `partial/summarize.py`, `partial/cmp.py` | run three noise levels, give every variant a unique name, summarise the AF3 check per noise level, and check a variant against its parent |
| `refold/mk_inputs.py`, `refold/run_all.sh`, `refold/analyze.py` | re-fold one design with many random seeds, with and without the target template, and measure how stable the prediction is |
| `results/*.csv` | AF3 check tables of the example runs |

## The oracle shim (read before relying on it)
RFD4's search scores partly denoised designs with an AF3 "oracle" that is normally run by `apptainer run af3-open.sif python run_alphafold_batch.py ...`.
`shim/apptainer` ignores the container arguments and runs that same script with the `af3` conda env; `shim/patched_worker.py` drops the one argument
(`of3_weights`) that only RFD4's patched AF3 build understands. Put `shim/` first on `PATH` and set `AF3_IMAGE` (any value), `AF3_MODEL_DIR`, `AF3_JAX_CACHE_DIR`
and `AF3_FLASH_ATTENTION_IMPLEMENTATION=xla` (see `search/launch_search50.sh`).
Limits: **stock AF3 only.** OpenFold3 weights need the patched build and are refused. A tokamax autotune error is printed once per run and is harmless (RFD4 falls back to default kernels).
Unset the `AF3_*` variables before running `design_pipeline.py`'s own AF3 stages.

## Results on the example target (5YXH; AF3 + target template, 5 samples per design)
| Run | Designs | Pass | iPTM >= 0.8 | Median iPTM | Max iPTM |
|---|---|---|---|---|---|
| plain RFD4 | 50 | 0 | 0 | 0.15 | 0.51 |
| RFD4 + AF3-pLDDT beam search (best candidate per design) | 50 | 1 | 1 | 0.15 | 0.82 |
| partial re-noising around the passing design (noise 0.5 / 0.75 / 0.9) | 51 | 11 | 13 | 0.61 | 0.86 |

"Pass" = iptm >= 0.8, binder pLDDT >= 80, binder RMSD <= 2.0 A, interface pAE <= 10. The passing design reproduced across 20 random seeds with the template (97/100 samples had iPTM >= 0.8 and binder RMSD <= 2 A)
and fell apart without it (0/100), because AF3 cannot fold this small target alone.

**Read these numbers with care.** The search is guided by AF3 and the final check is AF3 too, so they are not independent. Variants made at low noise are near copies of their parent
(about 90% sequence identity), so their passes are correlated. One run of each; nothing here is lab data.
