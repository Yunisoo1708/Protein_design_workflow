"""Link every variant under a unique p_<k> name and record fraction / source / identity to the original binder."""
import csv, glob, os, pathlib, gemmi
home = pathlib.Path.home(); P = home/"rfd4_runs/5YXH/partial"
ref = gemmi.one_letter_code([r.name for r in gemmi.read_structure(str(P/"rfd4_8_input.cif"))[0]["C"]])
out = P/"runs/combined/inference_samples"; os.makedirs(out, exist_ok=True)
rows, k = [], 0
for frac in ("0.5", "0.75", "0.9"):
    for d in sorted(glob.glob(str(P/f"runs/f{frac}/inference_samples/*")), key=lambda x: int(x.rsplit("_", 1)[1])):
        cif = glob.glob(d + "/*_generated.cif")[0]
        seq = gemmi.one_letter_code([r.name for r in gemmi.read_structure(cif)[0]["C"]])
        ident = sum(a == b for a, b in zip(seq, ref)) / len(ref) if len(seq) == len(ref) else float("nan")
        os.symlink(d, out/f"p_{k}"); rows.append({"job": f"rfd4_{k}", "fraction": frac, "source": os.path.basename(d), "seq_identity_to_rfd4_8": round(ident, 3)}); k += 1
w = csv.DictWriter(open(P/"runs/combined/variants.csv", "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "variants linked")
