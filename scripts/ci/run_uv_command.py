"""Execute a configured uv binary as an argv value, never as shell source."""

from __future__ import annotations

import os
import subprocess
import sys


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return 2
    executable = os.environ.get("UV")
    if not executable:
        print("ERROR: invalid uv executable configuration.", file=sys.stderr)
        return 2
    environment = dict(os.environ, UV_EXECUTABLE=executable)
    try:
        return subprocess.run([executable, *argv[1:]], check=False, env=environment).returncode
    except OSError as error:
        print(f"ERROR: unable to execute configured uv: {error}", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
