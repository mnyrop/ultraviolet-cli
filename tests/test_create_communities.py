# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Create Communities

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""


from ultraviolet_cli.commands.create_communities import create_communities


# Test create community CLI.
def test_cli_create_communities(cli_runner, running_app, admin_user):

    result = cli_runner(
        create_communities, [
            "TestCommunityName",
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "organization",
            "--policy", "open",
            "--owner", "adminuv@test.com"
        ]
    )

    assert result.exit_code == 0
    assert ('Created community TestCommunityName successfully with ID:'
            in result.output)


# Test missing required argument 'name'.
def test_cli_create_community_missing_name(
        cli_runner, running_app, admin_user):

    result = cli_runner(
        create_communities, [
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "organization",
            "--policy", "open",
            "--owner", "adminuv@test.com"
        ]
    )

    assert result.exit_code != 0
    assert "Missing argument 'NAME'." in result.output


# Test invalid community type.
def test_cli_create_community_invalid_type(
        cli_runner, running_app, admin_user):

    result = cli_runner(
        create_communities, [
            "TestCommunityName",
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "invalid_type",  # Invalid type
            "--policy", "open",
            "--owner", "adminuv@test.com"
        ]
    )

    assert result.exit_code != 0
    assert ("'invalid_type' is not one of 'organization', 'event', "
            "'topic', 'project'." in result.output)


# Test invalid owner email.
def test_cli_create_community_invalid_owner(cli_runner, running_app):

    result = cli_runner(
        create_communities, [
            "TestCommunityName",
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "organization",
            "--policy", "open",
            "--owner", "nonexistentowner@test.com"  # Invalid owner email
        ]
    )

    assert result.exit_code != 0
    assert "Could not get owner successfully" in result.output


# Test community creation with a group.
def test_cli_create_community_with_group(
        cli_runner, running_app, admin_user, group):

    result = cli_runner(
        create_communities, [
            "TestCommunityName",
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "organization",
            "--policy", "open",
            "--owner", "adminuv@test.com",
            "--add-group", "it-dep"
        ]
    )

    assert result.exit_code == 0
    assert ('Created community TestCommunityName successfully with ID:'
            in result.output)
    assert 'Added group it-dep successfully' in result.output


# Test attempting to create a duplicate community (PIDAlreadyExists).
def test_cli_create_duplicate_community(
        cli_runner, running_app, admin_user, mocker):

    result = cli_runner(
        create_communities, [
            "TestCommunityName",
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "organization",
            "--policy", "open",
            "--owner", "adminuv@test.com"
        ]
    )

    assert result.exit_code == 0

    result = cli_runner(
        create_communities, [
            "TestCommunityName",
            "--desc", "Test Community",
            "--visibility", "public",
            "--type", "organization",
            "--policy", "open",
            "--owner", "adminuv@test.com"
        ]
    )

    assert result.exit_code != 0
    assert "A community with this identifier already exists." in result.output
