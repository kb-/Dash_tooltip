import http.client
import os
import sys
import threading
import time

import dash
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow

from dash_tooltip import tooltip

dash_port = 8050


class MyApp(QMainWindow):
    """
    Main application window for the PyQt application.
    This class integrates a Dash application inside a PyQt WebEngineView.
    """

    def __init__(self):
        """
        Initialize the application window.
        """
        super().__init__()
        self.browser = None
        self.initUI()

    def initUI(self):
        """
        Set up the user interface of the app.
        """
        self.browser = QWebEngineView(self)
        self.browser.page().profile().downloadRequested.connect(self._on_download_fn)
        self.browser.load(QUrl("http://127.0.0.1:8050/"))  # Dash app default address
        self.setCentralWidget(self.browser)

        self.resize(800, 600)  # Set a default size
        self.show()

    def _on_download_fn(self, download):
        """
        Handle file download requests.

        Args:
            download: QWebEngineDownloadRequest object.
        """
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",  # Starting path
            "All Files (*);;PNG Files (*.png);;JPEG Files (*.jpeg)",
        )
        if fileName:
            directory = os.path.dirname(fileName)
            filename = os.path.basename(fileName)
            download.setDownloadDirectory(directory)
            download.setDownloadFileName(filename)
            download.accept()


def create_dash_app():
    """
    Create and configure the Dash application.

    Returns:
        A Dash app object.
    """
    app = dash.Dash(__name__)

    graph_config = {
        "editable": True,
        "edits": {
            "shapePosition": True,
            "annotationPosition": True,
        },
    }

    graph_style = {
        "width": "100%",
        "height": "100%",
        # "border": "2px solid red",
    }

    layout_margin = {"l": 25, "r": 25, "t": 25, "b": 25}

    # Creating a grid of x and y values
    x = np.linspace(0, 10, 400)
    y = np.linspace(0, 10, 400)
    X, Y = np.meshgrid(x, y)

    # Calculate Z as a function of X and Y
    Z = np.sin(X) * np.cos(Y)

    # Create a heatmap
    fig2 = go.Figure(
        data=go.Heatmap(
            z=Z,
            x=x,
            y=y,
            colorscale="Viridis",
            # You can change the colorscale as needed
        ),
        layout=go.Layout(margin=layout_margin),
    )

    # Define scatter data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    app.layout = html.Div(
        [
            dcc.Graph(
                id="example-graph1",
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
                    "layout": {
                        "title": "Dash by Plotly in PyQt",
                        "margin": layout_margin,
                    },
                },
                config=graph_config,
                style=graph_style,
            ),
            dcc.Graph(
                id="example-graph2", figure=fig2, config=graph_config, style=graph_style
            ),
        ],
        style={
            "display": "flex",
            "flex-direction": "column",  # Use "row" for side-by-side layout
            "width": "95vw",
            "height": "95vh",
            "overflow": "hidden",
        },  # Full viewport width and height
    )

    # Add the tooltip functionality to the app
    template1 = "x: %{x:.2f},<br>y: %{y:.2f}"
    tooltip(app, template=template1, graph_ids=["example-graph1"])
    template2 = "x: %{x:.2f},<br>y: %{y:.2f},<br>z: %{z:.3f}"
    tooltip_style = {
        "bgcolor": "rgba(255, 255, 255, 0.2)",
    }
    tooltip(app, style=tooltip_style, template=template2, graph_ids=["example-graph2"])
    return app


def run_dash():
    """
    Run the Dash app server.
    """
    app = create_dash_app()
    app.run_server()


# Check server availability
def is_server_available(host="127.0.0.1", port=dash_port):
    """Check if the Dash server is available."""
    conn = http.client.HTTPConnection(host, port)
    try:
        conn.request("GET", "/")
        return conn.getresponse().status == 200
    except (http.client.HTTPException, TimeoutError, ConnectionRefusedError):
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    # Start Dash app in a separate process
    dash_thread = threading.Thread(target=run_dash)
    dash_thread.start()

    # Wait for Dash server to be available
    while not is_server_available(port=dash_port):
        time.sleep(0.1)

    # PyQt app
    qt_app = QApplication(sys.argv)
    window = MyApp()
    window.setWindowTitle("Dash inside PyQt")
    web_view = window.centralWidget()
    assert isinstance(web_view, QWebEngineView)
    web_view.load(QUrl(f"http://localhost:{dash_port}/"))
    window.show()
    sys.exit(qt_app.exec())
