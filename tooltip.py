import plotly.graph_objs as go
import dash
from dash import Output, Input, State, dcc

def add_annotation_store(layout):
    """
    Adds an dcc.Store component to the layout for storing annotation removal data.
    """
    if not any(isinstance(child, dcc.Store) and child.id == 'annotations-to-remove' for child in layout.children):
        layout.children.append(dcc.Store(id="annotations-to-remove"))

# Default configuration for tooltip annotations
DEFAULT_ANNOTATION_CONFIG = {
    'text_color': 'black',
    'arrow_color': 'black',
    'arrow_size': 1.8,
    'arrow_width': 1,
    'arrow_head': 3,
    'x_anchor': 'left',
    'alignment': 'left'
}

DEFAULT_TEMPLATE = "x: {x},<br>y: {y}"  # Users can add ",<br>{customdata}" if they have custom data

def find_first_graph_id(layout):
    """
    Recursively search the layout for the first dcc.Graph component and return its id.
    Currently, Dash has a limitation where certain configurations are shared across all graphs. 
    Therefore any single graph id can be used.
    """
    if isinstance(layout, dcc.Graph):
        return layout.id
    
    if hasattr(layout, 'children'):
        if isinstance(layout.children, list):
            for child in layout.children:
                graph_id = find_first_graph_id(child)
                if graph_id:
                    return graph_id
        else:
            return find_first_graph_id(layout.children)
    return None

def tooltip(app, style=DEFAULT_ANNOTATION_CONFIG, template=DEFAULT_TEMPLATE):
    """
    Adds tooltip functionality to the specified Dash app.

    Parameters:
    - app: The Dash app instance.
    - style: A dictionary containing annotation styling properties.
    - template: A string defining how the tooltip should be displayed. Uses Python string formatting syntax.
                - Default: "x: {x},<br>y: {y}"
                - If the graph has custom data, you can extend the template to incorporate it like:
                  "x: {x},<br>y: {y},<br>{customdata}". 
                  Note that `{customdata}` will concatenate all elements in the customdata list.
                  To access specific items in customdata, use indexing, e.g., "{customdata[0]}" for the first item.
    """

    # Retrieve the first graph_id from the passed app
    graph_id = find_first_graph_id(app.layout)
    if not graph_id:
        raise ValueError("No dcc.Graph component found in the app layout.")

    # Merge default config with the user's custom config
    config = DEFAULT_ANNOTATION_CONFIG.copy()
    if style:
        config.update(style)

    @app.callback(
        Output(component_id=graph_id, component_property='figure'),
        Input(component_id=graph_id, component_property='clickData'),
        State(component_id=graph_id, component_property='figure')
    )
    def display_click_data(clickData, figure):
        # Check if the tooltip is active
        if not getattr(app, 'tooltip_active', True):
            raise dash.exceptions.PreventUpdate
        
        fig = go.Figure(figure)
        if clickData:
            point = clickData['points'][0]
            x_val = point['x']
            y_val = point['y']
            
            # Check if customdata key exists and get it
            custom_data = point.get('customdata')
            if custom_data and isinstance(custom_data, list):
                custom_data = custom_data[0]
            
            # If a template is provided, use it
            if template:
                text = template.format(x=x_val, y=y_val, customdata=custom_data)
            else:
                text = f"x: {x_val},<br>y: {y_val}"
                if custom_data:
                    text += f",<br>{custom_data}"
            
            fig.add_annotation(
                x=x_val, y=y_val,
                text=text,
                showarrow=True,
                arrowcolor=config['arrow_color'],
                arrowsize=config['arrow_size'],
                arrowwidth=config['arrow_width'],
                arrowhead=config['arrow_head'],
                xanchor=config['x_anchor'],
                align=config['alignment'],
                font=dict(color=config['text_color'])
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
