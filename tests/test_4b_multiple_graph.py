"""
Test4b: Multiple Graphs Test:
Call the tooltip function for an app with multiple graphs and verify that tooltips are
functional for all graphs.
This ensures that the function can handle multiple graphs correctly.
"""
import time
from typing import Any

import dash
import numpy as np
import plotly.graph_objects as go
import pytest
from dash import dcc, html
from plotly.subplots import make_subplots
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

# Initialize the Dash app
app = dash.Dash(__name__)

# Generate data for the simple scatter plots
np.random.seed(42)
x1 = np.arange(10)
y1 = np.random.randn(10)
x2 = np.arange(10)
y2 = np.random.randn(10) + 5

fig1 = go.Figure(data=[go.Scatter(x=x1, y=y1, mode="markers")])
fig2 = go.Figure(data=[go.Scatter(x=x2, y=y2, mode="markers")])

# Generate data and create 2x2 subplots
x = np.arange(10)
fig = make_subplots(
    rows=2, cols=2, subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4")
)

fig1.update_layout(height=250, width=400)
fig2.update_layout(height=250, width=400)
fig.update_layout(height=500, width=800)

for i in range(2):
    for j in range(2):
        fig.add_trace(
            go.Scatter(
                x=x,
                y=np.random.randn(10),
                mode="markers",
                name=f"Plot {(i * 2) + j + 1} Trace 1",
            ),
            row=i + 1,
            col=j + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=np.random.randn(10),
                mode="markers",
                name=f"Plot {(i * 2) + j + 1} Trace 2",
            ),
            row=i + 1,
            col=j + 1,
        )

# Define the layout of the app
editable_config = {
    "editable": True,
    "edits": {
        "annotationPosition": True,
        "annotationTail": True,
        "annotationText": True,
    },
}

app.layout = html.Div(
    [
        dcc.Graph(id="graph-1", figure=fig1, config=editable_config),
        dcc.Graph(id="graph-2", figure=fig2, config=editable_config),
        dcc.Graph(id="subplot-graph", figure=fig, config=editable_config),
    ]
)

# Apply tooltips to both graphs
tooltip(app, debug=True)


@pytest.mark.selenium
def test_multiple_graph_tooltips(dash_duo: Any) -> None:
    driver = dash_duo.driver
    driver.set_window_size(1920, 1080)
    # driver.maximize_window() # issue in Debian
    wait = WebDriverWait(driver, 30)

    # Start the Dash app
    dash_duo.start_server(app)

    # Helper function to perform the retry click
    def perform_retry_click(element: WebElement) -> bool:
        success = False
        for _ in range(100):
            ActionChains(driver).move_to_element(element).click().perform()
            time.sleep(0.01)  # This ensures the UI has a moment to update

            # Check if the annotation appeared to confirm the click was successful
            if element.is_displayed():
                success = True
                break

        return success

    # For each graph, interact with a data point to trigger the tooltip
    for graph_id in ["graph-1", "graph-2", "subplot-graph"]:
        if graph_id == "subplot-graph":
            # Handle subplots differently. Interact with each subplot.
            subplots = ["xy", "x2y2", "x3y3", "x4y4"]

            for subplot in subplots:
                # Interact with a data point in the current subplot
                element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            f"#{graph_id} .{subplot} .scatterlayer .trace .points path",
                        )
                    )
                )
                assert perform_retry_click(
                    element
                ), f"Failed to click on {subplot} in {graph_id}"

                # Wait for the tooltip's annotation to appear and ensure it's visible
                annotation_element = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, f"#{graph_id} .{subplot}")
                    )
                )
                assert annotation_element.is_displayed()

        else:
            element = driver.find_element(
                By.CSS_SELECTOR, f"#{graph_id} .scatterlayer .trace .points path"
            )
            assert perform_retry_click(element), f"Failed to click on {graph_id}"

            # Check the tooltip's presence
            annotation_element = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        f"#{graph_id} g.annotation-text-g text.annotation-text",
                    )
                )
            )
            assert annotation_element.is_displayed()
