![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash-tooltip)

# Dash Tooltip

A module to add interactive editable tooltips to your Dash applications. Inspired by `mplcursors` and Matlab's `datatip`.

![newplot(6)](https://github.com/kb-/Dash_tooltip/assets/2260417/0d62008c-25f2-4128-aa31-6746b6b82248)

## Installation

You can download the `dash_tooltip.py` module and place it in your working directory.

## Basic Usage

```python
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash_tooltip import tooltip

# Sample Data
np.random.seed(20)
y1 = np.random.normal(0, 10, 50)
x1 = np.arange(0, 50)
fig1 = px.scatter(x=x1, y=y1)
fig1.update_layout(title_text="Editable Title", title_x=0.5)

app1 = Dash(__name__)

#makes graph items, including tooltips editable
app1.layout = html.Div([
    dcc.Graph(
        id='graph1',
        figure=fig1,
        config={
            'editable': True,
            'edits': {
                'shapePosition': True,
                'annotationPosition': True
            }
        }
    )
])

# Add the tooltip functionality to the app
tooltip(app1)
```
Click on data points to add tooltips.
If `dcc.Graph` is configured editatble, tolltips:
- can be dragged around
- text can be edited on click
- can be deleted: click, delete text, enter. In some occasions a tooltip arrow may remain due to a Dash bug (clientside_callback not firing). In this cas, click near arrow end (mouse cursor changes to pointer), enter some text and repeat deletion and enter.


## Advanced Usage

If you want to customize the tooltips, hover templates, and more:

```python
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash_tooltip import tooltip

# Generate random time series data
date_rng = pd.date_range(start='2020-01-01', end='2020-12-31', freq='h')
ts1 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
ts2 = pd.Series(np.random.randn(len(date_rng)), index=date_rng)
df = pd.DataFrame({'Time Series 1': ts1, 'Time Series 2': ts2})

template = "x: %{x}<br>y: %{y}<br>ID: %{pointNumber}<br>name: %{customdata[0]}<br>unit: %{customdata[1]}"
fig10 = px.line(df, x=df.index, y=df.columns, title="Time Series Plot")

for i, trace in enumerate(fig10.data):
    trace.customdata = np.column_stack((np.repeat(df.columns[i], len(df)), np.repeat('#{}'.format(i+1), len(df))))
    trace.hovertemplate = template

app10 = Dash(__name__)

app10.layout = html.Div([
    dcc.Graph(
        id="graph-id",
        figure=fig10,
        config={
            'editable': True,
            'edits': {
                'shapePosition': True,
                'annotationPosition': True
            }
        }
    )
])

tooltip(app10, graph_ids=["graph-id"], template=template, debug=True)
```

## Custom Styling

```python
custom_config = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    # ... any other customization
}
tooltip(app10, graph_ids=["graph-id"], template=template, debug=True, **custom_config)
```

For more examples, refer to the provided `dash_tooltip_demo.py` or its Jupyter counterpart `dash_tooltip_demo.ipynb`.

## Debugging

If you encounter any issues or unexpected behaviors, enable the debug mode by setting the `debug` argument of the `tooltip` function to `True`. The log outputs will be written to `dash_app.log` in the directory where your script or application is located.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Inspired by `mplcursors` and Matlab's `datatip`.
