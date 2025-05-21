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
    if dst_path.exists() and dst_path.is_dir():
        out = dst_path / src.name
    elif create_output_dir and not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)
        out = dst_path / src.name
    else:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        out = dst_path
    if out.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Output must be file with {ALLOWED_EXTENSIONS} extension: {out}"
        )
    return out


class UTF8Converter:
    def __init__(
        self,
        input_file: Union[Path, str],
        output_file: Union[Path, str],
        sample_size: int = SAMPLE_SIZE,
        create_output_dir: bool = False,
    ):
        self.sample_size = sample_size
        self.input_file = validate_input_file(input_file)
        self.output_file = prepare_output_path(
            src=self.input_file, dst=output_file, create_output_dir=create_output_dir
        )

    @property
    def encoding_confidence(self) -> tuple[str | None, float]:
        """
        Detect the encoding of the input file.
        :return: encoding and confidence
        """
        if self.input_file.stat().st_size <= self.sample_size:
            data = self.input_file.read_bytes()
        else:
            with self.input_file.open("rb") as f:
                data = f.read(self.sample_size)

        detected = chardet.detect(data)
        return detected.get("encoding"), detected.get("confidence", 0.0)

    def convert(self):
        """
        Convert the input file to UTF-8 encoding.
        :return:
        """
        enc, confidence = self.encoding_confidence

        if not enc:
            raise ValueError(f"No encoding detected: {self.input_file}")
        text = self.input_file.read_text(encoding=enc)
        self.output_file.write_text(text, encoding="utf-8")

        logger.debug(
            f"File converted successfully "
            f"(encoding: {enc} confidence: {confidence:.2f}): "
            f"{self.input_file} -> {self.output_file}"
        )


def batch_processing(
    converters: list[UTF8Converter],
    use_processes: bool = False,
    max_workers: int = None,
) -> None:
    """
    Process files in batches using threads or processes.
    :param converters: list of UTF8Converter instances
    :param use_processes: flag to use multiprocessing
    :param max_workers: number of worker threads or processes
    :return:
    """
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
    """
    Create a list of UTF8Converter instances based on the source and destination paths.
    :param src: source file or directory
    :param dst: destination file or directory
    :param sample_size: sample size for encoding detection
    :param create_output_dir: flag to create output directory if it does not exist
    :return:
    """
    path = Path(src)
    if path.is_dir():
        return [
            UTF8Converter(
                input_file=file,
                output_file=dst,
                sample_size=sample_size,
                create_output_dir=create_output_dir,
            )
            for file in path.glob("*.txt")
        ]
    else:
        return [
            UTF8Converter(
                input_file=path,
                output_file=dst,
                sample_size=sample_size,
                create_output_dir=create_output_dir,
            )
        ]


if __name__ == "__main__":
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
        "-v", "--verbose", action="store_true", help="Enable debug logging"
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
    if not converters:
        logger.warning("No .txt files found to convert.")
    else:
        batch_processing(
            converters, use_processes=args.processes, max_workers=args.workers
        )
