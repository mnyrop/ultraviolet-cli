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

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_communities.members.errors import InvalidMemberError
from invenio_pidstore.errors import PIDAlreadyExists
from marshmallow.exceptions import ValidationError

from ultraviolet_cli.proxies import current_app, current_communities
from ultraviolet_cli.utils import create_community_data


@click.command()
@click.option(
    "-d",
    "--desc",
    type=str,
    required=True,
    help="A description of the community to be created",
)
@click.option(
    "-t",
    "--type",
    type=click.Choice(['organization', 'event', 'topic', 'project']),
    show_default=True,
    default="organization",
    help="Type of the Community to be created.",
)
@click.option(
    "-v",
    "--visibility",
    type=click.Choice(['public', 'restricted']),
    show_default=True,
    default="public",
    help="Visibility of the community.",
)
@click.option(
    "-p",
    "--policy",
    type=click.Choice(['open', 'closed']),
    show_default=True,
    default="open",
    help="Policy to be set for the members and records of the community.",
)
@click.option(
    "-o",
    "--owner",
    type=str,
    show_default=True,
    default="owner@nyu.edu",
    help="Email address of the designated owner of the community.",
)
@click.option(
    "-g",
    "--add-group",
    type=str,
    help="Automatically adds the Group to the community. "
         "Group/Role needs to be provided as input and "
         "needs to be created prior. Adds the given group "
         "as a reader by default.",
)
@click.argument('name')
@with_appcontext
def create_communities(desc, type, visibility, policy,
                       owner, add_group, name):
    """Create a community for Ultraviolet."""
    current_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://nyudatarepository:changeme@"
        "localhost/nyudatarepository"
    )
    click.secho("Creating community...", fg="yellow")

    community_data = create_community_data(
        name, desc, type, visibility, policy
    )
    click.secho(
        f"Created community data:"
        f"\n{json.dumps(community_data, indent=2)}"
    )

    service = current_communities.service
    try:
        owner_identity = get_identity(
            User.query.filter_by(email=owner).one()
        )
    except Exception:
        click.secho(f"Could not get owner successfully. "
                    f"Is {owner} a valid owner?", fg="red")
        sys.exit(-1)

    try:
        community = service.create(data=community_data,
                                   identity=owner_identity)
    except (PIDAlreadyExists, ValidationError) as err:
        click.secho(f"Error Creating Community: {err}"
                    f"\nAborting...", fg="red")
        sys.exit(-2)

    click.secho(f"Created community {name} successfully with ID: "
                f"{community.id}. Optionally, you can append this "
                f"ID to COMMUNITIES_AUTO_UPDATE list in invenio.cfg"
                f" to setup automatic update of community group "
                f"members.", fg="green")
    if add_group:
        members_service = current_communities.service.members
        try:
            members_service.add(
                system_identity,
                community.id,
                {
                    "members": [
                        {"type": "group", "id": add_group}
                    ],
                    "role": "reader",
                    "visible": True,
                },
            )
        except InvalidMemberError:
            click.secho(
                f"Group {add_group} not created yet. "
                f"Please create group using:\n\n"
                f"pipenv run invenio roles create {add_group}\n\n"
                f"And then, add the role manually.",
                fg="red"
            )
            return -3
        click.secho(
            f"Added group {add_group} successfully",
            fg="green"
        )

    sys.exit(0)
