"""Methods to assemble API calls with parameters from args and a template file."""
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
        "q": simple_query(query),
        "corpname": corpus,
        "fcrit": [f"{fcrit_attr} 0"],
    }
    return dt["id"]


def single_token(query):
    """Converts each token in a query following `simple` SkE query behavior."""
    return [f'[lc="{x.strip()}"|lemma_lc="{x.strip()}"]' for x in query.split()]


def hyphenation(query, mode="simple"):
    """Manages hyphen parsing for queries.

    `simple` mode follows SkE behavior and also searches for hyphens as separate tokens
    (`evidence-based` will also be queried as `evidence` `-` `based`). This is needed
    for corpora compiled with the Stanza NLP package, where hyphens are always separate
    tokens from adjoining words.
    """

    def apart(query):
        return query.replace("-", " ")

    def nospace(query):
        return query.replace("-", "")

    if mode == "asis":
        q = query
    elif mode == "apart":
        q = apart(query)
    elif mode == "asis+apart":
        q = query + "|" + apart(query)
    elif mode == "nospace+asis+apart":
        q = nospace(query) + "|" + apart(query) + "|" + query
    elif mode == "simple":
        if "--" in query:
            # FIXME can't differentiate preferences within a query if it
            # includes a mix of double and single dashes
            query = query.replace("--", "-")
            q = nospace(query) + "|" + apart(query) + "|" + query
        else:
            q = query + "|" + apart(query)
    else:
        raise ValueError(f"Bad hyphen_mode {mode}")
    return q


def simple_query(query: str, hyphen_mode="simple"):
    "Assembles a simple Ske query."

    if "|" in query:
        q = query.split("|")
        for x in range(len(q)):
            if "-" in q[x]:
                q[x] = hyphenation(q[x].strip(), hyphen_mode)
            else:
                q[x] = q[x].strip()
            q[x] = [single_token(y) for y in q[x].split("|")]
            q[x] = ["".join(y) for y in q[x]]
            q[x] = " | ".join(q[x])
        q = " | ".join(q)
    else:
        if "-" in query:
            query = hyphenation(query.strip(), hyphen_mode)
        q = [single_token(x) for x in query.split("|")]
        q = ["".join(x) for x in q]
        q = " | ".join(q)
    q = q.replace("?", ".")
    q = q.replace("*", ".*")
    return ["q" + q]
