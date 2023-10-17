# Quartz

Quartz is a container app for visualizing corpus data from Sketch Engine servers. It's a portable alternate interface that focuses on graphing quantitative data for linguistic analysis. Set up access to your corpora, make API queries to a Sketch Engine or NoSketch Engine server, and view results with interactive graphs.

Some default graphing features are included, but the repo is designed for adaptation to specific projects. Quartz is made with Python, the Dash framework and Docker. To use it you'll need API access to a Sketch Engine or NoSketch Engine server.

## Installation

Python dependencies:

`dash dash-bootstrap-components flask gunicorn plotly sgex`

Related software:

- [Sketch Engine](https://www.sketchengine.eu/)
- [NoSketch Engine](https://nlp.fi.muni.cz/trac/noske)
- [NoSketch Engine Docker](https://github.com/ELTE-DH/NoSketch-Engine-Docker)
- [Sketch Grammar Explorer](https://github.com/engisalor/sketch-grammar-explorer)
- [Plotly graphing library](https://plotly.com/python/)
- [Dash web app framework](https://dash.plotly.com/)
- [Docker containerization](https://www.docker.com/)

## Getting started

### Simply put

1. Clone the repo
2. Set up environment variables in `.env` (use `.env-example` to get started)
3. Set up configuration files in `config/` and make a `data/` directory for storing data
4. Option 1: run Quartz directly Flask app for testing or local usage without Docker
5. Option 2: build and use the Docker image `docker-compose up`
6. Visit the app at `http://127.0.0.1:8080/` and make corpus queries

### Also consider

To make queries to the Sketch Engine server, get an [API key](https://www.sketchengine.eu/documentation/api-documentation/).

To work with your own server, check out NoSketch Engine.

The example below uses the Susanne corpus on Sketch Engine, although any corpus on any (No)SkE server should work in principle. Review Sketch Engine's [fair use policy](https://www.sketchengine.eu/fair-use-policy/) before making calls.

>Warning: Quartz expects the (No)SkE server to be available when the app/container is first started and fails if otherwise. On startup it makes initial API calls to collect corpus information. Once those calls are cached, having server access isn't technically required.

### Environment variables

Quartz expects a few environment variables to be available. Set these up by renaming `.env-example` to `.env` and adapt as needed.

Key environment variables:

1. A YAML configuration file is needed to define which corpora are available
    - `CORPORA_YML=config/corpora-ske.yml`
2. A server to interact with
    - `SGEX_SERVER=ske` points to Sketch Engine's server
    - `SGEX_SERVER=https://api.sketchengine.eu/bonito/run.cgi` or use a full URL to a server
3. A username and API key for the server, if required
    - `SGEX_API_KEY="<KEY>"`
    - `SGEX_USERNAME="<USER>"`
4. Bind paths for configuration and data files
    - `CONFIG_DIR=/current/working/directory/config`
    - `DATA_DIR=/current/working/directory/data`

### Corpora configuration file

A YAML file is needed with details about each corpus to include in Quartz: see [config/corpora-ske.yml](/config/corpora-ske.yml) for an example. Several entries are needed to define how to access the corpus via API, interpret and label its attributes (text types), and make attributes comparable with those in other corpora (if applicable).

```yaml
preloaded/susanne:
  # name shown in graphs
  name: Susanne
  # corpus description file (optional)
  md_file: config/susanne.md
  # text types to exclude
  exclude:
    - doc.wordcount
    - font.type
  # text type labels (for cleaner in-app display and mapping to comparable attributes)
  label:
    doc.file: file
    doc.n: "n"
    head.type: head
```

### Trying out the app

Once `.env` and the YAML configuration file are ready, start the app and make a query, for example `with; without`. Two bar graphs will appear showing frequencies in the Susanne corpus in several text types. There's currently a page for making queries, one for inspecting corpora, and a user guide.

![image](/quartz-app.png)

Quartz can be used without much knowledge of corpus linguistics, but a range of complex corpus queries are also possible. That said, interpreting results is a question left to the researcher: Quartz just visualizes frequency data. It's a good idea to check its results directly in Sketch Engine to ensure frequencies are computed properly (so far it's been reliable for hundreds of queries).

### Development

API-based data collection requires understanding the [Sketch Grammar Explorer](https://github.com/engisalor/sketch-grammar-explorer) package (SGEX, a Sketch Engine API wrapper); try it out as a standalone tool if you plan on doing custom data processing. Also see [pages/freqs_viz.py](/pages/freqs_viz.py) for examples of how to make custom visualizations.

## About

Quartz was developed with funding from the [Humanitarian Encyclopedia](https://humanitarianencyclopedia.org) and support from the University of Granada [LexiCon research group](http://lexicon.ugr.es). It's the upstream repository for the [Humanitarian Encyclopedia Dashboard](https://humanitarianencyclopedia.org/analysis) ([GitHub repo](https://github.com/Humanitarian-Encyclopedia/he-dashboard)). If you're interested in the Dashboard or studying humanitarian discourse, make a free account at the Encyclopedia to try it out.

Quartz relies on APIs made available thanks to the work of [Lexical Computing](https://www.lexicalcomputing.com/) and [Sketch Engine contributors](https://www.sketchengine.eu/bibliography-of-sketch-engine/). The [Docker image](https://github.com/ELTE-DH/NoSketch-Engine-Docker) from Eötvös Loránd University Department of Digital Humanities has also been utilized.

This app includes [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/); also check out [Dash's community forum](https://community.plotly.com/) for tips on visualization techniques.

The name Quartz is a nod to Sketch Engine's GUI, Crystal.

## Citation

If you use Quartz, please [cite it](/CITATION.cff).
