import plotly.graph_objects as go
import plotly.io as pio

# print(pio.renderers)
pio.renderers.default = "browser"

fig = go.Figure(
    data=[
        go.Scatter(
            x=[1, 2, 3, 4],
            y=[10, 11, 12, 13],
            mode="markers",
            marker=dict(size=14),
            name="Data Series 1",
            customdata=[["info1"], ["info2"], ["info3"], ["info4"]],
        )
    ]
)

# Customize layout
fig.update_layout(title="Interactive Plot")
fig.update_layout(
    dragmode="drawrect",
    # style of new shapes
    newshape=dict(
        line_color="blue",
        fillcolor="turquoise",
        opacity=0.9,
        line_width=1,
        line_dash="dashdot",
    ),
)
print(
    fig.show(
        config={
            "displaylogo": False,
            "modeBarButtonsToAdd": [
                "drawline",
                "drawopenpath",
                "drawclosedpath",
                "drawcircle",
                "drawrect",
                "eraseshape",
                "toggleSpikelines",
            ],
        }
    )
)
