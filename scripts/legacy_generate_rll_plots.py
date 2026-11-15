#!/usr/bin/env python3
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

def main():
 root=Path('artifacts/rll-real-run'); plots=root/'plots'; plots.mkdir(parents=True,exist_ok=True); tables=root/'tables'
 hz=tables/'Hz_processed.csv'; bao=tables/'BAO_processed.csv'; mc=tables/'model_comparison.csv'; comp=tables/'rll_components.csv'; src=root/'raw'/'SOURCES.json'
 if hz.exists():
  d=pd.read_csv(hz); plt.figure(); plt.plot(d['z'],d['H_z']); plt.title('Hz curve'); plt.savefig(plots/'Hz_curve.png'); plt.close()
 else:
  plt.figure(); plt.text(0.2,0.5,'pending_data'); plt.savefig(plots/'Hz_curve.png'); plt.close()
 if bao.exists():
  d=pd.read_csv(bao); plt.figure(); plt.plot(d['z'],d['bao_obs'],label='obs'); plt.plot(d['z'],d['bao_rll'],label='rll'); plt.legend(); plt.savefig(plots/'BAO_comparison.png'); plt.close()
 if mc.exists():
  d=pd.read_csv(mc); plt.figure(); plt.bar(d['model'],d['chi2']); plt.savefig(plots/'chi2_barplot.png'); plt.close()
 if comp.exists():
  d=pd.read_csv(comp); plt.figure(); plt.plot(d['a'],d['E2_matter'],label='matter'); plt.plot(d['a'],d['E2_de'],label='de'); plt.legend(); plt.savefig(plots/'rll_components.png'); plt.close()
 if src.exists():
  s=json.loads(src.read_text()); st={}
  for x in s: st[x['status']]=st.get(x['status'],0)+1
  plt.figure(); plt.bar(list(st.keys()),list(st.values())); plt.xticks(rotation=25,ha='right'); plt.tight_layout(); plt.savefig(plots/'data_sources_status.png'); plt.close()
 return 0
if __name__=='__main__': raise SystemExit(main())
