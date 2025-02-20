# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for custom UltraViolet commands."""

from invenio_app.factory import create_app

from .commands.create_communities import create_communities
from .commands.create_draft_records import create_draft_records
from .commands.delete_record_soft import delete_record
from .commands.fixtures import fixtures
from .commands.update_vocabularies import update_vocabularies
from .commands.upload_files import upload_files
from .utils import create_cli

cli = create_cli(create_app=create_app)

cli.add_command(fixtures)
cli.add_command(create_communities)
cli.add_command(delete_record)
cli.add_command(upload_files)
cli.add_command(update_vocabularies)
cli.add_command(create_draft_records)
