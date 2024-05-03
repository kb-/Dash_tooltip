import plotly.graph_objs as go

from dash_tooltip import DEFAULT_TEMPLATE


class CustomFigure(go.Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tooltip_template = DEFAULT_TEMPLATE

    def update_template(self, template):
        self.layout._tooltip_template = template
