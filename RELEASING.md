# Releasing

This project builds with `uv` and derives its version from Git using `setuptools-scm`.
Python 3.8 or newer is required. There is no version number to edit in `pyproject.toml`.

## Development

Run `uv sync --group dev` before importing the package from a fresh checkout. The build
generates the Git-ignored `dash_tooltip/_version.py`, used by `dash_tooltip.__version__`.
If that file is missing in an unbuilt checkout, the runtime version is `0+unknown`;
this placeholder does not affect distribution metadata.

Clean `vX.Y.Z` tags produce version `X.Y.Z`. Subsequent commits produce development
versions; local suffixes identify the commit and dirty working tree. Release builds
must come from a clean tagged checkout so they have the exact release version.

## Prepare And Build A Release

1. Commit the release changes and ensure the working tree is clean with `git status`.
2. Fetch Git history and tags with `git fetch --tags` (unshallow the clone if needed).
3. Choose the next release version and create its tag, for example `git tag vX.Y.Z`
   with `X.Y.Z` replaced by the actual version. Do not reuse or move an existing tag.
4. Build from that clean tagged checkout:

```bash
uv build
```

This creates the source distribution and wheel in `dist/`. Check that both have version
`X.Y.Z`, and use a fresh output directory so older artifacts are not published by accident.
Keep the checkout clean between tagging and building; changes to tracked files alter
the inferred version.

The source distribution includes version metadata and the generated version module.
It can be extracted and rebuilt without `.git`, retaining the same version. An arbitrary
source copy without Git or source-distribution metadata fails to build rather than
silently using an invented release version.

## Install A Built Wheel Locally

```bash
uv pip install dist/*.whl
```

## Publish

```bash
uv publish
```

For PyPI uploads, prefer token-based authentication.
Push the release commit and its tag when publishing the release.
