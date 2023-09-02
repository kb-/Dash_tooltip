"""
Test 3: Configuration Test:
Call the tooltip function with a custom style configuration and check if the tooltips reflect the desired properties (e.g., arrow color, font size).
This ensures that the function respects custom configurations.
"""

import time
import pytest
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_tooltip import tooltip
import dash_bootstrap_components as dbc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import plotly.express as px

app = dash.Dash(__name__)
graphid_2 = 'graph2'

@app.callback(
    Output('output-div', 'children'),
    Input('graph-input', 'clickData')
)
def display_click_data(clickData):
    if clickData:
        point = clickData['points'][0]
        return f'You clicked on point {point["x"]}, {point["y"]}'
    return 'Click on a point to see its data.'

np.random.seed(42)
y2 = np.random.normal(0, 10, 50)
x2 = np.arange(0, 50)
custom_labels = [f"Label {i}" for i in range(50)]
fig2 = px.scatter(x=x2, y=y2, custom_data=[custom_labels])
fig2.update_layout(title_text="Editable Title", title_x=0.5)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Single Trace with Custom Data and Stylized Annotations", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id=graphid_2,
                figure=fig2,
                config={
                    'editable': True,
                    'edits': {
                        'shapePosition': True,
                        'annotationPosition': True
                    }
                }
            )
        ])
    ])
])

# Define a custom configuration
custom_config = {
    'arrowcolor': 'blue',
    'font': {
        'color': 'red',
        'size': 7
    },
    'arrowhead': 5
}

# Tooltip template from dash_tooltip_demo.py
tooltip_template = "x: %{x},<br>y: %{y},<br>%{customdata[0]}"

# Call the tooltip function with the custom configuration
tooltip(app, template=tooltip_template, style=custom_config, debug=True)

def test_tooltip_configuration(dash_duo):
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 600)

    # Start the Dash app
    dash_duo.start_server(app)

    # Interact with a data point to trigger the tooltip
    idx = 1
    element = driver.find_element(By.CSS_SELECTOR, f'.scatterlayer .trace .points path:nth-of-type({idx+1})')
    ActionChains(driver).move_to_element(element).click().perform()

    # Check the tooltip's stylistic properties
    annotation_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'g.annotation-text-g text.annotation-text')))

    # Pause to inspect the DOM
    # wait.until(EC.presence_of_element_located((By.ID, 'some-id')))

    # Extract text color and font size
    text_color = annotation_element.value_of_css_property('fill')
    font_size = annotation_element.value_of_css_property('font-size')

    # Extract arrow color from graph configuration
    arrow_element = driver.find_element(By.CSS_SELECTOR, 'g.annotation-arrow-g path')
    arrow_color = arrow_element.value_of_css_property('stroke')

    # Assertions
    assert arrow_color == 'rgb(0, 0, 255)'  # RGB equivalent of 'blue'
    assert text_color == 'rgb(255, 0, 0)'  # RGB equivalent of 'red'
    assert font_size == '7px'