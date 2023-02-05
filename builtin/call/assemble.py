"""Methods to assemble API calls with parameters from args and a template file."""
import sgex


def freqs_simple(
    query: str, corpus: str, fcrit_attr: str, call_file: str = "builtin/call/freqs.yml"
):
    """Assembles a simple freqs call from parameters and call file.

    Args:
        query: word or phrase to search for.
        corpus: corpus to search in (corresponds to ``corpname``).
        fcrit_attr: attribute (text type) to search in (e.g., ``doc.date``).
        call_file: file with default call parameters (besides)

    Notes:
        - Queries for both word_lc and lemma_lc, e.g., if ``query=eat``, the CQL is
            ``[lc="eat" | lemma_lc="eat"]``.
    """

    query_cql = [f'[lc="{x.strip()}" | lemma_lc="{x.strip()}"]' for x in query.split()]
    dt = sgex.parse(call_file)
    dt["id"]["call"] |= {
        "q": ["q" + "".join(query_cql)],
        "corpname": corpus,
        "fcrit": [f"{fcrit_attr} 0"],
    }
    return dt["id"]
