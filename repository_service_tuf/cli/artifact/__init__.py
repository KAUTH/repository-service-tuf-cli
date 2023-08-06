# SPDX-License-Identifier: MIT

from repository_service_tuf.cli import rstuf


@rstuf.group()
def artifact():
    """Artifact Management Commands"""
