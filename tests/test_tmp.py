from pathlib import Path
import dash
import re
from unittest.mock import patch, MagicMock


def mock_run(*args, **kwargs):
    print("Mocked run method called.")
    return None


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
            results[f"Demo {idx}"] = f"Failed with error: {str(e)}"

    return results


def test_code_execution():
    file_path = "tmp.py"
    code = Path(file_path).read_text()
    result = execute_demos(code)
    # Adjust the assertion to check if all demos passed
    all_passed = all([res == "Passed" for res in result.values()])
    assert all_passed, f"Error: {result}"


if __name__ == "__main__":
    test_code_execution()
