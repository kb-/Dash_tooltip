import time

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pytest
from dash import dcc, html
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app = dash.Dash(__name__)

# Create the scatter plot with plotly.graph_objects
x_data = [1, 2, 3, 4, 5]
y_data = [2, 3, 5, 7, 11]
scatter_fig = go.Figure(
    data=go.Scatter(x=x_data, y=y_data, mode="markers", name="Data Points")
)
scatter_fig.update_layout(
    title="Scatter Plot Example", xaxis_title="X Axis Label", yaxis_title="Y Axis Label"
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="scatter-plot",
                        figure=scatter_fig,
                        config={
                            "editable": True,
                            "edits": {
                                "shapePosition": True,
                                "annotationPosition": True,
                            },
                        },
                    )
                )
            ]
        ),
        html.Div(id="output-div"),
    ],
    fluid=True,
)

# Assuming a tooltip template similar to what was previously described
tooltip_template = "%{name},<br>x: %{x},<br>y: %{y:.2f}"
tooltip(app, graph_ids=["scatter-plot"], template=tooltip_template)


@pytest.mark.selenium
def test_customdata_tooltip(dash_duo):
    dash_duo.start_server(app)

    WebDriverWait(dash_duo.driver, 10).until(
        EC.presence_of_element_located((By.ID, "scatter-plot"))
    )
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 10)

    success = False  # Flag to indicate if the tooltip was successfully triggered
    actual_annotation_text = None  # Initialize variable to store annotation text

    idx = 1  # Index of the data point to test

    for attempt in range(100):  # Try up to 100 times
        element = driver.find_element(
            By.CSS_SELECTOR, f".scatterlayer .trace .points path:nth-of-type({idx})"
        )
        ActionChains(driver).move_to_element(element).click().perform()
        time.sleep(0.01)  # Short pause to allow tooltip to appear

        # Check if the tooltip is visible
        try:
            annotation_element = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "g.annotation-text-g text.annotation-text")
                )
            )
            actual_annotation_text = (
                annotation_element.text
            )  # Get the text content of the annotation element
            success = True  # Update the flag
            break  # Exit the loop
        except TimeoutException:
            continue  # Continue to the next iteration if the condition isn't met

    assert (
        success
    ), "Failed to successfully trigger the tooltip after multiple attempts."
    # Define the expected part of the tooltip text based on your tooltip_template and the data point
    expected_content_part = f"Data Points,x: {x_data[idx - 1]},y: {y_data[idx - 1]:.2f}"
    assert (
        expected_content_part in actual_annotation_text
    ), "Tooltip content does not match the expected."
