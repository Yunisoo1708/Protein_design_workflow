# Instructions for agents working in this repo

## Rule 1: every design iteration gets logged to the Obsidian vault, before the next one starts

An *iteration* is one run that reached a scoring stage (`score_af2` / `score_af3`) and wrote a `results_*.csv`: a batch of designs, a search,
a re-noising round, a re-fold test. The vault folder `binder-design/` is the user's record of what was tried and what came out.
Do not start the next iteration, and do not delete a run folder, until the previous iteration has a note there.

### The steps

1. **Check the run is complete and valid.** `results_*.csv` exists, the number of rows is the number of designs you meant to score, and job names
   are unique (an earlier run collapsed 50 designs onto 4 names and reported nonsense). If the run is wrong, still log it, with `status: invalid`
   in the properties and the reason under Findings: negative results are data.
2. **Generate the draft notes** (on the machine that has the run; standard library only):
   ```bash
   python log_iteration.py --run <output_dir> --title "<what this iteration was>" --goal "<the question it answers>" \
       --parent <slug of the iteration it follows from> --meta generator="<how designs were made>"
   ```
   `./setup.sh run-rfd4` already does this at its end (title/goal generic). Notes land in `<output_dir>/iteration_note/binder-design/`.
   The script never overwrites an existing note and writes nothing outside that folder.
3. **Write the interpretation** in the iteration note: *Findings*, *Caveats*, *Next step* (and *Lineage* in design notes). Rules:
   - Quote numbers from the *Results* table or `data/<slug>-results.csv`, not from memory. Say what the numbers do **not** show.
   - Compare with the parent iteration (same measures, same cutoffs). Say if the comparison is unfair (different generator, one run, selection among
     candidates).
   - Always name the standing caveats that apply: AF3 guiding and judging the same designs; near-copy designs inflating counts; in silico only, nothing is lab-tested.
   - Never claim binding, never describe a design as "validated". Leave `status: draft`; only the user sets `status: reviewed`.
4. **Copy the notes into the vault without overwriting anything there** (vault on the user's laptop: `C:\Research\llm-wiki`, `/mnt/c/Research/llm-wiki` in WSL):
   ```bash
   wsl.exe -- bash -c 'rsync -av --ignore-existing -e "ssh -o BatchMode=yes" \
       <user>@<server>:<output_dir>/iteration_note/binder-design/ /mnt/c/Research/llm-wiki/binder-design/'
   ```
   If you edited a note after it was already copied, edit the copy in the vault directly (rsync will not replace it).
5. **Rebuild the overview** (`iterations.md`) from the notes' properties:
   ```bash
   wsl.exe -- bash -c 'ssh -o BatchMode=yes <user>@<server> "cat ~/workflows/Protein_design_workflow/log_iteration.py" | python3 - --reindex /mnt/c/Research/llm-wiki'
   ```
6. **Tell the user** which iteration was logged, the slug, and the one-line result, and flag anything you could not verify.

### What goes where
```
binder-design/
  README.md              the process in the user's words (this file's rule 1, short)
  iterations.md          one row per iteration; rebuilt by --reindex, do not edit by hand
  iterations/<slug>.md   what was tried, setup, generated results, findings, caveats, next step, provenance
  designs/<slug>--<job>.md   a passing design (or the top 3 if none passed): sequence, metrics, lineage
  data/<slug>-results.csv    the run's results table, so every number can be re-checked
```
Slug = `<date>-<route>-<n>` unless you pass `--slug`. Link iterations with `--parent`, and designs to their parent design in *Lineage* with `[[wikilinks]]`.

### Do not
- edit the vault's `index.md`, `log.md`, `hermes/`, `concepts/` or `sources/` as part of logging; the user decides whether the hub is linked from `index.md`.
- put credentials, home-directory paths, or weights in a note.
- invent a result, a citation, or a comparison that is not in the run files. If a number is missing, write "not recorded".

## Rule 2: how this repo is used
- `./setup.sh` shows the state of the machine and the next step; `settings.py` is the only settings file (`ROUTE=af2|af3|rfd4_af3`).
- Use a fresh `output_dir` for every run (`OUTPUT_DIR=...`). `design_pipeline.py` records each invocation in `<output_dir>/run_info.json`;
  `./setup.sh run-rfd4` records the generator facts in `run_meta.json`. Those two files are the provenance of a note.
- Run `python tests/test_workflow.py` after code changes. Deleting anything on the remote machine needs the user's explicit approval.
