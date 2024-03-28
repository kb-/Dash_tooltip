import time

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pytest
from dash import dcc
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app = dash.Dash(__name__)

# Create the line chart with plotly.graph_objects
x_data_line = ["Jan", "Feb", "Mar", "Apr", "May"]
y_data_line = [10, 15, 13, 17, 20]
line_fig = go.Figure(
    data=go.Scatter(
        x=x_data_line, y=y_data_line, mode="lines+markers", name="Monthly Sales"
    )
)
line_fig.update_layout(
    title="Line Chart Example", xaxis_title="Month", yaxis_title="Sales"
)

# Add the line chart to your Dash app layout
app.layout = dbc.Container(
    [
        # Previous elements...
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="line-chart",
                        figure=line_fig,
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
        # Continue with the rest of the layout...
    ],
    fluid=True,
)

# Apply tooltip customization as needed
tooltip_template_line = "%{name},<br>x: %{x},<br>y: %{y}"
tooltip(app, graph_ids=["line-chart"], template=tooltip_template_line)


@pytest.mark.selenium
def test_line_chart_tooltip(dash_duo):
    dash_duo.start_server(app)

    WebDriverWait(dash_duo.driver, 10).until(
        EC.presence_of_element_located((By.ID, "line-chart"))
    )
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 10)

    success = False  # Flag to indicate if the tooltip was successfully triggered
    actual_annotation_text = None  # Initialize variable to store annotation text

    idx = 1  # Example: Index of the data point to test, adjust based on your data

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
    expected_content_part = (
        f"Monthly Sales,x: {x_data_line[idx - 1]},y: {y_data_line[idx - 1]}"
    )
    assert (
        expected_content_part in actual_annotation_text
    ), "Tooltip content does not match the expected."
