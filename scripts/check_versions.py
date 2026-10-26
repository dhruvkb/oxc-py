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
RELEASES_URL = "https://api.github.com/repos/oxc-project/oxc/releases?per_page=100"
PYPI_URL = "https://pypi.org/pypi/{project}/json"


def _get_json(url: str) -> Any:
	req = urllib.request.Request(url, headers={"User-Agent": "oxc-py"})
	token = os.environ.get("GITHUB_TOKEN")
	if token and url.startswith("https://api.github.com/"):
		# Unredirected so that the token is not forwarded to another host.
		req.add_unredirected_header("Authorization", f"Bearer {token}")
	with urllib.request.urlopen(req) as resp:
		return json.load(resp)


def tag_version(tool: str, tag: str) -> str | None:
	"""Extract the version from a release tag like ``oxlint_v1.87.0``.

	Tags with a pre-release suffix such as ``oxlint_v2.0.0-rc.1`` are rejected.
	"""
	m = re.fullmatch(rf"{tool}_v(\d+\.\d+\.\d+)", tag)
	return m.group(1) if m else None


def latest_release(tool: str, releases: list[dict]) -> tuple[dict, str] | None:
	for rel in releases:
		if rel.get("draft") or rel.get("prerelease"):
			continue
		version = tag_version(tool, rel.get("tag_name", ""))
		if version:
			return rel, version
	return None


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
	all_releases = _get_json(RELEASES_URL)
	releases: dict[str, dict] = {}
	versions: dict[str, str] = {}
	for tool in TOOLS:
		found = latest_release(tool, all_releases)
		if found is None:
			# Skip rather than fail so that one tool cannot block the other.
			sys.stderr.write(f"warning: no stable {tool}_v* release found\n")
			continue
		releases[tool], versions[tool] = found

	tools_to_build: list[str] = []
	for tool, version in versions.items():
		if needs_publish(pypi_version(tool), version):
			tools_to_build.append(tool)

	outputs = {
		"release_tags": json.dumps(
			{tool: release["tag_name"] for tool, release in releases.items()}
		),
		"tools": json.dumps(tools_to_build),
		"versions": json.dumps(versions),
	}
	gh_output = os.environ.get("GITHUB_OUTPUT")
	for key, value in outputs.items():
		sys.stdout.write(f"{key}={value}\n")
		if gh_output:
			with Path(gh_output).open("a") as fh:
				fh.write(f"{key}={value}\n")


if __name__ == "__main__":
	main()
