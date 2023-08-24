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

# %% jupyter={"source_hidden": true}
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
import plotly.io as pio
from tooltip import tooltip, add_annotation_store

pio.templates.default = "none"

graphid_1 = 'graph1'

np.random.seed(20)
y1 = np.random.normal(0, 10, 50)
x1 = np.arange(0, 50)
# custom_labels = [f"Label {i}" for i in range(50)]
fig1 = px.scatter(x=x1, y=y1)
fig1.update_layout(title_text="Editable Title", title_x=0.5)

app1 = Dash(__name__)

app1.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id=graphid_1,
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

# # Add the required dcc.Store for annotations
add_annotation_store(app1.layout)

# Add the tooltip functionality to the app
tooltip(app1)

if __name__ == '__main__':
    app1.run(debug=True, port=8086)


# %%
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
import plotly.io as pio
from tooltip import tooltip, add_annotation_store

pio.templates.default = "none"

graphid_2 = 'graph2'

np.random.seed(42)
y2 = np.random.normal(0, 10, 50)
x2 = np.arange(0, 50)
custom_labels = [f"Label {i}" for i in range(50)]
fig2 = px.scatter(x=x2, y=y2, custom_data=[custom_labels])
fig2.update_layout(title_text="Editable Title", title_x=0.5)

app2 = Dash(__name__)

app2.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations", style={"text-align": "center"})])
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

# Add the required dcc.Store for annotations
add_annotation_store(app2.layout)

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}

tooltip(app2, style=custom_config, template="x: {x},<br>y: {y},<br>{customdata[0]}")

if __name__ == '__main__':
    app2.run(debug=True, port=8087)

# %% jupyter={"source_hidden": true}
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
from tooltip import tooltip, add_annotation_store

app3 = Dash(__name__)

# Random data for three traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [f"A {i}" for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [f"B {i}" for i in range(50)]
y3 = np.random.normal(-5, 15, 50)
custom_labels3 = [f"C {i}" for i in range(50)]
x = np.arange(0, 50)

# Using Graph Objects for more flexibility
fig = go.Figure()

# Adding traces
fig.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1'))
fig.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2'))
fig.add_trace(go.Scatter(x=x, y=y3, mode='markers', name='Trace 3'))

fig.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app3.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations with multiple traces", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='multi-trace-graph',
                figure=fig,
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
add_annotation_store(app3.layout)

# Add the tooltip functionality to the app3
tooltip(app3)

if __name__ == '__main__':
    app3.run(debug=True, port=8088)


# %%
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
from tooltip import tooltip, add_annotation_store

app4 = Dash(__name__)

# Random data for three traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [f"A {i}" for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [f"B {i}" for i in range(50)]
y3 = np.random.normal(-5, 15, 50)
custom_labels3 = [f"C {i}" for i in range(50)]
x = np.arange(0, 50)

# Using Graph Objects for more flexibility
fig = go.Figure()

# Adding traces with custom data
fig.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1', customdata=custom_labels1))
fig.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2', customdata=custom_labels2))
fig.add_trace(go.Scatter(x=x, y=y3, mode='markers', name='Trace 3', customdata=custom_labels3))

fig.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app4.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations with multiple traces", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='multi-trace-graph',
                figure=fig,
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
add_annotation_store(app4.layout)

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}
template = "x: {x},<br>y: {y},<br>{customdata[0]}"
tooltip(app4, style=custom_config, template=template)

if __name__ == '__main__':
    app4.run_server(debug=True, port=8089)


# %%
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
from tooltip import tooltip, add_annotation_store

app5 = Dash(__name__)

# Random data for three traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [f"A {i}" for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [f"B {i}" for i in range(50)]
y3 = np.random.normal(-5, 15, 50)
custom_labels3 = [f"C {i}" for i in range(50)]
x = np.arange(0, 50)

# Using Graph Objects for more flexibility
fig = go.Figure()

# Adding traces with custom data
fig.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1', customdata=custom_labels1))
fig.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2', customdata=custom_labels2))
fig.add_trace(go.Scatter(x=x, y=y3, mode='markers', name='Trace 3', customdata=custom_labels3))

fig.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app5.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Dynamic and draggable annotations with multiple traces", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='multi-trace-graph',
                figure=fig,
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
add_annotation_store(app5.layout)

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}
template = "x: {x},<br>y: {y},<br>{customdata[0]}"
tooltip(app5, style=custom_config, template=template)

app5.tooltip_active = False

if __name__ == '__main__':
    app5.run_server(debug=True, port=8090)


# %% jupyter={"source_hidden": true}
import ipywidgets as widgets
from IPython.display import display

def toggle_tooltip(change):
    app5.tooltip_active = change['new']

# Create a toggle button
toggle = widgets.ToggleButton(
    value=app5.tooltip_active,
    description='Toggle Tooltip',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Toggle Tooltip Active Status',
    icon='check' # (FontAwesome names without the `fa-` prefix)
)

# Display the button
display(toggle)

# Link the button action to the function
toggle.observe(toggle_tooltip, 'value')


# %%
# Two Traces with Multiple Custom Data

app6 = Dash(__name__)

# Random data for two traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [[f"A {i}", f"X {i*2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [[f"B {i}", f"Y {i*3}"] for i in range(50)]
x = np.arange(0, 50)

fig6 = go.Figure()
fig6.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1', customdata=custom_labels1))
fig6.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2', customdata=custom_labels2))
fig6.update_layout(title_text="Two Traces with Multiple Custom Data", title_x=0.5)

app6.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Two Traces with Multiple Custom Data Tooltip", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='double-customdata-graph',
                figure=fig6,
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
add_annotation_store(app6.layout)

template6 = "x: {x},<br>y: {y},<br>Label1: {customdata[0]},<br>Label2: {customdata[1]}"
tooltip(app6, template=template6)

if __name__ == '__main__':
    app6.run_server(debug=True, port=8091)

# %%
custom_labels2

# %%
