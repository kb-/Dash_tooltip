DEFAULT_ANNOTATION_CONFIG = {
    # horizontal alignment of the text (can be 'left', 'center', or 'right')
    "align": "left",
    "arrowcolor": "black",  # color of the annotation arrow
    "arrowhead": 3,  # type of arrowhead, for Plotly (an integer from 0 to 8)
    "arrowsize": 1.8,  # relative size of the arrowhead to the arrow stem, for Plotly
    "arrowwidth": 1,  # width of the annotation arrow in pixels, for Plotly
    "font": {
        "color": "black",  # color of the annotation text
        "family": "Arial",  # font family of the annotation text, for Plotly
        "size": 12,  # size of the annotation text in points, for Plotly
    },
    "showarrow": True,
    # horizontal alignment of the text (can be 'left', 'center', or 'right')
    "xanchor": "left",
}

DEFAULT_TEMPLATE = "x: %{x},<br>y: %{y}"
