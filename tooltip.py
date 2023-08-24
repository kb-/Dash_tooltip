import plotly.graph_objs as go
import dash
from dash import Output, Input, State, dcc
import re

def add_annotation_store(layout):
    """
    Add a dcc.Store component to the layout to store annotation removal data.
    
    Parameters:
    - layout: The Dash layout object.
    
    Returns:
    - None
    """
    if not any(isinstance(child, dcc.Store) and child.id == 'tooltip-annotations-to-remove' for child in layout.children):
        layout.children.append(dcc.Store(id="tooltip-annotations-to-remove"))

DEFAULT_ANNOTATION_CONFIG = {
    'text_color': 'black',
    'arrow_color': 'black',
    'arrow_size': 1.8,
    'arrow_width': 1,
    'arrow_head': 3,
    'x_anchor': 'left',
    'alignment': 'left'
}

DEFAULT_TEMPLATE = "x: {x},<br>y: {y}"

def find_first_graph_id(layout):
    """
    Find the first dcc.Graph component's ID in the given layout.
    
    Parameters:
    - layout: The Dash layout object.
    
    Returns:
    - The ID of the first dcc.Graph component found, or None if not found.
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
    Add a tooltip callback to the app to display data when a point is clicked.
    
    Parameters:
    - app: The Dash app object.
    - style: A dictionary with custom styles for the tooltip.
    - template: A string defining how the tooltip should be displayed. Uses Python string formatting syntax.
                - Default: "x: {x},<br>y: {y}"
                - If the graph has custom data, you can extend the template to incorporate it like:
                  "x: {x},<br>y: {y},<br>{customdata}". 
                  Note that `{customdata}` will concatenate all elements in the customdata list.
                  To access specific items in customdata, use indexing, e.g., "{customdata[0]}" for the first item.
    
    Returns:
    - None
    """
    graph_id = find_first_graph_id(app.layout)
    if not graph_id:
        raise ValueError("No dcc.Graph component found in the app layout.")

    # Automatically add the required dcc.Store for annotations if it doesn't exist
    add_annotation_store(app.layout)

    # Merge default config with the user's custom config
    config = DEFAULT_ANNOTATION_CONFIG.copy()
    config.update(style)

    @app.callback(
        Output(component_id=graph_id, component_property='figure'),
        Input(component_id=graph_id, component_property='clickData'),
        State(component_id=graph_id, component_property='figure')
    )
    def display_click_data(clickData, figure):
        """
        Display the tooltip on the graph when a point is clicked.
        
        Parameters:
        - clickData: The data of the clicked point.
        - figure: The current figure data.
        
        Returns:
        - The updated figure data with the tooltip annotation added.
        """
        return _display_click_data(clickData, figure, app, template, config)

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
        Output('tooltip-annotations-to-remove', 'data'),
        Input(graph_id, 'relayoutData')
    )

    @app.callback(
        Output(graph_id, 'figure', allow_duplicate=True),
        Input('tooltip-annotations-to-remove', 'data'),
        State(graph_id, 'figure'),
        prevent_initial_call=True
    )
    def remove_empty_annotations(indices_to_remove, current_figure):
        """
        Remove annotations that are empty.
        
        Parameters:
        - indices_to_remove: A list of indices of annotations to remove.
        - current_figure: The current figure data.
        
        Returns:
        - The updated figure data with the specified annotations removed.
        """
        if indices_to_remove:
            annotations = current_figure['layout'].get('annotations', [])
            updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]
            current_figure['layout']['annotations'] = updated_annotations
        return current_figure

def _display_click_data(clickData, figure, app, template, config):
    """
    Create and display a tooltip based on the clicked data point.
    
    Parameters:
    - clickData: The data of the clicked point.
    - figure: The current figure data.
    - app: The Dash app object.
    - template: A string template for formatting the tooltip content.
    - config: A dictionary with styles for the tooltip.
    
    Returns:
    - The updated figure data with the tooltip annotation added.
    """
    fig = go.Figure(figure)
    
    # If the tooltip is not active, prevent the update
    if not getattr(app, 'tooltip_active', True):
        raise dash.exceptions.PreventUpdate
    
    if clickData:
        point = clickData['points'][0]
        x_val = point['x']
        y_val = point['y']
        
        custom_data = point.get('customdata', [])
        
        template_data = {'x': x_val, 'y': y_val}
        
        for idx, data in enumerate(custom_data):
            key = f"customdata[{idx}]"
            template_data[key] = data

        missing_keys = [key for key in re.findall(r"\{(.*?)\}", template) if key not in template_data]
        if missing_keys:
            raise ValueError(f"Missing keys in template_data: {', '.join(missing_keys)}. Available keys are: {', '.join(template_data.keys())}")

        for placeholder, value in template_data.items():
            template = template.replace("{" + placeholder + "}", str(value))
        
        fig.add_annotation(
            x=x_val, y=y_val,
            text=template,
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
