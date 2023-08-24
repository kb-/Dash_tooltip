
# Dash Tooltip

Easily add tooltips to your Plotly Dash applications with the `dash_tooltip` module. 

## Features

- **Simple Integration**: Just a few lines of code to integrate with your Dash application.
- **Customizable**: Customize tooltip appearance including text color, arrow color, arrow size, and more.
- **Template-based**: Define your own tooltip content using a template string.
- **Supports Custom Data**: If your graph has custom data, the tooltip can display it seamlessly.
- **Annotation Removal**: Tooltips (annotations) can be removed by the user (click, delete text, press enter).

## Installation

```bash
pip install dash-tooltip
```

## Usage

Here's a basic example of how to use the `dash_tooltip` module:

```python
from dash_tooltip import tooltip

# Your Dash app instance
app = dash.Dash(__name__)

# Your app layout with at least one graph
app.layout = html.Div([
    dcc.Graph(id='my-graph', figure=...),
])

# Add tooltips to your app
tooltip(app)

# Run your app
if __name__ == '__main__':
    app.run_server(debug=True)
```

### Advanced Usage

Customize the tooltip's appearance and content:

```python
from dash_tooltip import tooltip

# Define custom appearance for the tooltip
custom_style = {
    'text_color': 'red',
    'arrow_color': 'blue',
    'arrow_size': 2.5,
    'arrow_width': 1,
    'arrow_head': 3,
    'x_anchor': 'left',
    'alignment': 'left'
}

# Define custom template for the tooltip content
custom_template = "x: {x},<br>y: {y}<br>{customdata[0]}"

# Add tooltips with custom appearance and content
tooltip(app, style=custom_style, template=custom_template)
```

**Note**: The template string uses placeholders like `{x}`, `{y}`, `{customdata[0]}`, etc., based on the data available in the graph's `clickData`. To incorporate custom data in the tooltip, use the placeholder `{customdata[i]}` where `i` is the index of the desired item in the custom data list.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to open a pull request or raise an issue.

