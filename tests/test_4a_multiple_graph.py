"""
Test4a: Multiple Graphs with subplots Test:
Call the tooltip function for an app with multiple graphs and subplots
and verify that tooltips are functional for all graphs.
This ensures that the function can handle multiple graphs on subplots correctly.
"""

import dash
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import pytest
from dash import dcc, html
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

# Sample data
date_rng = pd.date_range(start="2020-01-01", end="2020-12-31", freq="m")
ts_data = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create a Dash app with multiple graphs
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(
            id="graph-1",
            figure={
                "data": [go.Scatter(x=date_rng, y=ts_data)],
                "layout": go.Layout(title="Graph 1"),
            },
        ),
        dcc.Graph(
            id="graph-2",
            figure={
                "data": [go.Scatter(x=date_rng, y=ts_data)],
                "layout": go.Layout(title="Graph 2"),
            },
        ),
    ]
)

# Apply tooltips to both graphs
tooltip(app, graph_ids=["graph-1", "graph-2"], style={"font": {"size": 10}})


@pytest.mark.selenium
def test_multiple_graph_tooltips(dash_duo):
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 600)

    # Start the Dash app
    dash_duo.start_server(app)

    # For each graph, interact with a data point to trigger the tooltip
    for graph_id in ["graph-1", "graph-2"]:
        element = driver.find_element(
            By.CSS_SELECTOR, f"#{graph_id} .scatterlayer .trace .points path"
        )
        ActionChains(driver).move_to_element(element).click().perform()

        # Check the tooltip's presence
        annotation_element = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f"#{graph_id} g.annotation-text-g text.annotation-text",
                )
            )
        )

        # Assert the presence of the tooltip
        assert annotation_element is not None

        # Close the tooltip to check the next one
        close_element = driver.find_element(
            By.CSS_SELECTOR, f"#{graph_id} g.annotation .cursor-pointer"
        )
        ActionChains(driver).move_to_element(close_element).click().perform()
