"""
Test 2: Template Formatting Test:
Call the tooltip function with a custom template and check if the tooltips are formatted according to the template.
This ensures that the function respects custom formatting.
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
        return f'You clicked on point {{point["x"]}}, {{point["y"]}}'
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

# Tooltip template from dash_tooltip_demo.py
tooltip_template = "x: %{x},<br>y: %{y},<br>%{customdata[0]}"
tooltip(app, template=tooltip_template, debug=True)

def test_customdata_tooltip(dash_duo):
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 10)

    # Customdata for the data point we're testing
    idx = 1  # Index of the data point
    expected_custom_label = custom_labels[idx]

    # Extract x and y values directly from the data
    x_value = x2[idx]
    y_value = y2[idx]

    expected_annotation_text = tooltip_template.replace("<br>", "").replace("%{x}", str(x_value)).replace("%{y}",
                                                                                                            str(y_value)).replace(
        "%{customdata[0]}", expected_custom_label)

    # Start the Dash app
    dash_duo.start_server(app)

    # Select the data point with index=2
    element = dash_duo.driver.find_element(By.CSS_SELECTOR, f'.scatterlayer .trace .points path:nth-of-type({idx+1})')
    ActionChains(driver).move_to_element(element).click().perform()

    # Use ActionChains to move the mouse slightly to click on the annotation
    annotation_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'g.annotation-text-g text.annotation-text')))

    # Get the text content of the annotation element
    actual_annotation_text = annotation_element.text

    # Check if the actual annotation text matches the expected text based on the customdata
    assert actual_annotation_text == expected_annotation_text
