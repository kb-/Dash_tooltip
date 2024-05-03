import dash
import pandas as pd
import plotly.graph_objs as go
from dash import callback_context, dcc, html
from dash.dependencies import Input, Output

from dash_tooltip import tooltip

# from icecream import ic


# Sample DataFrame with DatetimeIndex
date_range = pd.date_range(start="2022-01-01", periods=5)
df = pd.DataFrame(
    {
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 6, 8, 10],
        "z": [3, 6, 9, 12, 15],
        "a": [4, 8, 12, 16, 20],
        "b": [5, 10, 15, 20, 25],
    },
    index=date_range,
)

# Initialize the Dash app
app16 = dash.Dash(__name__)

# Define the layout
app16.layout = html.Div(
    [
        html.Label("Select X and Y columns:"),
        dcc.Dropdown(
            id="x-column",
            options=[{"label": col, "value": col} for col in df.columns],
            value=df.columns[0],
        ),
        dcc.Dropdown(
            id="y-column",
            options=[{"label": col, "value": col} for col in df.columns],
            value=df.columns[1],
        ),
        dcc.Graph(
            id="scatter-plot",
            style={"width": "800px", "height": "800px"},
            config={
                "editable": True,
                "edits": {"shapePosition": True, "annotationPosition": True},
            },
        ),
    ]
)

tooltip(app16, debug=True, graph_ids=["scatter-plot"])
once = False


# Define callback to update the scatter plot
@app16.callback(
    Output("scatter-plot", "figure", allow_duplicate=True),
    [Input("x-column", "value"), Input("y-column", "value")],
    prevent_initial_call=True,
)
def update_scatter_plot(x_column, y_column):
    global once
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    # ic(triggered_id)
    if triggered_id in ["x-column", "y-column"]:
        # ic()
        # x_column = 'x'
        # y_column = 'y'
        non_selected_columns = [
            col for col in df.columns if col not in [x_column, y_column]
        ]
        customdata = df[non_selected_columns].apply(
            lambda row: "<br>".join(
                f"<b>{col}</b>: {val}" for col, val in zip(non_selected_columns, row)
            ),
            axis=1,
        )

        template = (
            "<b>Date</b>: %{customdata}<br>"
            + f"<b>{x_column}</b>: %{{x}}<br>"
            + f"<b>{y_column}</b>: %{{y}}<br>"
        )

        if not once:
            # ic()
            tooltip(app16, debug=True, graph_ids=["scatter-plot"], template=template)
            once = True

        trace = go.Scatter(
            x=df[x_column],
            y=df[y_column],
            mode="markers",
            marker=dict(color="blue"),
            customdata=df.index.strftime("%Y-%m-%d %H:%M:%S") + "<br>" + customdata,
            # Include date and time with other data
            hovertemplate=template,
        )
        layout = go.Layout(
            title="Scatter Plot",
            xaxis=dict(title=x_column),
            yaxis=dict(title=y_column),
            hovermode="closest",
            height=800,
            width=800,
        )
        return {"data": [trace], "layout": layout}


# Run the app
if __name__ == "__main__":
    app16.run_server(debug=True, port=8096)
