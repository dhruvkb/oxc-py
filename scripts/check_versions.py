"""Decide which oxc tools need a fresh PyPI publish."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from packaging.version import Version

TOOLS = ("oxlint", "oxfmt")
RELEASES_URL = "https://api.github.com/repos/oxc-project/oxc/releases?per_page=30"
PYPI_URL = "https://pypi.org/pypi/{project}/json"


def _get_json(url: str) -> Any:
	req = urllib.request.Request(url, headers={"User-Agent": "oxc-py"})
	with urllib.request.urlopen(req) as resp:
		return json.load(resp)


def parse_versions(title: str) -> dict[str, str]:
	"""Extract per-tool versions from a release title.

	Titles look like ``oxlint v1.72.0 & oxfmt v0.57.0``.
	"""
	out: dict[str, str] = {}
	for tool in TOOLS:
		m = re.search(rf"{tool} v(\d+\.\d+\.\d+)", title)
		if m:
			out[tool] = m.group(1)
	return out


def latest_apps_release() -> dict:
	releases = _get_json(RELEASES_URL)
	for rel in releases:
		if rel.get("tag_name", "").startswith("apps_"):
			return rel
	raise RuntimeError("no apps_* release found in latest 30 releases")


def pypi_version(project: str) -> str | None:
	try:
		data = _get_json(PYPI_URL.format(project=project))
	except urllib.error.HTTPError as exc:
		if exc.code == 404:
			return None
		raise
	return data["info"]["version"]


def needs_publish(current: str | None, candidate: str) -> bool:
	if current is None:
		return True
	return Version(candidate) > Version(current)


def main() -> None:
	release = latest_apps_release()
	versions = parse_versions(release["name"])
	tools_to_build: list[str] = []
	for tool, version in versions.items():
		if needs_publish(pypi_version(tool), version):
			tools_to_build.append(tool)

	outputs = {
		"release_tag": release["tag_name"],
		"tools": json.dumps(tools_to_build),
		"versions": json.dumps(versions),
	}
	gh_output = os.environ.get("GITHUB_OUTPUT")
	for key, value in outputs.items():
		sys.stdout.write(f"{key}={value}")
		if gh_output:
			with Path(gh_output).open("a") as fh:
				fh.write(f"{key}={value}\n")


if __name__ == "__main__":
	main()
