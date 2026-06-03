from dash_tooltip.__init__ import _apply_annotation_relayout


def test_apply_annotation_relayout_updates_dragged_annotation_position() -> None:
    figure = {
        "layout": {
            "annotations": [
                {"x": 1, "y": 2, "ax": 20, "ay": -30, "text": "first"},
                {"x": 3, "y": 4, "ax": 20, "ay": -30, "text": "second"},
            ]
        }
    }

    changed = _apply_annotation_relayout(
        figure,
        {
            "annotations[0].x": 10,
            "annotations[0].y": 11,
            "annotations[0].ax": 30,
            "annotations[0].ay": -40,
        },
    )

    assert changed is True
    assert figure["layout"]["annotations"][0] == {
        "x": 10,
        "y": 11,
        "ax": 30,
        "ay": -40,
        "text": "first",
    }
    assert figure["layout"]["annotations"][1] == {
        "x": 3,
        "y": 4,
        "ax": 20,
        "ay": -30,
        "text": "second",
    }


def test_apply_annotation_relayout_ignores_unrelated_relayout_keys() -> None:
    figure = {"layout": {"annotations": [{"x": 1, "y": 2, "text": "first"}]}}

    changed = _apply_annotation_relayout(
        figure,
        {
            "xaxis.range[0]": 0,
            "xaxis.range[1]": 5,
        },
    )

    assert changed is False
    assert figure["layout"]["annotations"][0] == {"x": 1, "y": 2, "text": "first"}


def test_apply_annotation_relayout_ignores_out_of_range_annotation_index() -> None:
    figure = {"layout": {"annotations": [{"x": 1, "y": 2, "text": "first"}]}}

    changed = _apply_annotation_relayout(
        figure,
        {
            "annotations[2].x": 10,
            "annotations[2].y": 11,
        },
    )

    assert changed is False
    assert figure["layout"]["annotations"] == [{"x": 1, "y": 2, "text": "first"}]
