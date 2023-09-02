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
    dcc.Graph(id='graph-input', figure={
        'data': [{
            'mode': 'markers',
            'type': 'scatter',
            'x': [1, 2, 3],
            'y': [4, 5, 6]
        }],
        'layout': {}
    }),
    html.Div(id='output-div')
])

# Set up tooltip functionality for the app
tooltip(app)

def test_basic_usage(dash_duo):

    driver = dash_duo.driver
    wait = WebDriverWait(driver, 600)
    
    # Start the Dash app
    dash_duo.start_server(app)

    # Select the data point corresponding to (2, 5)
    element = dash_duo.driver.find_element_by_css_selector('.scatterlayer .trace .points path:nth-of-type(2)')
    ActionChains(driver).move_to_element(element).click().perform()
    # driver.execute_script("arguments[0].click();", point)
    # Wait for the obstructing element to disappear
    # WebDriverWait(dash_duo.driver, 3).until(
        # EC.presence_of_element_located((By.CSS_SELECTOR, "rect.nsewdrag.drag"))
    # )
    # point.click()
    # dash_duo.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {view: window, bubbles: true, cancelable: true}));", point)


    # Give it some time to process
    # time.sleep(2)
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, 'output-div'), 'You clicked on point (2, 5)')
    )

    # Check if the clicked point's data is displayed
    output_div = dash_duo.find_element('#output-div')

    assert output_div.text == 'You clicked on point (2, 5)'

    # Get the updated graph figure and check if the tooltip annotation has been added
    updated_graph = dash_duo.find_element('#graph-input')
    WebDriverWait(driver, 100).until(
        lambda x: updated_graph.get_attribute('data-dash-figure') is not None
    )
    figure_data = updated_graph.get_attribute('data-dash-figure')
    import json

    try:
        figure_data_json = json.loads(figure_data)
        assert "annotations" in figure_data_json, "Tooltip annotation not added after click."
    except json.JSONDecodeError:
        raise AssertionError("data-dash-figure is not a valid JSON string.")
    
    # assert "annotations" in figure_data, "Tooltip annotation not added after click."

