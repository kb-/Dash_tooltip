"""Coordinate and callback regressions shared by the log-axis demos."""

from copy import deepcopy

import plotly.graph_objects as go
import pytest
from dash import Dash, dcc, html

import dash_tooltip
from dash_tooltip import CustomFigure, tooltip
from dash_tooltip.utils import _display_click_data, get_axis_type


def click_data(x=100, y=1000):
    return {"points": [{"curveNumber": 0, "pointNumber": 0, "x": x, "y": y}]}


@pytest.mark.parametrize("references", [(None, None), ("x", "y"), ("x2", "y2"), ("x10", "y10")])
@pytest.mark.parametrize("log_axes", ["x", "y", "xy"])
@pytest.mark.parametrize("updated", [False, True], ids=["static", "updated"])
@pytest.mark.parametrize("apply_log_fix", [None, True, False], ids=["default", "enabled", "disabled"])
def test_new_tooltip_uses_current_axis_coordinates(references, log_axes, updated, apply_log_fix):
    xref, yref = references
    fig = CustomFigure(go.Scatter(x=[100], y=[1000], xaxis=xref, yaxis=yref))
    for letter, reference in zip("xy", references):
        axis_key = letter + "axis" + (reference or letter)[1:]
        fig.update_layout(**{axis_key: {"type": "linear" if updated or letter not in log_axes else "log"}})
    if updated:
        if "x" in log_axes:
            fig.update_xaxes(type="log")
        if "y" in log_axes:
            fig.update_yaxes(type="log")

    kwargs = {} if apply_log_fix is None else {"apply_log_fix": apply_log_fix}
    data = click_data()
    result = _display_click_data(data, fig, "x: %{x}<br>y: %{y:.2f}", {}, **kwargs)
    annotation = result.layout.annotations[0]
    assert annotation.x == (2 if "x" in log_axes and apply_log_fix is not False else 100)
    assert annotation.y == (3 if "y" in log_axes and apply_log_fix is not False else 1000)
    assert (annotation.xref, annotation.yref) == (xref or "x", yref or "y")
    assert annotation.text == "x: 100<br>y: 1000.00"
    assert data["points"][0]["x"] == 100
    assert data["points"][0]["y"] == 1000
    _display_click_data(data, result, "Changed template", {}, **kwargs)
    assert len(result.layout.annotations) == 1


@pytest.mark.parametrize("reference", ["x", "y", "x2", "y10"])
def test_missing_axis_type_is_non_logarithmic(reference):
    assert get_axis_type(CustomFigure(), reference) == "linear"


@pytest.mark.parametrize("representation", ["custom", "dict"])
@pytest.mark.parametrize("axis_type", ["linear", "log"])
def test_splom_without_scalar_axis_properties_uses_default_axes(representation, axis_type):
    figure = CustomFigure(
        go.Splom(
            dimensions=[dict(label="X", values=[100]), dict(label="Y", values=[1000])],
            meta=["metadata"],
            name="Matrix",
        )
    )
    figure.update_xaxes(type=axis_type)
    figure.update_yaxes(type=axis_type)
    if representation == "dict":
        figure = figure.to_dict()

    result = _display_click_data(click_data(), figure, "%{name}: %{meta[0]} x: %{x} y: %{y}", {})

    annotation = result.layout.annotations[0]
    assert (annotation.xref, annotation.yref) == ("x", "y")
    assert (annotation.x, annotation.y) == ((2, 3) if axis_type == "log" else (100, 1000))
    assert annotation.text == "Matrix: metadata x: 100 y: 1000"


@pytest.mark.parametrize("axis", ["x", "y"])
@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_invalid_log_coordinate_does_not_add_partial_annotation(axis, value, caplog, monkeypatch):
    fig = CustomFigure(go.Scatter(x=[100], y=[1000]))
    fig.update_xaxes(type="log")
    fig.update_yaxes(type="log")
    fig.add_annotation(x=1, y=1, xref="x", yref="y", text="Existing")
    before = deepcopy(fig.to_dict())
    data = click_data()
    data["points"][0][axis] = value
    monkeypatch.setattr(dash_tooltip.logger, "propagate", True)
    with caplog.at_level("WARNING", logger="dash_tooltip"):
        result = _display_click_data(data, fig, "x: %{x}<br>y: %{y}", {})
    assert result.to_dict() == before
    assert "Skipping tooltip with invalid log coordinates" in caplog.text


@pytest.mark.parametrize("apply_log_fix", [None, True, False], ids=["default", "enabled", "disabled"])
@pytest.mark.parametrize("axis", ["x", "y"])
def test_dash_click_callback_uses_updated_figure(axis, apply_log_fix):
    graph_id = "callback-log-{}-{}".format(axis, apply_log_fix)
    fig = go.Figure(go.Scatter(x=[100], y=[1000]))
    fig.update_xaxes(type="linear")
    fig.update_yaxes(type="linear")
    app = Dash(__name__)
    app.layout = html.Div([dcc.Graph(id=graph_id, figure=fig)])
    kwargs = {} if apply_log_fix is None else {"apply_log_fix": apply_log_fix}
    tooltip(app, graph_ids=[graph_id], **kwargs)
    if axis == "x":
        fig.update_xaxes(type="log")
    else:
        fig.update_yaxes(type="log")
    payload = {
        "output": graph_id + ".figure",
        "outputs": {"id": graph_id, "property": "figure"},
        "inputs": [{"id": graph_id, "property": "clickData", "value": click_data()}],
        "state": [{"id": graph_id, "property": "figure", "value": fig.to_dict()}],
        "changedPropIds": [graph_id + ".clickData"],
    }
    response = app.server.test_client().post("/_dash-update-component", json=payload)
    assert response.status_code == 200
    figure = response.get_json()["response"][graph_id]["figure"]
    annotation = figure["layout"]["annotations"][0]
    expected = (2 if axis == "x" else 3) if apply_log_fix is not False else (100 if axis == "x" else 1000)
    assert annotation[axis] == expected
    assert (annotation["xref"], annotation["yref"]) == ("x", "y")


@pytest.mark.parametrize("representation", ["custom", "dict", "plotly"])
@pytest.mark.parametrize("apply_log_fix", [True, False])
def test_manager_forwards_conversion_option_for_each_figure_representation(representation, apply_log_fix):
    graph_id = "representation-{}-{}".format(representation, apply_log_fix)
    figure = CustomFigure(go.Scatter(x=[100], y=[1000]))
    figure.update_yaxes(type="log")
    app = Dash(__name__)
    app.layout = html.Div([dcc.Graph(id=graph_id, figure=figure)])
    tooltip(app, graph_ids=[graph_id], apply_log_fix=apply_log_fix)
    if representation == "dict":
        figure = figure.to_dict()
    elif representation == "plotly":
        figure = go.Figure(figure)
    callback = app.callback_map[graph_id + ".figure"]["callback"].__wrapped__
    result = callback(click_data(), figure)
    assert result.layout.annotations[0].y == (3 if apply_log_fix else 1000)


def test_adding_tooltip_after_scale_change_preserves_existing_annotations():
    fig = CustomFigure(go.Scatter(x=[100], y=[1000]))
    fig.update_yaxes(type="linear")
    fig.add_annotation(x=50, y=500, xref="x", yref="y", text="User annotation", ax=20, ay=-30)
    existing = fig.layout.annotations[0].to_plotly_json()
    fig.update_yaxes(type="log")
    _display_click_data(click_data(), fig, "y: %{y}", {})
    assert fig.layout.annotations[0].to_plotly_json() == existing
    assert fig.layout.annotations[1].y == 3
