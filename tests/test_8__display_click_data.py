"""
Test 8: Tooltip Display Logic with `_display_click_data` Function
===========================================================

Description:
------------
This test suite focuses on the `_display_click_data` function, which is responsible for
handling the display of tooltips on the graph when a data point is clicked.

The suite includes:

1. **No Click Data Test:**
    Ensures that if no valid click data is provided (i.e., an empty click event or an
    uninitialized state), the function should not modify the figure.
    If there's no click, there shouldn't be a tooltip.

2. **With Click Data Test:**
    Checks the function's behavior when valid click data is provided.
    The figure should be updated with a new annotation corresponding to the clicked
    data point.

3. **Custom Style Test:**
    Evaluates the function's capability to adapt and display tooltips with
    custom styles. It ensures that the tooltip's appearance aligns with the
    provided custom configurations.

By ensuring that the `_display_click_data` function behaves as expected in these
scenarios, we maintain the tooltip feature's integrity, ensuring that users get
consistent and accurate tooltip displays during interactions.
"""
from typing import Dict, List, Union

import dash
import plotly.graph_objs as go

from dash_tooltip import (  # Adjust the import based on where the function is defined.
    _display_click_data,
)

# Assuming these constants are defined elsewhere in your code or test environment.
SAMPLE_APP = dash.Dash(__name__)
DEFAULT_TEMPLATE = "x: %{x},<br>y: %{y}"
DEFAULT_ANNOTATION_CONFIG = {
    "align": "left",
    "arrowcolor": "black",
    "arrowhead": 3,
    "arrowsize": 1.8,
    "arrowwidth": 1,
    "font": {"color": "black", "family": "Arial", "size": 12},
    "showarrow": True,
    "xanchor": "left",
}


def test_display_click_data_no_click() -> None:
    fig_before = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 3, 2])])

    # Use an empty dictionary as the dummy clickData
    dummy_click_data: Dict[str, List[Dict[str, Union[int, float]]]] = {}

    fig_after = _display_click_data(
        dummy_click_data,
        fig_before,
        SAMPLE_APP,
        DEFAULT_TEMPLATE,
        DEFAULT_ANNOTATION_CONFIG,
        True,
        False,
    )

    assert fig_before == fig_after, "Figures should be identical with no click data."


def test_display_click_data_with_click() -> None:
    fig_before = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 3, 2])])
    click_data = {
        "points": [
            {
                "x": 2,
                "y": 3,
                "curveNumber": 0,
                # ... other potential attributes
            }
        ]
    }
    fig_after = _display_click_data(
        click_data,
        fig_before,
        SAMPLE_APP,
        DEFAULT_TEMPLATE,
        DEFAULT_ANNOTATION_CONFIG,
        True,
        False,
    )
    assert len(fig_after.layout.annotations) == 1, "One annotation should be added."
    assert fig_after.layout.annotations[0].text == "x: 2,<br>y: 3"


def test_display_click_data_custom_style() -> None:
    custom_style = {
        "arrowcolor": "red",
        "font": {"color": "green", "size": 15, "family": "Verdana"},
        "arrowhead": 4,
        "bordercolor": "blue",
    }
    fig_before = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 3, 2])])
    click_data = {
        "points": [
            {
                "x": 2,
                "y": 3,
                "curveNumber": 0,
                # ... other potential attributes
            }
        ]
    }
    fig_after = _display_click_data(
        click_data, fig_before, SAMPLE_APP, DEFAULT_TEMPLATE, custom_style, True, False
    )
    annotation = fig_after.layout.annotations[0]
    assert annotation.arrowcolor == "red", "Arrow color mismatch."
    # Add additional assertions for other styles.
