# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for custom UltraViolet commands."""

import os
import uuid

import click
from flask.cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import MultipartObject, Part
from invenio_pidstore.errors import PIDDoesNotExistError
from six import BytesIO

from ultraviolet_cli.config import DEFAULT_CHUNK_SIZE
from ultraviolet_cli.proxies import current_app, current_rdm_records


@click.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(),
    default="",
    help="File to be uploaded.",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(),
    default="",
    help="Directory with the files to be uploaded.",
)
@click.argument("pid")
@with_appcontext
def upload_files(file, directory, pid):
    """Upload file for a draft."""
    current_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://nyudatarepository:changeme@"
        "localhost/nyudatarepository"
    )
    try:
        draft = current_rdm_records.records_service.draft_cls.pid.resolve(
            pid, registered_only=False
        )
    except PIDDoesNotExistError:
        click.secho(f"PID {pid} does not exist. Please check input.",
                    fg="red")
        return -1

    click.secho(
        f"Uploading files to Draft: {draft['metadata']['title']}...",
        fg="green"
    )

    uploads = []
    if file:
        if not os.path.exists(os.path.abspath(file)):
            click.secho(f"File {file} does not exist. Please check input.",
                        fg="red")
            return -1
        uploads.append(os.path.abspath(file))
    if directory:
        if not os.path.exists(os.path.abspath(directory)):
            click.secho(
                f"Directory {directory} does not exist. Please check input.",
                fg="red"
            )
            return -1
        for item in os.listdir(directory):
            uploads.append(os.path.join(os.path.abspath(directory), item))

    if not file and not directory:
        click.secho(
            f"Please specify a file or directory to upload using -f or -d.",
            fg="red"
        )
        return -1
    for upload in uploads:
        file_size = os.stat(upload).st_size
        file_name = os.path.basename(upload)
        if file_size < DEFAULT_CHUNK_SIZE:
            obj = open(upload, "rb")
        else:
            n_chunks = int(file_size / DEFAULT_CHUNK_SIZE)
            last_chunk = file_size % DEFAULT_CHUNK_SIZE
            mp = MultipartObject.create(
                draft.bucket,
                file_name,
                size=file_size,
                chunk_size=DEFAULT_CHUNK_SIZE,
            )
            with open(upload, "rb") as f:
                with click.progressbar(
                    length=file_size, label=f"{file_name}:"
                ) as bar:
                    try:
                        for i in range(n_chunks + 1):
                            if i < n_chunks:
                                part_size = DEFAULT_CHUNK_SIZE
                            else:
                                part_size = last_chunk
                            data = BytesIO(f.read(part_size))
                            Part.create(mp, i, stream=data)
                            del data
                            db.session.commit()
                            bar.update(part_size)
                    except Exception as err:
                        db.session.rollback()
                        click.secho(
                            f"\nError while uploading "
                            f"{file_name}: {err}",
                            fg="red"
                        )
                        return -1
            mp.complete()
            db.session.commit()
            version_id = str(uuid.uuid4())
            obj = mp.merge_parts(version_id=version_id)
            db.session.commit()
        if file_name in draft.files:
            click.secho(
                f"{file_name} already exists in draft.", fg="yellow")
            new_file_name = input(
                "Press Enter to replace existing file or "
                "type in the new file name:\n"
            )
            if new_file_name:
                file_name = new_file_name
        draft.files[file_name] = obj
        db.session.commit()
        click.secho(f"Uploaded {file_name}.", fg="green")
    click.secho(f"Operation completed successfully.", fg="green")
    return 0
