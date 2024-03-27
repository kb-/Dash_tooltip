# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
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
import warnings

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
                            figure=fig1,
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

# Add the tooltip functionality to the app
tooltip(app1, debug=True)

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
fig2 = px.scatter(x=x2, y=y2, custom_data=[custom_labels, y2 * 2])
fig2.update_layout(title_text="Editable Title", title_x=0.5)

app2 = Dash(__name__)

app2.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Single Trace with Custom Data and Stylized" " Annotations",
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
                            id=graphid_2,
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

tooltip(
    app2,
    style=custom_style,
    template="x: %{x},"
    "<br>y: %{y:.2f},"
    "<br>%{customdata[0]},"
    "<br>2y=%{customdata[1]:.3f}",
)

if __name__ == "__main__":
    app2.run(debug=True, port=8082)

# %% jupyter={"source_hidden": true}

app3 = Dash(__name__)
# ---- Test 3: Multiple Traces with Draggable Annotations ----
# Random data for three traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
y2 = np.random.normal(5, 5, 50)
y3 = np.random.normal(-5, 15, 50)
x = np.arange(0, 50)

# Using Graph Objects for more flexibility
fig3 = go.Figure()

# Adding traces
fig3.add_trace(go.Scatter(x=x, y=y1, mode="markers", name="Trace 1"))
fig3.add_trace(go.Scatter(x=x, y=y2, mode="markers", name="Trace 2"))
fig3.add_trace(go.Scatter(x=x, y=y3, mode="markers", name="Trace 3"))

fig3.update_layout(title_text="Multiple Traces with Draggable Annotations", title_x=0.5)

app3.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Multiple Traces with Draggable Annotations",
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
                            id="multi-trace-graph",
                            figure=fig3,
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

# Add the tooltip functionality to the app3
tooltip(app3)

if __name__ == "__main__":
    app3.run(debug=True, port=8083)

# %%
# ---- Test 4: Multiple Traces with Tooltips ----
app4 = Dash(__name__)

# Random data for three traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels4_1 = [f"A {i}" for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels4_2 = [f"B {i}" for i in range(50)]
y3 = np.random.normal(-5, 15, 50)
custom_labels4_3 = [f"C {i}" for i in range(50)]
x = np.arange(0, 50)

# Using Graph Objects for more flexibility
fig4 = go.Figure()

# Adding traces with custom data
fig4.add_trace(
    go.Scatter(x=x, y=y1, mode="markers", name="Trace 1", customdata=custom_labels4_1)
)
fig4.add_trace(
    go.Scatter(x=x, y=y2, mode="markers", name="Trace 2", customdata=custom_labels4_2)
)
fig4.add_trace(
    go.Scatter(x=x, y=y3, mode="markers", name="Trace 3", customdata=custom_labels4_3)
)

fig4.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app4.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Multiple Traces with Custom Data and Stylized"
                            " Annotations",
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
                            id="multi-trace-graph",
                            figure=fig4,
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

# Add the tooltip functionality to the app
custom_style = {
    "font": {"size": 10},
    "arrowcolor": "blue",
    "arrowsize": 2.5,
    # ... any other customization
}
template = "%{label},<br>x: %{x},<br>y: %{y},<br>%{customdata[0]}"
tooltip(app4, style=custom_style, template=template)

if __name__ == "__main__":
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
fig5.add_trace(
    go.Scatter(x=x, y=y1, mode="markers", name="Trace 1", customdata=custom_labels1)
)
fig5.add_trace(
    go.Scatter(x=x, y=y2, mode="markers", name="Trace 2", customdata=custom_labels2)
)
fig5.add_trace(
    go.Scatter(x=x, y=y3, mode="markers", name="Trace 3", customdata=custom_labels3)
)

fig5.update_layout(title_text="Multiple Traces with Tooltips", title_x=0.5)

app5.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Multiple Traces with Toggable Tooltip function",
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
                            id="multi-trace-graph",
                            figure=fig5,
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

# Add the tooltip functionality to the app
custom_style = {
    "font": {"size": 10},
    "arrowcolor": "blue",
    "arrowsize": 2.5,
    # ... any other customization
}
template = "x: %{x},<br>y: %{y},<br>%{customdata[0]}"
tooltip(app5, style=custom_style, template=template)

app5.tooltip_active = False

if __name__ == "__main__":
    app5.run(debug=True, port=8085)


# %% jupyter={"source_hidden": true}
# ---- Test 6: Two Traces with Multiple Custom Data ----
def toggle_tooltip(change):
    app5.tooltip_active = change["new"]


# Create a toggle button
toggle = widgets.ToggleButton(
    value=app5.tooltip_active,
    description="Toggle Tooltip",
    disabled=False,
    button_style="",  # 'success', 'info', 'warning', 'danger' or ''
    tooltip="Toggle Tooltip Active Status",
    icon="check",  # (FontAwesome names without the `fa-` prefix)
)

# Display the button
display(toggle)

# Link the button action to the function
toggle.observe(toggle_tooltip, "value")

# %% jupyter={"source_hidden": true}
# Two Traces with Multiple Custom Data

app6 = Dash(__name__)

# Random data for two traces
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels6_1 = [[f"A {i}", f"X {i * 2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels6_2 = [[f"B {i}", f"Y {i * 3}"] for i in range(50)]
x = np.arange(0, 50)

fig6 = go.Figure()
fig6.add_trace(
    go.Scatter(x=x, y=y1, mode="markers", name="Trace 1", customdata=custom_labels6_1)
)
fig6.add_trace(
    go.Scatter(x=x, y=y2, mode="markers", name="Trace 2", customdata=custom_labels6_2)
)
fig6.update_layout(title_text="Two Traces with Multiple Custom Data", title_x=0.5)

app6.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Two Traces with Multiple Data Points in Tooltips",
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
                            id="double-customdata-graph",
                            figure=fig6,
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

template6 = (
    "x: %{x},<br>y: %{y},<br>Label1: %{customdata[0]},<br>Label2: %{customdata[1]}"
)
tooltip(app6, template=template6)

if __name__ == "__main__":
    app6.run(debug=True, port=8086)

# %% jupyter={"source_hidden": true}
# ---- Test 7: Comparison of Graphs with and without Tooltip Functionality ----
app7 = Dash(__name__)

# Random data for two graphs
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels7_1 = [[f"A {i}", f"X {i * 2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels7_2 = [[f"B {i}", f"Y {i * 3}"] for i in range(50)]
x = np.arange(0, 50)

fig7_1 = go.Figure()
fig7_1.update_layout({"title": "With Tooltip"})
fig7_1.add_trace(
    go.Scatter(
        x=x, y=y1, mode="markers", name="Graph 1 Trace 1", customdata=custom_labels7_1
    )
)
fig7_2 = go.Figure()
fig7_2.update_layout({"title": "Without Tooltip"})
fig7_2.add_trace(
    go.Scatter(
        x=x, y=y2, mode="markers", name="Graph 2 Trace 1", customdata=custom_labels7_2
    )
)

app7.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Comparison of Graphs with and"
                            " without Tooltip Functionality",
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
                            id="app7-graph1",
                            figure=fig7_1,
                            config={
                                "editable": True,
                                "edits": {
                                    "shapePosition": True,
                                    "annotationPosition": True,
                                },
                            },
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="app7-graph2",
                            figure=fig7_2,
                            config={
                                "editable": True,
                                "edits": {
                                    "shapePosition": True,
                                    "annotationPosition": True,
                                },
                            },
                        )
                    ]
                ),
            ]
        ),
    ]
)

template7 = (
    "x: %{x},<br>y: %{y},<br>Label1: %{customdata[0]},<br>Label2: %{customdata[1]}"
)
tooltip(app7, template=template7, graph_ids=["app7-graph1"], debug=True)

if __name__ == "__main__":
    app7.run(debug=True, port=8087, jupyter_height=1000)

# %% jupyter={"source_hidden": true}
# ---- Test 8: Two Graphs with Draggable Tooltips for Custom Data ----
app8 = Dash(__name__)

# Random data for two graphs
np.random.seed(0)
y1 = np.random.normal(0, 10, 50)
custom_labels8_1 = [[f"A {i}", f"X {i * 2}"] for i in range(50)]
y2 = np.random.normal(5, 5, 50)
custom_labels8_2 = [[f"B {i}", f"Y {i * 3}"] for i in range(50)]
x = np.arange(0, 50)

fig8_1 = go.Figure()
fig8_1.add_trace(
    go.Scatter(
        x=x, y=y1, mode="markers", name="Graph 1 Trace 1", customdata=custom_labels8_1
    )
)

fig8_2 = go.Figure()
fig8_2.add_trace(
    go.Scatter(
        x=x, y=y2, mode="markers", name="Graph 2 Trace 1", customdata=custom_labels8_2
    )
)

app8.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Two Graphs with Draggable Tooltips for Custom Data",
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
                            id="app8-graph1",
                            figure=fig8_1,
                            config={
                                "editable": True,
                                "edits": {
                                    "shapePosition": True,
                                    "annotationPosition": True,
                                },
                            },
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="app8-graph2",
                            figure=fig8_2,
                            config={
                                "editable": True,
                                "edits": {
                                    "shapePosition": True,
                                    "annotationPosition": True,
                                },
                            },
                        )
                    ]
                ),
            ]
        ),
    ]
)

template8 = (
    "x: %{x},<br>y: %{y},<br>Label1: %{customdata[0]},<br>Label2: %{customdata[1]}"
)
tooltip(app8, template=template8)

if __name__ == "__main__":
    app8.run(debug=True, port=8088, jupyter_height=1000)

# %% jupyter={"source_hidden": true}
# ---- Test 9: Pandas Time Series Plot (not editable) ----
# plotly_resampler allows to display very large dataset with dynamic
# selective downsampling

# In the context of the provided code, we've encountered specific FutureWarning messages
# related to the behavior of certain methods in the pandas library and the
# plotly_resampler library.

# Suppress the specific warning about the DatetimeProperties.to_pydatetime method
# in pandas
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*DatetimeProperties.to_pydatetime.*"
)

# Suppress the specific warning about the is_datetime64tz_dtype method
# in plotly_resampler
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*is_datetime64tz_dtype is deprecated.*"
)

# Suppress the specific warning about H
# in plotly_resampler
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*'H' is deprecated.*"
)

# Suppress the specific warning about m
# in plotly_resampler
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*'m' is deprecated.*"
)

# Generate random time series data
date_rng = pd.date_range(start="2020-01-01", end="2020-12-31", freq="h")
ts1 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
ts2 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create a DataFrame to hold the time series
df = pd.DataFrame({"Time Series 1": ts1, "Time Series 2": ts2})

# Plotting the time series
fig9 = FigureResampler(px.line(df, x=df.index, y=df.columns, title="Time Series Plot"))
# noinspection PyTypeChecker
fig9.show_dash(mode="inline", port=8089)
fig9.update_layout(title_text="Pandas Time Series Plot (not editable)")
tooltip(fig9._app)

# %% jupyter={"source_hidden": true}
# ---- Test 10: Pandas Time Series Plot (editable) ----
# Generate random time series data
date_rng = pd.date_range(start="2020-01-01", end="2020-12-31", freq="h")
ts1 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
ts2 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create a DataFrame to hold the time series - hover and matching tooltip content
df = pd.DataFrame({"Time Series 1": ts1, "Time Series 2": ts2})

# Plotting the time series
template = (
    "x: %{x}<br>y: %{y}<br>ID: %{pointNumber}<br>"
    "name: %{customdata[0]}<br>unit: %{customdata[1]}"
)

fig10 = FigureResampler(px.line(df, x=df.index, y=df.columns, title="Time Series Plot"))

# Modify each trace to include the desired hovertemplate
for i, trace in enumerate(fig10.data):
    trace.customdata = np.column_stack(
        (np.repeat(df.columns[i], len(df)), np.repeat("#{}".format(i + 1), len(df)))
    )
    trace.hovertemplate = template

# Construct app & its layout
app10 = Dash(__name__)

app10.layout = html.Div(
    [
        dcc.Graph(
            id="graph-id",
            figure=fig10,
            config={
                "editable": True,
                "edits": {"shapePosition": True, "annotationPosition": True},
            },
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
# wrapper function
def interactive_plot(fig, graphid, template):
    """
    Creates a Dash app with an interactive plot.

    Parameters:
    - fig: plotly figure
    - graphid: id for the dcc.Graph component

    Returns:
    - Dash app instance and the figure
    """
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id=graphid,
                                figure=fig,
                                config={
                                    "editable": True,
                                    "edits": {
                                        "shapePosition": True,
                                        "annotationPosition": True,
                                    },
                                },
                            ),
                            TraceUpdater(id="trace-updater", gdID=graphid),
                        ]
                    )
                ]
            )
        ]
    )

    # Add tooltip functionality to the app
    tooltip(app, template=template)

    # Register the callback with FigureResampler
    fig.register_update_graph_callback(app, graphid, "trace-updater")

    return app, fig


# %% jupyter={"source_hidden": true}
# ---- Test 11: Wrapper function ----
# Generate random time series data
graphid_11 = "graphid11"
date_rng = pd.date_range(start="2020-01-01", end="2020-12-31", freq="h")
ts1 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
ts2 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create a DataFrame to hold the time series - hover and matching tooltip content
df = pd.DataFrame({"Time Series 1": ts1, "Time Series 2": ts2})
# Plotting the time series
template = (
    "x: %{x}<br>y: %{y}<br>ID: %{pointNumber}<br>"
    "name: %{customdata[0]}<br>unit: %{customdata[1]}"
)
fig11 = FigureResampler(px.line(df, x=df.index, y=df.columns, title="Time Series Plot"))
# Modify each trace to include the desired hovertemplate
for i, trace in enumerate(fig11.data):
    trace.customdata = np.column_stack(
        (np.repeat(df.columns[i], len(df)), np.repeat("#{}".format(i + 1), len(df)))
    )
    trace.hovertemplate = template

app11, fig11 = interactive_plot(fig11, graphid_11, template)
if __name__ == "__main__":
    app11.run(debug=True, port=8091)

# %% jupyter={"source_hidden": true}
# ---- Test 12: 2x2 Subplot with 2 traces on each subplot (Organized like Test 10) ----

# Generate random time series data
date_rng = pd.date_range(start="2020-01-01", end="2020-12-31", freq="m")

ts_data = {}
for i in range(4):
    ts_data[f"ts{i + 1}_1"] = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
    ts_data[f"ts{i + 1}_2"] = pd.Series(np.random.randn(len(date_rng)), index=date_rng)

# Create 2x2 subplots
fig12 = FigureResampler(
    make_subplots(
        rows=2,
        cols=2,
        shared_xaxes=True,
        subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4"),
    )
)

# Add data to subplots
for i in range(1, 3):
    for j in range(1, 3):
        # noinspection PyTypeChecker
        fig12.add_trace(
            go.Scatter(
                x=date_rng,
                y=ts_data[f"ts{(i - 1) * 2 + j}_1"],
                name=f"Trace 1, Plot {(i - 1) * 2 + j}",
            ),
            row=i,
            col=j,
        )
        # noinspection PyTypeChecker
        fig12.add_trace(
            go.Scatter(
                x=date_rng,
                y=ts_data[f"ts{(i - 1) * 2 + j}_2"],
                name=f"Trace 2, Plot {(i - 1) * 2 + j}",
            ),
            row=i,
            col=j,
        )

# Modify each trace to include the desired hovertemplate
template12 = (
    "x: %{x}<br>y: %{y}<br>ID: %{pointNumber}<br>"
    "name: %{customdata[0]}<br>unit: %{customdata[1]}"
)
for i, trace in enumerate(fig12.data):
    trace.customdata = np.column_stack(
        (
            np.repeat(trace.name, len(date_rng)),
            np.repeat("#{}".format(i + 1), len(date_rng)),
        )
    )
    trace.hovertemplate = template12

# Construct app & its layout
app12 = Dash(__name__)

app12.layout = html.Div(
    [
        dcc.Graph(
            id="graph-id12",
            figure=fig12,
            config={
                "editable": True,
                "edits": {"shapePosition": True, "annotationPosition": True},
            },
        ),
        TraceUpdater(id="trace-updater12", gdID="graph-id12"),
    ]
)

# Add tooltip functionality
tooltip(
    app12,
    graph_ids=["graph-id12"],
    style={"font": {"size": 10}},
    template=template12,
    debug=True,
)

# Update layout title
fig12.update_layout(title_text="2x2 Subplots with 2 Traces Each")

# Register the callback with FigureResampler
fig12.register_update_graph_callback(app12, "graph-id12", "trace-updater12")

# Code to run the Dash app
# (commented out for now, but can be used in a local environment)
app12.run(debug=True, port=8092)

# %% jupyter={"source_hidden": true}
# ---- Test 13: Direct Data Injection into dcc.Graph with Draggable Annotations ----
graphid_1 = "graph1"

np.random.seed(20)
y1 = np.random.normal(0, 10, 50)
x1 = np.arange(0, 50)
# custom_labels = [f"Label {i}" for i in range(50)]
# fig13 = px.scatter(x=x1, y=y1)
# fig13.update_layout(title_text="Editable Title", title_x=0.5)

app13 = Dash(__name__)

app13.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="example-graph",
                            figure={
                                "data": [
                                    {
                                        "x": x1,
                                        "y": y1,
                                        "type": "line",
                                        "mode": "lines",
                                        "name": "sin(x)",
                                    }
                                ],
                                "layout": {
                                    "title": "Direct Data Injection into "
                                    "dcc.Graph with Draggable Annotations"
                                },
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
            ]
        ),
    ]
)

# Add the tooltip functionality to the app
tooltip(app13, debug=True)

if __name__ == "__main__":
    app13.run(debug=True, port=8093)

# %% jupyter={"source_hidden": true}
# ---- Test 14: log axis ----

# Generate exponential data
x_data = np.linspace(1, 100, 100)  # Generating 100 points from 1 to 100

ts_data = {}
for i in range(4):
    ts_data[f"ts{i + 1}_1"] = np.exp(
        0.05 * x_data
    )  # Exponential growth with a base of exp(1)
    ts_data[f"ts{i + 1}_2"] = np.exp(
        0.03 * x_data
    )  # Slower exponential growth with a base of exp(1)


# Create 2x2 subplots
fig14 = FigureResampler(
    make_subplots(
        rows=2,
        cols=2,
        shared_xaxes=True,
        subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4"),
    )
)

# Add data to subplots
for i in range(1, 3):
    for j in range(1, 3):
        # noinspection PyTypeChecker
        fig14.add_trace(
            go.Scatter(
                x=x_data,
                y=ts_data[f"ts{(i - 1) * 2 + j}_1"],
                name=f"Trace 1, Plot {(i - 1) * 2 + j}",
            ),
            row=i,
            col=j,
        )
        # noinspection PyTypeChecker
        fig14.add_trace(
            go.Scatter(
                x=x_data,
                y=ts_data[f"ts{(i - 1) * 2 + j}_2"],
                name=f"Trace 2, Plot {(i - 1) * 2 + j}",
            ),
            row=i,
            col=j,
        )

# Set log axis
fig14.update_layout(
    yaxis1=dict(type="log"),
    xaxis1=dict(type="log"),
    yaxis2=dict(type="log"),
    xaxis3=dict(type="log"),
)

# Modify each trace to include the desired hovertemplate
template14 = (
    "x: %{x}<br>y: %{y:0.2f}<br>ID: %{pointNumber}<br>"
    "name: %{customdata[0]}<br>unit: %{customdata[1]}"
)
for i, trace in enumerate(fig14.data):
    trace.customdata = np.column_stack(
        (
            np.repeat(
                trace.name, len(x_data)
            ),  # Updated from len(date_rng) to len(x_data)
            np.repeat(
                "#{}".format(i + 1), len(x_data)
            ),  # Updated from len(date_rng) to len(x_data)
        )
    )
    trace.hovertemplate = template14

# Construct app & its layout
app14 = Dash(__name__)

app14.layout = html.Div(
    [
        dcc.Graph(
            id="graph-id14",
            figure=fig14,
            config={
                "editable": True,
                "edits": {"shapePosition": True, "annotationPosition": True},
            },
        ),
        TraceUpdater(id="trace-updater14", gdID="graph-id14"),
    ]
)

# Add tooltip functionality
tooltip(
    app14,
    graph_ids=["graph-id14"],
    style={"font": {"size": 10}},
    template=template14,
    debug=True,
)

# Update layout title
fig14.update_layout(title_text="2x2 Subplots with 2 Traces Each", height=800)

# Register the callback with FigureResampler
fig14.register_update_graph_callback(app14, "graph-id14", "trace-updater14")

# Code to run the Dash app
# (commented out for now, but can be used in a local environment)
app14.run(debug=True, port=8094, jupyter_height=800)


# %% jupyter={"source_hidden": true}
# ---- Test 15: log axis (placement should fail if Plotly bug still present)----

# Plotly bug https://github.com/plotly/plotly.py/issues/2580

# Generate exponential data
x_data = np.linspace(1, 100, 100)  # Generating 100 points from 1 to 100

ts_data = {}
for i in range(4):
    ts_data[f"ts{i + 1}_1"] = np.exp(
        0.05 * x_data
    )  # Exponential growth with a base of exp(1)
    ts_data[f"ts{i + 1}_2"] = np.exp(
        0.03 * x_data
    )  # Slower exponential growth with a base of exp(1)


# Create 2x2 subplots
fig15 = FigureResampler(
    make_subplots(
        rows=2,
        cols=2,
        shared_xaxes=True,
        subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4"),
    )
)

# Add data to subplots
for i in range(1, 3):
    for j in range(1, 3):
        # noinspection PyTypeChecker
        fig15.add_trace(
            go.Scatter(
                x=x_data,
                y=ts_data[f"ts{(i - 1) * 2 + j}_1"],
                name=f"Trace 1, Plot {(i - 1) * 2 + j}",
            ),
            row=i,
            col=j,
        )
        # noinspection PyTypeChecker
        fig15.add_trace(
            go.Scatter(
                x=x_data,
                y=ts_data[f"ts{(i - 1) * 2 + j}_2"],
                name=f"Trace 2, Plot {(i - 1) * 2 + j}",
            ),
            row=i,
            col=j,
        )

# Set log axis
fig15.update_layout(
    yaxis1=dict(type="log"),
    xaxis1=dict(type="log"),
    yaxis2=dict(type="log"),
    xaxis3=dict(type="log"),
)

# Modify each trace to include the desired hovertemplate
template15 = (
    "x: %{x}<br>y: %{y:0.2f}<br>ID: %{pointNumber}<br>"
    "name: %{customdata[0]}<br>unit: %{customdata[1]}"
)
for i, trace in enumerate(fig15.data):
    trace.customdata = np.column_stack(
        (
            np.repeat(
                trace.name, len(x_data)
            ),  # Updated from len(date_rng) to len(x_data)
            np.repeat(
                "#{}".format(i + 1), len(x_data)
            ),  # Updated from len(date_rng) to len(x_data)
        )
    )
    trace.hovertemplate = template15

# Construct app & its layout
app15 = Dash(__name__)

app15.layout = html.Div(
    [
        dcc.Graph(
            id="graph-id15",
            figure=fig15,
            config={
                "editable": True,
                "edits": {"shapePosition": True, "annotationPosition": True},
            },
        ),
        TraceUpdater(id="trace-updater15", gdID="graph-id15"),
    ]
)

# Add tooltip functionality
tooltip(
    app15,
    graph_ids=["graph-id15"],
    style={"font": {"size": 10}},
    template=template15,
    apply_log_fix=False,
    debug=True,
)

# Update layout title
fig15.update_layout(
    title_text="2x2 Subplots with 2 Traces Each (tooltip placement should work after Plotly issue fix)",
    height=800,
)

# Register the callback with FigureResampler
fig15.register_update_graph_callback(app15, "graph-id15", "trace-updater15")

# Code to run the Dash app
# (commented out for now, but can be used in a local environment)
app15.run(debug=True, port=8095, jupyter_height=800)


# %% jupyter={"source_hidden": true}
