import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from pathlib import Path
import logging
from typing import Union

import chardet

from tqdm import tqdm


logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".txt"}
SAMPLE_SIZE = 1024 * 100


def validate_file(src: Union[Path, str], should_exist: bool = True) -> Path:
    path = Path(src)
    if should_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Path is not a file: {path}")
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension: {path.suffix}")

    return path


class UTF8Converter:
    def __init__(
        self,
        input_file: Union[Path, str],
        output_file: Union[Path, str],
        sample_size: int = SAMPLE_SIZE,
        create_output_dir: bool = False,
    ):
        self.sample_size = sample_size
        self.input_file = validate_file(input_file)
        self.output_file = validate_file(output_file, False)

        if create_output_dir:
            logger.debug(f"Creating output directory: {self.output_file.parent}")
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.output_file.parent.exists():
            raise FileNotFoundError(
                f"Output directory does not exist: {self.output_file.parent}"
            )

    @property
    def encoding_confidence(self) -> tuple[str | None, float]:
        if self.input_file.stat().st_size <= self.sample_size:
            data = self.input_file.read_bytes()
        else:
            with self.input_file.open("rb") as f:
                data = f.read(self.sample_size)

        detected = chardet.detect(data)
        return detected.get("encoding"), detected.get("confidence")

    def convert(self) -> Path:
        enc, confidence = self.encoding_confidence

        if not enc:
            raise ValueError(f"No encoding detected: {self.input_file}")
        text = self.input_file.read_text(encoding=enc)
        self.output_file.write_text(text, encoding="utf-8")

        logger.debug(
            f"File converted successfully (encoding: {enc} confidence: {confidence}): {self.input_file} -> {self.output_file}"
        )
        return self.output_file


def batch_processing(
    converters: list[UTF8Converter],
    use_processes: bool = False,
    max_workers: int = None,
) -> None:
    Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    with Executor(max_workers=max_workers) as executor, tqdm(
        total=len(converters),
        desc="Converting",
        dynamic_ncols=True,
        leave=True,
        unit="file",
    ) as progress:
        futures = [
            executor.submit(
                c.convert,
            )
            for c in converters
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Error processing file: {e}")
            finally:
                progress.update(1)


def make_converters(
    src: Union[Path, str],
    dst: Union[Path, str],
    sample_size: int = SAMPLE_SIZE,
    create_output_dir: bool = False,
) -> list[UTF8Converter]:
    path = Path(src)
    dst = Path(dst)
    if path.is_dir():
        return [
            UTF8Converter(
                input_file=file,
                output_file=dst / file.name,
                sample_size=sample_size,
                create_output_dir=create_output_dir,
            )
            for file in path.glob("*.txt")
        ]
    else:
        return [
            UTF8Converter(
                input_file=src,
                output_file=dst,
                sample_size=sample_size,
                create_output_dir=create_output_dir,
            )
        ]


if __name__ == "__main__":
    # Example usage

    parser = argparse.ArgumentParser(description="Convert files to UTF-8")
    parser.add_argument(
        "-s", "--src", type=str, required=True, help="Source file or directory"
    )
    parser.add_argument(
        "-d", "--dst", type=str, required=True, help="Destination file or directory"
    )
    parser.add_argument(
        "-p", "--processes", action="store_true", help="Use multiprocessing"
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=os.cpu_count(),
        help="Number of worker threads",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Logging verbosity level"
    )
    parser.add_argument(
        "--sample_size",
        type=int,
        default=SAMPLE_SIZE,
        help="Sample size for encoding detection",
    )
    parser.add_argument(
        "--create_output_dir",
        action="store_true",
        help="Create output directory if it does not exist",
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )

    converters = make_converters(
        src=args.src,
        dst=args.dst,
        sample_size=args.sample_size,
        create_output_dir=args.create_output_dir,
    )

    batch_processing(converters, use_processes=args.processes, max_workers=args.workers)
