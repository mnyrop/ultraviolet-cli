# ultraviolet-cli

Invenio module for custom Ultraviolet commands

## Prerequisites

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Pyenv](https://github.com/pyenv/pyenv#installation)
- [OpenSSL >= 1.1](https://www.openssl.org/source/)

## Install and run locally

- Please make sure OpenSSL >= 1.1.0 on your machine. Install/Update of OpenSSL varies from one machine to another.
- Clone the repository
  ```sh
  git clone git@github.com:nyudlts/ultraviolet-cli.git && cd ultraviolet-cli
  ```
- Install & use specified python version
  ```sh
  pyenv install --skip-existing
  ```
- Install python requirements in a project pip environment (pipenv) based on setup.py
  ```sh
  pip install --upgrade -U pip pipenv
  pipenv run pip install -e .
  pipenv lock
  ```
- Set up db uri
  ```sh
  export SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://ultraviolet:ultraviolet@localhost/ultraviolet”
  ```
- Invoke the `ultraviolet-cli` root command via `pipenv`
  ```sh
  pipenv run ultraviolet-cli
  ```

## Testing

- Set up testing db
  ```sh
  export SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://invenio-app-rdm:invenio-app-rdm@localhost/invenio-app-rdm
  ```
- Run tests
  ```sh
  bash run-tests.sh
  ```

## Create Communities

### Usage

```sh
Usage: ultraviolet-cli create-communities [OPTIONS] NAME

  Create a community for Ultraviolet.

Options:
  -d, --desc TEXT                 A description of the community to be created
                                  [required]
  -t, --type [organization|event|topic|project]
                                  Type of the Community to be created.
                                  [default: organization]
  -v, --visibility [public|restricted]
                                  Visibility of the community.  [default:
                                  public]
  -p, --policy [open|closed]      Policy to be set for the members and records
                                  of the community.  [default: open]
  -o, --owner TEXT                Email address of the designated owner of the
                                  community.  [default: owner@nyu.edu]
  -g, --add-group TEXT            Automatically adds the Group to the
                                  community. Group/Role needs to be provided
                                  as input and needs to be created prior. Adds
                                  the given group as a reader by default.
  --help                          Show this message and exit.
```

### Example

```sh
pipenv run ultraviolet-cli create-communities -d "Community for NYU students" -g "nyustudents" -o "sampleadmin@nyu.edu" "NYU Students Community"
```

The code assumes owner and the group are valid within Invenio, otherwise, they have to be created for the code to complete successfully.

## Delete Records

### Usage

```sh
Usage: ultraviolet-cli delete-record [OPTIONS] PID removalreason-pid-value [removalreason-note]

  Delete Record from Ultraviolet.

Options:
  --help  Show this message and exit.
```

### Example

```sh
pipenv run ultraviolet-cli delete-record pid1-sample deaccession "Officially removed by NYU staff."
```

The code soft delete a published record, not a draft one, leave a metadata-only tombstone page.

## Upload Files

### Usage

```sh
Usage: ultraviolet-cli upload-files [OPTIONS] PID

  Upload file for a draft.

Options:
  -f, --file PATH       File to be uploaded.
  -d, --directory PATH  Directory with the files to be uploaded.
  --help                Show this message and exit.
```

### Example

```sh
pipenv run ultraviolet-cli upload-files -f file_path pid1-sample
```

```sh
pipenv run ultraviolet-cli upload-files -d dir_path pid1-sample
```

## Update Vocabularies

### Usage

```sh
Usage: ultraviolet-cli update_vocabularies vocabulary_key vocabulary_data

  Adds a new entry to the Ultraviolet vocabulary.

Arguments:
  VOCABULARY_TYPE       Type of vocabulary to update. Valid options including:
                        languages (lng), licenses (lic), resourcetypes (rsrct),
                        creatorsroles (crr), affiliations (aff), subjects (sub)  [required]
  VOCABULARY_TYPE       JSON string containing the vocabulary entry data  [required]

Options:
  --help                Show this message and exit.
```

### Example

```sh
ultraviolet-cli update-vocabularies languages '{"id": "testid", "tags": ["individual", "living"], "props": {"alpha_2": "22"}, "title": {"en": "testlanguagetitle"}, "type": "languages"}'

ultraviolet-cli update-vocabularies lng '{"id": "testid", "tags": ["individual", "living"], "props": {"alpha_2": "22"}, "title": {"en": "testlanguagetitle"}, "type": "languages"}'

```

The code add a new language record to vocabulary.

```sh
ultraviolet-cli update-vocabularies sub '{"id": "http://www.test.com", "scheme": "FOS", "subject": "test subject", "type": "subjects"}'

```

The code add a new subject record to vocabulary.

```sh
ultraviolet-cli update-vocabularies rsrct '{"id": "testid", "tags": ["testtag1", "testtag2"], "props": {"csl": "testcsl", "datacite_general": "testdatacite_general", "datacite_type": "testdatacite_type", "openaire_resourceType": "testopenaire_resourceType", "openaire_type": "testopenaire_type", "schema.org": "https://schema.org/testschema", "subtype": "testsubtype", "subtype_name": "testsubtype_name", "type": "testtype", "type_icon": "testtype_icon", "type_name": "testtype_name"}, "title": {"en": "testtitle"}, "type": "resourcetypes"}'

```

The code add a new resource type record to vocabulary.

```sh
ultraviolet-cli update-vocabularies creatorsroles '{"id": "testid", "type": "creatorsroles", "props": {"datacite": "testdatacite"}, "title": {"en": "testtitle"}}'

```

The code add a new creator role record to vocabulary.

```sh
ultravoilet-cli update-vocabularies licenses '{"id": "TEST-ID", "icon": "https://example.com/icon.png", "tags": ["TAG1", "TAG2"], "props": {"url": "https://example.com/license", "scheme": "spdx", "osi_approved": "y"}, "title": {"en": "Example License"}, "type": "licenses"}'
```

The code add a new license record to vocabulary.

```sh
ultraviolet-cli update-vocabularies affiliations '{"acronym": "TST", "id": "TESTID123", "identifiers": [{"identifier": "019wvm591","scheme": "ror"}],"name": "Test University", "title": {"en": "Test University", "fr": "Université de Test"}}'
```

The code add a new affiliation record to vocabulary.

Required Fields for vocabularies:

- Languages (lng):
  Required: id, title, props, tags, type

- Licenses (lic):
  Required: id, tags, props, title, type

- Resource Types (rsrct):
  Required: id, title, props, tags, type

- Creators Roles (crr):
  Required: id, title, props, type

- Subjects (sub):
  Required: id, scheme, subject

- Affiliations (aff):
  Required: id, identifiers, name, title

## Create Draft Records

### Usage

```sh
Usage: ultraviolet-cli create-draft-records [OPTIONS]

  Create a draft record.

Options:
  -o, --owner TEXT      Email address of the designated owner of the
                        community.  [default: owner@nyu.edu]
  -d, --data            Record metadata.
  --help                Show this message and exit.
```

### Example

```sh
pipenv run ultraviolet-cli create-draft-records -o adminUV@test.com -d '{"access": {"record": "public","files": "public"},"files": {"enabled": true},"metadata": {"title": "A Romans story","publication_date": "2020-06-01","publisher": "Acme Inc","resource_type": {"id": "image-photo"},"creators":[{"person_or_org":{"name":"Troy Inc.","type":"organizational"}}]}}'

```

The code create a draft record and return the PID in cmd.
