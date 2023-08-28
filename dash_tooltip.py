
import plotly.graph_objs as go
import dash
from dash import Output, Input, State, dcc
from typing import List, Optional, Dict, Union
import re
import json
from typing import Optional

def add_annotation_store(layout: dash.html.Div, graph_id: Optional[str] = None) -> str:
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

def find_first_graph_id(layout: dash.html.Div) -> Optional[str]:
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

def tooltip(app: dash.Dash, style: Dict[str, Union[str, float, int]] = DEFAULT_ANNOTATION_CONFIG, template: str = DEFAULT_TEMPLATE, graph_ids: Optional[List[str]] = None, debug: bool = False) -> None:
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
            if indices_to_remove:
                annotations = current_figure['layout'].get('annotations', [])
                updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]
                current_figure['layout']['annotations'] = updated_annotations
            return current_figure

def _find_all_graph_ids(layout: dash.html.Div) -> List[str]:
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

def extract_value_from_point(point, key):
    parts = key.split('.')
    
    temp = point
    for part in parts:
        if re.match(r"\w+\[\d+\]", part):
            name = part.split('[')[0]
            index = int(part.split('[')[1].replace(']', ''))
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

def _display_click_data(clickData: Dict[str, Union[float, str, List[Dict[str, Union[float, str]]]]], 
                        figure: go.Figure, 
                        app: dash.Dash, 
                        template: str, 
                        config: Dict[str, Union[str, float, int]],
                        debug: bool) -> go.Figure:
    fig = go.Figure(figure)
    merged_config = {**DEFAULT_ANNOTATION_CONFIG, **config}
    
    if not getattr(app, 'tooltip_active', True):
        raise dash.exceptions.PreventUpdate
    
    if clickData:
        point = clickData['points'][0]
        x_val = point['x']
        y_val = point['y']

        if debug:
            with open('tooltip.log', 'a') as f:
                f.write("Point data:\n")
                f.write(json.dumps(point, indent=4))
                f.write("\nTrace data:\n")
                f.write(json.dumps(figure['data'][point['curveNumber']], indent=4))
                f.write("\n" + "="*40 + "\n")

            
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
