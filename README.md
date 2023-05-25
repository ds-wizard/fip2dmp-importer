# FIP-to-DMP DSW Project Importer

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/ds-wizard/fip2dmp-importer)](https://github.com/ds-wizard/fip2dmp-importer/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/datastewardshipwizard/fip2dmp-importer)](https://hub.docker.com/r/datastewardshipwizard/fip2dmp-importer)
[![LICENSE](https://img.shields.io/github/license/ds-wizard/fip2dmp-importer)](LICENSE)

FIP-to-DMP project importer for Data Stewardship Wizard

## Usage

### Mapping Specification

The mapping can be specified in the source knowledge model using annotations. There is a detailed information on that topic in the [HOWTO.md](HOWTO.md) document.

### Configuration

All configuration is done through environment variables:

* `DSW_API_URL` = API URL of the DSW instance from which source questionnaires/projects (i.e. FIPs) should be loaded
* `DSW_API_KEY` = [API key](https://guide.ds-wizard.org/en/latest/application/profile/edit/api-keys.html) for that DSW instance
* `PACKAGE_IDS` = specification of a KM filter, e.g. `gofair:fip-wizard-3:all,gofair:fip-wizard-2:all` to list all FIPs made using `gofair:fip-wizard-3` (all versions) and `gofair:fip-wizard-2` (all versions)

### Deployment

This application supports [WSGI](https://wsgi.readthedocs.io/en/latest/index.html) as it is Python-based web application. The suggested deployment is through Docker (see [Dockerfile](Dockerfile)).

### Development

For development, you can use `.env` file and start the app using `run.sh` script.

## License

This project is licensed under the Apache License v2.0 - see the
[LICENSE](LICENSE) file for more details.
