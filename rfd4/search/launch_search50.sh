# RFD4 reward-guided beam search for 50 designs (AF3 pLDDT reward via the shim), then: pick the best candidate per design -> convert -> AF3 check -> report.
# Needs shim/ and tiny_search.yaml installed (see rfd4/README.md); about 2.5 h for 50 designs on one RTX 5060 Ti.
W=$HOME/rfd4_runs/5YXH
PD=$HOME/workflows/Protein_design_workflow
export PATH=$HOME/shim:$PATH AF3_IMAGE=dummy.sif AF3_JAX_CACHE_DIR=$HOME/.cache/jax_af3 AF3_MODEL_DIR=$HOME/af3_models AF3_FLASH_ATTENTION_IMPLEMENTATION=xla
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1
[ -e $W/runs/search50 ] && { echo "search50 exists -> stop"; exit 1; }
[ -e $HOME/run_RFD4S_5YXH ] && { echo "run_RFD4S_5YXH exists -> stop"; exit 1; }
S=$(date +%s)
~/rfd4_venv/bin/rfd4-generate inference_experiment=tiny_search inputs=$W/spec_5YXH.yaml hf_ckpt_path=nvidia/RFD4-Proteina hf_ckpt_revision=a06e2509c7033b010fc43614e9fd840303588502 num_replicates=50 out_dir=$W/runs/search50 compile_lengths=null "hydra.searchpath=[file://$HOME/rfd4_cfg]" > $W/search50.log 2>&1
echo "[chain] SEARCH_EXIT=$? WALL=$(( $(date +%s) - S ))"
~/rfd4_venv/bin/python $W/select_best.py $W/runs/search50 $W/runs/search50_best || { echo "[chain] select problem -> stop"; exit 1; }
TS=$(~/rfd4_venv/bin/python -c "
import csv,pathlib
print([x for x in csv.DictReader(open(pathlib.Path.home()/'run_5YXH/2_mpnn/sequences.csv'))][0]['target_seq'])")
~/rfd4_venv/bin/python $PD/rfd4_to_af3_jobs.py --rfd4_samples $W/runs/search50_best/inference_samples --out $HOME/run_RFD4S_5YXH --target_seq "$TS" || { echo "[chain] conversion problem -> stop"; exit 1; }
cd $PD
S=$(date +%s)
unset AF3_IMAGE AF3_MODEL_DIR AF3_JAX_CACHE_DIR AF3_FLASH_ATTENTION_IMPLEMENTATION
~/miniconda3/envs/rfd_bw/bin/python design_pipeline.py --settings settings_rfd4_af3_5YXH.py --output_dir $HOME/run_RFD4S_5YXH --stages af3,score_af3 2>&1 | grep -vE "cuda_executor" | tail -n 70
echo "[chain] AF3_WALL_SECONDS=$(( $(date +%s) - S ))"
~/rfd4_venv/bin/python $PD/rfd4_af3_report.py --run $HOME/run_RFD4S_5YXH
echo CHAIN_DONE
