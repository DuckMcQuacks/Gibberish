#!/usr/bin/env python3
"""Extract the first instruction byte from Ghidra disassembly text files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = SCRIPT_DIR / "Disassembled"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "OpcodeBytes"
SEPARATOR_VALUE = ' '


def extract_first_opcode_bytes(input_txt: Path) -> str:
	opcode_bytes = []
	for line in input_txt.read_text(encoding="utf-8").splitlines():
		columns = line.split("\t")
		if len(columns) < 3:
			continue

		instruction_bytes = columns[1].strip().split()
		if instruction_bytes and len(instruction_bytes[0]) == 2:
			try:
				int(instruction_bytes[0], 16)
			except ValueError:
				continue
			opcode_bytes.append(instruction_bytes[0].upper())

	return SEPARATOR_VALUE.join(opcode_bytes)


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Extract the first byte of each instruction from disassembly text files."
	)
	parser.add_argument(
		"--input",
		type=Path,
		nargs="?",
		default=DEFAULT_INPUT_DIR,
		help="A .txt disassembly file or a directory of .txt files (searched recursively).",
	)
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		help=(
			"Output .txt path for a single input file, or output directory for a directory input. "
			f"Defaults to {DEFAULT_OUTPUT_DIR}."
		),
	)
	args = parser.parse_args()

	source = args.input.expanduser().resolve()
	if source.is_file():
		input_files = [source]
		output_root = None
	elif source.is_dir():
		input_files = sorted(
			path
			for path in source.rglob("*")
			if path.is_file() and path.suffix.lower() == ".txt"
		)
		output_root = args.output.expanduser().resolve() if args.output else DEFAULT_OUTPUT_DIR
		if not input_files:
			print(f"No .txt files found in {source}", file=sys.stderr)
			return 1
	else:
		print(f"Input does not exist: {source}", file=sys.stderr)
		return 2

	try:
		for input_txt in input_files:
			if output_root is None:
				output_txt = (
					args.output.expanduser().resolve()
					if args.output
					else DEFAULT_OUTPUT_DIR / input_txt.name
				)
			else:
				output_txt = output_root / input_txt.relative_to(source)

			output_txt.parent.mkdir(parents=True, exist_ok=True)
			output_txt.write_text(
				extract_first_opcode_bytes(input_txt) + "\n", encoding="utf-8"
			)
			print(f"Extracted opcode bytes: {input_txt} -> {output_txt}")
	except OSError as error:
		print(f"Error: {error}", file=sys.stderr)
		return 1

	print(f"Finished: {len(input_files)} file(s) processed.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
