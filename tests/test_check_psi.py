import subprocess
import sys
from pathlib import Path


def test_cli_no_arguments():
    script_path = Path("src/check_psi/cli.py")

    result = subprocess.run(
        [sys.executable, str(script_path), "-h"],
        capture_output=True,
        text=True,
    )

    # Help should exit with 0
    assert result.returncode == 0, f"Expected return code 0, got {result.returncode}"

    output = result.stdout.lower() + result.stderr.lower()
    assert "usage" in output, "Expected 'usage' in help output"


def test_cli_requires_resource_argument():
    script_path = Path("src/check_psi/cli.py")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2

    output = result.stdout.lower() + result.stderr.lower()

    assert "required" in output
    assert "resource" in output
