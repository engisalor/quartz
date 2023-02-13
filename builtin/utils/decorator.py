"""Decorator functions."""
import functools
import logging
import time


def timer(func):
    """Times a function and returns a tuple of (return of func, n_seconds)."""

    @functools.wraps(func)
    def _timit(*args, **kwargs):
        t0 = time.perf_counter()
        item = func(*args, **kwargs)
        t1 = time.perf_counter()
        n_seconds = t1 - t0
        return item, round(n_seconds, 2)

    return _timit


def timer_log(func):
    """Times a function and logs its duration."""

    @functools.wraps(func)
    def _timit(*args, **kwargs):
        t0 = time.perf_counter()
        item = func(*args, **kwargs)
        t1 = time.perf_counter()
        n_seconds = round(t1 - t0, 6)
        logging.debug(f"{func.__name__} {n_seconds}")
        return item

    return _timit


def while_loop(func):
    """Repeats a function until it returns False."""

    @functools.wraps(func)
    def _while_loop(*args, **kwargs):
        repeat = True
        while repeat:
            repeat = func(*args, **kwargs)

    return _while_loop
