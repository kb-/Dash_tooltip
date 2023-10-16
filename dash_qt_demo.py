# qt_app_demo.py
import multiprocessing
import sys

import dash
import numpy as np
from dash import dcc, html
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

from dash_tooltip import tooltip


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.browser = QWebEngineView(self)
        self.browser.load(QUrl("http://127.0.0.1:8050/"))  # Dash app default address
        self.setCentralWidget(self.browser)

        # Either set a default size:
        self.resize(800, 600)

        # Or start maximized:
        # self.showMaximized()

        self.show()


app = dash.Dash(__name__)

x = np.linspace(0, 10, 100)
y = np.sin(x)

app.layout = html.Div(
    [
        dcc.Graph(
            id="example-graph",
            figure={
                "data": [
                    {
                        "x": x,
                        "y": y,
                        "type": "scatter",  # Use scatter type
                        "mode": "lines",  # Specify lines mode for scatter plot
                        "name": "sin(x)",
                    }
                ],
                "layout": {"title": "Dash by Plotly in PyQt"},
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
# Add the tooltip functionality to the app
template = "x: %{x},<br>y: %{y:.2f}"
tooltip(app, template=template)


def run_dash():
    app.run_server()


if __name__ == "__main__":
    # Start Dash app in a separate process
    dash_process = multiprocessing.Process(target=run_dash)
    dash_process.start()

    # PyQt app
    app = QApplication(sys.argv)
    window = MyApp()
    window.setWindowTitle("Dash inside PyQt")
    web_view = window.centralWidget()
    assert isinstance(web_view, QWebEngineView)
    web_view.load(QUrl("http://localhost:8050/"))
    window.show()
    sys.exit(app.exec())
