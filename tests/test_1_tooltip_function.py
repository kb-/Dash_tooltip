"""
Test 1: Basic Usage Test:
Call the tooltip function with minimal arguments and check if it returns without errors.
This tests the basic functionality and setup of tooltips.
Run multiple times because of variability in click results
"""
import time
from typing import Any, Dict

import pytest
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app = Dash(__name__)


@app.callback(Output("output-div", "children"), Input("graph-input", "clickData"))
def display_click_data(clickData: Dict[str, Any]) -> str:
    if clickData:
        point = clickData["points"][0]
        return f'You clicked on point ({point["x"]}, {point["y"]})'
    return "Click on a point to see its data."


app.layout = html.Div(
    [
        dcc.Graph(
            id="graph-input",
            figure={
                "data": [
                    {
                        "mode": "markers",
                        "type": "scatter",
                        "x": [1, 2, 3],
                        "y": [4, 5, 6],
                    }
                ],
                "layout": {},
            },
            config={"editable": True, "edits": {"annotationPosition": True}},
        ),
        html.Div(id="output-div"),
    ]
)

# Set up tooltip functionality for the app
tooltip_template = "Point: x=%{x}, y=%{y}"
tooltip(app, template=tooltip_template)


@pytest.mark.parametrize("iteration", range(1))
@pytest.mark.selenium
def test_basic_usage(iteration: int, dash_duo: Any) -> None:
    driver = dash_duo.driver
    WebDriverWait(driver, 600)

    # Tooltip template
    x_val, y_val = 2, 5  # The coordinates of the data point we're testing
    expected_annotation_text = tooltip_template.replace("%{x}", str(x_val)).replace(
        "%{y}", str(y_val)
    )

    # Start the Dash app
    dash_duo.start_server(app)

    # Ensure the element is clickable before interacting
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".scatterlayer .trace .points path:nth-of-type(2)")
        )
    )

    success = False  # flag to indicate if the click was successful

    for _ in range(100):  # Try up to 100 times (clicks sometimes not detected)
        element = driver.find_element(
            By.CSS_SELECTOR, ".scatterlayer .trace .points path:nth-of-type(2)"
        )
        ActionChains(driver).move_to_element(element).click().perform()
        time.sleep(0.01)

        # Check if the click was successful
        try:
            WebDriverWait(driver, 1).until(
                EC.text_to_be_present_in_element(
                    (By.ID, "output-div"), "You clicked on point (2, 5)"
                )
            )
            success = True  # update the flag
            break  # exit the loop
        except TimeoutException:
            continue  # continue to the next iteration if the condition isn't met

    # Check if the loop exited due to a successful click or if all attempts were
    # exhausted
    assert success, "Failed to successfully click the point after multiple attempts."

    # Remaining test steps
    annotation_text_element = driver.find_element(
        By.CSS_SELECTOR, "g.annotation-text-g text.annotation-text"
    )
    actual_annotation_text = annotation_text_element.text
    assert actual_annotation_text == expected_annotation_text
