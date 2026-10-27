"""AF3 settings for the 5YXH target run: the generic AF3 settings + the target template."""
import runpy
from pathlib import Path
S = runpy.run_path(str(Path(__file__).with_name("settings_server_af3.py")))["SETTINGS"]
S["af3_target_template_cif"] = str(Path(__file__).parent / "prepared_protein_structure/5YXH_target_template.cif")
S["output_dir"] = str(Path.home() / "run_5YXH_af3_tmpl")
SETTINGS = S
