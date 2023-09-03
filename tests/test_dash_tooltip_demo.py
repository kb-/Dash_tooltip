import re
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import dash
from dash import Dash
from plotly_resampler import FigureResampler


def mock_show_dash(*args, **kwargs):
    # If the first argument is an instance of FigureResampler
    if hasattr(args[0], "_app"):
        # Set a dummy Dash app
        args[0]._app = Dash(__name__)
    print("show_dash mock called!")


# Backup of the original __init__ method of FigureResampler
original_init = FigureResampler.__init__


def mock_init(self, *args, **kwargs):
    # Call the original __init__ method
    original_init(self, *args, **kwargs)

    # Set a mock Dash app for _app attribute
    self._app = Dash(__name__)


# Patch the __init__ method of FigureResampler
FigureResampler.__init__ = mock_init


def execute_demos(file_content):
    """
    Execute each demo from the provided file_content.
    Returns a dictionary with the results.
    """
    # Split the file content using the delimiter '# %%' while retaining the delimiter
    code_blocks = re.split("(# %%)", file_content)
    code_blocks = [
        "".join(x) for x in zip(code_blocks[1::2], code_blocks[2::2])
    ]  # combine delimiter with the subsequent block

    results = {}
    namespace = {"__name__": "__main__"}

    for idx, block in enumerate(code_blocks, start=1):
        try:
            with patch("dash.Dash.run", return_value=None), patch(
                "plotly_resampler.FigureResampler.show_dash", return_value=MagicMock()
            ):
                exec(block, namespace)
            results[f"Demo {idx}"] = "Passed"
        except Exception as e:
            # Extract a snippet of code around the error
            lines = block.split("\n")
            error_line = getattr(e, "lineno", "N/A")
            if len(lines) <= 15:
                snippet = "\n".join(lines)
            else:
                snippet = "\n".join(lines[:5]) + "\n..."

            results[f"Demo {idx}"] = (
                f"Failed with error at line {error_line}: {str(e)}\n\n"
                f"Code Snippet:\n{snippet}\n"
                f"{'-' * 80}"
            )

    return results


def test_code_execution():
    file_path = "dash_tooltip_demo.py"
    code = Path(file_path).read_text()
    result = execute_demos(code)
    # Adjust the assertion to check if all demos passed
    all_passed = all([res == "Passed" for res in result.values()])
    assert all_passed, f"Error: {result}"


if __name__ == "__main__":
    test_code_execution()
