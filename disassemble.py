#!/usr/bin/env python3
"""Export instructions from Windows executables using Ghidra's headless analyzer."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
GHIDRA_SCRIPT_DIR = SCRIPT_DIR / "ghidra_scripts"
GHIDRA_HOME = Path(r"C:\Users\theda\Downloads\ghidra_12.1.4_PUBLIC")
DEFAULT_INPUT_DIR = SCRIPT_DIR / "ToDisassemble"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "Disassembled"


def find_analyze_headless(ghidra_home: Path | None, explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        executable = explicit_path.expanduser().resolve()
        if executable.is_file():
            return executable
        raise FileNotFoundError(f"Headless analyzer not found: {executable}")

    if ghidra_home is not None:
        home = ghidra_home.expanduser().resolve()
        candidates = [
            home / "support" / "analyzeHeadless.bat",
            home / "support" / "analyzeHeadless",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise FileNotFoundError(
            f"Could not find support/analyzeHeadless under Ghidra home: {home}"
        )

    for command in ("analyzeHeadless.bat", "analyzeHeadless"):
        found = shutil.which(command)
        if found:
            return Path(found).resolve()

    raise FileNotFoundError(
        "Ghidra headless analyzer was not found. Set GHIDRA_HOME, add "
        "analyzeHeadless to PATH, or pass --analyze-headless."
    )


def disassemble(analyzer: Path, executable: Path, output_txt: Path) -> None:
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ghidra-headless-") as project_dir:
        command = [
            str(analyzer),
            project_dir,
            "DisassemblyProject",
            "-import",
            str(executable),
            "-scriptPath",
            str(GHIDRA_SCRIPT_DIR),
            "-postScript",
            "ExportOpcodes.java",
            str(output_txt.resolve()),
        ]
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            raise RuntimeError(
                f"Ghidra failed for {executable} (exit code {result.returncode})."
            )
        if not output_txt.is_file():
            raise RuntimeError(
            f"Ghidra completed but did not create the expected output: {output_txt}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Disassemble EXE files with Ghidra and export instructions to text files."
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=DEFAULT_INPUT_DIR,
        help="An .exe file or a directory containing .exe files (searched recursively).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Text file for a single EXE, or output directory for a directory input. "
            f"Defaults to {DEFAULT_OUTPUT_DIR}."
        ),
    )
    parser.add_argument(
        "--ghidra-home",
        type=Path,
        default=Path(os.environ.get("GHIDRA_HOME", str(GHIDRA_HOME))),
        help=(
            "Ghidra installation directory. Defaults to the GHIDRA_HOME variable in this script; "
            "the GHIDRA_HOME environment variable can also override it."
        ),
    )
    parser.add_argument(
        "--analyze-headless",
        type=Path,
        help="Path to analyzeHeadless/analyzeHeadless.bat; overrides --ghidra-home.",
    )
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if source.is_file():
        executables = [source]
        output_root = None
    elif source.is_dir():
        executables = sorted(
            path for path in source.rglob("*") if path.is_file() and path.suffix.lower() == ".exe"
        )
        output_root = args.output.expanduser().resolve() if args.output else DEFAULT_OUTPUT_DIR
        if not executables:
            print(f"No .exe files found in {source}", file=sys.stderr)
            return 1
    else:
        print(f"Input does not exist: {source}", file=sys.stderr)
        return 2

    try:
        analyzer = find_analyze_headless(args.ghidra_home, args.analyze_headless)
        for executable in executables:
            if output_root is None:
                output_txt = (
                    args.output.expanduser().resolve()
                    if args.output
                    else DEFAULT_OUTPUT_DIR / f"{executable.stem}.txt"
                )
            else:
                relative_path = executable.relative_to(source).with_suffix(".txt")
                output_txt = output_root / relative_path

            print(f"Disassembling {executable} -> {output_txt}")
            disassemble(analyzer, executable, output_txt)
    except (FileNotFoundError, RuntimeError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Finished: {len(executables)} file(s) disassembled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
