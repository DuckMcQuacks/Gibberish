# Ghidra headless disassembler

This utility imports Windows `.exe` files into Ghidra, runs Ghidra's normal analysis, and exports each decoded instruction to a tab-separated `.txt` file. Each line includes the address, instruction bytes, mnemonic, and operands; it does not attempt to turn an executable's raw bytes into instructions without analysis.

## Requirements

- Ghidra installed, including its `support/analyzeHeadless` script.
- Java version supported by your installed Ghidra release.
- Python 3.10 or later.

The script's `GHIDRA_HOME` variable is set to `C:\Users\theda\Downloads\ghidra_12.1.4_PUBLIC`. Change that variable in `disassemble.py` if Ghidra is installed elsewhere. You can also override it with the `GHIDRA_HOME` environment variable or pass the analyzer path explicitly with `--analyze-headless`.

## Usage

With no arguments, the script reads all `.exe` files under `ToDisassemble` (including subdirectories) and writes `.txt` files into `Disassembled`, preserving any subdirectory structure:

```powershell
python .\disassemble.py
```

You can also pass one executable or another input directory explicitly. For one executable, the text file is written to `Disassembled/<name>.txt` by default:

To choose an exact text output path:

```powershell
python .\disassemble.py .\ToDisassemble\sample.exe --output .\Disassembled\sample.txt
```

To process all `.exe` files under another directory, preserving subdirectories in the output:

```powershell
python .\disassemble.py .\ToDisassemble
```

For a directory input, `--output` selects the output directory. Each Ghidra run uses a temporary project, which is removed after the text file has been exported.

## Extracting opcode bytes

`FeatureSelection.py` reads Ghidra disassembly text files and takes the first byte from each instruction's `BYTES` column. It writes the bytes in instruction order, separated by semicolons, to a matching `.txt` file under `OpcodeBytes`:

```powershell
python .\FeatureSelection.py
```

By default, it processes `.txt` files recursively from `Disassembled` and preserves subdirectories in `OpcodeBytes`. You can pass a different input directory and output directory:

```powershell
python .\FeatureSelection.py .\Disassembled --output .\OpcodeBytes
```

For one input file, `--output` can specify the exact output file path:

```powershell
python .\FeatureSelection.py .\Disassembled\sample.txt --output .\OpcodeBytes\sample.txt
```
