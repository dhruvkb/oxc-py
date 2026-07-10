from scripts.check_versions import needs_publish, parse_versions


def test_parse_versions_extracts_both_tools():
	title = "oxlint v1.72.0 & oxfmt v0.57.0"
	assert parse_versions(title) == {"oxlint": "1.72.0", "oxfmt": "0.57.0"}


def test_parse_versions_ignores_unrelated_titles():
	assert parse_versions("oxc crates_v0.138.0") == {}


def test_needs_publish_logic():
	assert needs_publish(None, "1.0.0") is True
	assert needs_publish("1.0.0", "1.0.1") is True
	assert needs_publish("1.0.1", "1.0.1") is False
	assert needs_publish("1.1.0", "1.0.1") is False
