"""Per-noise-level summary of the AF3 check of the partial re-noising variants (joins results_af3.csv with variants.csv from combine.py)."""
import csv, collections, statistics, pathlib
home = pathlib.Path.home()
var = {r["job"]: r for r in csv.DictReader(open(home/"rfd4_runs/5YXH/partial/runs/combined/variants.csv"))}
res = {r["job"]: r for r in csv.DictReader(open(home/"run_RFD4P_5YXH/results_af3.csv"))}
by = collections.defaultdict(list)
for j, r in res.items(): by[var[j]["fraction"]].append((r, var[j]))
print(f"{'noise':>6}{'n':>4}{'PASS':>6}{'iptm>=.8':>9}{'iptm>=.7':>9}{'med iptm':>9}{'med seq id':>11}")
for f in ("0.5", "0.75", "0.9"):
    L = by.get(f, [])
    if not L: continue
    ip = [float(r["iptm"]) for r, _ in L]
    print(f"{f:>6}{len(L):>4}{sum(r['pass']=='PASS' for r,_ in L):>6}{sum(x>=.8 for x in ip):>9}{sum(x>=.7 for x in ip):>9}{statistics.median(ip):>9.2f}{statistics.median(float(v['seq_identity_to_rfd4_8']) for _, v in L):>11.0%}")
print("\nbest 12 by iptm:")
print(f"{'job':9s}{'noise':>6}{'id%':>6}{'len':>4}{'iptm':>6}{'pae':>7}{'plddt_b':>8}{'rmsd':>7}  verdict")
for r, v in sorted(by_all := [(r, var[j]) for j, r in res.items()], key=lambda t: -float(t[0]["iptm"]))[:12]:
    print(f"{r['job']:9s}{v['fraction']:>6}{float(v['seq_identity_to_rfd4_8']):>6.0%}{len(r['binder_seq']):>4}{r['iptm']:>6}{r['pae_interaction']:>7}{r['plddt_binder']:>8}{r['rmsd_binder']:>7}  {r['pass']}")
