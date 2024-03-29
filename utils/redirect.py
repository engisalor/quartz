"""Manage app URL redirection and parsing search parameters."""
import logging

import dash
from flask import redirect, request

from settings import corp_data, env, stats


def global_policy():
    """Basic policy used across the app (points to page-specific policies)."""
    page_registry = dict(dash.page_registry.items())
    paths = [v["path"] for v in page_registry.values()]
    # ignore unrelated requests
    if request.path not in paths:
        return None
    # ignore if no args
    dt = request.args.to_dict()
    if not bool(dt):
        return None
    # policies for each page
    if request.path == "/":
        return frequencies_policy(dt)


def frequencies_policy(dt):
    # unsupported args
    supported = ["attribute", "corpora", "query", "statistics", "attribute_filter"]
    if [x for x in dt.keys() if x not in supported]:
        logging.debug(f"reject args: {dt.keys()}")
        return redirect(request.path)
    # too many combined queries
    if dt["query"].count(";") > env.MAX_QUERIES:
        logging.debug(f'reject N queries: {dt["query"]}')
        return redirect(request.path)
    # unsupported corpora
    for corpus in dt["corpora"].split(";"):
        if corpus not in corp_data.dt.keys():
            logging.debug(f"reject corpus: {corpus}")
            return redirect(request.path)
    # unsupported statistics
    for stat in dt["statistics"].split(";"):
        if stat not in stats.keys():
            logging.debug(f"reject statistic: {stat}")
            return redirect(request.path)


def corpora(corpora):
    # default to first corpus
    if not len(corpora):
        corpora = [k for k in corp_data.dt.keys()]
        return [corpora[0]]
    else:
        return corpora.split(";")


def sort(sort):
    # limit to one of two options
    if sort not in ["frq", "rel"]:
        return env.SORTING
    else:
        return sort


def page(page):
    # limit to one of two options
    if not page or not isinstance(page, int):
        return 1
    if page < 1:
        return 1
    else:
        return page


def statistics(statistics):
    # default to first statistic
    if not len(statistics):
        return [list(stats.keys())[0]]
    else:
        return statistics.split(";")


def attribute(attribute):
    # prohibit multiple attribute values
    if isinstance(attribute, list):
        if len(attribute):
            return attribute[0]
        else:
            return ""
    elif len(attribute):
        if len(attribute.split(";")) > 1:
            return attribute.split(";")[0]
        return attribute
    else:
        return ""


def attribute_filter(attribute_filter):
    # default to no filter
    if not len(attribute_filter):
        return []
    else:
        return attribute_filter.split(";")
