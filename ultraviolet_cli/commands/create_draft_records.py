# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for custom UltraViolet commands."""

import json
import os
import sys
import tempfile
import uuid

import click
import jsonschema
from flask.cli import with_appcontext
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_db import db
from invenio_files_rest.models import Bucket, Location
from jsonschema import validate

from ultraviolet_cli.proxies import current_app, current_rdm_records

SCHEMA = {
    "type": "object",
    "properties": {
        "access": {
            "type": "object",
            "properties": {
                "record": {"type": "string"},
                "files": {"type": "string"}
            },
            "required": ["record", "files"]
        },
        "files": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"}
            },
            "required": ["enabled"]
        },
        "metadata": {
            "type": "object",
            "properties": {
                "creators": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "person_or_org": {
                                "type": "object",
                                "properties": {
                                    "family_name": {"type": "string"},
                                    "given_name": {"type": "string"},
                                    "name": {"type": "string"},
                                    "type": {
                                        "type": "string",
                                        "enum": ["personal", "organizational"]
                                    }
                                },
                                "required": ["type"]
                            }
                        }
                    }
                },
                "publication_date": {"type": "string", "format": "date"},
                "publisher": {"type": "string"},
                "resource_type": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"]
                },
                "title": {"type": "string"}
            },
            "required": ["creators", "publication_date",
                         "publisher", "resource_type", "title"]
        }
    },
    "required": ["access", "files", "metadata"]
}


@click.command()
@click.option(
    "-o",
    "--owner",
    type=str,
    show_default=True,
    default="owner@nyu.edu",
    help="Email address of the user who create draft record.",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="default",
    help="Location name for the bucket. Use default location if not provided.",
)
@click.option(
    "-d",
    "--data",
    type=str,
    required=True,
    help="The data of the draft record.",
)
# @click.argument('data')
@with_appcontext
def create_draft_records(name, owner, data):
    """Create a draft Record."""
    current_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://nyudatarepository:changeme@"
        "localhost/nyudatarepository"
    )

    try:
        jsonData = json.loads(data)

        validate(instance=jsonData, schema=SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        click.secho(
            f"Invalid data: {e.message}",
            fg="red", bold=True
        )
        sys.exit(-1)

    try:
        identity = get_identity(
            User.query.filter_by(email=owner).one()
        )
    except Exception as e:
        click.secho(f"Could not get user successfully. "
                    f"Is {owner} a valid user?", fg="red")
        click.secho(str(e))
        sys.exit(-1)

    if name == "default":
        # use default bucket
        try:
            service = current_rdm_records.records_service
            draft_record = service.create(identity, jsonData)
        except Exception as e:
            click.secho(
                f"Cannot create record: {str(e)}",
                fg="red", bold=True
            )
            sys.exit(-1)

        click.secho(
            f"Draft record created with default bucket location.",
            fg="green"
        )
        click.secho(f"Draft record PID: {draft_record.id}.", fg="green")
        click.secho(f"Operation completed successfully.", fg="green")
        return 0

    location = None
    location_created = False

    try:
        location = Location.query.filter_by(name=name).one_or_none()
        if location is None:
            generated_prefix = f"loc-{uuid.uuid4()}".lower()
            tmppath = tempfile.mkdtemp(prefix=generated_prefix)
            location = Location(name=name, uri=tmppath, default=False)
            db.session.add(location)
            db.session.commit()
            location_created = True
            click.secho(f"Created bucket location: {name}", fg="green")
        else:
            click.secho(f"Use existing bucket location: {name}", fg="green")
    except Exception as e:
        db.session.rollback()
        click.secho(
            f"Cannot create or retrieve Location: {str(e)}",
            fg="red", bold=True
        )
        sys.exit(-1)

    try:
        service = current_rdm_records.records_service
        draft_record = service.create(identity, jsonData)
        default_bucket = draft_record._record.bucket

        bucket = Bucket.create(location=location)

        draft_record._record.bucket = bucket
        draft_record._record.bucket_id = bucket.id

        if default_bucket:
            db.session.delete(default_bucket)

        db.session.commit()

        click.secho(
            f"Draft record created with bucket location: {name}.",
            fg="green"
        )
        click.secho(f"Draft record PID: {draft_record.id}.", fg="green")
        click.secho(f"Operation completed successfully.", fg="green")
        return 0
    except Exception as e:
        click.secho(
            f"Cannot create record: {str(e)}",
            fg="red", bold=True
        )
        if location_created:
            try:
                db.session.delete(location)
                db.session.commit()
                click.secho(
                    f"Remove created location due to record creation failure.",
                    fg="yellow"
                )
            except Exception as delete_error:
                db.session.rollback()
                click.secho(
                    "Warning: Could not remove created location: "
                    f"{str(delete_error)}",
                    fg="yellow", bold=True
                )

        sys.exit(-1)
