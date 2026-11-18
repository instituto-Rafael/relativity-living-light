"""Fail-closed fσ8 source parsing and explicit prediction-only semantics."""
import hashlib
import math
from pathlib import Path

import pytest
from scripts.check_rll_growth import build_parser, evaluate_models, read_data


def write_csv(tmp_path, content):
    p=tmp_path/"fsigma8.csv"
    p.write_text(content,encoding="utf-8")
    return p


def test_explicit_missing_file_raises_not_silent_none(tmp_path):
    p=tmp_path/"not_there.csv"
    with pytest.raises(FileNotFoundError,match="FSIGMA8_INPUT_MISSING"):
        read_data(str(p))


def test_prediction_only_input_is_explicit_not_missing():
    assert read_data(None)==[]
    assert read_data("")==[]


@pytest.mark.parametrize("csvtext,reason",[
    ("z,fs8,sigma\n","FSIGMA8_INPUT_NO_DATA_ROWS"),
    ("","FSIGMA8_INPUT_EMPTY"),
    ("z,fs8,sigma\n0.3,0.4,0\n","FSIGMA8_INPUT_INVALID_PHYSICAL_ROW"),
    ("z,fs8,sigma\n0.3,0.4,-0.01\n","FSIGMA8_INPUT_INVALID_PHYSICAL_ROW"),
    ("z,fs8,sigma\n-0.3,0.4,0.01\n","FSIGMA8_INPUT_INVALID_PHYSICAL_ROW"),
    ("z,fs8,sigma\nNaN,0.4,0.01\n","FSIGMA8_INPUT_INVALID_PHYSICAL_ROW"),
    ("z,fs8,sigma\n0.3,inf,0.01\n","FSIGMA8_INPUT_INVALID_PHYSICAL_ROW"),
    ("z,fs8,sigma\n0.3,0.4,nan\n","FSIGMA8_INPUT_INVALID_PHYSICAL_ROW"),
    ("z,fs8,sigma\n0.3,abc,0.01\n","FSIGMA8_INPUT_MALFORMED"),
    ("wrong,columns\n0.3,0.4\n","FSIGMA8_INPUT_MALFORMED"),
])
def test_wrong_observational_csv_fails_closed(tmp_path,csvtext,reason):
    p=write_csv(tmp_path,csvtext)
    with pytest.raises(ValueError,match=reason):
        read_data(str(p))


def test_duplicate_redshift_is_preserved_and_fingerprinted(tmp_path):
    content="z,fs8,sigma,survey\n0.6,0.43,0.04,A\n0.6,0.433,0.067,B\n"
    p=write_csv(tmp_path,content)
    rows=read_data(str(p))
    assert len(rows)==2
    assert rows[0]["z"] == rows[1]["z"]
    args=build_parser().parse_args(["--model","lcdm","--steps","128","--data",str(p)])
    summary,predictions=evaluate_models(args)
    assert summary["models"]["lcdm"]["n_data"]==2
    assert math.isfinite(summary["models"]["lcdm"]["chi2_fsigma8"])
    assert summary["data_policy"]["input_status"]=="PRESENT_VALIDATED"
    assert summary["data_policy"]["input_sha256"]==hashlib.sha256(p.read_bytes()).hexdigest()
    assert summary["data_policy"]["input_row_count"]==2
    assert summary["data_policy"]["claim_allowed"] is False


def test_rejects_silent_grid_extrapolation(tmp_path):
    p=write_csv(tmp_path,"z,fs8,sigma\n1.5,0.4,0.1\n")
    args=build_parser().parse_args(["--model","lcdm","--a-min","0.5","--data",str(p)])
    with pytest.raises(ValueError,match="FSIGMA8_INPUT_OUTSIDE_INTEGRATION_GRID"):
        evaluate_models(args)


def test_checked_in_real_fsigma8_has_positive_errors_and_retains_z_duplicates():
    repo=Path(__file__).resolve().parents[1]
    p=repo/"data/real/cosmology/fsigma8_growth_real.csv"
    rows=read_data(str(p))
    assert len(rows)>=16
    assert all(math.isfinite(x["sigma"]) and x["sigma"]>0 for x in rows)
    assert sum(x["z"]==0.6 for x in rows)>=2
