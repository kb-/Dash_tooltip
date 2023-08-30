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

# ---- Imports ----

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from plotly_resampler import FigureResampler
from dash_tooltip import tooltip, add_annotation_store
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from trace_updater import TraceUpdater  # Assuming you've imported this module
import ipywidgets as widgets
from IPython.display import display

pio.templates.default = "none"

# %% jupyter={"source_hidden": true}
# ---- Test 1: Single Trace with Draggable Annotations ----
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
        dbc.Col([html.H1("Single Trace with Draggable Annotations", style={"text-align": "center"})])
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

# Add the tooltip functionality to the app
tooltip(app1)

if __name__ == '__main__':
    app1.run(debug=True, port=8081)

# %% jupyter={"source_hidden": true}
# ---- Test 2: Single Trace with Custom Data and Stylized Annotations ----
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

# Add the dcc.Store for annotations (optional for other uses)
dcc_store_id = add_annotation_store(app2.layout, graphid_2)
print("dcc_store_id:", dcc_store_id)

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}

tooltip(app2, style=custom_config, template="x: %{x},<br>y: %{y},<br>%{customdata[0]}")

if __name__ == '__main__':
    app2.run(debug=True, port=8082)

# %% jupyter={"source_hidden": true}

app3 = Dash(__name__)
# ---- Test 3: Multiple Traces with Draggable Annotations ----
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
fig3 = go.Figure()

# Adding traces
fig3.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1'))
fig3.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2'))
fig3.add_trace(go.Scatter(x=x, y=y3, mode='markers', name='Trace 3'))

fig3.update_layout(title_text="Multiple Traces with Draggable Annotations", title_x=0.5)

app3.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Multiple Traces with Draggable Annotations", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='multi-trace-graph',
                figure=fig3,
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

# Add the tooltip functionality to the app3
tooltip(app3)

if __name__ == '__main__':
    app3.run(debug=True, port=8083)

# %% jupyter={"source_hidden": true}
# ---- Test 4: Multiple Traces with Tooltips ----
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
fig4 = go.Figure()

# Adding traces with custom data
fig4.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1', customdata=custom_labels1))
fig4.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2', customdata=custom_labels2))
fig4.add_trace(go.Scatter(x=x, y=y3, mode='markers', name='Trace 3', customdata=custom_labels3))

fig4.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app4.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Multiple Traces with Custom Data and Stylized Annotations", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='multi-trace-graph',
                figure=fig4,
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

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}
template = "x: %{x},<br>y: %{y},<br>%{customdata[0]}"
tooltip(app4, style=custom_config, template=template)

if __name__ == '__main__':
    app4.run(debug=True, port=8084)

# %% jupyter={"source_hidden": true}
# ---- Test 5: Multiple Traces with Toggable Tooltip function ----
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
fig5 = go.Figure()

# Adding traces with custom data
fig5.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1', customdata=custom_labels1))
fig5.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2', customdata=custom_labels2))
fig5.add_trace(go.Scatter(x=x, y=y3, mode='markers', name='Trace 3', customdata=custom_labels3))

fig5.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app5.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Multiple Traces with Toggable Tooltip function", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='multi-trace-graph',
                figure=fig5,
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

# Add the tooltip functionality to the app
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}
template = "x: %{x},<br>y: %{y},<br>%{customdata[0]}"
tooltip(app5, style=custom_config, template=template)

app5.tooltip_active = False

if __name__ == '__main__':
    app5.run(debug=True, port=8085)

# %% jupyter={"source_hidden": true}
# ---- Test 6: Two Traces with Multiple Custom Data ----
def toggle_tooltip(change):
    app5.tooltip_active = change['new']


# Create a toggle button
toggle = widgets.ToggleButton(
    value=app5.tooltip_active,
    description='Toggle Tooltip',
    disabled=False,
    button_style='',  # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Toggle Tooltip Active Status',
    icon='check'  # (FontAwesome names without the `fa-` prefix)
)

# Display the button
display(toggle)

# Link the button action to the function
toggle.observe(toggle_tooltip, 'value')

# %% jupyter={"source_hidden": true}
# Two Traces with Multiple Custom Data

app6 = Dash(__name__)

# Random data for two traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [[f"A {i}", f"X {i * 2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [[f"B {i}", f"Y {i * 3}"] for i in range(50)]
x = np.arange(0, 50)

fig6 = go.Figure()
fig6.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Trace 1', customdata=custom_labels1))
fig6.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Trace 2', customdata=custom_labels2))
fig6.update_layout(title_text="Two Traces with Multiple Custom Data", title_x=0.5)

app6.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Two Traces with Multiple Data Points in Tooltips", style={"text-align": "center"})])
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

template6 = "x: %{x},<br>y: %{y},<br>Label1: %{customdata[0]},<br>Label2: %{customdata[1]}"
tooltip(app6, template=template6)

if __name__ == '__main__':
    app6.run(debug=True, port=8086)

# %% jupyter={"source_hidden": true}
# ---- Test 7: Comparison of Graphs with and without Tooltip Functionality ----
app7 = Dash(__name__)

# Random data for two graphs
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [[f"A {i}", f"X {i * 2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [[f"B {i}", f"Y {i * 3}"] for i in range(50)]
x = np.arange(0, 50)

fig7_1 = go.Figure()
fig7_1.update_layout({'title':'With Tooltip'})
fig7_1.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Graph 1 Trace 1', customdata=custom_labels1))
fig7_2 = go.Figure()
fig7_2.update_layout({'title':'Without Tooltip'})
fig7_2.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Graph 2 Trace 1', customdata=custom_labels2))

app7.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Comparison of Graphs with and without Tooltip Functionality", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='app7-graph1',
                figure=fig7_1,
                config={
                    'editable': True,
                    'edits': {
                        'shapePosition': True,
                        'annotationPosition': True
                    }
                }
            )
        ]),
        dbc.Col([
            dcc.Graph(
                id='app7-graph2',
                figure=fig7_2,
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

template7 = "x: %{x},<br>y: %{y},<br>Label1: %{customdata[0]},<br>Label2: %{customdata[1]}"
tooltip(app7, template=template7, graph_ids=['app7-graph1'], debug=True)

if __name__ == '__main__':
    app7.run(debug=True, port=8087, jupyter_height=1000)


# %% jupyter={"source_hidden": true}
# ---- Test 8: Two Graphs with Draggable Tooltips for Custom Data ----
app8 = Dash(__name__)

# Random data for two graphs
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels1 = [[f"A {i}", f"X {i * 2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels2 = [[f"B {i}", f"Y {i * 3}"] for i in range(50)]
x = np.arange(0, 50)

fig8_1 = go.Figure()
fig8_1.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Graph 1 Trace 1', customdata=custom_labels1))

fig8_2 = go.Figure()
fig8_2.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='Graph 2 Trace 1', customdata=custom_labels2))

app8.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Two Graphs with Draggable Tooltips for Custom Data", style={"text-align": "center"})])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='app8-graph1',
                figure=fig8_1,
                config={
                    'editable': True,
                    'edits': {
                        'shapePosition': True,
                        'annotationPosition': True
                    }
                }
            )
        ]),
        dbc.Col([
            dcc.Graph(
                id='app8-graph2',
                figure=fig8_2,
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

template8 = "x: %{x},<br>y: %{y},<br>Label1: %{customdata[0]},<br>Label2: %{customdata[1]}"
tooltip(app8, template=template8)

if __name__ == '__main__':
    app8.run(debug=True, port=8088, jupyter_height=1000)

# %% jupyter={"source_hidden": true}
# ---- Test 9: Pandas Time Series Plot (not editable) ----
# plotly_resampler allows to display very large dataset with dynamic selective downsampling

# Generate random time series data
date_rng = pd.date_range(start='2020-01-01', end='2020-12-31', freq='h')
ts1 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
ts2 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create a DataFrame to hold the time series
df = pd.DataFrame({'Time Series 1': ts1, 'Time Series 2': ts2})

# Plotting the time series
fig9 = FigureResampler(px.line(df, x=df.index, y=df.columns, title="Time Series Plot"))
fig9.show_dash(mode='inline', port=8089)
fig9.update_layout(title_text="Pandas Time Series Plot (not editable)")
tooltip(fig9._app)


# %% jupyter={"source_hidden": true}
# ---- Test 10: Pandas Time Series Plot (editable) ----
# Generate random time series data
date_rng = pd.date_range(start='2020-01-01', end='2020-12-31', freq='h')
ts1 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
ts2 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create a DataFrame to hold the time series - hover and matching tooltip content
df = pd.DataFrame({'Time Series 1': ts1, 'Time Series 2': ts2})

# Plotting the time series
import plotly.express as px

template = "x: %{x}<br>y: %{y}<br>ID: %{pointNumber}<br>name: %{customdata[0]}<br>unit: %{customdata[1]}"

fig10 = FigureResampler(px.line(df, x=df.index, y=df.columns, title="Time Series Plot"))

# Modify each trace to include the desired hovertemplate
for i,trace in enumerate(fig10.data):
    trace.customdata = np.column_stack((np.repeat(df.columns[i], len(df)), np.repeat('#{}'.format(i+1), len(df))))
    trace.hovertemplate = template

# Construct app & its layout
app10 = Dash(__name__)

app10.layout = html.Div(
    [
        dcc.Graph(
            id="graph-id", 
            figure=fig10,
            config=
            {
                'editable': True,
                'edits': {
                    'shapePosition': True,
                    'annotationPosition': True
                }
            }
        ),
        TraceUpdater(id="trace-updater", gdID="graph-id"),
    ]
)

fig10.update_layout(title_text="Pandas Time Series Plot (editable)")

# Add tooltip functionality
template10 = template
tooltip(app10, graph_ids=["graph-id"], template=template10, debug=True)

# Register the callback with FigureResampler
fig10.register_update_graph_callback(app10, "graph-id", "trace-updater")

# Show the Dash app
app10.run(debug=True, port=8090, jupyter_height=500)


# %% jupyter={"source_hidden": true}
