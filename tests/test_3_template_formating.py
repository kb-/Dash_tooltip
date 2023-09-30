"""
Test 3: Template Formatting Test:
Call the tooltip function with a custom template and check if the tooltips are formatted
according to the template.
This ensures that the function respects custom formatting.
"""
import time
from typing import Any, Dict

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import pytest
from dash import dcc, html
from dash.dependencies import Input, Output
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app = dash.Dash(__name__)
graphid_2 = "graph2"


@app.callback(Output("output-div", "children"), Input("graph-input", "clickData"))
def display_click_data(clickData: Dict[str, Any]) -> str:
    if clickData:
        point = clickData["points"][0]
        return f'You clicked on point {point["x"]}, {point["y"]}'
    return "Click on a point to see its data."


np.random.seed(42)
y2 = np.random.normal(0, 10, 50)
x2 = np.arange(0, 50)
custom_labels = [f"Label {i}" for i in range(50)]
fig2 = px.scatter(x=x2, y=y2, custom_data=[custom_labels])
fig2.update_layout(title_text="Editable Title", title_x=0.5)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Single Trace with Custom Data and Stylized Annotations",
                            style={"text-align": "center"},
                        )
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id=graphid_2,
                            figure=fig2,
                            config={
                                "editable": True,
                                "edits": {
                                    "shapePosition": True,
                                    "annotationPosition": True,
                                },
                            },
                        )
                    ]
                )
            ]
        ),
    ]
)

# Tooltip template from dash_tooltip_demo.py
tooltip_template = "x: %{x},<br>y: %{y},<br>%{customdata[0]}"
tooltip(app, template=tooltip_template, debug=True)


@pytest.mark.selenium
def test_customdata_tooltip(dash_duo: Any) -> None:
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 30)

    # Customdata for the data point we're testing
    idx = 1  # Index of the data point
    expected_custom_label = custom_labels[idx]

    # Extract x and y values directly from the data
    x_value = x2[idx]
    y_value = y2[idx]

    expected_annotation_text = (
        tooltip_template.replace("<br>", "")
        .replace("%{x}", str(x_value))
        .replace("%{y}", str(y_value))
        .replace("%{customdata[0]}", expected_custom_label)
    )

    # Start the Dash app
    dash_duo.start_server(app)

    success = False  # flag to indicate if the tooltip was successfully triggered
    actual_annotation_text = None  # Initialize variable to store annotation text

    for _ in range(100):  # Try up to 100 times
        element = dash_duo.driver.find_element(
            By.CSS_SELECTOR, f".scatterlayer .trace .points path:nth-of-type({idx+1})"
        )
        ActionChains(driver).move_to_element(element).click().perform()
        time.sleep(0.01)

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
            success = True  # update the flag
            break  # exit the loop
        except TimeoutException:
            continue  # continue to the next iteration if the condition isn't met

    # Check if the loop exited due to a successful tooltip trigger or if all attempts
    # were exhausted
    assert (
        success
    ), "Failed to successfully trigger the tooltip after multiple attempts."

    # Check if the actual annotation text matches the expected text based on the
    # customdata
    assert actual_annotation_text == expected_annotation_text
