"""Settings for the GPU server with LOCAL AlphaFold 3 as the structure-check step.
Run:  ~/miniconda3/envs/rfd_bw/bin/python design_pipeline.py --settings settings_server_af3.py --stages rfd,mpnn,af3,score_af3
(Same as settings_server.py for RFdiffusion + ProteinMPNN; only step 3 differs.)"""
from pathlib import Path

HOME = Path.home()
ENVS = HOME / "miniconda3/envs"
TOOLS = HOME / "tools"

# GPU 0 = RTX 5060 Ti (16 GB, fast, new)   GPU 1 = GTX 1660 SUPER (6 GB, slower, older)
RFD_PY = str(ENVS / "rfd_bw/bin/python")
MPNN_PY = str(ENVS / "rfdiffusion/bin/python")

SETTINGS = {
    "target_pdb": str(TOOLS / "RFdiffusion/examples/input_pdbs/insulin_target.pdb"),
    "target_range": "A1-150",
    "hotspots": "A59,A83,A91",
    "binder_length": "50-60",
    "num_backbones": 4,
    "seqs_per_backbone": 4,
    "rfd_noise": 0,
    "output_dir": str(HOME / "real_run_af3"),

    "rfdiffusion_cmd": [RFD_PY, str(TOOLS / "RFdiffusion/scripts/run_inference.py")],
    "rfdiffusion_env": {"CUDA_VISIBLE_DEVICES": "0"},
    "mpnn_cmd": [MPNN_PY, str(TOOLS / "ProteinMPNN/protein_mpnn_run.py")],
    "mpnn_env": {"CUDA_VISIBLE_DEVICES": "1"},

    # ---- Step 3: AlphaFold 3, run locally (google-deepmind/alphafold3, env "af3") ----
    "af3_cmd": [str(ENVS / "af3/bin/python"), str(TOOLS / "alphafold3/run_alphafold.py")],
    # AF3 needs compute capability >= 8.0: ONLY the 5060 Ti (GPU 0). The GTX 1660 (7.5) cannot run it.
    "af3_env": {"CUDA_VISIBLE_DEVICES": "0",
                "JAX_COMPILATION_CACHE_DIR": str(HOME / ".cache/jax_af3")},
    # Folder with the AF3 model parameters (af3.bin.zst). You must request these from Google and accept
    # their terms yourself; they are not part of the code repository.
    "af3_model_dir": str(HOME / "af3_models"),
    # None = no genetic databases: each chain from its single sequence (fast, no 630 GB download, but the target
    # is predicted less reliably). Or give the folder made by ~/tools/alphafold3/fetch_databases.sh.
    "af3_db_dir": None,
    "af3_diffusion_samples": 1,        # AF3 default is 5; 1 is much faster, raise it for the final shortlist
    "af3_flash_attention": "xla",      # "triton" is faster but may not support the Blackwell card; "xla" is safe
    "af3_seed": 1,

    # What counts as a good design (rules of thumb).
    "min_iptm": 0.8, "min_plddt": 80, "max_rmsd": 2.0, "max_pae_interaction": 10,
}
