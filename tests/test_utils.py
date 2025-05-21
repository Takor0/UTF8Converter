from pathlib import Path

import pytest

from converter.utils import validate_input_file, prepare_output_path


def test_validate_input_file(tmp_path):
    p = tmp_path / "file.txt"
    p.write_text("mail metrics")
    assert validate_input_file(p) == p

    with pytest.raises(FileNotFoundError):
        validate_input_file(tmp_path / "not_exist.txt")
    with pytest.raises(IsADirectoryError):
        validate_input_file(tmp_path)
    p2 = tmp_path / "wrong_ext.bin"
    p2.write_text("data")
    with pytest.raises(ValueError):
        validate_input_file(p2)

def test_prepare_output_path(tmp_path):
    src = Path("input.txt")
    dst = tmp_path / ("out_"
                      "dir")
    dst.mkdir()
    out = prepare_output_path(src, dst, create_output_dir=False)
    assert out == dst / "input.txt"
    new_dir = tmp_path / "new_dir"
    out2 = prepare_output_path(src, new_dir, create_output_dir=True)
    assert new_dir.exists() and out2 == new_dir / "input.txt"
    file = tmp_path / "file.txt"
    out3 = prepare_output_path(src, file, create_output_dir=False)
    assert file.parent.exists() and out3 == file
    bad = tmp_path / "bad.bin"
    with pytest.raises(ValueError):
        prepare_output_path(src, bad, create_output_dir=True)