# Installing MT2IR

Typically, preparing the system involves the following:

1. Install the software dependencies
1. Install elasticsearch
1. Start elasticsearch
1. Run software (experiments, etc.)
1. Stop elasticsearch

Some of these (particularly, managing an elasticsearch instance)
may be obviated by shared instances (e.g. on CLSP network), but
are covered here for clarity.

## Convenience script

See [here](setup/install.sh) for a script that attempts to
both set up an environment for the software as well as
download and install elasticsearch.

## Requirements

### Python

The system has a collection of `python3` scripts that are used
to interact with input data and elasticsearch.

The system requires both `python3` (currently `3.5.x`) as well
as `virtualenv`. On CLSP, these tools are already installed.
On a personal machine, `python3` and `virtualenv` can typically be
found in either system packages (perhaps `virtualenv3`) or can be
installed via `pip`.

#### Set up virtualenv

Set up a new virtual environment for the project using `python3`:

``` shell
virtualenv -p $(which python3) /a/path/you/choose/elastic4clir
```

#### Activate the virtualenv

Whenever you want to work with the project, activate its
`virtualenv`.

Enter the `virtualenv`:

``` shell
source /a/path/you/choose/elastic4clir/bin/activate
```

#### Dependencies

Once inside the new `virtualenv`, you'll need to install the projects'
software dependencies.

This only needs to be done once per `virtualenv`.

After activating, install the project's dependencies by running:

``` shell
pip install -r requirements.txt
python setup.py install
```

#### Deactivate the virtualenv

When finished with the environment:

``` shell
deactivate
```

### Elasticsearch

See [this document](ELASTICSEARCH.md) for information about
running elasticsearch.
