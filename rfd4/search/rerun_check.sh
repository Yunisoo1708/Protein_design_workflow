# Re-run only the selection, conversion, AF3 check and report on a finished search (runs/search50).
W=$HOME/rfd4_runs/5YXH
PD=$HOME/workflows/Protein_design_workflow
~/rfd4_venv/bin/python $W/select_best.py $W/runs/search50 $W/runs/search50_best || { echo "[chain] select problem -> stop"; exit 1; }
TS=$(~/rfd4_venv/bin/python -c "
import csv,pathlib
print([x for x in csv.DictReader(open(pathlib.Path.home()/'run_5YXH/2_mpnn/sequences.csv'))][0]['target_seq'])")
~/rfd4_venv/bin/python $PD/rfd4_to_af3_jobs.py --rfd4_samples $W/runs/search50_best/inference_samples --out $HOME/run_RFD4S_5YXH --target_seq "$TS" || { echo "[chain] conversion problem -> stop"; exit 1; }
echo "[chain] pdbs: $(ls $HOME/run_RFD4S_5YXH/1_rfdiffusion | wc -l)"
cd $PD
S=$(date +%s)
~/miniconda3/envs/rfd_bw/bin/python design_pipeline.py --settings settings_rfd4_af3_5YXH.py --output_dir $HOME/run_RFD4S_5YXH --stages af3,score_af3 2>&1 | grep -vE "cuda_executor" | tail -n 70
echo "[chain] AF3_WALL_SECONDS=$(( $(date +%s) - S ))"
~/rfd4_venv/bin/python $PD/rfd4_af3_report.py --run $HOME/run_RFD4S_5YXH
echo CHAIN_DONE
