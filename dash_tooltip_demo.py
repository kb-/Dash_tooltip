# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.0
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

# %%
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
import plotly.io as pio
from tooltip import tooltip, add_annotation_store

pio.templates.default = "none"

np.random.seed(42)
y = np.random.normal(0, 10, 50)
x = np.arange(0, 50)
custom_labels = [f"Label {i}" for i in range(50)]
fig1 = px.scatter(x=x, y=y, custom_data=[custom_labels])
fig1.update_layout(title_text="Editable Title", title_x=0.5)

app = Dash(__name__)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph1',
                figure=fig1,
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

# Add the required dcc.Store for annotations
add_annotation_store(app.layout)

# Add the tooltip functionality to the app
tooltip(app)

if __name__ == '__main__':
    app.run_server(debug=True)


# %%
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
import plotly.io as pio
from tooltip import tooltip, add_annotation_store

pio.templates.default = "none"

np.random.seed(42)
y = np.random.normal(0, 10, 50)
x = np.arange(0, 50)
custom_labels = [f"Label {i}" for i in range(50)]
fig1 = px.scatter(x=x, y=y, custom_data=[custom_labels])
fig1.update_layout(title_text="Editable Title", title_x=0.5)

app1 = Dash(__name__)

app1.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph1',
                figure=fig1,
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

# Add the required dcc.Store for annotations
add_annotation_store(app1.layout)

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}

tooltip(app1, style=custom_config)

if __name__ == '__main__':
    app1.run_server(debug=True)

# %%
