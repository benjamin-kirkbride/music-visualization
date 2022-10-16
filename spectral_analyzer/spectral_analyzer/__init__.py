from pathlib import Path

import tomli

PROJECT_ROOT = Path(__file__).parent

with open(PROJECT_ROOT.parent / "config.toml", "rb") as f:
    config = tomli.load(f)
