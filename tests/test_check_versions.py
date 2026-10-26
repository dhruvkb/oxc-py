from scripts.check_versions import latest_release, needs_publish, tag_version


def test_tag_version_extracts_version():
	assert tag_version("oxlint", "oxlint_v1.87.0") == "1.87.0"
	assert tag_version("oxfmt", "oxfmt_v0.72.0") == "0.72.0"


def test_tag_version_rejects_other_tags():
	assert tag_version("oxlint", "oxfmt_v0.72.0") is None
	assert tag_version("oxlint", "crates_v0.138.0") is None
	assert tag_version("oxlint", "oxlint_v2.0.0-rc.1") is None


def test_latest_release_skips_drafts_and_prereleases():
	releases = [
		{"tag_name": "oxlint_v2.0.0", "draft": True},
		{"tag_name": "oxlint_v1.99.0", "prerelease": True},
		{"tag_name": "crates_v0.138.0"},
		{"tag_name": "oxlint_v1.87.0"},
	]
	assert latest_release("oxlint", releases) == (releases[3], "1.87.0")


def test_latest_release_returns_none_when_missing():
	assert latest_release("oxfmt", [{"tag_name": "oxlint_v1.87.0"}]) is None


def test_needs_publish_logic():
	assert needs_publish(None, "1.0.0") is True
	assert needs_publish("1.0.0", "1.0.1") is True
	assert needs_publish("1.0.1", "1.0.1") is False
	assert needs_publish("1.1.0", "1.0.1") is False
