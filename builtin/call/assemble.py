"""Methods to assemble API calls with parameters from args and a template file."""
import re

import sgex


def freqs_simple(
    query: str, corpus: str, fcrit_attr: str, call_file: str = "builtin/call/freqs.yml"
):
    """Assembles a simple `freqs` call from parameters and call file.

    Args:
        query: word or phrase to search for.
        corpus: corpus to search in (corresponds to ``corpname``).
        fcrit_attr: attribute (text type) to search in (e.g., ``doc.date``).
        call_file: path to file with default call parameters.
    """

    dt = sgex.parse(call_file)
    dt["id"]["call"] |= {
        "q": [simple_query(query)],
        "corpname": corpus,
        "fcrit": [f"{fcrit_attr} 0"],
    }
    return dt["id"]


def phrase_to_cql(phrase):
    """Converts each phrase in a query following `simple` SkE query behavior."""
    words = [x for x in phrase.split() if x]
    return " ".join([f'[lc="{w.strip()}" | lemma_lc="{w.strip()}"]' for w in words])


def apart(query):
    return query.replace("-", " ").replace("  ", " ")


def nospace(query):
    return query.replace("-", "")


def joined(query):
    return query.replace("--", "-")


def atomic(query):
    return " ".join(re.split("(-)", query)).replace("-  -", "-")


def if_atomic(query, atomic_hyphens):
    if atomic_hyphens:
        return atomic(query)
    else:
        return None


def query_to_dict(query: str, atomic_hyphens=True):
    "Decomposes a query string into a dict of components."

    query = query.strip().split("|")
    queries = {}
    for x in range(len((query))):
        q = query[x].strip()
        queries[x] = {}
        q = query[x].split()
        for y in range(len(q)):
            queries[x][y] = []
            if "--" in q[y]:
                queries[x][y] = [
                    nospace(q[y]),
                    apart(q[y]),
                    joined(q[y]),
                    if_atomic(q[y], atomic_hyphens),
                ]
            elif "-" in q[y]:
                queries[x][y] = [q[y], if_atomic(q[y], atomic_hyphens)]
            else:
                queries[x][y] = [q[y]]
            queries[x][y] = [a for a in queries[x][y] if a]
    return queries


def simple_query(query: str, atomic_hyphens=True):
    """Converts a query into CQL following SkE `simple` behavior."""
    queries = query_to_dict(query, atomic_hyphens)
    dt = queries.copy()
    all = []
    for v in dt.values():
        ls = []
        for c in v.keys():
            v[c] = [phrase_to_cql(phrase) for phrase in v[c]]
            if len(v[c]) > 1:
                v[c] = "( " + " | ".join(v[c]) + " )"
            else:
                v[c] = " | ".join(v[c])
            ls.append(v[c])
        all.append("".join(ls))
    cql = "q" + "|".join(all)
    cql = cql.replace("*", ".*").replace("?", ".")
    return cql
