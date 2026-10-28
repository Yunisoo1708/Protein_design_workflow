"""Score every sample of the multi-seed refold: iPTM, binder RMSD to the design (aligned on the target), distance to the hotspot residues."""
import glob, json, pathlib
import gemmi, numpy as np
home = pathlib.Path.home()
design = gemmi.read_structure(str(home/"run_RFD4S_5YXH/1_rfdiffusion/rfd4_8.pdb"))[0]
dt = [r["CA"][0].pos for r in design["A"]]; db = [r["CA"][0].pos for r in design["B"]]
orig = list(range(16, 109)) + list(range(113, 152)); hot = [i for i, o in enumerate(orig) if o in {31, 32, 122, 123}]
def ca(chain): return [r["CA"][0].pos for r in chain if r.find_atom("CA", "*")]
rows = {}
for tag in ("tmpl", "notmpl"):
    out = []
    for d in sorted(glob.glob(str(home/f"rfd4_8_refold/out_{tag}/r8_{tag}/seed-*_sample-*"))):
        m = next(pathlib.Path(d).glob("*model.cif")); s = json.loads(next(pathlib.Path(d).glob("*summary_confidences.json")).read_text())
        mod = gemmi.read_structure(str(m))[0]
        tgt, bnd = ca(mod["B"]), ca(mod["A"])
        if len(tgt) != len(dt) or len(bnd) != len(db): continue
        sup = gemmi.superpose_positions(dt, tgt)
        rm = float(np.sqrt(np.mean([(sup.transform.apply(b) - p).length() ** 2 for b, p in zip(bnd, db)])))
        hat = np.array([a.pos.tolist() for i in hot for a in mod["B"][i]]); bat = np.array([a.pos.tolist() for r in mod["A"] for a in r])
        hd = float(np.sqrt(((hat[:, None] - bat[None]) ** 2).sum(-1)).min())
        out.append((s["iptm"], rm, hd, s["ptm"], s["ranking_score"]))
    rows[tag] = np.array(out)
for tag, a in rows.items():
    if not len(a): print(tag, "no samples"); continue
    iptm, rm, hd = a[:, 0], a[:, 1], a[:, 2]
    ok = (iptm >= 0.8) & (rm <= 2.0)
    print(f"{tag:7s} n={len(a)} | iPTM mean {iptm.mean():.2f} min {iptm.min():.2f} max {iptm.max():.2f} | iPTM>=0.8: {int((iptm>=0.8).sum())}/{len(a)}"
          f" | binder RMSD to design median {np.median(rm):.2f} (min {rm.min():.2f}, max {rm.max():.2f}) | rmsd<=2: {int((rm<=2).sum())}/{len(a)}"
          f" | iPTM>=0.8 & rmsd<=2: {int(ok.sum())}/{len(a)} | hotspot<=4.5A: {int((hd<=4.5).sum())}/{len(a)} (median {np.median(hd):.1f})")
    print("   per-seed best iPTM (first 10 seeds):", " ".join(f"{x:.2f}" for x in iptm.reshape(-1, 5).max(1)[:10]) if len(a) % 5 == 0 else "")
