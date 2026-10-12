"""
Demo 13: Direct figure definition in dcc.Graph with Draggable Annotations
This test checks the functionality of a graph where data is directly injected
as a np.array into dcc. Graph and has draggable annotations.
"""

from typing import Any

import dash_bootstrap_components as dbc
import numpy as np
import pytest
from dash import Dash, dcc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app13 = Dash(__name__)

np.random.seed(20)
y1 = np.random.normal(0, 10, 15)
x1 = np.arange(0, 15)

app13.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="example-graph",
                            figure={
                                "data": [
                                    {
                                        "x": x1,
                                        "y": y1,
                                        "type": "scatter",
                                        "marker": {"size": 12},
                                        "mode": "lines+markers",
                                        "name": "sin(x)",
                                    }
                                ],
                                "layout": {
                                    "title": "Direct np.array Injection into dcc.Graph with Draggable Annotations"
                                },
                            },
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

# Add the tooltip functionality to the app
tooltip(app13)


@pytest.mark.parametrize("iteration", range(1))
@pytest.mark.selenium
def test_direct_data_injection(iteration: int, dash_duo: Any) -> None:
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 15)

    # Define expected values
    x_val, y_val = x1[10], y1[10]  # The coordinates of the data point we're testing
    expected_annotation_text = f"x: {x_val},y: {y_val}"

    # Start the Dash app
    dash_duo.start_server(app13)

    element = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".scatterlayer .trace .points path:nth-of-type(11)"))
    )
    ActionChains(driver).move_to_element(element).perform()
    wait.until(
        lambda d: d.execute_script(
            """
            const gd = document.querySelector('#example-graph .js-plotly-plot');
            return gd._hoverdata && gd._hoverdata.some(p => p.x === arguments[0]);
            """,
            int(x_val),
        )
    )
    ActionChains(driver).click().perform()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "g.annotation-text-g text.annotation-text")))

    # Check if the tooltip annotation has the expected text
    annotation_text_element = driver.find_element(By.CSS_SELECTOR, "g.annotation-text-g text.annotation-text")
    actual_annotation_text = annotation_text_element.text
    assert actual_annotation_text == expected_annotation_text
