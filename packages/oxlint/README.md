# <img src="https://github.com/dhruvkb/oxc-py/raw/main/readme_assets/logo.png" alt="" align="left" width="40" height="40"> oxlint

[Oxlint](https://oxc.rs/docs/guide/usage/linter) (`/oʊ-ɛks-lɪnt/`) is a high-performance linter for
JavaScript and TypeScript built on the Oxc compiler stack.

This package ships the official prebuilt `oxlint` binary as a PyPI wheel, so you can install it with
any Python package manager:

```bash
uv tool install oxlint
oxlint --help
```

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

For documentation and issues about oxfmt itself, see the
[Oxc project](https://github.com/oxc-project/oxc).
