"""
Test4a: Multiple Graphs with subplots Test:
Call the tooltip function for an app with multiple graphs and subplots
and verify that tooltips are functional for all graphs.
This ensures that the function can handle multiple graphs on subplots correctly.
"""
import time
from typing import Any

import dash
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import pytest
from dash import dcc, html
from selenium.common import TimeoutException
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
def test_multiple_graph_tooltips(dash_duo: Any) -> None:
    driver = dash_duo.driver
    WebDriverWait(driver, 600)

    # Start the Dash app
    dash_duo.start_server(app)

    # For each graph, interact with a data point to trigger the tooltip
    for graph_id in ["graph-1", "graph-2"]:
        success = False  # flag to indicate if the tooltip was successfully triggered

        for _ in range(100):  # Try up to 100 times
            element = driver.find_element(
                By.CSS_SELECTOR, f"#{graph_id} .scatterlayer .trace .points path"
            )
            ActionChains(driver).move_to_element(element).click().perform()
            time.sleep(0.01)

            # Check if the tooltip is visible
            try:
                WebDriverWait(driver, 1).until(
                    EC.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            f"#{graph_id} g.annotation-text-g text.annotation-text",
                        )
                    )
                )
                success = True  # update the flag
                break  # exit the loop
            except TimeoutException:
                continue  # continue to the next iteration if the condition isn't met

        # Check if the loop exited due to a successful tooltip trigger or if all
        # attempts were exhausted
        assert success, (
            f"Failed to successfully trigger the tooltip for {graph_id}"
            f" after multiple attempts."
        )
