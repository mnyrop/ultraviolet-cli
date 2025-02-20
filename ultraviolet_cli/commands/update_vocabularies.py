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
from pathlib import Path

import click
import jsonschema
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_rdm_records.fixtures.tasks import create_vocabulary_record
from invenio_rdm_records.fixtures.vocabularies import VocabulariesFixture
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from jsonschema import validate

from ultraviolet_cli.proxies import current_app, current_rdm_records

VOCABULARY_MAP = {
    'languages': 'lng',
    'licenses': 'lic',
    'resourcetypes': 'rsrct',
    'creatorsroles': 'crr',
    'affiliations': 'aff',
    'subjects': 'sub',
}

SCHEMAS = {
    'languages': {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {
                "type": "object",
                "properties": {"en": {"type": "string"}}
            },
            "props": {
                "type": "object",
                "properties": {"alpha_2": {"type": "string"}}
            },
            "tags": {"type": "array", "items": {"type": "string"}},
            "type": {"type": "string"}
        },
        "required": ["id", "title", "props", "tags", "type"]
    },
    'licenses': {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "icon": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "props": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "format": "uri"},
                    "scheme": {"type": "string"},
                    "osi_approved": {"type": "string"}
                }
            },
            "title": {
                "type": "object",
                "properties": {"en": {"type": "string"}},
                "required": ["en"]
            },
            "type": {"type": "string"}
        },
        "required": ["id", "tags", "props", "title", "type"]
    },
    'resourcetypes': {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {
                "type": "object",
                "properties": {"en": {"type": "string"}}
            },
            "props": {
                "type": "object",
                "properties": {
                    "csl": {"type": "string"},
                    "datacite_general": {"type": "string"},
                    "datacite_type": {"type": "string"},
                    "openaire_resourceType": {"type": "string"},
                    "openaire_type": {"type": "string"},
                    "schema.org": {"type": "string"},
                    "subtype": {"type": "string"},
                    "subtype_name": {"type": "string"},
                    "type": {"type": "string"},
                    "type_icon": {"type": "string"},
                    "type_name": {"type": "string"}
                },
            },
            "tags": {"type": "array", "items": {"type": "string"}},

        },
        "required": ["id", "title", "props", "tags", "type"]
    },
    'creatorsroles': {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "props": {
                "type": "object",
                "properties": {"datacite": {"type": "string"}}
            },
            "title": {
                "type": "object",
                "properties": {"en": {"type": "string"}}
            },
            "type": {"type": "string"}
        },
        "required": ["id", "title", "props", "type"]
    },
    'subjects': {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "scheme": {"type": "string"},
            "subject": {"type": "string"},
        },
        "required": ["id", "scheme", "subject"]
    },
    'affiliations': {
        "type": "object",
        "properties": {
            "acronym": {"type": "string"},
            "id": {"type": "string"},
            "identifiers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "identifier": {"type": "string"},
                        "scheme": {"type": "string"}
                    },
                    "required": ["identifier", "scheme"]
                }
            },
            "name": {"type": "string"},
            "title": {
                "type": "object",
                "properties": {
                    "en": {"type": "string"},
                },

            },
        },
        "required": ["id", "identifiers", "name", "title"]
    }
}


@click.command()
@click.argument('vocabulary_key')
@click.argument('vocabulary_data')
@with_appcontext
def update_vocabularies(vocabulary_key, vocabulary_data):
    """Add a new entry to the specified vocabulary."""
    current_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://nyudatarepository:changeme@"
        "localhost/nyudatarepository"
    )

    try:
        data = json.loads(vocabulary_data)

        vocabulary_name = None
        for name, pid in VOCABULARY_MAP.items():
            if vocabulary_key in (name, pid):
                vocabulary_name = name
                break

        if not vocabulary_name:
            click.secho(
                f"Unknown vocabulary key: {vocabulary_key}",
                fg="red", bold=True
            )
            # return -1
            sys.exit(-1)

        schema = SCHEMAS.get(vocabulary_name)

        try:
            validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            click.secho(
                f"Invalid data: {e.message}",
                fg="red", bold=True
            )
            # return -1
            sys.exit(-1)

        if vocabulary_name == 'subjects' or vocabulary_name == 'affiliations':
            create_and_refresh_with_schemes(vocabulary_name, data)
        else:
            create_and_refresh(data)

        click.secho(
            f"Entry added to '{vocabulary_name}' vocabulary "
            "and index refreshed.",
            fg="green"
        )

    except json.JSONDecodeError:
        click.secho(
            f"Invalid JSON input.",
            fg="red", bold=True
        )
        # return -1
        sys.exit(-1)
    except PIDAlreadyExists as e:
        click.secho(
            "Cannot create entry: ID already exists",
            fg="red", bold=True
        )
        sys.exit(-1)
    except Exception as e:
        click.secho(
            f"Cannot create entry: {str(e)}",
            fg="red", bold=True
        )
        # return -1
        sys.exit(-1)


def create_and_refresh(entry):
    """Create the vocabulary entry and refresh the index."""
    vocabulary_service.create(system_identity, entry)
    Vocabulary.index.refresh()


def create_and_refresh_with_schemes(service_str, entry):
    """Create the vocabulary entry for specific vocabulary with schemes."""
    create_vocabulary_record(service_str, entry)
