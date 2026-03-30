# Findings

## Question

Can a Python project be run directly from GitHub with:

`uvx --from "git+https://github.com/owner/repo.git@branch" script-name`

and can that CLI load static assets from the installed package?

## Short answer

Yes. A GitHub-hosted project works with `uvx` when the repo has a valid `pyproject.toml` and a console script entry point. Static assets are available at runtime when they are included as package data and loaded with `importlib.resources`.

## Repo under test

- Repo: `https://github.com/sanand0/uvx-static-assets-test`
- Branch: `main`
- Console script: `uvx-static-assets-test`

## Implementation used for the test

- `pyproject.toml` defines the project and console script.
- `src/uvx_static_assets_test/cli.py` renders a text template.
- `src/uvx_static_assets_test/templates/message.txt` is the packaged asset.
- `tests/test_cli.py` covers asset loading, rendering, and JSON CLI output.

The CLI command shape is:

```bash
uvx-static-assets-test Ada --project asset-demo --branch main --format json --show-paths
```

## Validation

### 1. Tests

Command:

```bash
uv run --group dev pytest
```

Observed result:

```text
3 passed in 0.03s
```

### 2. Build artifact check

Command:

```bash
uv build
```

Observed package contents:

```text
WHEEL uvx_static_assets_test-0.1.0-py3-none-any.whl
  uvx_static_assets_test-0.1.0.dist-info/entry_points.txt
  uvx_static_assets_test/templates/message.txt
SDIST uvx_static_assets_test-0.1.0.tar.gz
  uvx_static_assets_test-0.1.0/pyproject.toml
  uvx_static_assets_test-0.1.0/src/uvx_static_assets_test/templates/message.txt
```

This confirms the template asset is part of both the wheel and source distribution.

One ancillary note: `setuptools` still emitted a non-blocking `sdist: standard file not found` warning because there is no conventional `README`, `README.md`, or similarly named file in the repo. Pointing `readme = "findings.md"` at this document did not affect `uvx`, but it also did not suppress that legacy warning.

### 3. Local `uvx --from .` check

Command:

```bash
uvx --from . uvx-static-assets-test Ada --project asset-demo --branch main --format json --show-paths
```

Observed result:

```json
{
  "rendered": "Hello, Ada!\n\nThis report was rendered for the asset-demo project from the main branch.\nIt proves the CLI can load this packaged text template as a static asset at runtime.\n",
  "template_path": "/home/vscode/.cache/uv/archive-v0/Znt-m3ehLa8JgpvcZ2aVi/lib/python3.14/site-packages/uvx_static_assets_test/templates/message.txt",
  "package_root": "/home/vscode/.cache/uv/archive-v0/Znt-m3ehLa8JgpvcZ2aVi/lib/python3.14/site-packages/uvx_static_assets_test"
}
```

### 4. Remote `uvx --from git+https://github.com/...` check

Command:

```bash
uvx --from "git+https://github.com/sanand0/uvx-static-assets-test.git@main" uvx-static-assets-test Ada --project asset-demo --branch main --format json --show-paths
```

Observed result:

```json
{
  "rendered": "Hello, Ada!\n\nThis report was rendered for the asset-demo project from the main branch.\nIt proves the CLI can load this packaged text template as a static asset at runtime.\n",
  "template_path": "/home/vscode/.cache/uv/archive-v0/Ve8Iqf0mtCT2k2VfTwal3/lib/python3.14/site-packages/uvx_static_assets_test/templates/message.txt",
  "package_root": "/home/vscode/.cache/uv/archive-v0/Ve8Iqf0mtCT2k2VfTwal3/lib/python3.14/site-packages/uvx_static_assets_test"
}
```

The rendered text came from `templates/message.txt`, proving the packaged asset was present and readable inside the `uvx` install created from GitHub.

## What `uvx` actually made available

### Installed package files

After the remote run, the installed package directory contained:

```text
__init__.py
__pycache__/__init__.cpython-314.pyc
__pycache__/cli.cpython-314.pyc
cli.py
templates/message.txt
```

This is the runtime environment used by the command.

### Git checkout cache

`uvx` also kept a cached checkout of the repo at:

`/home/vscode/.cache/uv/git-v0/checkouts/4a4489fe388295f3/aee0cfc`

Top-level contents observed there:

```text
.git/
.gitignore
.ok
build/
prompts.md
pyproject.toml
src/
tests/
uv.lock
```

Important note: `build/` was created by the build step inside the cached checkout; it is not a source file from the repo.

## Conclusion

1. `uvx --from "git+https://github.com/owner/repo.git@branch" script-name` works for this repo.
2. Static assets work when they are packaged and loaded with `importlib.resources`.
3. `uvx` does fetch/check out the full Git repo in its cache.
4. The running CLI does **not** see every repo file in `site-packages`; it sees the built package contents. So static assets must be included as package data if the program needs them at runtime.
5. In practice: if you want a file available to the CLI when installed through `uvx`, put it inside the package and declare it in packaging metadata.

## Final answer

This test confirms that the `uvx` GitHub flow is viable for small Python CLIs with static assets, as long as the assets are packaged correctly.
