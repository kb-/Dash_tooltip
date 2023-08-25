import plotly.graph_objs as go
import dash
from dash import Output, Input, State, dcc
from typing import List, Optional, Dict, Union
import re

from typing import Optional


def add_annotation_store(layout: dash.html.Div, graph_id: Optional[str] = None) -> str:
    """
    Add a dcc.Store component to the layout to store annotation removal data.
    
    If you do not manually call this function, the `tooltip()` function will automatically 
    call it and generate the store using a default ID or with the provided graph ID.
    
    If the graph_id is provided, it will be used as a suffix to the store ID. This can be useful
    if you want to explicitly manage the store in other parts of your application.
    
    Parameters:
    - layout: The Dash layout object.
    - graph_id (optional): The ID of the graph. If provided, it will be used as a suffix for the store ID.
    
    Returns:
    - str: The ID of the created or existing dcc.Store.
    """
    store_id = "tooltip-annotations-to-remove"
    if graph_id:
        store_id += f"-{graph_id}"

    if not any(isinstance(child, dcc.Store) and child.id == store_id for child in layout.children):
        layout.children.append(dcc.Store(id=store_id))
    
    return store_id


DEFAULT_ANNOTATION_CONFIG: Dict[str, Union[str, float, int]] =  {
    'text_color': 'black',
    'arrow_color': 'black',
    'arrow_size': 1.8,
    'arrow_width': 1,
    'arrow_head': 3,
    'x_anchor': 'left',
    'alignment': 'left'
}

DEFAULT_TEMPLATE: str = "x: %{x},<br>y: %{y}"


def find_first_graph_id(layout: dash.html.Div) -> Optional[str]:
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


def tooltip(app: dash.Dash, 
            style: Dict[str, Union[str, float, int]] = DEFAULT_ANNOTATION_CONFIG, 
            template: str = DEFAULT_TEMPLATE, 
            graph_ids: Optional[List[str]] = None) -> None:
    """
    Add tooltip functionality to a Dash app.

    Note:
    To ensure annotations are editable, the dcc.Graph component(s) you want to apply the tooltip on 
    should have the following configuration:
        config={
            'editable': True,
            'edits': {
                'shapePosition': True,
                'annotationPosition': True
            }
        }

    Parameters:
    - app (dash.Dash): The Dash app instance.
    - style (dict, optional): Configuration for the tooltip's appearance.
    - template (str, optional): A string defining how the tooltip should be displayed. 
                                Uses Python string formatting syntax.
                                - Default: "x: {x},<br>y: {y}"
                                - If the graph has custom data, you can extend the template to incorporate it like:
                                  "x: {x},<br>y: {y},<br>{customdata[0]}". 
                                  Use "{customdata[index]}" to access specific items in the customdata list, 
                                  where index corresponds to the custom data's position.

    - graph_ids (list, optional): A list of graph IDs to apply the tooltip to. 
                                  If not provided, tooltips will be added to all graphs in the app.
    """
    
    if graph_ids is None:
        # If no graph_ids are provided, find all graph IDs in the layout
        graph_ids = _find_all_graph_ids(app.layout)
        if not graph_ids:
            raise ValueError("No graphs found in the app layout. Please provide a graph ID.")
    
    for graph_id in graph_ids:
        # Add the required dcc.Store for annotations if it isn't already present
        add_annotation_store(app.layout, graph_id)

        # Register the main callback for displaying click data as annotations
        @app.callback(
            Output(component_id=graph_id, component_property='figure'),
            Input(component_id=graph_id, component_property='clickData'),
            State(component_id=graph_id, component_property='figure')
        )
        def display_click_data(clickData, figure):
            return _display_click_data(clickData, figure, app, template, style)

        # Register the clientside callback for capturing annotation removal
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
            Output(f'tooltip-annotations-to-remove-{graph_id}', 'data'),
            Input(graph_id, 'relayoutData')
        )

        # Register the callback for removing annotations
        @app.callback(
            Output(graph_id, 'figure', allow_duplicate=True),
            Input(f'tooltip-annotations-to-remove-{graph_id}', 'data'),
            State(graph_id, 'figure'),
            prevent_initial_call=True
        )
        def remove_empty_annotations(indices_to_remove, current_figure):
            if indices_to_remove:
                annotations = current_figure['layout'].get('annotations', [])
                updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]
                current_figure['layout']['annotations'] = updated_annotations
            return current_figure


def _find_all_graph_ids(layout: dash.html.Div) -> List[str]:
    """
    Recursively find all dcc.Graph IDs in a Dash layout.
    """
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


def _display_click_data(clickData: Dict[str, Union[float, str, List[Dict[str, Union[float, str]]]]], 
                        figure: go.Figure, 
                        app: dash.Dash, 
                        template: str, 
                        config: Dict[str, Union[str, float, int]]) -> go.Figure:
    """
    Create and display a tooltip based on the clicked data point.
    """
    fig = go.Figure(figure)
    
    # Merge the provided config with the default one
    merged_config = {**DEFAULT_ANNOTATION_CONFIG, **config}
    
    # If the tooltip is not active, prevent the update
    if not getattr(app, 'tooltip_active', True):
        raise dash.exceptions.PreventUpdate
    
    if clickData:
        point = clickData['points'][0]
        x_val = point['x']
        y_val = point['y']
        
        # Extract keys from the template
        keys_in_template = re.findall(r"\%{(.*?)(?:\[(\d+)\])?}", template)  # This will capture both 'key' and 'index' if present
        
        template_data = {}
        for key, idx in keys_in_template:
            if idx:  # If there's an index, it means it's a list-like parameter
                data_list = point.get(key, [])
                if int(idx) < len(data_list):
                    key_name = f"{key}[{idx}]"
                    template_data[key_name] = data_list[int(idx)]
            else:
                value = point.get(key, "")
                template_data[key] = value
        
        # Replace placeholders in the template with their corresponding values
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
