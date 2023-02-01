# Quartz

*- Under construction -*

Quartz is a dashboard for visualizing corpus data from Sketch Engine servers. It's built with Python and Plotly's Dash framework and is deployable as a Docker container.

This repo is oriented toward developers and researchers wanting to automate custom data visualization tasks for corpus linguistics. To use Quartz you'll need a compiled Sketch Engine corpus (if using locally) and/or API access to a Sketch Engine server (for making external queries - under development).

Quartz is designed as an application template to allow for easy adaptation, though it can be used as-is with its built-in visualizations. These features are meant to be a common resource for developing corpus visualization methods (contributions are welcome). Some modifications may be needed depending on how your data is structured.

## Installation

Get started by cloning/forking this repo. Also check out these links for information on each software dependency:

- [Sketch Engine](https://www.sketchengine.eu/)
- [NoSketch Engine](https://nlp.fi.muni.cz/trac/noske)
- [NoSketch Engine Docker](https://github.com/ELTE-DH/NoSketch-Engine-Docker)
- [Sketch Grammar Explorer](https://github.com/engisalor/sketch-grammar-explorer)
- [Plotly graphing library](https://plotly.com/python/)
- [Dash web app framework](https://dash.plotly.com/)
- [Docker containerization](https://www.docker.com/)

### Get started

Run the following snippet to copy default configuration files. Modify these files as needed to fit your project.

```bash
cp -i builtin/config/.env .env
make get_started
```

#### Environment variables

Environment variables are managed in these files.

- `.env` is for `docker-compose` variables
- `environment/.env` is for production environments
- `environment/.env.dev` is for development/running Quartz as a standalone Flask app
- the development environment activates automatically for VScode users via `.vscode/launch.json`

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
pip install dash dash[celery] dash[diskcache] flask gunicorn pandas plotly pre-commit python-dotenv pyyaml requests sgex
```

#### SGEX config

Quartz uses the SGEX Python package for making Sketch Engine API requests. This requires a `config.yml` file with server names and settings (see SGEX documentation for details). By default, `make get_started` settings only work with a local NoSkE server.

### Build images

Run `docker-compose build` to build a Quartz image and pull the NoSketch Engine Docker image.

### Run NoSketch Engine

Before starting Quartz, run `make noske` to start NoSketch Engine. Be aware that the container may not work if the `CORPORA_DIR` path isn't correct, is empty, or has invalid corpus files. See the NoSketch Engine Docker repo listed earlier for more guidance.

Run `docker stop noske` to stop the container.

### Run Quartz

#### With Gunicorn

Quartz can run like any normal Flask web app as long as `ENVIRONMENT_FILE` is set first: run `ENVIRONMENT_FILE=.env.dev python3 app.py`. VScode users can press `F5` to start the app with debugging enabled.

#### With docker

Run `make quartz` to start Quartz, and to stop the container run `docker stop quartz`.

### Developing Quartz

#### Notes

-
- `.dockerignore` excludes everything by default

## About

Quartz was developed with funding from the [Humanitarian Encyclopedia](https://humanitarianencyclopedia.org) and support from the University of Granada's [LexiCon research group](http://lexicon.ugr.es).

Quartz is possible thanks to the work of [Lexical Computing](https://www.lexicalcomputing.com/), researchers who've [contributed to Sketch Engine](https://www.sketchengine.eu/bibliography-of-sketch-engine/), and the Dockerized version by the Eötvös Loránd University Department of Digital Humanities. NoSketch Engine is available under [GPL licenses](https://nlp.fi.muni.cz/trac/noske).

This app includes [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) and its Docker implementation is based on [this template](https://github.com/CzakoZoltan08/dash-clean-architecture-template). [Dash's community forum](https://community.plotly.com/) also deserves thanks.

The name Quartz is a nod to Sketch Engine's GUI, Crystal.

## Citation

If you use Quartz, please [cite it](/CITATION.cff).
