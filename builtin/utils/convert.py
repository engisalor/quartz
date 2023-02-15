"""Functions for converting data types and shapes."""
import pandas as pd


def list_of_dict(ls: list) -> dict:
    """Recursively converts a list of dicts to a dict of lists.

    Notes:
        Returns objects as-is if they're not lists or dicts."""

    def _flatten(ls):
        if not isinstance(ls, list):
            return ls
        else:
            if dict not in [type(x) for x in ls]:
                return ls
            # for [dict, dict, nan] objects
            else:
                # convert nan to empty dict
                ls = [x if isinstance(x, dict) else {} for x in ls]
                # convert list of dicts to dict of lists
                dt = pd.DataFrame(ls).to_dict(orient="list")
                # continue with recursion if needed
                for k, v in dt.items():
                    dt[k] = _flatten(v)
                return dt

    return _flatten(ls)


def multivalue_to_unique(items: list, separator="|"):
    """Takes a list of str with value separators and returns unique values."""

    ls = []
    nested = [x.split(separator) for x in items]
    unnested = [v for ls in nested for v in ls if v]
    ls.extend(unnested)
    return sorted(list(set(ls)))
