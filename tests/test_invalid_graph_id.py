import dash
import pytest
from dash import html

from dash_tooltip import tooltip

# Create a simple Dash app
app = dash.Dash(__name__)
app.layout = html.Div([])  # Empty layout


def test_invalid_graph_id() -> None:
    with pytest.raises(ValueError, match="Invalid graph ID provided: invalid-graph-id"):
        # Call the tooltip function with an invalid graph ID
        tooltip(app, graph_ids=["invalid-graph-id"])
