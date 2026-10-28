"""Check variants against their parent input: target unchanged? how far did the binder move (CA RMSD, sequence identity)? usage: cmp.py 'runs/x/inference_samples/*/*_generated.cif'"""
import glob, sys, gemmi, numpy as np
ref = gemmi.read_structure("rfd4_8_input.cif")[0]
def seq(c): return gemmi.one_letter_code([r.name for r in c])
def ca(c): return [r["CA"][0].pos for r in c]
for f in sorted(glob.glob(sys.argv[1])):
    m = gemmi.read_structure(f)[0]
    ch = {c.name: c for c in m}
    if [c.name for c in m] != ["A", "B", "C"] or any(len(ch[k]) != len(ref[k]) for k in "ABC"):
        print(f.split("/")[-2], "chains/lengths differ:", [(c.name, len(c)) for c in m]); continue
    tsame = seq(ch["A"]) == seq(ref["A"]) and seq(ch["B"]) == seq(ref["B"])
    tr = np.sqrt(np.mean([(a - b).length() ** 2 for k in "AB" for a, b in zip(ca(ch[k]), ca(ref[k]))]))
    sup = gemmi.superpose_positions(ca(ref["C"]), ca(ch["C"]))
    ident = np.mean([a == b for a, b in zip(seq(ch["C"]), seq(ref["C"]))])
    print(f.split("/")[-2], f"target seq same: {tsame}, target CA rmsd {tr:.3f} | binder len {len(ch['C'])}, binder CA rmsd (own superposition) {sup.rmsd:.2f}, seq identity {ident:.0%}")
