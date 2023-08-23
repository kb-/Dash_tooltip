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
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State
import plotly.io as pio

pio.templates.default = "none"

# some random data
np.random.seed(42)
y = np.random.normal(0, 10, 50)
x = np.arange(0, 50)

# Let's add some custom labels as an example
custom_labels = [f"Label {i}" for i in range(50)]

app = Dash(__name__)
# app.run(jupyter_mode="jupyterlab")

# Create a scatter plot with custom data
fig1 = px.scatter(x=x, y=y, custom_data=[custom_labels])
fig1.update_layout(title_text="Editable Title", title_x=0.5)  # Centered title

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
    ]),
    dcc.Store(id="annotations-to-remove")
])

@app.callback(
    Output(component_id='graph1', component_property='figure'),
    Input(component_id='graph1', component_property='clickData'),
    State(component_id='graph1', component_property='figure')
)
def display_click_data(clickData, figure):
    fig = go.Figure(figure)
    
    if clickData:
        point = clickData['points'][0]
        x_val = point['x']
        y_val = point['y']
        custom_data = point['customdata'][0]  # Accessing the custom data
        fig.add_annotation(
            x=x_val, y=y_val,
            text=f"x: {x_val},<br>y: {y_val},<br>{custom_data}",
            showarrow=True,
            arrowcolor="black",
            arrowsize=1.8,
            arrowwidth=1,
            arrowhead=3,
            xanchor='left',
            align='left'
        )
    return fig

app.clientside_callback(
    """
    function(relayoutData) {
        var annotationPattern = /annotations\[(\d+)\].text/;
        var indicesToRemove = [];
        for (var key in relayoutData) {
            var match = key.match(annotationPattern);
            if (match && relayoutData[key] === "") {
                indicesToRemove.push(parseInt(match[1]));
            }
        }
        return indicesToRemove;
    }
    """,
    Output('annotations-to-remove', 'data'),
    Input('graph1', 'relayoutData')
)

@app.callback(
    Output('graph1', 'figure', allow_duplicate=True),
    Input('annotations-to-remove', 'data'),
    State('graph1', 'figure'),
    prevent_initial_call=True
)
def remove_empty_annotations(indices_to_remove, current_figure):
    if indices_to_remove:
        annotations = current_figure['layout'].get('annotations', [])
        updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]
        current_figure['layout']['annotations'] = updated_annotations
    return current_figure

if __name__ == '__main__':
    app.run_server(debug=True)


# %%
