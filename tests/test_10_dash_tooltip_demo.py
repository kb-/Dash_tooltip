import re
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

from dash import Dash


# Mock the run method of the Dash app
def mock_run_app(*args: Any, **kwargs: Any) -> None:
    print("Dash app run method mock called!")


# Override the run method
def new_run(self: Dash, *args: Any, **kwargs: Any) -> None:
    print("Overridden Dash app run method!")
    # You can add any additional setup or configuration code here if necessary


def execute_demos(file_content: str) -> Dict[str, str]:
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


def test_code_execution() -> None:
    with patch.object(
        Dash, "run", new_run
    ):  # Temporarily replace Dash.run with new_run
        file_path = "dash_tooltip_demo.py"
        code = Path(file_path).read_text()
        result = execute_demos(code)
        # Adjust the assertion to check if all demos passed
        all_passed = all([res == "Passed" for res in result.values()])
        assert all_passed, f"Error: {result}"


if __name__ == "__main__":
    test_code_execution()
