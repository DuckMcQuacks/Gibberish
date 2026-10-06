// Export the instructions produced by Ghidra's analysis as a text file.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class ExportOpcodes extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("Usage: ExportOpcodes.java <output.txt>");
        }

        Path output = Paths.get(args[0]);
        Path parent = output.toAbsolutePath().getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }

        Listing listing = currentProgram.getListing();
        long count = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            writer.write("ADDRESS\tBYTES\tINSTRUCTION");
            writer.newLine();

            InstructionIterator instructions = listing.getInstructions(true);
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction instruction = instructions.next();
                writer.write(instruction.getAddress().toString());
                writer.write('\t');
                writer.write(bytesToHex(instruction.getBytes()));
                writer.write('\t');
                writer.write(instruction.getMnemonicString());
                String operands = operandText(instruction);
                if (!operands.isEmpty()) {
                    writer.write(' ');
                    writer.write(operands);
                }
                writer.newLine();
                count++;
            }
        }

        println("Exported " + count + " instructions to " + output.toAbsolutePath());
    }

    private String operandText(Instruction instruction) {
        StringBuilder operands = new StringBuilder();
        for (int index = 0; index < instruction.getNumOperands(); index++) {
            if (index > 0) {
                operands.append(", ");
            }
            operands.append(instruction.getDefaultOperandRepresentation(index));
        }
        return operands.toString();
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder hex = new StringBuilder(bytes.length * 3 - 1);
        for (int index = 0; index < bytes.length; index++) {
            if (index > 0) {
                hex.append(' ');
            }
            byte value = bytes[index];
            hex.append(String.format("%02X", value & 0xFF));
        }
        return hex.toString();
    }

}
