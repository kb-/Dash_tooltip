"""Public version metadata and imports from an unbuilt source checkout."""

import json
import os
import shutil
import site
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import dash_tooltip


def test_public_version_matches_installed_distribution():
    from dash_tooltip._version import __version__

    assert dash_tooltip.__version__ == __version__ == version("Dash_tooltip")


def test_unbuilt_checkout_without_generated_version_can_be_imported(tmp_path):
    package = Path(dash_tooltip.__file__).parent
    shutil.copytree(package, tmp_path / "dash_tooltip", ignore=shutil.ignore_patterns("_version.py", "__pycache__"))
    env = dict(os.environ, PYTHONPATH=str(tmp_path))
    # Skip .pth import hooks from the editable install while retaining dependencies.
    script = """
import json
import sys
sys.path.extend(json.loads(sys.argv[1]))
import dash_tooltip
print(dash_tooltip.__version__)
"""

    result = subprocess.run(
        [sys.executable, "-S", "-c", script, json.dumps(site.getsitepackages())],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == "0+unknown"
