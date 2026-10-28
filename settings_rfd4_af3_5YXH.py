"""AF3 check of RFD4 designs against the 5YXH target: target template + 5 diffusion samples."""
import runpy
from pathlib import Path
S = runpy.run_path(str(Path(__file__).with_name("settings_server_af3_5YXH.py")))["SETTINGS"]
S["af3_diffusion_samples"] = 5
S["output_dir"] = str(Path.home() / "run_RFD4_5YXH")
SETTINGS = S
