# SPDX-License-Identifier: MIT

import hashlib
import os
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import click


class PayloadTargetsHashes(str, Enum):
    """The supported hashes of `TargetsInfo`"""

    # TODO: Update if needed after https://github.com/repository-service-tuf/repository-service-tuf-api/issues/379  # noqa: E501

    blake2b_256 = "blake2b-256"


@dataclass
class TargetsInfo:
    """The target information of `Targets`"""

    # An integer length in bytes
    # https://theupdateframework.github.io/specification/latest/#metapath-length
    length: int
    hashes: Dict[PayloadTargetsHashes, str]
    custom: Optional[Dict[str, Any]]


@dataclass
class Targets:
    """A target of `AddPayload`"""

    info: TargetsInfo
    path: str


@dataclass
class AddPayload:
    """The `POST /api/v1/artifacts/` required payload."""

    targets: List[Targets]
    # Whether to add the id of the task in custom
    add_task_id_to_custom: bool = False
    # Whether to publish the targets
    publish_targets: bool = True

    def to_dict(self):
        return asdict(self)


def calculate_blake2b_256(filepath: str) -> str:
    """
    Calculate the blake2b-256 hash of the given file.

    :param filepath: THe path to the file for which we want to calculate the
    hash.
    """

    # Using default digest size of 32
    hasher = hashlib.blake2b(digest_size=32)

    # 8kB chunk size
    chunk_size_bytes = 8 * 1024

    with open(filepath, "rb") as file:
        # We calculate the hash of the file in chunks as to not load it all
        # at once in memory.
        for chunk in iter(lambda: file.read(chunk_size_bytes), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def create_artifact_payload_from_filepath(
    filepath: str, path: str
) -> Dict[str, Any]:
    """
    Create the payload for the API request of `POST api/v1/artifacts/`.

    :param filepath: The path to the file to be added as an artifact to the
    metadata.
    :param path: The path defined in the metadata for the target.
    """

    length: int = os.path.getsize(filepath)
    blake2b_256_hash: str = calculate_blake2b_256(filepath)

    payload = AddPayload(
        targets=[
            Targets(
                info=TargetsInfo(
                    length=length,
                    hashes={
                        PayloadTargetsHashes.blake2b_256: blake2b_256_hash
                    },
                    custom=None,
                ),
                path=path,
            )
        ]
    )

    return asdict(payload)


def validate_cli_add_artifact_options(
    settings: Dict[str, Any], token: Optional[str], api_url: Optional[str]
) -> None:
    """
    Validate the CLI options that are given for `rstuf artifact add`.
    Updates the `settings` based on the given options.

    :param settings: Settings loaded from RSTUF config file.
    :param token: RSTUF API token.
    :param api_url: RSTUF API server URL.
    :raise click.ClickException: When the passed CLI options are not valid.
    """

    if settings.get("AUTH") is False:

        if token is None:
            raise click.ClickException(
                "Use the built-in authentication (--auth) or provide an RSTUF"
                "API token (-t/--token)."
            )

        else:
            if api_url is None and settings.get("SERVER") is None:
                raise click.ClickException("Provide the --api-url option.")

            # Not writing the info to the actual `.rstuf.ini` file until we
            # define its use besides for the login.
            settings.setdefault("SERVER", api_url)

            # We are not setting `settings["TOKEN"]` to the value of `token`
            # because this token is an admin token. This way we can also
            # differentiate the error messages in :func:`is_logged`.
