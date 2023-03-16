# Quartz

Quartz is an app for visualizing corpus data from Sketch Engine servers. It's structured as an application template: you can build custom features on top of the defaults. It's made with Python and the Dash framework and is deployable as a Docker container.

This repo is oriented toward developers and researchers wanting to automate custom data visualization tasks for corpus linguistics. To use Quartz you'll need API access to a Sketch Engine or NoSketch Engine server, as well as familiarity with the tools below.

## Installation

Get started by cloning this repo and checking out these links for information on each dependency:

- [Sketch Engine](https://www.sketchengine.eu/)
- [NoSketch Engine](https://nlp.fi.muni.cz/trac/noske)
- [NoSketch Engine Docker](https://github.com/ELTE-DH/NoSketch-Engine-Docker)
- [Sketch Grammar Explorer](https://github.com/engisalor/sketch-grammar-explorer)
- [Plotly graphing library](https://plotly.com/python/)
- [Dash web app framework](https://dash.plotly.com/)
- [Docker containerization](https://www.docker.com/)

To make queries to the Sketch Engine server, get an [API key](https://www.sketchengine.eu/documentation/api-documentation/).

To make queries to your own server, see the above NoSketch Engine resources.

API-based data collection requires understanding the SGEX package (a Sketch Engine API wrapper); try it out as a standalone tool first.

### Get started

Run the following snippet to copy default configuration files.

```bash
cp -i builtin/config/.env .env
make get_started
```

#### Environment variables

Environment variables are managed in these files - review them and make adjustments as needed.

- `.env` is for `docker-compose` variables
- `environment/.env` is for production environments
- `environment/.env.dev` is for development/running Quartz as a standalone Flask app
- the development environment activates automatically for VScode users via `.vscode/launch.json`

Below are some of the configuration variables. Develop your own content in `custom/` and update as needed. For example, to use a set of custom pages set this variable `PAGES_DIR="custom/pages"`.

```bash
# the server to send requests to
SGEX_SERVER="ske"

# server configuration (this example is for Sketch Engine's main server)
SGEX_CONFIG_JSON='{"ske": {"api_key": "<key>", "host": "https://api.sketchengine.eu/bonito/run.cgi", "username": "<user>", "wait": {"0": 1, "2": 99, "5": 899, "45": null}}}'

# a key for encrypting API response data (see environment/settings.py)
SERIALIZER_KEY='<fernet_key>'

# the assets to use
ASSETS_DIR="builtin/assets"

# the pages to use
PAGES_DIR="builtin/pages"

# the layout to use
LAYOUT_MODULE="builtin.layout.layout"

# the list of corpora to use
CORPORA_FILE="builtin/config/corpora-ske.yml"
```

#### Virtual environments

Add a Python virtual environment and install Quartz dependencies:

```bash
python3 -m venv .venv
source $PWD/.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

This is the pip command for installing packages from scratch:

```python
pip install cryptography dash dash-bootstrap-components flask gunicorn pandas plotly pre-commit python-dotenv pyyaml requests sgex
```

Configure pre-commit with `pre-commit install` if you plan on adhering to Quartz's coding style.

### Build images

Run `docker-compose build` to build a Quartz image and pull the NoSketch Engine Docker image. There are a few `Makefile` commands to manage running containers. If you never plan on using a local server, comment out the `noske` lines in `docker-compose.yml`.

#### Option 1: make queries to Sketch Engine

Skip this if you aren't using a local server. (But do review Sketch Engine's API policy.)

#### Option 2: use a local NoSketch Engine server

Before starting Quartz, run `make noske` to start NoSketch Engine. The `CORPORA_DIR` path must be correct and contain valid corpus files. See the NoSketch Engine Docker repo for guidance.

To stop the container, run `docker stop noske`.

### Run Quartz

#### With Gunicorn

Quartz can run like any normal Flask web app as long as `ENVIRONMENT_FILE` is set first: run `ENVIRONMENT_FILE=.env.dev python3 app.py`. VScode users can press `F5` to start the app with debugging enabled.

#### With docker

Run `make quartz` to start Quartz (to stop it, run `docker stop quartz`).

### Use Quartz

Open Quartz in a web browser and try it out. These are the default features included so far. They've been tested on a handful of corpora, so they are stable - but don't expect perfect compatibility out of the box.

- a `Corpora` page to analyze corpus composition (sizes, attributes, text types, etc.)
- a `Frequencies` page to automatically graph frequency data

(Available corpora must be defined in the `CORPORA_FILE` beforehand.)

### Develop Quartz

- `builtin/` has the app's default content
- add your own content in `custom/`
- customize app settings in `environment/settings.py`
- `environment/labels.yml` is for customizing graph annotations: this is a dict of mapping items (`{original_string: replacement_string}`)
- API response data is encrypted in a filesystem cache by default, but the backend can be changed with [requests-cache](https://requests-cache.readthedocs.io) settings
- `data/` is not excluded in `.dockerignore` by default: change git/Docker settings as needed before building your own images

## About

Quartz was developed with funding from the [Humanitarian Encyclopedia](https://humanitarianencyclopedia.org) and support from the University of Granada ([LexiCon research group](http://lexicon.ugr.es)). It's possible thanks to the work of [Lexical Computing](https://www.lexicalcomputing.com/), researchers who've [contributed to Sketch Engine](https://www.sketchengine.eu/bibliography-of-sketch-engine/), and the Dockerized version by the Eötvös Loránd University Department of Digital Humanities. NoSketch Engine is available under [GPL licenses](https://nlp.fi.muni.cz/trac/noske).

This app includes [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) and its early Docker implementation was based on [this template](https://github.com/CzakoZoltan08/dash-clean-architecture-template). Also check out [Dash's community forum](https://community.plotly.com/).

The name Quartz is a nod to Sketch Engine's GUI, Crystal.

## Citation

If you use Quartz, please [cite it](/CITATION.cff).
