import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from data.pipelines.structure_d import run_all


def test_active_datasets_have_model_mapping_for_classic_profiles():
    cfg_path = REPO_ROOT / "data/pipelines/structure_d/datasets_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    profiles = cfg.get("profiles", {})
    datasets = cfg.get("datasets", {})
    model_coverage = set(run_all.MODEL_BY_DATASET.keys())
    real_profile = run_all.REAL_PROFILE

    missing = []
    for profile_name, profile in profiles.items():
        active = profile.get("active_datasets", [])
        unknown = [dataset_id for dataset_id in active if dataset_id not in datasets]
        assert not unknown, f"profile {profile_name} referencia datasets desconhecidos: {unknown}"

        all_active_real = bool(active) and all(
            datasets[dataset_id].get("dataset_type") == "real_observational"
            for dataset_id in active
        )
        is_dedicated_real = (
            profile.get("real_data_profile") is True
            or profile_name == real_profile
            or profile_name.startswith("structure_d_real_")
            or all_active_real
        )
        if is_dedicated_real:
            continue
        for dataset_id in active:
            if dataset_id not in model_coverage:
                missing.append((profile_name, dataset_id))

    assert not missing, f"datasets sem modelo em profiles clássicos: {missing}"
