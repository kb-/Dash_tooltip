import plotly.graph_objs as go
import dash
from dash import Output, Input, State, dcc
from dash.html import Div
from typing import List, Optional, Dict, Union, Any
import re
import json
import logging

# Create a logger for your module
logger = logging.getLogger('dash_tooltip')
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('dash_app.log')
file_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

# Prevent logs from being propagated to the root logger
logger.propagate = False

# Now, you can log messages
logger.debug("dash_tooltip log active")


def add_annotation_store(layout: Div, graph_id: Optional[str] = None) -> str:
    """
    Adds a dcc.Store component to the layout to store annotations for tooltips.

    Args:
    - layout (dash.html.Div): The Dash app layout.
    - graph_id (str, optional): The ID of the graph component to which the store is linked.

    Returns:
    - str: The ID of the added dcc.Store component.
    """
    store_id = "tooltip-annotations-to-remove"
    if graph_id:
        store_id += f"-{graph_id}"

    if not any(isinstance(child, dcc.Store) and child.id == store_id for child in layout.children):
        layout.children.append(dcc.Store(id=store_id))
    
    return store_id


DEFAULT_ANNOTATION_CONFIG = {
    'text_color': 'black',
    'arrow_color': 'black',
    'arrow_size': 1.8,
    'arrow_width': 1,
    'arrow_head': 3,
    'x_anchor': 'left',
    'alignment': 'left'
}

DEFAULT_TEMPLATE = "x: %{x},<br>y: %{y}"


def tooltip(app: dash.Dash, 
            style: Dict[str, Union[str, float, int]] = DEFAULT_ANNOTATION_CONFIG, 
            template: str = DEFAULT_TEMPLATE, 
            graph_ids: Optional[List[str]] = None, 
            debug: bool = False) -> None:
    """
    Add tooltip functionality to Dash graph components.

    Args:
    - app (dash.Dash): The Dash app instance.
    - style (dict): Configuration for the tooltip appearance. Users can provide any valid Plotly annotation style options.
                    Default values are set in DEFAULT_ANNOTATION_CONFIG.
    - template (str): A string defining how the tooltip should be displayed using Plotly's template syntax. Users can modify this template to customize the tooltip content.
    - graph_ids (list, optional): List of graph component IDs for the tooltip functionality. If None, function will try to find graph IDs automatically.
    - debug (bool): If True, debug information will be written to a log file (tooltip.log).

    Example:
    tooltip(app, style={'text_color': 'red'}, template="x: %{x},<br>y: %{y}<br>ID: %{pointNumber}", graph_ids=['graph-1'])
    """
    if graph_ids is None:
        graph_ids = _find_all_graph_ids(app.layout)
        if not graph_ids:
            raise ValueError("No graphs found in the app layout. Please provide a graph ID.")
    
    for graph_id in graph_ids:
        add_annotation_store(app.layout, graph_id)

        @app.callback(
            Output(component_id=graph_id, component_property='figure'),
            Input(component_id=graph_id, component_property='clickData'),
            State(component_id=graph_id, component_property='figure')
        )
        def display_click_data(clickData, figure):
            return _display_click_data(clickData, figure, app, template, style, debug)

        app.clientside_callback(
            '''
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
            ''',
            Output(f'tooltip-annotations-to-remove-{graph_id}', 'data'),
            Input(graph_id, 'relayoutData')
        )

        @app.callback(
            Output(graph_id, 'figure', allow_duplicate=True),
            Input(f'tooltip-annotations-to-remove-{graph_id}', 'data'),
            State(graph_id, 'figure'),
            prevent_initial_call=True
        )
        def remove_empty_annotations(indices_to_remove, current_figure):
            """Remove annotations that have been deleted by the user."""
            if indices_to_remove:
                annotations = current_figure['layout'].get('annotations', [])

                # Log the original annotations
                logger.debug(f"Original Annotations: {annotations}")
                
                updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]

                # Log the indices being removed
                logger.debug(f"Indices to Remove: {indices_to_remove}")
                
                # Log the updated annotations
                logger.debug(f"Updated Annotations: {updated_annotations}")
                
                current_figure['layout']['annotations'] = updated_annotations
                return current_figure #update figure with new annotations list
            return dash.no_update #prevent undesired update when no change is done (also prevents breaking 


def _find_all_graph_ids(layout: Div) -> List[str]:
    """Recursively search for all graph component IDs in the app layout."""
    graph_ids = []

    if isinstance(layout, dcc.Graph):
        return [layout.id]
    
    if hasattr(layout, 'children'):
        if isinstance(layout.children, list):
            for child in layout.children:
                graph_ids.extend(_find_all_graph_ids(child))
        else:
            graph_ids.extend(_find_all_graph_ids(layout.children))
    
    return graph_ids


def extract_value_from_point(point: Dict[str, Any], key: str) -> Optional[Union[str, float, int]]:
    """Extracts the value from the point dictionary using a dot notation key."""
    try:
        parts = key.split('.')
        temp = point
        for part in parts:
            match = re.match(r"(\w+)\[(\d+)\]", part)
            if match:
                name, index = match.groups()
                index = int(index)
                if temp and isinstance(temp, dict) and name in temp:
                    temp = temp.get(name, [])[index]
                else:
                    return None
            else:
                if temp and isinstance(temp, dict):
                    temp = temp.get(part)
                else:
                    return None
        return temp
    except Exception as e:
        print(f"Error extracting value with key {key}. Error: {e}")
        return None


def _display_click_data(clickData: Dict[str, Any], 
                        figure: go.Figure, 
                        app: dash.Dash, 
                        template: str, 
                        config: Dict[str, Union[str, float, int]],
                        debug: bool) -> go.Figure:
    """Displays the tooltip on the graph when a data point is clicked."""
    fig = go.Figure(figure)
    merged_config = {**DEFAULT_ANNOTATION_CONFIG, **config}
    
    if not getattr(app, 'tooltip_active', True):
        raise dash.exceptions.PreventUpdate
    
    if clickData:
        point = clickData['points'][0]
        x_val = point['x']
        y_val = point['y']

        if debug:
            # with open('tooltip.log', 'a') as f:
            #     f.write("Point data:\n")
            #     f.write(json.dumps(point, indent=4))
            #     f.write("\nTrace data:\n")
            #     f.write(json.dumps(figure['data'][point['curveNumber']], indent=4))
            #     f.write("\n" + "="*40 + "\n")
            logger.debug("Point data:\n%s", json.dumps(point, indent=4))
            logger.debug("Trace data:\n%s", json.dumps(figure['data'][point['curveNumber']], indent=4))

        placeholders = re.findall(r"\%{(.*?)\}", template)
    
        template_data = {}
        for placeholder in placeholders:
            value = extract_value_from_point(point, placeholder)
            if value is not None:
                template_data[placeholder] = value
        
        for placeholder, value in template_data.items():
            template = template.replace("%{" + placeholder + "}", str(value))
        
        fig.add_annotation(
            x=x_val, y=y_val,
            text=template,
            showarrow=True,
            arrowcolor=merged_config['arrow_color'],
            arrowsize=merged_config['arrow_size'],
            arrowwidth=merged_config['arrow_width'],
            arrowhead=merged_config['arrow_head'],
            xanchor=merged_config['x_anchor'],
            align=merged_config['alignment'],
            font=dict(color=merged_config['text_color'])
        )
    return fig
