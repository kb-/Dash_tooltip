import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

import dash
import plotly.graph_objs as go
from dash import dcc
from dash.html import Div

from dash_tooltip import DEFAULT_ANNOTATION_CONFIG

logger = logging.getLogger("dash_tooltip")


def add_annotation_store(layout: Div, graph_id: Optional[str] = None) -> str:
    """
    Adds a dcc.Store component to the layout to store annotations for tooltips.

    Args:
    - layout (dash.html.Div): The Dash app layout.
    - graph_id (str, optional): The ID of the graph component to which the store is
    linked.

    Returns:
    - str: The ID of the added dcc.Store component.
    """
    store_id = "tooltip-annotations-to-remove"
    if graph_id:
        store_id += f"-{graph_id}"

    if not any(
        isinstance(child, dcc.Store) and child.id == store_id
        for child in layout.children
    ):
        layout.children.append(dcc.Store(id=store_id))

    return store_id


def _find_all_graph_ids(layout: Div) -> List[str]:
    """Recursively search for all graph component IDs in the app layout."""
    graph_ids = []

    if isinstance(layout, dcc.Graph):
        return [layout.id]

    if hasattr(layout, "children"):
        if isinstance(layout.children, list):
            for child in layout.children:
                graph_ids.extend(_find_all_graph_ids(child))
        else:
            graph_ids.extend(_find_all_graph_ids(layout.children))

    return graph_ids


def extract_value_from_point(point: Dict[str, Any], key: str) -> Any:
    """Extracts the value from the point dictionary using a dot notation key."""
    try:
        parts = key.split(".")
        temp: Any = point  # fix type hint issue
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
    Truncate arrays in a JSON string representation to a specified limit, both at top
    level and nested.

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


def _display_click_data(
    clickData: Dict[str, Any],
    figure: Union[go.Figure, Dict[str, Any]],  # Allow both go.Figure and dictionary
    app: dash.Dash,
    template: str,
    config: Dict[Any, Any],
    debug: bool,
) -> go.Figure:
    """Displays the tooltip on the graph when a data point is clicked."""

    # Check if figure is a dictionary
    if isinstance(figure, dict):
        # Extract data and layout from the figure dictionary
        raw_data = figure.get("data", [])
        layout = figure.get("layout", {})

        # Convert dictionary representations of traces into actual trace objects
        data = []
        for trace in raw_data:
            trace_type = trace.pop("type")
            trace_class = getattr(go, trace_type.capitalize())
            data.append(trace_class(**trace))

        # Construct the go.Figure using data and layout
        fig = go.Figure(data=data, layout=layout)
    else:
        fig = figure

    merged_config = deep_merge_dicts(DEFAULT_ANNOTATION_CONFIG.copy(), config)

    if not getattr(app, "tooltip_active", True):
        raise dash.exceptions.PreventUpdate

    if clickData:
        point = clickData["points"][0]
        x_val = point["x"]
        y_val = point["y"]

        # Extract the clicked axis information from the curve data
        if "xaxis" in figure["data"][point["curveNumber"]]:
            xaxis = figure["data"][point["curveNumber"]]["xaxis"]
        else:
            xaxis = "x"

        if "yaxis" in figure["data"][point["curveNumber"]]:
            yaxis = figure["data"][point["curveNumber"]]["yaxis"]
        else:
            yaxis = "y"

        if debug:
            logger.debug(
                f"clickData: {truncate_json_arrays(json.dumps(clickData, indent=4),2)}"
            )
            logger.debug(
                f"figure: {truncate_json_arrays(json.dumps(figure, indent=4),2)}"
            )
            logger.debug(
                "Point data:\n%s", truncate_json_arrays(json.dumps(point, indent=4), 2)
            )
            logger.debug(
                "Trace data:\n%s",
                truncate_json_arrays(
                    json.dumps(figure["data"][point["curveNumber"]], indent=4), 2
                ),
            )

        placeholders = re.findall(r"%{(.*?)}", template)

        template_data = {}
        for placeholder in placeholders:
            parts = placeholder.split(":")
            var_name = parts[0]
            format_spec = parts[1] if len(parts) > 1 else None

            value = extract_value_from_point(point, var_name)
            if value is not None:
                if format_spec:
                    try:
                        # Applying the format specifier directly
                        template_data[placeholder] = f"{value:{format_spec}}"
                    except ValueError as e:
                        # Fallback to string representation if formatting fails
                        logger.error(
                            f"Error formatting value {value}, with format {format_spec}"
                            f" properties in {merged_config}. Error: {e}"
                        )
                        template_data[placeholder] = str(value)
                else:
                    template_data[placeholder] = str(value)

        for placeholder, value in template_data.items():
            template = template.replace(f"%{{{placeholder}}}", value)

        try:
            fig.add_annotation(
                x=x_val, y=y_val, xref=xaxis, yref=yaxis, text=template, **merged_config
            )
        except ValueError as e:
            logger.error(
                f"Failed to add annotation due to invalid"
                f" properties in {merged_config}. Error: {e}"
            )
            raise e
    return fig
