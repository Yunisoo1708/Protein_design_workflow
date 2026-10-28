# Partial re-noising at three noise levels (0.5, 0.75, 0.9; 17 variants each) -> combine -> convert -> AF3 check -> report and per-noise summary.
P=$HOME/rfd4_runs/5YXH/partial; PD=$HOME/workflows/Protein_design_workflow
cd $P
[ -e $HOME/run_RFD4P_5YXH ] && { echo "run_RFD4P_5YXH exists -> stop"; exit 1; }
for f in 0.5 0.75 0.9; do bash run_partial.sh $f 17 f$f | tail -n 1; done
~/rfd4_venv/bin/python combine.py || { echo "[chain] combine problem -> stop"; exit 1; }
TS=$(~/rfd4_venv/bin/python -c "
import csv,pathlib
print([x for x in csv.DictReader(open(pathlib.Path.home()/'run_5YXH/2_mpnn/sequences.csv'))][0]['target_seq'])")
~/rfd4_venv/bin/python $PD/rfd4_to_af3_jobs.py --rfd4_samples $P/runs/combined/inference_samples --out $HOME/run_RFD4P_5YXH --target_seq "$TS" || { echo "[chain] conversion problem -> stop"; exit 1; }
cd $PD
S=$(date +%s)
~/miniconda3/envs/rfd_bw/bin/python design_pipeline.py --settings settings_rfd4_af3_5YXH.py --output_dir $HOME/run_RFD4P_5YXH --stages af3,score_af3 2>&1 | grep -vE "cuda_executor" | tail -n 4
echo "[chain] AF3_WALL_SECONDS=$(( $(date +%s) - S ))"
~/rfd4_venv/bin/python $PD/rfd4_af3_report.py --run $HOME/run_RFD4P_5YXH | head -n 12
echo "---- by noise level"
~/rfd4_venv/bin/python $P/summarize.py
echo CHAIN_DONE
