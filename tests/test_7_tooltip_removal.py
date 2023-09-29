"""
Test 7: Test tooltip annotation

This test aims to validate the tooltip annotation functionality of a Dash app.
The primary objectives are:
1. Verify that tooltips can be added to data points on a scatter plot by clicking
   on them.
2. Ensure that a tooltip, once added, can be deleted.
3. Validate that, after the tooltip's deletion, the number of tooltips decreases by one.

Steps:
1. Start the Dash app.
2. Iteratively click on data points to add tooltips.
3. After adding tooltips, count the total number of tooltips.
4. Delete a specific tooltip.
5. Count the number of tooltips again and validate that it has decreased by one.
"""
import time
from typing import Any, Dict

import pytest
from dash import Dash, dcc, html
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
graph_id = "graph-input"


@app.callback(Output("output-div", "children"), Input(graph_id, "clickData"))
def display_click_data(clickData: Dict[str, Any]) -> str:
    if clickData:
        point = clickData["points"][0]
        return f'You clicked on point ({point["x"]}, {point["y"]})'
    return "Click on a point to see its data."


app.layout = html.Div(
    [
        dcc.Graph(
            id=graph_id,
            figure={
                "data": [
                    {
                        "mode": "markers",
                        "type": "scatter",
                        "x": [1, 2, 3, 4],
                        "y": [4, 5, 1, 2],
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
def test_annotation_removal(iteration: int, dash_duo: Any) -> None:
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 600)

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
                            f'g.annotation[data-index="{point_index-1}"] '
                            f"g.annotation-text-g text.annotation-text",
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

    # Count the number of tooltips before deletion
    initial_tooltips_count = len(driver.find_elements(By.CSS_SELECTOR, "g.annotation"))

    # Now, delete the second tooltip
    annotation_element = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'g.annotation[data-index="1"] text.annotation-text')
        )
    )
    ActionChains(driver).move_to_element(annotation_element).click().perform()
    ActionChains(driver).send_keys(Keys.DELETE).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    WebDriverWait(driver, 10).until(staleness_of(annotation_element))

    # Custom waiting condition for the tooltips count to decrease by one
    def tooltips_count_decreased(driver):
        current_count = len(driver.find_elements(By.CSS_SELECTOR, "g.annotation"))
        return current_count == initial_tooltips_count - 1

    # Wait for the condition to be satisfied
    wait.until(tooltips_count_decreased)

    # Count the number of tooltips after deletion
    final_tooltips_count = len(driver.find_elements(By.CSS_SELECTOR, "g.annotation"))

    # Verify that one tooltip was deleted
    assert (
        final_tooltips_count == initial_tooltips_count - 1
    ), "Tooltip was not deleted."
