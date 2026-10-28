# usage: run_partial.sh FRACTION REPLICATES OUTNAME -- RFD4 partial re-noising of the binder in spec_partial.yaml (higher FRACTION = more noise).
# usage: run_partial.sh FRACTION REPLICATES OUTNAME
P=$HOME/rfd4_runs/5YXH/partial
cd $P
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1
rm -rf $P/runs/$3
~/rfd4_venv/bin/rfd4-generate inputs=$P/spec_partial.yaml hf_ckpt_path=nvidia/RFD4-Proteina hf_ckpt_revision=a06e2509c7033b010fc43614e9fd840303588502 num_replicates=$2 out_dir=$P/runs/$3 '~metrics' compile_lengths=null generation.args.partial_trajectory_fraction_steps=$1 > $P/$3.log 2>&1
echo "EXIT=$? $3"
