# SPDX-License-Identifier: MIT

from click import Context

from repository_service_tuf.cli import click, console
from repository_service_tuf.cli.artifact import artifact
from repository_service_tuf.helpers.api_client import URL, send_payload
from repository_service_tuf.helpers.cli import (
    create_artifact_payload_from_filepath,
    validate_cli_add_artifact_options,
)


@artifact.command()
@click.argument(
    "filepath",
    type=click.Path(exists=True),
    # Currently, this is required. If we support adding artifacts without
    # giving the filepath then we need to set it to `False` and implement our
    # own validation to check whether the argument is needed based on the
    # passed user options.
    required=True,
)
@click.option(
    "--rstuf-server",
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
        "RSTUF API authentication token (required scope: write:targets). If "
        "the `--auth` option is provided this token is not used for "
        "authentication."
    ),
    required=False,
    default=None,
)
@click.option(
    "-p",
    "--path",
    help="A custom path (`TARGETPATH`) for the file, defined in the metadata.",
    type=str,
    required=True,
    default=None,
)
@click.pass_context
def add(
    context: Context, filepath: str, rstuf_server: str, token: str, path: str
) -> str:
    """
    Add artifacts to the metadata (`targets.json`).

    A POST /api/v1/artifacts/ request to the RSTUF API service is carried out,
    where:
    - built-in or token authentication is used
    - file info is discovered and added to the request payload
    - `custom` key of the payload is an empty object
    - `path` key of the payload is defined by the user
    """

    settings = context.obj.get("settings")

    validate_cli_add_artifact_options(
        settings=settings, token=token, rstuf_server=rstuf_server
    )

    payload = create_artifact_payload_from_filepath(
        filepath=filepath, path=path
    )

    task_id = send_payload(
        settings=settings,
        url=URL.artifacts.value,
        payload=payload,
        expected_msg="Target(s) successfully submitted.",
        command_name="Artifact Addition",
    )

    console.print(
        "Successfully submitted task with a payload of:"
        f"\n{payload}"
        f"\nRSTUF task ID (use to check its status) is: {task_id}"
    )

    return task_id
