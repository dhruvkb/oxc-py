"""Assemble one PyPI wheel from one oxc release binary."""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

TOOLS = ("oxlint", "oxfmt")

TARGETS: dict[str, list[str]] = {
	"x86_64-apple-darwin": ["macosx_10_12_x86_64"],
	"aarch64-apple-darwin": ["macosx_11_0_arm64"],
	# oxc's gnu binaries reference GLIBC_2.18, so 2.18 is the honest floor.
	"x86_64-unknown-linux-gnu": ["manylinux_2_18_x86_64"],
	"aarch64-unknown-linux-gnu": ["manylinux_2_18_aarch64"],
	"x86_64-unknown-linux-musl": ["musllinux_1_2_x86_64"],
	"aarch64-unknown-linux-musl": ["musllinux_1_2_aarch64"],
	"x86_64-pc-windows-msvc": ["win_amd64"],
}

SUMMARIES = {
	"oxlint": "The oxc linter, oxlint, distributed as a PyPI package.",
	"oxfmt": "The oxc formatter, oxfmt, distributed as a PyPI package.",
}


def asset_name(tool: str, target: str) -> str:
	ext = "zip" if "windows" in target else "tar.gz"
	return f"{tool}-{target}.{ext}"


def binary_name(tool: str, target: str) -> str:
	return f"{tool}.exe" if "windows" in target else tool


def download_url(tag: str, asset: str) -> str:
	return f"https://github.com/oxc-project/oxc/releases/download/{tag}/{asset}"


def _fetch(url: str) -> bytes:
	req = urllib.request.Request(url, headers={"User-Agent": "oxc-py"})
	with urllib.request.urlopen(req) as resp:
		return resp.read()


def _extract_binary(blob: bytes, target: str) -> bytes:
	"""Return the sole binary from an oxc release archive.

	Each archive contains exactly one regular file — the binary, named after the
	asset (e.g. ``oxlint-aarch64-apple-darwin``), not after the tool.
	"""
	if "windows" in target:
		with zipfile.ZipFile(io.BytesIO(blob)) as zf:
			member = next(n for n in zf.namelist() if not n.endswith("/"))
			return zf.read(member)
	with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
		member = next(m for m in tf.getmembers() if m.isfile())
		extracted = tf.extractfile(member)
		if extracted is None:
			raise RuntimeError("could not extract binary from archive")
		return extracted.read()


def _read_long_description(tool: str) -> str:
	readme = Path(__file__).parent.parent / "packages" / tool / "README.md"
	return readme.read_text() if readme.exists() else SUMMARIES[tool]


def build(tool: str, version: str, target: str, release_tag: str, outdir: Path) -> Path:
	tags = TARGETS[target]
	bin_name = binary_name(tool, target)
	blob = _fetch(download_url(release_tag, asset_name(tool, target)))
	binary = _extract_binary(blob, target)

	work = outdir / f"_build_{tool}_{target}"
	distinfo = work / f"{tool}-{version}.dist-info"
	scripts = work / f"{tool}-{version}.data" / "scripts"
	distinfo.mkdir(parents=True, exist_ok=True)
	scripts.mkdir(parents=True, exist_ok=True)

	bin_path = scripts / bin_name
	bin_path.write_bytes(binary)
	bin_path.chmod(0o755)

	long_desc = _read_long_description(tool)
	metadata = [
		"Metadata-Version: 2.1",
		f"Name: {tool}",
		f"Version: {version}",
		f"Summary: {SUMMARIES[tool]}",
		"License: MIT",
		"Project-URL: Homepage, https://oxc.rs",
		"Project-URL: Source, https://github.com/oxc-project/oxc",
		"Project-URL: Packaging, https://github.com/dhruvkb/oxc-py",
		"Classifier: License :: OSI Approved :: MIT License",
		"Classifier: Programming Language :: Rust",
		"Classifier: Intended Audience :: Developers",
		"Description-Content-Type: text/markdown",
		"",
		long_desc,
	]
	(distinfo / "METADATA").write_text("\n".join(metadata))

	wheel_lines = [
		"Wheel-Version: 1.0",
		"Generator: oxc-py",
		"Root-Is-Purelib: false",
	]
	wheel_lines += [f"Tag: py3-none-{t}" for t in tags]
	(distinfo / "WHEEL").write_text("\n".join(wheel_lines) + "\n")

	dist = outdir / "dist"
	dist.mkdir(parents=True, exist_ok=True)
	subprocess.run(
		[sys.executable, "-m", "wheel", "pack", str(work), "--dest-dir", str(dist)],
		check=True,
	)
	return sorted(dist.glob(f"{tool}-{version}-*.whl"))[-1]


def main() -> None:
	p = argparse.ArgumentParser()
	p.add_argument("--tool", required=True, choices=TOOLS)
	p.add_argument("--version", required=True)
	p.add_argument("--target", required=True, choices=list(TARGETS))
	p.add_argument("--release-tag", required=True)
	p.add_argument("--outdir", default="build")
	args = p.parse_args()
	path = build(
		args.tool, args.version, args.target, args.release_tag, Path(args.outdir)
	)
	sys.stdout.write(str(path))


if __name__ == "__main__":
	main()
