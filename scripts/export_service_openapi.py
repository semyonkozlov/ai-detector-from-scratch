#!/usr/bin/env python3
"""Write the scoring service's OpenAPI spec to openapi.yaml."""

from pathlib import Path

import yaml

from ai_detector.service import app


OUTPUT = Path(__file__).resolve().parents[1] / "openapi.yaml"


def main():
    OUTPUT.write_text(
        yaml.safe_dump(app.openapi(), sort_keys=False), encoding="utf-8"
    )
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
