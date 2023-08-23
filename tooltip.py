# tooltip.py

import plotly.graph_objs as go
from dash import Output, Input, State, dcc

def add_annotation_store(layout):
    """
    Adds an dcc.Store component to the layout for storing annotation removal data.
    """
    if not any(isinstance(child, dcc.Store) and child.id == 'annotations-to-remove' for child in layout.children):
        layout.children.append(dcc.Store(id="annotations-to-remove"))

def tooltip(app, graph_id='graph1'):
    """
    Adds tooltip functionality to the specified Dash app and graph.
    """
    @app.callback(
        Output(component_id=graph_id, component_property='figure'),
        Input(component_id=graph_id, component_property='clickData'),
        State(component_id=graph_id, component_property='figure')
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
        Input(graph_id, 'relayoutData')
    )

    @app.callback(
        Output(graph_id, 'figure', allow_duplicate=True),
        Input('annotations-to-remove', 'data'),
        State(graph_id, 'figure'),
        prevent_initial_call=True
    )
    def remove_empty_annotations(indices_to_remove, current_figure):
        if indices_to_remove:
            annotations = current_figure['layout'].get('annotations', [])
            updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]
            current_figure['layout']['annotations'] = updated_annotations
        return current_figure
