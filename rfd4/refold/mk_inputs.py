"""Write two AF3 inputs for one design: seeds 101-120, with and without the target template (run them with run_all.sh)."""
import json, pathlib, copy
home = pathlib.Path.home()
d = json.load(open(home/"run_RFD4S_5YXH/3_af3_inputs/rfd4_8.json"))
for tag, tmpl in (("tmpl", True), ("notmpl", False)):
    x = copy.deepcopy(d); x["name"] = f"r8_{tag}"; x["modelSeeds"] = list(range(101, 121))
    if not tmpl:
        for s in x["sequences"]:
            s["protein"]["templates"] = []
    p = home/"rfd4_8_refold"/f"in_{tag}"; p.mkdir(exist_ok=True)
    json.dump(x, open(p/f"r8_{tag}.json", "w"), indent=1)
