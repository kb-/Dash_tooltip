import logging
from string import Template
from typing import Any, Dict, List, Optional, Union

import plotly.graph_objs as go
from dash import Input, Output, State, dash

from .config import DEFAULT_ANNOTATION_CONFIG
from .utils import _display_click_data, _find_all_graph_ids, add_annotation_store

# Logger setup
logger = logging.getLogger("dash_tooltip")
logger.setLevel(logging.DEBUG)

# File handler setup
file_handler = logging.FileHandler("dash_app.log")
file_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

# Prevent logs from being propagated to the root logger
logger.propagate = False

# Now, you can log messages
logger.debug("dash_tooltip log active")

DEFAULT_TEMPLATE = "x: %{x},<br>y: %{y}"


def tooltip(
    app: dash.Dash,
    style: Dict[Any, Any] = DEFAULT_ANNOTATION_CONFIG,
    template: str = DEFAULT_TEMPLATE,
    graph_ids: Optional[List[str]] = None,
    debug: bool = False,
) -> None:
    """
    Add tooltip functionality to Dash graph components.

    Args:
    - app (dash.Dash): The Dash app instance.
    - style (dict): Configuration for the tooltip appearance. Users can provide any
                    valid Plotly annotation style options.
                    Default values are set in DEFAULT_ANNOTATION_CONFIG.
    - template (str): A string defining how the tooltip should be displayed using
                    Plotly's template syntax. Users can modify this template to
                    customize the tooltip content.
    - graph_ids (list, optional): List of graph component IDs for the tooltip
                    functionality. If None, function will try to find graph IDs
                    automatically.
    - debug (bool): If True, debug information will be written to a log file
                    (tooltip.log).

    Example:
    tooltip(app,
            style={'text_color': 'red'},
            template="x: %{x},<br>y: %{y}<br>ID: %{pointNumber}",
            graph_ids=['graph-1'])
    """
    if graph_ids is None:
        graph_ids = _find_all_graph_ids(app.layout)
        if not graph_ids:
            raise ValueError(
                "No graphs found in the app layout. Please provide a graph ID."
            )

    for graph_id in graph_ids:
        if graph_id not in app.layout:
            raise ValueError(f"Invalid graph ID provided: {graph_id}")
        add_annotation_store(app.layout, graph_id)

        @app.callback(  # type: ignore
            Output(component_id=graph_id, component_property="figure"),
            Input(component_id=graph_id, component_property="clickData"),
            State(component_id=graph_id, component_property="figure"),
        )
        def display_click_data(
            clickData: Dict[str, Any], figure: go.Figure
        ) -> go.Figure:
            return _display_click_data(clickData, figure, app, template, style, debug)

        dbg_str = "console.log(relayoutData);"

        app.clientside_callback(
            Template(
                r"""
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
            """
            ).substitute(dbg_str=dbg_str),
            Output(f"tooltip-annotations-to-remove-{graph_id}", "data"),
            Input(graph_id, "relayoutData"),
        )

        @app.callback(  # type: ignore
            Output(graph_id, "figure", allow_duplicate=True),
            Input(f"tooltip-annotations-to-remove-{graph_id}", "data"),
            State(graph_id, "figure"),
            prevent_initial_call=True,
        )
        def remove_empty_annotations(
            indices_to_remove: List[int], current_figure: Dict[str, Any]
        ) -> Union[Dict[str, Any], dash._callback.NoUpdate]:
            """Remove annotations that have been deleted by the user."""
            if indices_to_remove:
                annotations = current_figure["layout"].get("annotations", [])

                # Log the original annotations
                logger.debug(f"Original Annotations: {annotations}")

                updated_annotations = [
                    anno
                    for idx, anno in enumerate(annotations)
                    if idx not in indices_to_remove
                ]

                # Log the indices being removed
                logger.debug(f"Indices to Remove: {indices_to_remove}")

                # Log the updated annotations
                logger.debug(f"Updated Annotations: {updated_annotations}")

                current_figure["layout"]["annotations"] = updated_annotations
                return current_figure  # update figure with new annotations list
            return dash.no_update  # prevent undesired update when no change is done
            # (also prevents breaking)


__all__ = [
    "tooltip",
    "add_annotation_store",
    "DEFAULT_ANNOTATION_CONFIG",
    "DEFAULT_TEMPLATE",
]
