from __future__ import annotations

import json

from click.testing import CliRunner

from uvx_static_assets_test.cli import load_template, main, render_report


runner = CliRunner()


def test_load_template_reads_packaged_asset() -> None:
    """The template should be installed as package data and readable at runtime."""

    template, template_path = load_template()
    assert template_path.name == "message.txt"
    assert "$name" in template.template
    assert "static asset" in template.template


def test_render_report_substitutes_values() -> None:
    """Rendering should replace placeholders with CLI-provided values."""

    result = render_report(
        name="Ada",
        project="asset-demo",
        branch="feature/static-assets",
    )
    assert "Hello, Ada!" in result.rendered
    assert "asset-demo" in result.rendered
    assert "feature/static-assets" in result.rendered
    assert result.template_path.endswith("message.txt")


def test_cli_json_output_includes_resolved_paths() -> None:
    """The CLI should expose the installed asset path when requested."""

    result = runner.invoke(
        main,
        [
            "Ada",
            "--project",
            "asset-demo",
            "--branch",
            "feature/static-assets",
            "--format",
            "json",
            "--show-paths",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "Hello, Ada!" in payload["rendered"]
    assert payload["template_path"].endswith("message.txt")
    assert payload["package_root"].endswith("uvx_static_assets_test")
