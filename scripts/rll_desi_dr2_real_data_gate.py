#!/usr/bin/env python3
"""Public DESI DR2 source bytes provenance gate. No private data, models, or dependencies."""
import hashlib
import json
import math
import pathlib
import urllib.request
import os

COMMIT = "bb0c1c9009dc76d1391300e169e8df38fd1096db"
BASE = "https://raw.githubusercontent.com/CobayaSampler/bao_data/" + COMMIT + "/desi_bao_dr2/"
ITEMS = {
    "mean": ("desi_gaussian_bao_ALL_GCcomb_mean.txt", "8aff444fdb42c0946342aa0011ab287eda097c4c"),
    "cov": ("desi_gaussian_bao_ALL_GCcomb_cov.txt", "fd8e5697ab61379b07b52efb781ea6713417a4d9"),
}
def get(name, sha):
    with urllib.request.urlopen(BASE + name, timeout=20) as stream:
        if stream.url != BASE + name:
            raise ValueError("source redirect/ref changed")
        content = stream.read(65537)
    if len(content) > 65536 or not content:
        raise ValueError("unexpected size")
    b = hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()
    if b != sha:
        raise ValueError("pinned source blob mismatch")
    return content

def audit(mean, cov):
    m=[]
    for raw in mean.decode("utf-8").splitlines():
        line=raw.strip()
        if not line or line.startswith("#"):continue
        fields=line.split()
        if len(fields)!=3:raise ValueError("mean columns")
        z,v=float(fields[0]),float(fields[1]);kind=fields[2]
        if not(0<z<=5 and v>0 and math.isfinite(z) and math.isfinite(v)) or kind not in {"DV_over_rs","DM_over_rs","DH_over_rs"}:
            raise ValueError("mean domains")
        m.append((z,v,kind))
    if len(m)!=13:raise ValueError("wrong mean dimension")
    rows=[list(map(float,line.split())) for line in cov.decode("utf-8").splitlines() if line.strip() and not line.startswith("#")]
    if len(rows)!=13 or any(len(r)!=13 for r in rows):raise ValueError("wrong covariance dimension")
    lower=[[0.0]*13 for _ in range(13)]
    for i in range(13):
        for j in range(13):
            if not math.isfinite(rows[i][j]) or not math.isclose(rows[i][j],rows[j][i],abs_tol=1e-8):
                raise ValueError("covariance symmetry")
        for j in range(i+1):
            t=rows[i][j]-sum(lower[i][k]*lower[j][k] for k in range(j))
            if i==j:
                if t<=1e-13:raise ValueError("covariance not positive definite")
                lower[i][j]=math.sqrt(t)
            else:lower[i][j]=t/lower[j][j]
    return m,rows

def main():
    mean=get(*ITEMS["mean"])
    cov=get(*ITEMS["cov"])
    m,rows=audit(mean,cov)
    receipt={
        "schema":"rll.desi-dr2.source-gate.v1",
        "source":BASE,
        "source_commit":COMMIT,
        "mean_git_blob":ITEMS["mean"][1],
        "cov_git_blob":ITEMS["cov"][1],
        "mean_sha256":hashlib.sha256(mean).hexdigest(),
        "cov_sha256":hashlib.sha256(cov).hexdigest(),
        "measurements":len(m),
        "covariance_shape":[13,13],
        "covariance_positive_definite":True,
        "data_fetched_live_in_ci":True,
        "model_fitting":"NOT_RUN",
        "science_claim_allowed":False,
        "physical_device_install":"TOKEN_VAZIO_NOT_ATTESTED",
        "rights":"TOKEN_VAZIO_REDISTRIBUTION_LICENSE",
    }
    path=pathlib.Path("artifacts/rll-desi-dr2-source-receipt.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("RLL_REAL_DESI_DR2_DOWNLOAD_PASS points=13 cov=13x13 mean_sha256="+receipt["mean_sha256"]+" cov_sha256="+receipt["cov_sha256"])
if __name__=="__main__":main()
