import sgex
from dash import html

from builtin.utils import decorator

debug_ske = sgex.parse("builtin/call/debug_ske.yml")
debug_noske = sgex.parse("builtin/call/debug_noske.yml")


def check_call(n_clicks, server, calls):
    @decorator.timer
    def timed_call(params, server):
        return sgex.Call(params, server=server, output="json")

    results = [html.P(f"Clicks: {n_clicks}")]
    for k, v in calls.items():
        job, t = timed_call({k: v}, server)
        results.append(
            html.Div([html.H6(f"{k} ({t:,}s)"), html.P(f"{str(job.data)[:100]}")])
        )
    return html.Div(results)
