import logging
import re
from string import Template
from typing import Any, Dict, List, Optional, Union

import plotly.graph_objs as go
from dash import Input, Output, State, dash
from dash.exceptions import PreventUpdate

from .config import DEFAULT_ANNOTATION_CONFIG, DEFAULT_TEMPLATE
from .custom_figure import CustomFigure
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

registered_callbacks = set()
ANNOTATION_RELAYOUT_KEY = re.compile(r"annotations\[(\d+)\]\.(.+)")


def _apply_annotation_relayout(current_figure: Dict[str, Any], relayout_data: Dict[str, Any]) -> bool:
    """Persist client-side annotation edits back into the server-side figure."""
    if not relayout_data:
        return False

    annotation_updates: Dict[int, Dict[str, Any]] = {}
    for key, value in relayout_data.items():
        match = ANNOTATION_RELAYOUT_KEY.fullmatch(key)
        if not match:
            continue

        index = int(match.group(1))
        property_name = match.group(2)
        annotation_updates.setdefault(index, {})[property_name] = value

    if not annotation_updates:
        return False

    layout = current_figure.get("layout")
    if not isinstance(layout, dict):
        return False

    annotations = layout.get("annotations", [])
    if not isinstance(annotations, list) or not annotations:
        return False

    changed = False
    for index, properties in annotation_updates.items():
        if index >= len(annotations):
            continue
        annotation = annotations[index]
        if not isinstance(annotation, dict):
            annotation = dict(annotation)
        annotation.update(properties)
        annotations[index] = annotation
        changed = True

    if changed:
        layout["annotations"] = annotations
    return changed


class TooltipManager:
    def __init__(
        self,
        app: dash.Dash,
        style: Dict[Any, Any],
        template: str,
        graph_ids: List[str],
        apply_log_fix: bool,
        debug: bool,
    ):
        self.figures = {graph_id: CustomFigure() for graph_id in graph_ids}
        self.templates = {graph_id: template for graph_id in graph_ids}
        self.style = style
        self.apply_log_fix = apply_log_fix
        self.debug = debug
        self.app = app
        self.graph_ids = graph_ids
        self.tooltip_active = True  # Default to active
        self.initialize_callbacks()

    def update_template(self, graph_id: str, template: str):
        if graph_id in self.figures:
            self.templates[graph_id] = template
            self.figures[graph_id].update_template(template)

    def initialize_callbacks(self):
        for graph_id in self.graph_ids:
            callback_identifier = (graph_id, "figure")
            if callback_identifier in registered_callbacks:
                # Skip reattaching if already registered
                continue
            registered_callbacks.add(callback_identifier)

            # Check for valid graph ID and add annotation store
            if graph_id not in self.app.layout:
                raise ValueError(f"Invalid graph ID provided: {graph_id}")
            add_annotation_store(self.app.layout, graph_id)

            @self.app.callback(
                Output(component_id=graph_id, component_property="figure"),
                Input(component_id=graph_id, component_property="clickData"),
                State(component_id=graph_id, component_property="figure"),
            )
            def display_click_data(
                clickData: Dict[str, Any],
                figure: Union[CustomFigure, Dict[str, Any]],
            ) -> CustomFigure:
                """Display data on click event."""
                if not self.tooltip_active:
                    raise PreventUpdate

                if figure is None:
                    figure = CustomFigure()

                template = self.templates[graph_id]
                if isinstance(figure, CustomFigure):
                    return _display_click_data(clickData, figure, template, self.style)
                # Check if figure is a dictionary
                elif isinstance(figure, dict):
                    # Extract data and layout from the figure dictionary
                    raw_data = figure.get("data", [])
                    layout = figure.get("layout", {})

                    # Convert dictionary representations of traces into actual trace objects
                    data = []
                    for trace in raw_data:
                        trace_type = trace.pop("type")
                        trace_class = getattr(go, trace_type.capitalize())
                        data.append(trace_class(**trace))

                    # Construct the CustomFigure(go.Figure) using data and layout
                    custom_figure = CustomFigure(data=data, layout=layout)
                    return _display_click_data(clickData, custom_figure, template, self.style)
                else:
                    custom_figure = CustomFigure(figure)
                    return _display_click_data(clickData, custom_figure, template, self.style)

            @self.app.callback(
                Output(graph_id, "figure", allow_duplicate=True),
                Input(graph_id, "relayoutData"),
                State(graph_id, "figure"),
                prevent_initial_call=True,
            )
            def persist_annotation_relayout(
                relayout_data: Dict[str, Any], current_figure: Dict[str, Any]
            ) -> Union[Dict[str, Any], dash._callback.NoUpdate]:
                """Persist dragged or edited annotation properties."""
                if current_figure and _apply_annotation_relayout(current_figure, relayout_data):
                    return current_figure
                return dash.no_update

            @self.app.callback(
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
                    logger.debug(f"Original Annotations: {annotations}")
                    updated_annotations = [anno for idx, anno in enumerate(annotations) if idx not in indices_to_remove]
                    logger.debug(f"Indices to Remove: {indices_to_remove}")
                    logger.debug(f"Updated Annotations: {updated_annotations}")
                    current_figure["layout"]["annotations"] = updated_annotations
                    return current_figure
                return dash.no_update

            # Client-side callback to identify annotations to remove
            dbg_str = "console.log(relayoutData);" if self.debug else ""
            self.app.clientside_callback(
                Template(
                    """
                    function(relayoutData) {
                        $dbg_str
                        var annotationPattern = /annotations\\[(\\d+)\\].text/;
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


def tooltip(
    app: dash.Dash,
    style: Dict[Any, Any] = DEFAULT_ANNOTATION_CONFIG,
    template: str = DEFAULT_TEMPLATE,
    graph_ids: Optional[List[str]] = None,
    apply_log_fix: bool = True,
    debug: bool = False,
) -> TooltipManager:
    """
    Add tooltip functionality to Dash graph components.

    Args:
        app (dash.Dash): The Dash app instance.
        style (dict): Configuration for the tooltip appearance.
                      Users can provide any valid Plotly annotation style options.
        template (str): The default annotation template.
                        Default is a basic string template.
        graph_ids (list, optional): List of graph IDs to apply tooltips to.
                                    If not provided, will try to auto-detect from the layout.
        apply_log_fix (bool): If True, applies a fix for logging issues.
        debug (bool): If True, enables debugging mode.

    Returns:
        TooltipManager: An instance of TooltipManager class.
    """
    if graph_ids is None:
        graph_ids = _find_all_graph_ids(app.layout)
        if not graph_ids:
            raise ValueError("No graphs found in the app layout. Please provide a graph ID.")
    return TooltipManager(app, style, template, graph_ids, apply_log_fix, debug)


__all__ = [
    "tooltip",
    "add_annotation_store",
    "DEFAULT_ANNOTATION_CONFIG",
    "DEFAULT_TEMPLATE",
]
