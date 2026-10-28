# Fold one design with 20 seeds x 5 samples, with and without the target template (inputs from mk_inputs.py); then run analyze.py.
cd ~/rfd4_8_refold
export CUDA_VISIBLE_DEVICES=0 XLA_PYTHON_CLIENT_PREALLOCATE=false JAX_COMPILATION_CACHE_DIR=$HOME/.cache/jax_af3
for t in tmpl notmpl; do
  S=$(date +%s)
  ~/miniconda3/envs/af3/bin/python ~/tools/alphafold3/run_alphafold.py --input_dir=in_$t --output_dir=out_$t --model_dir=$HOME/af3_models --num_diffusion_samples=5 --flash_attention_implementation=xla --run_data_pipeline=false 2>&1 | grep -v cuda_executor | tail -n 3
  echo "[refold] $t wall $(( $(date +%s) - S ))"
done
echo REFOLD_DONE
