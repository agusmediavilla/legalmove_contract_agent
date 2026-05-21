from pathlib import Path

import pytest

from src.image_parser import validate_image_path


def test_validate_image_path_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        validate_image_path("missing.jpg")


def test_validate_image_path_rejects_unsupported_suffix(tmp_path: Path):
    p = tmp_path / "contract.txt"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        validate_image_path(p)
