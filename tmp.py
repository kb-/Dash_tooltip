# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# Open in Jupyter Lab and save to create *.ipynb (by jupytext)
#
# Usage:
# Click on data points to add annotations. Annotations are draggable and editable.
# To delete and annotation, just delete its text: Click on text, delete and press enter

# %% jupyter={"source_hidden": true}
import dash
import dash_bootstrap_components as dbc

# ---- Imports ----
import ipywidgets as widgets
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, dcc, html
from IPython.display import display
from plotly.subplots import make_subplots
from plotly_resampler import FigureResampler
from trace_updater import TraceUpdater  # Assuming you've imported this module

from dash_tooltip import add_annotation_store, tooltip

pio.templates.default = "none"

# %% jupyter={"source_hidden": true}
# ---- Test 1: Single Trace with Draggable Annotations ----
graphid_1 = "graph1"

np.random.seed(20)
y1 = np.random.normal(0, 10, 50)
x1 = np.arange(0, 50)
# custom_labels = [f"Label {i}" for i in range(50)]
fig1 = px.scatter(x=x1, y=y1)
fig1.update_layout(title_text="Editable Title", title_x=0.5)

app1 = Dash(__name__)

app1.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Single Trace with Draggable Annotations",
                            style={"text-align": "center"},
                        )
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id=graphid_1,
                            toto='hi',
                            figure=fig1,
                            config={
                                "editable": 'maybe',
                                "edits": {
                                    "shapePosition": True,
                                    "annotationPosition": True,
                                },
                            },
                        )
                    ]
                )
            ]
        ),
    ]
)

# Add the tooltip functionality to the app
tooltip(app1, debug='yes')

if __name__ == "__main__":
    app1.run(debug=True, port=8081)

# %% jupyter={"source_hidden": true}
# ---- Test 2: Single Trace with Custom Data and Stylized Annotations ----
pio.templates.default = "none"

graphid_2 = "graph2"

np.random.seed(42)
y2 = np.random.normal(0, 10, 50)
x2 = np.arange(0, 50)
custom_labels = [f"Label {i}" for i in range(50)]
fig2 = px.scatter(x=x2, y=y2, custom_data=[custom_labels])
fig2.update_layout(title_text="Editable Title", title_x=0.5)

app2 = Dash(__name__)

app2.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Single Trace with Custom Data and Stylized Annotations",
                            style={"text-align": "center"},
                        )
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id='yo',
                            figure=fig2,
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
            ]
        ),
    ]
)

# Add the dcc.Store for annotations (optional for other uses)
dcc_store_id = add_annotation_store(app2.layout, graphid_2)
print("dcc_store_id:", dcc_store_id)

# Add the tooltip functionality to the app
custom_style = {
    "font": {"size": 10},
    "arrowcolor": "blue",
    "arrowsize": 2.5,
    # ... any other customization
}

tooltip(app2, style=custom_style, template="x: %{x},<br>y: %{y},<br>%{customdata[0]}")

# if __name__ == "__main__":
    # app2.run(debug=True, port=8082)