from pathlib import Path
from typing import Union

import chardet

from cli import logger
from converter.constants import SAMPLE_SIZE
from converter.utils import validate_input_file, prepare_output_path


class UTF8Converter:
    def __init__(
        self,
        input_file: Union[Path, str],
        output_file: Union[Path, str],
        sample_size: int = SAMPLE_SIZE,
        create_output_dir: bool = False,
        encoding: str = None,
    ):
        self.sample_size = sample_size
        self.encoding = encoding
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
        if self.encoding:
            return self.encoding, 1.0
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
