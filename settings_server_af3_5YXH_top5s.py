"""5YXH, AF3 + target template, 5 diffusion samples per design (for re-checking a short list)."""
import runpy
from pathlib import Path
S = runpy.run_path(str(Path(__file__).with_name("settings_server_af3_5YXH.py")))["SETTINGS"]
S["af3_diffusion_samples"] = 5
S["output_dir"] = str(Path.home() / "run_5YXH_af3_top5s")
SETTINGS = S
