# Findings

## Goal

Build the smallest practical proof that this works:

```bash
uvx --from "git+https://github.com/owner/repo.git@branch" script-name
```

while still letting the program load a static text asset.

## Final repo shape

Committed top-level files used for the proof:

```text
.gitignore
findings.md
main.py
messages.txt
prompts.md
pyproject.toml
uv.lock
```

Notably, there is:

- no `src/` directory
- no package directory
- no tests
- no runtime dependency other than the Python standard library

## Minimal implementation

### `main.py`

This is the entire program:

```python
from pathlib import Path; import sys
def main():
    p = Path(sys.prefix) / "messages.txt"; print(p.read_text().format(name=sys.argv[1]), end=""); print(p)
if __name__ == "__main__": main()
```

### `messages.txt`

```text
Hello, {name}!
```

## Packaging setup

The important part of `pyproject.toml` is:

```toml
[project.scripts]
uvx-static-assets-test = "main:main"

[tool.setuptools]
py-modules = ["main"]

[tool.setuptools.data-files]
"." = ["messages.txt"]
```

This makes the single root Python file importable as `main` and installs the root `messages.txt` into the `uvx` environment root.

## Validation

### 1. Build

Command:

```bash
uv build
```

Observed wheel contents:

```text
main.py
uvx_static_assets_test-0.1.0.data/data/messages.txt
uvx_static_assets_test-0.1.0.dist-info/entry_points.txt
```

Observed sdist contents:

```text
uvx_static_assets_test-0.1.0/main.py
uvx_static_assets_test-0.1.0/messages.txt
uvx_static_assets_test-0.1.0/pyproject.toml
```

That is the key proof that the root `messages.txt` is shipped.

### 2. Local `uvx --from .`

Command:

```bash
uvx --from . uvx-static-assets-test Ada
```

Observed output:

```text
Hello, Ada!
/home/vscode/.cache/uv/archive-v0/<cache-id>/messages.txt
```

This proves the installed command can read the asset from the `uvx` environment, not from the source checkout.

### 3. Remote `uvx --from git+https://github.com/...`

Command:

```bash
uvx --refresh --from "git+https://github.com/sanand0/uvx-static-assets-test.git@main" uvx-static-assets-test Ada
```

Observed output:

```text
Hello, Ada!
/home/vscode/.cache/uv/archive-v0/<cache-id>/messages.txt
```

This proves the GitHub-hosted repo works with `uvx`, and that the asset is accessible after installation.

## What `uvx` did behind the scenes

`uvx` kept a cached git checkout under a path like:

`/home/vscode/.cache/uv/git-v0/checkouts/<repo-id>/<commit>`

Top-level contents observed there:

```text
.git/
.gitignore
.ok
build/
findings.md
main.py
messages.txt
prompts.md
pyproject.toml
uv.lock
uvx_static_assets_test.egg-info/
```

Important note: `build/` and `uvx_static_assets_test.egg-info/` were created during the package build inside the cache. They are not part of the committed minimal source layout.

The exact cache IDs and checkout commit directories vary from run to run, but the structure above is what was observed.

## Conclusion

Yes, the smallest practical proof of concept works.

The repo can be reduced to:

- one Python script at the repo root
- one `messages.txt` at the repo root
- `pyproject.toml` plus the requested supporting files

And the command still works:

```bash
uvx --from "git+https://github.com/sanand0/uvx-static-assets-test.git@main" uvx-static-assets-test Ada
```

The important packaging detail is that the asset must be explicitly installed. In this minimal version, that is done with setuptools `data-files`, and the script reads the file from `sys.prefix / "messages.txt"`.

## Small caveat

`uv build` still emits a non-blocking setuptools warning about the lack of a conventional `README` file. That warning does not affect the `uvx` result.
