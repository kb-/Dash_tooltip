import plotly.graph_objs as go
import dash
from dash import Output, Input, State, dcc
from dash.html import Div
from typing import List, Optional, Dict, Union, Any
import re
import json
import logging
from string import Template

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
    'align': 'left',             # horizontal alignment of the text (can be 'left', 'center', or 'right')
    'arrowcolor': 'black',       # color of the annotation arrow
    'arrowhead': 3,              # type of arrowhead, for Plotly (an integer from 0 to 8)
    'arrowsize': 1.8,            # relative size of the arrowhead to the arrow stem, for Plotly
    'arrowwidth': 1,             # width of the annotation arrow in pixels, for Plotly
    'font': {
        'color': 'black',      # color of the annotation text
        'family': 'Arial',     # font family of the annotation text, for Plotly
        'size': 12             # size of the annotation text in points, for Plotly
    },
    'showarrow': True,
    'xanchor': 'left'            # horizontal alignment of the text (can be 'left', 'center', or 'right')
}

# Type Hint Definitions
FontConfigType = Dict[str, Union[str, int]]
AnnotationConfigType = Dict[str, Union[str, int, float, bool, FontConfigType]]

DEFAULT_TEMPLATE = "x: %{x},<br>y: %{y}"


def tooltip(app: dash.Dash, 
            style: AnnotationConfigType = DEFAULT_ANNOTATION_CONFIG,
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

        dbg_str = 'console.log(relayoutData);'
        
        app.clientside_callback(
            Template('''
                function(relayoutData) {
                    $dbg_str
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
            ''').substitute(dbg_str=dbg_str),
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
            return dash.no_update #prevent undesired update when no change is done (also prevents breaking) 


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


def truncate_json_arrays(json_str: str, limit: int) -> str:
    """
    Truncate arrays in a JSON string representation to a specified limit, both at top level and nested.
    
    Parameters:
    - json_str (str): The JSON string representation to be processed.
    - limit (int): The maximum number of elements to keep in any array.
    
    Returns:
    - str: The processed JSON string with arrays truncated.
    """
    
    def truncate_arrays(data: Any) -> Any:
        """
        Recursively truncate arrays in a data structure (dicts or lists).
        """
        if isinstance(data, list):
            truncated_data = data[:limit]
            if len(data) > limit:
                truncated_data.append("[TRUNCATED]")
            return [truncate_arrays(item) for item in truncated_data]
        elif isinstance(data, dict):
            return {key: truncate_arrays(value) for key, value in data.items()}
        else:
            return data

    data = json.loads(json_str)
    truncated_data = truncate_arrays(data)
    
    return json.dumps(truncated_data, indent=4)


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges two dictionaries.
    Nested keys from dict2 will overwrite those in dict1.
    """
    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
            dict1[key] = deep_merge_dicts(dict1[key], value)
        else:
            dict1[key] = value
    return dict1


def _display_click_data(clickData: Dict[str, Any], 
                        figure: go.Figure, 
                        app: dash.Dash, 
                        template: str, 
                        config: Dict[str, Union[str, float, int]],
                        debug: bool) -> go.Figure:
    """Displays the tooltip on the graph when a data point is clicked."""
    fig = go.Figure(figure)
    merged_config = deep_merge_dicts(DEFAULT_ANNOTATION_CONFIG.copy(), config)
    
    if not getattr(app, 'tooltip_active', True):
        raise dash.exceptions.PreventUpdate
    
    if clickData:
        point = clickData['points'][0]
        x_val = point['x']
        y_val = point['y']
        
        # Extract the clicked axis information from the curve data
        if 'xaxis' in figure['data'][point['curveNumber']]:
            xaxis = figure['data'][point['curveNumber']]['xaxis']
        else:
            xaxis = 'x'

        if 'yaxis' in figure['data'][point['curveNumber']]:
            yaxis = figure['data'][point['curveNumber']]['yaxis']
        else:
            yaxis = 'y'

        if debug:
            logger.debug(f"clickData: {truncate_json_arrays(json.dumps(clickData, indent=4),2)}")
            logger.debug(f"figure: {truncate_json_arrays(json.dumps(figure, indent=4),2)}")
            logger.debug("Point data:\n%s", truncate_json_arrays(json.dumps(point, indent=4),2))
            logger.debug("Trace data:\n%s", truncate_json_arrays(json.dumps(figure['data'][point['curveNumber']], indent=4), 2))

        placeholders = re.findall(r"\%{(.*?)\}", template)
    
        template_data = {}
        for placeholder in placeholders:
            value = extract_value_from_point(point, placeholder)
            if value is not None:
                template_data[placeholder] = value
        
        for placeholder, value in template_data.items():
            template = template.replace("%{" + placeholder + "}", str(value))
        
        try:
            fig.add_annotation(
                x=x_val, y=y_val,
                xref=xaxis,
                yref=yaxis,
                text=template,
                **merged_config
            )
        except ValueError as e:
            logger.error(
                f"Failed to add annotation due to invalid properties in {merged_config}. Error: {e}"
            )
            raise e
    return fig
