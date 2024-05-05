import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pytest
from dash import dcc, html
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip

app = dash.Dash(__name__)

# Create the scatter plot with plotly.graph_objects
x_data = [1, 2, 3, 4, 5]
y_data = [2, 3, 5, 7, 11]
scatter_fig = go.Figure(
    data=go.Scatter(x=x_data, y=y_data, mode="markers", name="Data Points")
)
scatter_fig.update_layout(
    title="Scatter Plot Example", xaxis_title="X Axis Label", yaxis_title="Y Axis Label"
)

GRAPH_ID = "scatter-plot16"

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id=GRAPH_ID,
                        figure=scatter_fig,
                        config={
                            "editable": True,
                            "edits": {
                                "shapePosition": True,
                                "annotationPosition": True,
                            },
                        },
                    )
                )
            ]
        ),
        html.Div(id="output-div"),
    ],
    fluid=True,
)

# Assuming a tooltip template similar to what was previously described
tooltip_template = "%{name},<br>x: %{x},<br>y: %{y:.2f}"
tooltip_instance = tooltip(app, graph_ids=[GRAPH_ID], template=tooltip_template)


# Example usage in a test function
@pytest.mark.selenium
def test_customdata_tooltip(dash_duo):
    dash_duo.start_server(app)

    # Wait for the graph to be fully loaded
    WebDriverWait(dash_duo.driver, 10).until(
        EC.presence_of_element_located((By.ID, GRAPH_ID))
    )

    # Click the first data point
    first_point = WebDriverWait(dash_duo.driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".scatterlayer .trace .points path:nth-of-type(1)")
        )
    )
    ActionChains(dash_duo.driver).move_to_element(first_point).click().perform()

    # Wait for the first tooltip to appear
    WebDriverWait(dash_duo.driver, 10).until(
        lambda driver: driver.find_element(
            By.CSS_SELECTOR, "g.annotation-text-g text.annotation-text"
        ).text.strip()
        != ""
    )

    # Update the tooltip template
    tooltip_template = "UPDATED,<br>x: %{x},<br>y: %{y:.2f}"
    tooltip_instance.update_template(GRAPH_ID, tooltip_template)

    # Click the second data point
    second_point = WebDriverWait(dash_duo.driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".scatterlayer .trace .points path:nth-of-type(2)")
        )
    )
    ActionChains(dash_duo.driver).move_to_element(second_point).click().perform()

    # Wait for the second tooltip to appear
    WebDriverWait(dash_duo.driver, 10).until(
        lambda driver: len(
            driver.find_elements(
                By.CSS_SELECTOR, "g.annotation-text-g text.annotation-text"
            )
        )
        >= 2
    )

    # Use JavaScript to retrieve all tooltip texts
    tooltip_texts = dash_duo.driver.execute_script(
        "return Array.from(document.querySelectorAll('g.annotation-text-g text.annotation-text')).map(e => e.textContent.trim());"
    )

    # Assert that there are exactly two tooltips and their contents are correct
    assert len(tooltip_texts) == 2, "There should be exactly two tooltips displayed."
    assert (
        "Data Points,x: 1,y: 2.00" in tooltip_texts[0]
    ), f"First tooltip content does not match: {tooltip_texts[0]}"
    assert (
        "UPDATED,x: 2,y: 3.00" in tooltip_texts[1]
    ), f"Second tooltip content does not match: {tooltip_texts[1]}"
