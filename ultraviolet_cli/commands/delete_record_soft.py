# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for custom UltraViolet commands."""
import os

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity

from ultraviolet_cli.proxies import current_app, current_rdm_records


@click.command()
@click.argument('pid')
@click.argument('removal_reason_id')
@click.argument('note', required=False)
@with_appcontext
def delete_record(pid, removal_reason_id, note):
    """Delete (soft-delete) a published record in UltraViolet with a tombstone."""
    current_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://ultraviolet:ultraviolet@localhost/ultraviolet"
    )

    tombstone_info = {
        "removal_reason": {"id": removal_reason_id},
        "note": note if note else ""
    }

    try:
        current_rdm_records.records_service.delete_record(
            identity=system_identity,
            id_=pid,
            data=tombstone_info
        )
    except Exception as e:
        click.secho(
            f"Could not delete record: PID {pid} does not exist "
            "or is assigned to a draft record.",
            fg="red"
        )
        click.secho("Error message: " + str(e), fg="red")
        return False

    click.secho(f"Deleted record {pid} successfully (tombstone created).", fg="green")
    return True
