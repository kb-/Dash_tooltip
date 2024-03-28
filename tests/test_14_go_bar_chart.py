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

# Create the bar chart with plotly.graph_objects
categories = ["Category A", "Category B", "Category C"]
values = [100, 200, 150]
bar_fig = go.Figure(data=go.Bar(x=categories, y=values, name="Sales by Category"))
bar_fig.update_layout(
    title="Bar Chart Example", xaxis_title="Category", yaxis_title="Sales"
)

# Add the bar chart to your Dash app layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id="bar-chart",
                    figure=bar_fig,
                    config={
                        "editable": True,
                        "edits": {
                            "shapePosition": True,
                            "annotationPosition": True,
                        },
                    },
                )
            )
        ),
        # Include other elements as necessary...
    ],
    fluid=True,
)

# Apply tooltip customization
tooltip_template_bar = "%{name},<br>x: %{x},<br>y: %{y}"
tooltip(app, graph_ids=["bar-chart"], template=tooltip_template_bar)


@pytest.mark.selenium
def test_bar_chart_tooltip(dash_duo):
    dash_duo.start_server(app)

    WebDriverWait(dash_duo.driver, 10).until(
        EC.presence_of_element_located((By.ID, "bar-chart"))
    )
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 10)

    success = False  # Flag to indicate if the tooltip was successfully triggered
    actual_annotation_text = None  # Initialize variable to store annotation text

    idx = 1  # Adjust based on which bar you'd like to test

    for attempt in range(100):  # Try up to 100 times to trigger tooltip
        element = driver.find_element(
            By.CSS_SELECTOR,
            f".barlayer .trace.bars:nth-child(1) .point:nth-of-type({idx})",
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
            actual_annotation_text = annotation_element.text  # Get the text content
            success = True  # Update the flag
            break  # Exit the loop
        except TimeoutException:
            continue  # Continue to the next iteration if the condition isn't met

    assert (
        success
    ), "Failed to successfully trigger the tooltip after multiple attempts."
    # Define the expected content based on the tooltip template and data point
    expected_content_part = (
        f"Sales by Category,x: {categories[idx - 1]},y: {values[idx - 1]}"
    )
    assert (
        expected_content_part in actual_annotation_text
    ), "Tooltip content does not match the expected."
