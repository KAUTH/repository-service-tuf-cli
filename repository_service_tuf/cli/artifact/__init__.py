# SPDX-License-Identifier: MIT

from typing import Optional

from click import Context

from repository_service_tuf.cli import click, rstuf


@rstuf.group()
@click.option(
    "--api-url",
    help=(
        "RSTUF API Server address. Not required if the `--auth` option is "
        "passed."
    ),
    required=False,
    default=None,
)
@click.option(
    "-t",
    "--token",
    help=(
        "RSTUF API authentication token. If the `--auth` option is provided"
        "this token is not used for authentication."
    ),
    required=False,
    default=None,
)
@click.pass_context
def artifact(context: Context, api_url: Optional[str], token: Optional[str]):
    """Artifact Management Commands"""

    context.obj["api_url"] = api_url
    context.obj["token"] = token
