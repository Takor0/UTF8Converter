from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Union

from tqdm import tqdm

from converter.constants import SAMPLE_SIZE
from converter.converter import UTF8Converter
from cli import logger


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
    encoding: str = None,
) -> list[UTF8Converter]:
    """
    Create a list of UTF8Converter instances based on the source and destination paths.
    :param src: source file or directory
    :param dst: destination file or directory
    :param sample_size: sample size for encoding detection
    :param create_output_dir: flag to create output directory if it does not exist
    :param encoding: encoding to convert from
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
                encoding=encoding,
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
