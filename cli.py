import argparse
import logging
import os

from converter.constants import SAMPLE_SIZE

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    from converter.batch import make_converters, batch_processing
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
    parser.add_argument(
        "-e", "--encoding", type=str, help="Encoding to convert from", default=None
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
        encoding=args.encoding,
    )
    if not converters:
        logger.warning("No .txt files found to convert.")
    else:
        batch_processing(
            converters, use_processes=args.processes, max_workers=args.workers
        )
