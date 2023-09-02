"""
Test 1: Basic Usage Test:
Call the tooltip function with minimal arguments and check if it returns without errors.
This tests the basic functionality and setup of tooltips.
"""

import time
import pytest
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_tooltip import tooltip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json

app = dash.Dash(__name__)

@app.callback(
    Output('output-div', 'children'),
    Input('graph-input', 'clickData')
)
def display_click_data(clickData):
    if clickData:
        point = clickData['points'][0]
        return f'You clicked on point ({point["x"]}, {point["y"]})'
    return 'Click on a point to see its data.'

app.layout = html.Div([
    dcc.Graph(id='graph-input',
              figure={
                  'data': [{
                      'mode': 'markers',
                      'type': 'scatter',
                      'x': [1, 2, 3],
                      'y': [4, 5, 6]
                  }],
                  'layout': {}
              },
              config={
                  'editable': True,
                  'edits': {
                      'annotationPosition': True
                  }
              }),
    html.Div(id='output-div')
])

# Set up tooltip functionality for the app
tooltip_template = "Point: x=%{x}, y=%{y}"
tooltip(app, template=tooltip_template)

def test_basic_usage(dash_duo):
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 600)

    # Tooltip template
    x_val, y_val = 2, 5  # The coordinates of the data point we're testing
    expected_annotation_text = tooltip_template.replace("%{x}", str(x_val)).replace("%{y}", str(y_val))

    # Start the Dash app
    dash_duo.start_server(app)

    # Select the data point corresponding to (2, 5)
    element = dash_duo.driver.find_element(By.CSS_SELECTOR, '.scatterlayer .trace .points path:nth-of-type(2)')
    ActionChains(driver).move_to_element(element).click().perform()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, 'output-div'), 'You clicked on point (2, 5)')
    )

    # Use ActionChains to move the mouse slightly to click on the annotation
    annotation_element = dash_duo.driver.find_element(By.CSS_SELECTOR, 'g.annotation-text-g rect.bg')
    action = ActionChains(dash_duo.driver)
    action.move_to_element(annotation_element).click().perform()

    # Add a delay of 1 second
    time.sleep(0.1)

    # Simulate pressing the Enter key
    action.send_keys('\ue007').perform()

    # Use the simplified CSS selector to locate the annotation text element
    annotation_text_element = dash_duo.driver.find_element(By.CSS_SELECTOR, 'g.annotation-text-g text.annotation-text')

    # Get the text content of the annotation element
    actual_annotation_text = annotation_text_element.text

    # Check if the actual annotation text matches the expected text
    assert actual_annotation_text == expected_annotation_text

