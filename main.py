import os
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from pathlib import Path
import logging
from typing import Optional, Union

import chardet
import re

from tqdm import tqdm

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".txt"}
SAMPLE_SIZE = 1024 * 100


def detect_encoding(path: Path) -> Optional[str]:
    if path.stat().st_size <= SAMPLE_SIZE:
        data = path.read_bytes()
    else:
        with path.open("rb") as f:
            data = f.read(SAMPLE_SIZE)

    enc = chardet.detect(data).get("encoding")
    return enc


def convert_file(input_file: Path, output_file: Path) -> None:
    enc = detect_encoding(input_file)
    if not enc:
        raise ValueError(f"Cannot detect encoding: {input_file}")
    text = input_file.read_text(encoding=enc)
    output_file.write_text(text, encoding="utf-8")


def validate_file(src: Union[Path, str], should_exist: bool) -> Path:
    path = Path(src)
    if path.is_file() and path.suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension: {path.suffix}")
    if should_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path



class UTF8Converter:
    def __init__(self, src: Union[Path, str], dst: Union[Path, str]):
        self.src = validate_file(src, True)
        self.dst = validate_file(dst, False)

    @property
    def files(self) -> list[Path]:
        if self.src.is_dir():
            return list(self.src.glob("*.txt"))
        else:
            return [self.src]

    def convert(self, use_processes: bool = False, max_workers: int = None) -> None:
        Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        with Executor(max_workers=max_workers) as executor, tqdm(
            total=len(self.files)
        ) as progress:
            futures = [
                executor.submit(
                    convert_file,
                    f,
                    self.dst / f.name if self.src.is_dir() else self.dst,
                )
                for f in self.files
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error processing file: {e}")
                finally:
                    progress.update(1)


timer = time()
conv = UTF8Converter(
    "/home/tomi0985/PycharmProjects/utf8-converter/test_data_future/input",
    "/home/tomi0985/PycharmProjects/utf8-converter/test_data_future/output",
)
conv.convert(True)
print(f"time with futures: {time() - timer:.10f} seconds")


timer = time()
conv = UTF8Converter(
    "/home/tomi0985/PycharmProjects/utf8-converter/test_data/input",
    "/home/tomi0985/PycharmProjects/utf8-converter/test_data/output",
)
conv.convert(False)
print(f"time without futures: {time() - timer:.10f} seconds")
