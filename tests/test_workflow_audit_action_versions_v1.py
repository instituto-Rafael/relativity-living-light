from tools.audit_github_workflows import action_majors, has_checkout_action, has_supported_upload_artifact


def test_upload_artifact_v4_and_newer_are_supported():
    assert has_supported_upload_artifact("uses: actions/upload-artifact@v4\n")
    assert has_supported_upload_artifact("uses: actions/upload-artifact@v7\n")
    assert not has_supported_upload_artifact("uses: actions/upload-artifact@v3\n")


def test_checkout_major_is_detected_independently_of_specific_major():
    assert has_checkout_action("uses: actions/checkout@v4\n")
    assert has_checkout_action("uses: actions/checkout@v7\n")
    assert action_majors("uses: actions/checkout@v7\n", "checkout") == [7]


def test_incidental_text_does_not_count_as_action_reference():
    text = "message: actions/upload-artifact should be used\n"
    assert not has_supported_upload_artifact(text)
