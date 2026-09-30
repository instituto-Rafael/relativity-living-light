from tools.audit_github_workflows import has_supported_upload_artifact


def test_upload_artifact_v4_is_supported():
    assert has_supported_upload_artifact("uses: actions/upload-artifact@v4")


def test_upload_artifact_newer_major_is_supported():
    assert has_supported_upload_artifact("uses: actions/upload-artifact@v7")


def test_upload_artifact_v3_is_rejected():
    assert not has_supported_upload_artifact("uses: actions/upload-artifact@v3")


def test_unrelated_action_is_rejected():
    assert not has_supported_upload_artifact("uses: actions/checkout@v7")
