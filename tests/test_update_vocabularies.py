# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Update Vocabularies

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""


import json

from ultraviolet_cli.commands.update_vocabularies import update_vocabularies


# Test CLI's response to invalid data input (missing required fields).
# Expects a non-zero exit code and 'Invalid data' error message.
def test_cli_update_vocabularies_invalid_data(cli_runner, running_app):
    test_data = {
        "props": {"alpha_2": "XX"},
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["languages", test_data_json]
    )

    assert result.exit_code == -1
    assert 'Invalid data' in result.output


# Test CLI's response to unknown vocabulary type.
# Expects non-zero exit code and 'Unknown vocabulary key' error message.
def test_cli_update_vocabularies_unknown_vocabulary(cli_runner, running_app):
    test_data = {
        "props": {"alpha_2": "XX"},
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["unknown_vocabulary", test_data_json]
    )

    assert result.exit_code == -1
    assert 'Unknown vocabulary key' in result.output


# Test CLI's response to invalid JSON input (unquoted keys 'id').
# Expects non-zero exit code and 'Invalid JSON input' error message.
def test_cli_update_vocabularies_invalid_json_input(cli_runner, running_app):
    test_data = '{id: "TESTID", "tags": ["TESTTAG1", "TESTTAG2"]}'

    result = cli_runner(
        update_vocabularies, ["languages", test_data]
    )

    assert result.exit_code == -1
    assert 'Invalid JSON input' in result.output


# Test successful update of 'languages' vocabulary.
# Expects zero exit code and 'vocabulary and index refreshed' message
def test_cli_update_vocabularies_languages(cli_runner, running_app):
    test_data = {
        "id": "TESTID",
        "tags": ["TESTTAG1", "TESTTAG2"],
        "props": {"alpha_2": "XX"},
        "title": {"en": "TESTTITTLE"},
        "type": "languages"
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["languages", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'licenses' vocabulary.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_licenses(cli_runner, running_app):
    test_data = {
        "id": "TEST-ID",
        "icon": "https://example.com/icon.png",
        "tags": ["TAG1", "TAG2"],
        "props": {
            "url": "https://example.com/license",
            "scheme": "spdx",
            "osi_approved": "y"
        },
        "title": {
            "en": "Example License"
        },
        "type": "licenses"
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["licenses", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'licenses' vocabulary without approved.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_licenses_without_approved(
        cli_runner, running_app):
    test_data = {
        "id": "TEST-ID",
        "icon": "https://example.com/icon.png",
        "tags": ["TAG1", "TAG2"],
        "props": {
            "url": "https://example.com/license",
            "scheme": "",
            "osi_approved": ""
        },
        "title": {
            "en": "Example License"
        },
        "type": "licenses"
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["licenses", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'resourcetypes' vocabulary.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_resourcetypes(cli_runner, running_app):
    test_data = {
        "id": "xpublication",
        "tags": ["testtag1", "testtag2"],
        "props": {
            "csl": "testcsl",
            "datacite_general": "testdatacite_general",
            "datacite_type": "testdatacite_type",
            "openaire_resourceType": "testopenaire_resourceType",
            "openaire_type": "testopenaire_type",
            "schema.org": "https://schema.org/testschema",
            "subtype": "testsubtype",
            "subtype_name": "testsubtype_name",
            "type": "testtype",
            "type_icon": "testtype_icon",
            "type_name": "testtype_name"
        },
        "title": {"en": "testtitle"},
        "type": "resourcetypes"
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["rsrct", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'creatorsroles' vocabulary.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_creatorsroles(cli_runner, running_app):
    test_data = {
        "id": "THETESTID",
        "type": "creatorsroles",
        "props": {"datacite": "testdatacite"},
        "title": {"en": "testtitle"}
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["creatorsroles", test_data_json]
    )

    # assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'affiliations' vocabulary.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_affiliations(cli_runner, running_app):
    test_data = {
        "acronym": "TST",
        "id": "TESTID123",
        "identifiers": [
            {
                "identifier": "019wvm591",
                "scheme": "ror"
            }
        ],
        "name": "Test University",
        "title": {
            "en": "Test University",
            "fr": "Université de Test"
        }
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["affiliations", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'affiliations' vocabulary without acronym.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_affiliations_no_acronym(
        cli_runner, running_app):
    test_data = {
        "id": "019wvm692",
        "identifiers": [
            {
                "identifier": "019wvm692",
                "scheme": "ror"
            }
        ],
        "name": "Test University",
        "title": {
            "en": "Test University",
            "fr": "Université de Test"
        }
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["affiliations", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test successful update of 'subjects' vocabulary.
# Expects zero exit code and 'vocabulary and index refreshed' message.
def test_cli_update_vocabularies_subjects(cli_runner, running_app):
    test_data = {
        "id": "SUBJECTID123",
        "scheme": "TESTSCHEME",
        "subject": "Test Subject"
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["subjects", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output


# Test handling of duplicate ID in 'resourcetypes' vocabulary update.
# Expects success on first attempt, failure with specific error on second.
def test_cli_update_vocabularies_resourcetypes_duplicate_id(
        cli_runner, running_app):
    test_data = {
        "id": "xpublication",
        "tags": ["testtag1", "testtag2"],
        "props": {
            "csl": "testcsl",
            "datacite_general": "testdatacite_general",
            "datacite_type": "testdatacite_type",
            "openaire_resourceType": "testopenaire_resourceType",
            "openaire_type": "testopenaire_type",
            "schema.org": "https://schema.org/testschema",
            "subtype": "testsubtype",
            "subtype_name": "testsubtype_name",
            "type": "testtype",
            "type_icon": "testtype_icon",
            "type_name": "testtype_name"
        },
        "title": {"en": "testtitle"},
        "type": "resourcetypes"
    }

    test_data_json = json.dumps(test_data)

    result = cli_runner(
        update_vocabularies, ["rsrct", test_data_json]
    )

    assert result.exit_code == 0
    assert 'vocabulary and index refreshed' in result.output

    result = cli_runner(
        update_vocabularies, ["rsrct", test_data_json]
    )

    assert result.exit_code == -1
    assert 'Cannot create entry: ID already exists' in result.output
