# Quartz

Quartz is an app for visualizing corpus data from Sketch Engine servers. It's an alternate interface that focuses on automatically graphing quantitative data for linguistic analysis. Set up your corpora, make API queries to a Sketch Engine or NoSketch Engine server, and view results with interactive graphs.

The project is structured as a Flask web app template: it includes some default graphing features, but you can also build custom features to fit your own data and workflow. Quartz is made with Python, the Dash framework, and Docker containerization. To use it you'll need API access to a Sketch Engine or NoSketch Engine server, as well as familiarity with the tools below.

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

To make queries to your own server, see the resources on NoSketch Engine.

API-based data collection requires understanding the Sketch Grammar Explorer package (SGEX, a Sketch Engine API wrapper); try it out as a standalone tool if you plan on doing custom data processing.

### Get started

Run the following snippet to copy default configuration files, then modify them as shown in the following steps.

```bash
cp -i builtin/config/.env .env
make get_started
```

#### Install dependencies

Add a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source ${PWD}/.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

This is the pip command for installing packages from scratch:

```python
pip install cryptography dash dash-bootstrap-components flask gunicorn pandas plotly pre-commit python-dotenv pyyaml requests sgex
```

Configure pre-commit with `pre-commit install` if you plan on adhering to Quartz's coding style.

#### Repo structure

Quartz has two main directories for the app's content, `builtin/`, which has the repository's basic features, and `custom/`, where you can add your own content. You can stick with the built-in content or create an entirely new structure in `custom/` and periodically integrate updates from `builtin/`. The `make get_started` command will copy some basic files to have a minimal working example.

#### Environment variables

Environment variables are managed in these files:

- `.env` is needed for `docker` and `docker-compose` commands
- `environment/.env` is for production environments (Docker)
- `environment/.env.dev` is for development/running Quartz locally (Gunicorn)
- the development environment activates automatically for VScode users (see `.vscode/launch.json`)

Two secret variables must be added manually to get started: `SGEX_CONFIG_JSON` (Sketch Engine API configuration) and `SERIALIZER_KEY` (encryption key for saved data).

```bash
# server configuration
SGEX_CONFIG_JSON='{"ske": {"api_key": "<key>", "host": "https://api.sketchengine.eu/bonito/run.cgi", "username": "<user>", "wait": {"0": 1, "2": 99, "5": 899, "45": null}}}'

# a key for encrypting API response data
SERIALIZER_KEY='<fernet_key>'
```

The default `SGEX_CONFIG_JSON` can be used to make calls to the main Sketch Engine server by adding your API key and username (add more servers if needed). A `SERIALIZER_KEY` can be generated like this:

```python
from cryptography.fernet import Fernet

# generate a key and then add it to env files
Fernet.generate_key().decode()
```

Other environment variables can be set to change the app's appearance, content, etc. For example, switch between servers with `SGEX_SERVER` and enable custom content by replacing `builtin/` with `custom/` in the other variables below.

```bash
# the server to send requests to
SGEX_SERVER="ske"

# assets (images, favicon, CSS)
ASSETS_DIR="builtin/assets"

# pages (navigable pages in the app)
PAGES_DIR="builtin/pages"

# layout (general app appearance)
LAYOUT_MODULE="builtin.layout.layout"

# list of available corpora
CORPORA_FILE="builtin/config/corpora-ske.yml"
```

### Run Quartz

The instructions above will set up Quartz for making queries to the Susanne corpus on Sketch Engine. Review Sketch Engine's [fair use policy](https://www.sketchengine.eu/fair-use-policy/) before making calls.

Start the app with one of the methods below and open it in a broswer (defaults to http://127.0.0.1:8080/).

These are the default features included so far. They've been tested on a handful of corpora, so they are stable - but don't expect perfect compatibility out of the box.

- a Corpora page to analyze corpus composition (sizes, attributes, text types, etc.)
- a Frequencies page to automatically graph frequency data

#### With Gunicorn

Quartz can run locally with Gunicorn as long as `ENVIRONMENT_FILE` is set first, e.g., by running `ENVIRONMENT_FILE=.env.dev python3 app.py`. VScode users can press `F5` to start the app with debugging enabled.

#### With Docker

Run `docker-compose build` to build a Quartz image and pull the NoSketch Engine Docker image. Alternatively, run `docker build . -t quartz:latest` if you don't need NoSketch Engine. There are a few `Makefile` commands to manage running containers, e.g., `make quartz` starts the container.

Note that `data/` is not excluded in `.dockerignore` by default: change Docker settings as needed before building your own images. API response data is encrypted in `data/` by default, but the backend can be changed by modifying [requests-cache](https://requests-cache.readthedocs.io) settings (`session_params` in `environment/settings.py`).

#### Using a local NoSketch Engine server

If you're using NoSketch Engine, start its container with `make noske` before starting Quartz. The `CORPORA_DIR` path must be correct and contain valid corpus files. See the NoSketch Engine Docker repo for guidance.

### Customize Quartz

#### Available corpora

Quartz can make calls to multiple Sketch Engine servers and any accessible corpus. To do so, each server needs to be configured in `SGEX_CONFIG_JSON`, as shown above, and also have its own YAML file with a list of available corpora (`CORPORA_FILE`).

For example, the default `SGEX_CONFIG_JSON` settings are for the main Sketch Engine server, which is given the name `ske`. Likewise, the default `CORPORA_FILE`, called `corpora-ske.yml`, contains this entry:

```yaml
# the `corpname` field for making calls to a corpus
preloaded/susanne:
  # a display name
  name: Susanne
  # a markdown file with a description of the corpus
  md_file: builtin/markdown/preloaded/susanne.md
```

#### Data labels

Data that's visualized in Quartz uses Sketch Engine's default field names in most cases. These can be replaced with a `labels.yml` file, where each key is the original string and its value is the desired replacement. On startup, `labels.yml` is added to a list of default labels for statistics in `environment.settings.py`, so `frq` and `rel` become `occurrences` and `relative density %` and so on.

```yaml
# environment/labels.yml
nicearg: query
corpname: corpus
preloaded/susanne: Susanne
susanne: Susanne
```

#### Comparing corpora

If you'd like to make several corpora comparable - so they appear together in the same visualizations - set up `comparable_attributes` for them in the `CORPORA_FILE`.

The example below has two corpora, both of which contain metadata for date, genre, and author. One  corpus uses the `class` prefix and the other `doc`. To make these comparable, add a `comparable_attributes` dictionary that maps a shared name for the attribute to each corpus. Quartz then recognizes that `class.date` and `doc.date`, for instance, can be grouped together while making queries.

```yaml
first_corpus:
  name: A custom corpus
  md_file: custom/markdown/first_corpus.md
  comparable_attributes:
    date: class.date
    genre: class.genre
    author: class.author
second_corpus:
  name: Another custom corpus
  md_file: custom/markdown/second_corpus.md
  comparable_attributes:
    date: doc.date
    genre: doc.genre
    author: doc.author
```

## About

Quartz was developed with funding from the [Humanitarian Encyclopedia](https://humanitarianencyclopedia.org) and support from the University of Granada ([LexiCon research group](http://lexicon.ugr.es)). It relies on APIs made available thanks to the work of [Lexical Computing](https://www.lexicalcomputing.com/) and [Sketch Engine contributors](https://www.sketchengine.eu/bibliography-of-sketch-engine/), as well as the Docker image from Eötvös Loránd University Department of Digital Humanities.

This app includes [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) and its early Docker implementation was based on [this template](https://github.com/CzakoZoltan08/dash-clean-architecture-template). Also check out [Dash's community forum](https://community.plotly.com/).

The name Quartz is a nod to Sketch Engine's GUI, Crystal.

## Citation

If you use Quartz, please [cite it](/CITATION.cff).
