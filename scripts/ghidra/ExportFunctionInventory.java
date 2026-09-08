// Export a complete, read-only Ghidra function inventory for boundary review.
//@author N0zoM1z0
//@category TH04

import ghidra.app.util.headless.HeadlessScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.address.SegmentedAddress;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class ExportFunctionInventory extends HeadlessScript
{
    private static String csv(String value)
    {
        if (value == null)
            return "";
        String flat = value.replace("\r", "\\r").replace("\n", "\\n");
        if (flat.contains(",") || flat.contains("\"") || flat.contains("\n"))
            return "\"" + flat.replace("\"", "\"\"") + "\"";
        return flat;
    }

    private static String hex(long value)
    {
        return String.format("0x%x", value);
    }

    private static String segment(Address address)
    {
        return address instanceof SegmentedAddress
            ? String.format("0x%04x", ((SegmentedAddress)address).getSegment())
            : "";
    }

    private static String segmentOffset(Address address)
    {
        return address instanceof SegmentedAddress
            ? String.format("0x%04x", ((SegmentedAddress)address).getSegmentOffset())
            : "";
    }

    @Override
    protected void run() throws Exception
    {
        String[] args = getScriptArgs();
        if (args.length != 3)
            throw new IllegalArgumentException(
                "usage: ExportFunctionInventory.java OUTPUT_DIR EXPECTED_SHA256 NONCE");
        Path output = Path.of(args[0]).toAbsolutePath();
        String expectedSha256 = args[1];
        String nonce = args[2];
        if (!expectedSha256.matches("[0-9a-f]{64}"))
            throw new IllegalArgumentException("expected SHA-256 must be lowercase hex");
        if (!nonce.matches("[0-9a-f]{32}"))
            throw new IllegalArgumentException("nonce must be 32 lowercase hex digits");
        if (!expectedSha256.equals(currentProgram.getExecutableSHA256()))
            throw new IllegalStateException(
                "program executable digest differs from wrapper input: " +
                currentProgram.getExecutableSHA256());
        Files.createDirectories(output);

        int count = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(
            output.resolve("functions.csv"), StandardCharsets.UTF_8))
        {
            writer.write(
                "index,entry_linear,entry_segment,entry_offset,body_min_linear," +
                "body_max_linear,body_addresses,body_span,body_range_count,contiguous," +
                "name,signature,calling_convention,parameter_count,is_thunk,is_external," +
                "is_no_return,is_varargs,has_custom_storage,symbol_source,caller_count," +
                "callee_count\n");
            FunctionIterator functions =
                currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext())
            {
                monitor.checkCancelled();
                Function function = functions.next();
                Address entry = function.getEntryPoint();
                Address minimum = function.getBody().getMinAddress();
                Address maximum = function.getBody().getMaxAddress();
                int rangeCount = 0;
                AddressRangeIterator ranges = function.getBody().getAddressRanges(true);
                while (ranges.hasNext())
                {
                    AddressRange ignored = ranges.next();
                    rangeCount++;
                }
                long span = maximum.getOffset() - minimum.getOffset() + 1;
                int callers = function.getCallingFunctions(monitor).size();
                int callees = function.getCalledFunctions(monitor).size();
                writer.write(
                    count + "," + hex(entry.getOffset()) + "," + segment(entry) + "," +
                    segmentOffset(entry) + "," + hex(minimum.getOffset()) + "," +
                    hex(maximum.getOffset()) + "," + function.getBody().getNumAddresses() +
                    "," + span + "," + rangeCount + "," + (rangeCount == 1) + "," +
                    csv(function.getName(true)) + "," +
                    csv(function.getSignature().getPrototypeString()) + "," +
                    csv(function.getCallingConventionName()) + "," +
                    function.getParameterCount() + "," + function.isThunk() + "," +
                    function.isExternal() + "," + function.hasNoReturn() + "," +
                    function.hasVarArgs() + "," + function.hasCustomVariableStorage() + "," +
                    function.getSymbol().getSource().name() + "," + callers + "," +
                    callees + "\n");
                count++;
            }
        }

        try (BufferedWriter properties = Files.newBufferedWriter(
            output.resolve("inventory.properties"), StandardCharsets.UTF_8))
        {
            properties.write("schema_version=1\n");
            properties.write("export_nonce=" + nonce + "\n");
            properties.write("program_name=" + currentProgram.getName() + "\n");
            properties.write("executable_path=" + currentProgram.getExecutablePath() + "\n");
            properties.write(
                "executable_sha256=" + currentProgram.getExecutableSHA256() + "\n");
            properties.write(
                "executable_format=" + currentProgram.getExecutableFormat() + "\n");
            properties.write("language_id=" + currentProgram.getLanguageID() + "\n");
            properties.write(
                "compiler_spec_id=" +
                currentProgram.getCompilerSpec().getCompilerSpecID() + "\n");
            properties.write("image_base=" + currentProgram.getImageBase() + "\n");
            properties.write("function_count=" + count + "\n");
            properties.write(
                "instruction_count=" + currentProgram.getListing().getNumInstructions() + "\n");
            properties.write(
                "headless_analysis_timed_out=" + analysisTimeoutOccurred() + "\n");
        }
        println("Exported " + count + " functions to " + output);
    }
}
