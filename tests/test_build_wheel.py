import io
import tarfile

from scripts.build_wheel import (
	_extract_binary,
	asset_name,
	binary_name,
	download_url,
)


def test_extract_binary_returns_sole_file_from_tarball():
	buf = io.BytesIO()
	payload = b"\x7fELF fake binary"
	with tarfile.open(fileobj=buf, mode="w:gz") as tf:
		info = tarfile.TarInfo(name="oxlint-x86_64-unknown-linux-gnu")
		info.size = len(payload)
		tf.addfile(info, io.BytesIO(payload))
	assert _extract_binary(buf.getvalue(), "x86_64-unknown-linux-gnu") == payload


def test_asset_name_unix_and_windows():
	assert (
		asset_name("oxlint", "x86_64-apple-darwin")
		== "oxlint-x86_64-apple-darwin.tar.gz"
	)
	assert (
		asset_name("oxfmt", "x86_64-pc-windows-msvc")
		== "oxfmt-x86_64-pc-windows-msvc.zip"
	)


def test_binary_name_adds_exe_on_windows():
	assert binary_name("oxlint", "x86_64-unknown-linux-gnu") == "oxlint"
	assert binary_name("oxlint", "x86_64-pc-windows-msvc") == "oxlint.exe"


def test_download_url():
	assert download_url("apps_v1.72.0", "oxlint-x86_64-apple-darwin.tar.gz") == (
		"https://github.com/oxc-project/oxc/releases/download/"
		"apps_v1.72.0/oxlint-x86_64-apple-darwin.tar.gz"
	)
