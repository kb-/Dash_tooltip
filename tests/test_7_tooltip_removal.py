"""
Test 7: Test tooltip annotation removal
"""
import time

import pytest
from dash import Dash, State, dcc, html
from dash.dependencies import Input, Output
from selenium.common import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app = Dash(__name__)


@app.callback(Output("output-div", "children"), Input("graph-input", "clickData"))
def display_click_data(clickData):
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
                        "x": [1, 2, 3, 4],
                        "y": [4, 5, 6, 2],
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


@pytest.mark.parametrize("iteration", range(3))
@pytest.mark.selenium
def test_annotation_removal(iteration, dash_duo):
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 10)

    # Start the Dash app
    dash_duo.start_server(app)

    # Add tooltips to all points by clicking on them
    for point_index in range(1, 4):
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    f".scatterlayer .trace .points path:nth-of-type({point_index})",
                )
            )
        )

        success = False

        for _ in range(100):
            element = driver.find_element(
                By.CSS_SELECTOR,
                f".scatterlayer .trace .points path:nth-of-type({point_index})",
            )
            ActionChains(driver).move_to_element(element).click().perform()
            time.sleep(0.01)

            # Check if the click was successful by looking for the tooltip
            try:
                WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            f"g.annotation-text-g:nth-of-type({point_index}) text.annotation-text",
                        )
                    )
                )
                success = True
                break
            except TimeoutException:
                continue

        assert (
            success
        ), f"Failed to add tooltip for point {point_index} after multiple attempts."

    # Now, delete the second tooltip
    annotation_element = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "g.annotation-text-g:nth-of-type(2) text.annotation-text")
        )
    )
    ActionChains(driver).move_to_element(annotation_element).click().perform()
    ActionChains(driver).send_keys(Keys.DELETE).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    WebDriverWait(driver, 10).until(staleness_of(annotation_element))

    # Check if the annotation (tooltip) is removed from the graph
    with pytest.raises(EC.NoSuchElementException):
        driver.find_element(
            By.CSS_SELECTOR, "g.annotation-text-g:nth-of-type(2) text.annotation-text"
        )


# Callback to retrieve annotations after a graph relayout
@app.callback(
    Output("annotations-output", "children"),
    Input("graph-input", "relayoutData"),
    State("graph-input", "figure"),
)
def get_annotations(relayoutData, current_figure):
    x_val, y_val = 2, 5  # The coordinates of the data point we're testing
    expected_annotation_text = f"Point: x={x_val}, y={y_val}"

    annotations = current_figure["layout"].get("annotations", [])
    for annotation in annotations:
        if annotation["text"] == expected_annotation_text:
            return "Annotation found!"
    return "Annotation not found!"
