"""Demo 17: new tooltips stay on their data points after changing the y scale."""

import plotly.graph_objects as go
import pytest
from dash import Dash, Input, Output, State, dcc, html
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from dash_tooltip import tooltip


def create_app(case):
    graph_id = "log-axis-update-" + case
    scale_id = "scale-" + case
    fig = go.Figure(go.Scatter(x=[1, 2, 3], y=[10, 100, 1000], mode="lines+markers", marker_size=12))
    fig.update_layout(width=800, height=500, xaxis_type="linear", yaxis_type="linear")
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RadioItems(
                id=scale_id,
                options=[{"label": "Linear", "value": "linear"}, {"label": "Log", "value": "log"}],
                value="linear",
                inline=True,
            ),
            dcc.Graph(id=graph_id, figure=fig, config={"editable": True, "edits": {"annotationPosition": True}}),
        ]
    )
    tooltip(app, graph_ids=[graph_id], template="x: %{x}<br>y: %{y:.2f}")

    @app.callback(
        Output(graph_id, "figure", allow_duplicate=True),
        Input(scale_id, "value"),
        State(graph_id, "figure"),
        prevent_initial_call=True,
    )
    def change_scale(scale, current_figure):
        figure = go.Figure(current_figure)
        figure.update_yaxes(type=scale, autorange=True, range=None)
        return figure

    return app, graph_id, scale_id


def axis_is_rendered(driver, graph_id, expected):
    return driver.execute_script(
        """
        const graph = document.getElementById(arguments[0]);
        const gd = graph && graph.querySelector('.js-plotly-plot');
        return !!(gd && gd._fullLayout && !gd._fullLayout._replotting &&
            gd._fullLayout.yaxis.type === arguments[1] &&
            gd.querySelectorAll('.scatterlayer .points path.point').length === 3);
        """,
        graph_id,
        expected,
    )


@pytest.mark.selenium
@pytest.mark.parametrize(
    "scales",
    [(), ("log",), ("log", "linear"), ("log", "linear", "log")],
    ids=["linear", "linear-to-log", "roundtrip-linear", "roundtrip-log"],
)
def test_new_tooltip_after_yaxis_update(dash_duo, scales, request):
    case = request.node.callspec.id
    app, graph_id, scale_id = create_app(case)
    dash_duo.driver.set_window_size(1200, 900)
    dash_duo.start_server(app)
    driver = dash_duo.driver
    wait = WebDriverWait(driver, 15)
    wait.until(lambda d: axis_is_rendered(d, graph_id, "linear"))
    for scale in scales:
        driver.find_element(By.CSS_SELECTOR, '#{} input[value="{}"]'.format(scale_id, scale)).click()
        wait.until(lambda d: axis_is_rendered(d, graph_id, scale))

    marker_selector = "#{} .scatterlayer .points path.point:nth-of-type(2)".format(graph_id)
    marker = driver.find_element(By.CSS_SELECTOR, marker_selector)
    ActionChains(driver).move_to_element(marker).perform()
    wait.until(
        lambda d: d.execute_script(
            """
            const gd = document.getElementById(arguments[0]).querySelector('.js-plotly-plot');
            return gd._hoverdata && gd._hoverdata.some(p => p.x === 2 && p.y === 100);
            """,
            graph_id,
        )
    )
    ActionChains(driver).click().perform()

    def annotation_is_rendered(d):
        return d.execute_script(
            """
            const gd = document.getElementById(arguments[0]).querySelector('.js-plotly-plot');
            return gd.layout.annotations && gd.layout.annotations.length === 1 &&
                !!gd.querySelector('g.annotation-arrow-g path[transform]');
            """,
            graph_id,
        )

    wait.until(annotation_is_rendered)
    annotation = driver.execute_script(
        "return document.getElementById(arguments[0]).querySelector('.js-plotly-plot').layout.annotations[0];",
        graph_id,
    )
    expected_y = 2 if scales and scales[-1] == "log" else 100
    assert annotation["y"] == pytest.approx(expected_y)
    assert (annotation["xref"], annotation["yref"]) == ("x", "y")
    assert annotation["text"] == "x: 2<br>y: 100.00"
    assert len(driver.find_elements(By.CSS_SELECTOR, "#{} g.annotation".format(graph_id))) == 1

    distance = driver.execute_script(
        """
        const graph = document.getElementById(arguments[0]);
        const marker = graph.querySelector('.scatterlayer .points path.point:nth-of-type(2)');
        // Plotly backs the arrowhead's origin away from the anchor. Measure
        // the actual tip of the default right-pointing head, then transform it.
        const head = graph.querySelector('g.annotation-arrow-g path[transform]');
        const svg = graph.querySelector('svg.main-svg');
        const origin = svg.createSVGPoint();
        const tip = svg.createSVGPoint();
        const bounds = head.getBBox();
        tip.x = bounds.x + bounds.width;
        tip.y = bounds.y + bounds.height / 2;
        const markerPosition = origin.matrixTransform(marker.getScreenCTM());
        const headPosition = tip.matrixTransform(head.getScreenCTM());
        return Math.hypot(headPosition.x - markerPosition.x, headPosition.y - markerPosition.y);
        """,
        graph_id,
    )
    assert distance <= 2, "Tooltip arrowhead is {:.2f}px away from the clicked marker".format(distance)
