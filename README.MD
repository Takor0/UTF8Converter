# Utf8 Converter

A simple Python tool to convert text files to UTF-8 encoding, with optional batch processing, encoding auto-detection, and containerized deployment.

## Features

* Convert individual `.txt` files to UTF-8.
* Optional encoding auto-detection using `chardet`.
* Batch conversion of directories with progress tracking (`tqdm`).
* CLI interface for easy usage.
* Dockerfile for containerization.
* Makefile for common tasks (install, build, run, test).

## Project Structure

```
converter/         # Package source
  ├── __init__.py
  ├── constants.py
  ├── utils.py       # Validation & path preparation
  ├── converter.py   # UTF8Converter class
  └── batch.py       # Batch processing functions
cli.py              # Command-line entrypoint
tests/              # Unit tests
  └── test_utils.py
Makefile            # Build & run automation
Dockerfile          # Container setup
requirements.txt    # Python dependencies
README.md           # This file
```

## Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```
   
2. Setup a virtual environment (optional but recommended):

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:

   ```bash
   make dev_install
   ```

## Usage

### CLI

Convert a single file:

```bash
python cli.py -s input.txt -d output.txt
```

Batch convert a directory:

```bash
python cli.py -s ./input_dir -d ./output_dir -p -v
```

* `-s` / `--source`: source file or directory
* `-d` / `--destination`: destination file or directory
* `-p` / `--processes`: use multiprocessing
* `-v` / `--verbose`: enable debug logging
* `--create_output_dir`: create destination directory if it doesn't exist
* `--sample_size`: number of bytes to read for encoding detection (default: 1024 * 100)
* `-w` / `--workers`: number of worker or processes (default: os.cpu_count())"
* `-e` / `--encoding`: specify encoding (default: auto-detect)

### Docker

Build the image:

```bash
make docker-build
```

Run the container (mount local folders):

```bash
make docker-run
```

## Testing

Run the unit tests with:

```bash
make test
```

## License

MIT License
