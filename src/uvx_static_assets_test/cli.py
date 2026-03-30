from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import as_file, files
import json
from pathlib import Path
from string import Template
import sys

import click


class OutputFormat(StrEnum):
    """Supported response formats."""

    TEXT = "text"
    JSON = "json"


@dataclass(frozen=True, slots=True)
class RenderResult:
    """Rendered template content and the resolved package paths used to build it."""

    rendered: str
    template_path: str
    package_root: str


def template_resource():
    """Return the packaged template resource."""

    return files("uvx_static_assets_test").joinpath("templates/message.txt")


def load_template() -> tuple[Template, Path]:
    """Load the packaged template and resolve it to a concrete filesystem path."""

    with as_file(template_resource()) as template_path:
        return Template(template_path.read_text(encoding="utf-8")), template_path


def render_report(name: str, project: str, branch: str) -> RenderResult:
    """Render the packaged report template with CLI-supplied values."""

    template, template_path = load_template()
    rendered = template.substitute(name=name, project=project, branch=branch)
    return RenderResult(
        rendered=rendered,
        template_path=str(template_path),
        package_root=str(template_path.parent.parent),
    )


def choose_output_format(output_format: OutputFormat | None) -> OutputFormat:
    """Prefer JSON when stdout is piped so agents can parse the response."""

    if output_format is not None:
        return output_format
    return OutputFormat.TEXT if sys.stdout.isatty() else OutputFormat.JSON


def emit(result: RenderResult, *, output_format: OutputFormat, show_paths: bool) -> None:
    """Print the rendered result in text or JSON form."""

    if output_format is OutputFormat.JSON:
        payload = {"rendered": result.rendered}
        if show_paths:
            payload["template_path"] = result.template_path
            payload["package_root"] = result.package_root
        click.echo(json.dumps(payload, indent=2))
        return

    click.echo(result.rendered)
    if show_paths:
        click.echo("")
        click.echo(f"template_path={result.template_path}")
        click.echo(f"package_root={result.package_root}")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("name")
@click.option(
    "--project",
    default="uvx-static-assets-test",
    show_default=True,
    help="Project label to render into the template.",
)
@click.option(
    "--branch",
    default="main",
    show_default=True,
    help="Git branch label to render into the template.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice([item.value for item in OutputFormat], case_sensitive=False),
    help="Output format. Defaults to json when stdout is piped.",
)
@click.option(
    "--show-paths",
    is_flag=True,
    help="Include resolved package and template paths in the response.",
)
def main(
    name: str,
    project: str,
    branch: str,
    output_format: str | None,
    show_paths: bool,
) -> None:
    """Render the packaged text template to prove static assets ship with the CLI."""

    emit(
        render_report(name=name, project=project, branch=branch),
        output_format=choose_output_format(
            OutputFormat(output_format) if output_format else None
        ),
        show_paths=show_paths,
    )


def cli() -> None:
    """Console-script entrypoint."""

    main.main()


if __name__ == "__main__":
    cli()
