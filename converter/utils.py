from pathlib import Path
from typing import Union

from converter.constants import ALLOWED_EXTENSIONS


def validate_input_file(src: Union[Path, str]) -> Path:
    """
    Validate the input file.
    :param src:
    :return: validated file path
    """
    path = Path(src)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Path is not a file: {path}")
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension: {path.suffix}")
    return path


def prepare_output_path(
    src: Path, dst: Union[Path, str], create_output_dir: bool
) -> Path:
    """
    Create and validate the output path.
    :param src: path to the source file
    :param dst: path to the destination file or directory
    :param create_output_dir: flag to create output directory if it does not exist
    :return: validated output path
    """
    dst_path = Path(dst)
    if dst_path.suffix and dst_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Output must be a .txt file or directory: invalid extension {dst_path.suffix}"
        )
    if dst_path.exists() and dst_path.is_dir():
        output_file = dst_path / src.name
    elif create_output_dir and not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)
        output_file = dst_path / src.name
    else:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        output_file = dst_path
    if output_file.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Output must be file with {ALLOWED_EXTENSIONS} extension: {output_file}"
        )
    return output_file
