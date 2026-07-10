# <img src="https://github.com/dhruvkb/oxc-py/raw/main/readme_assets/logo.png" alt="" align="left" width="40" height="40"> oxc-py

This repo repackages Oxlint and Oxfmt for PyPI, so they can be installed with `uv` or `pipx`.

```bash
uv tool install oxlint
uv tool install oxfmt
```

This repository contains no code, just a workflow that watches Oxc's official releases and, whenever
a newer version than the one on PyPI is released, downloads the release's prebuilt binaries, wraps
each one in a platform-tagged wheel, and publishes it to PyPI.

## How it works

- `scripts/check_versions.py` — finds the latest oxc `apps_*` release, parses the per-tool versions
  from the release title, and compares them against the versions currently on PyPI.
- `scripts/build_wheel.py` — downloads one tool's binary for one target and assembles a wheel with
  the binary placed directly on `PATH`.
- `.github/workflows/release.yml` — runs daily (and on demand), fans out a `{tool} × {platform}`
  build matrix, and publishes any tool that is out of date.

## Supported platforms

| OS            | Architectures |
| ------------- | ------------- |
| macOS         | x86_64, arm64 |
| Linux (glibc) | x86_64, arm64 |
| Linux (musl)  | x86_64, arm64 |
| Windows       | x86_64        |

## Notes

This is not an official distribution. But the process is completely automated and the automation
code is open-source and auditable at [dhruvkb/oxc-py](https://github.com/dhruvkb/oxc-py).
