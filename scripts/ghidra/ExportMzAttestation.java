// Export a private, independently checkable view of one loaded TH04 MZ target.
//@author N0zoM1z0
//@category TH04

import ghidra.app.util.headless.HeadlessScript;
import ghidra.program.database.mem.FileBytes;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.SegmentedAddress;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.mem.MemoryBlockSourceInfo;
import ghidra.program.model.reloc.Relocation;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;

public class ExportMzAttestation extends HeadlessScript
{
    private record SourceRange(
        String blockName,
        boolean initialized,
        boolean loaded,
        long fileOffset,
        long length,
        Address minAddress,
        Address maxAddress,
        String description)
    {
    }

    private static String csv(String value)
    {
        if (value == null)
            return "";
        if (value.contains(",") || value.contains("\"") || value.contains("\n"))
            return "\"" + value.replace("\"", "\"\"") + "\"";
        return value;
    }

    private static String hex(byte[] bytes)
    {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes)
            result.append(String.format("%02x", Byte.toUnsignedInt(value)));
        return result.toString();
    }

    private static String sha256(byte[] bytes) throws Exception
    {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String values(long[] values)
    {
        if (values == null)
            return "";
        StringBuilder result = new StringBuilder();
        for (int index = 0; index < values.length; index++)
        {
            if (index != 0)
                result.append(';');
            result.append(Long.toUnsignedString(values[index]));
        }
        return result.toString();
    }

    private static int unsigned(String value)
    {
        return Integer.parseUnsignedInt(value.startsWith("0x") ? value.substring(2) : value,
            value.startsWith("0x") ? 16 : 10);
    }

    private List<SourceRange> sourceRanges(FileBytes expectedFileBytes) throws Exception
    {
        List<SourceRange> ranges = new ArrayList<>();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks())
        {
            for (MemoryBlockSourceInfo source : block.getSourceInfos())
            {
                if (source.getFileBytes().isEmpty() ||
                    !source.getFileBytes().get().equals(expectedFileBytes))
                    continue;
                if (source.getFileBytesOffset() < 0)
                    throw new IllegalStateException(
                        "complex file-byte mapping is unsupported: " + block.getName());
                ranges.add(new SourceRange(
                    block.getName(), block.isInitialized(), block.isLoaded(),
                    source.getFileBytesOffset(), source.getLength(),
                    source.getMinAddress(), source.getMaxAddress(), source.getDescription()));
            }
        }
        ranges.sort(Comparator.comparingLong(SourceRange::fileOffset)
            .thenComparing(item -> item.minAddress().toString()));
        return ranges;
    }

    private byte[] snapshot(
        List<SourceRange> ranges, long start, int length, boolean requireLoaded,
        String requiredAddressSpace) throws Exception
    {
        Address[] addresses = new Address[length];
        for (SourceRange range : ranges)
        {
            if (!range.initialized())
                continue;
            long overlapStart = Math.max(start, range.fileOffset());
            long overlapEnd = Math.min(start + length, range.fileOffset() + range.length());
            if (overlapStart >= overlapEnd)
                continue;
            if (range.loaded() != requireLoaded)
                continue;
            if (!range.minAddress().getAddressSpace().getName().equals(requiredAddressSpace))
                continue;
            for (long fileOffset = overlapStart; fileOffset < overlapEnd; fileOffset++)
            {
                int outputIndex = Math.toIntExact(fileOffset - start);
                if (addresses[outputIndex] != null)
                    throw new IllegalStateException(
                        "file offset has multiple eligible mappings: 0x" +
                        Long.toHexString(fileOffset));
                addresses[outputIndex] =
                    range.minAddress().add(fileOffset - range.fileOffset());
            }
        }
        Memory memory = currentProgram.getMemory();
        byte[] result = new byte[length];
        for (int index = 0; index < length; index++)
        {
            if (addresses[index] == null)
                throw new IllegalStateException(
                    "file offset is not mapped exactly once: 0x" + Long.toHexString(start + index));
            result[index] = memory.getByte(addresses[index]);
        }
        return result;
    }

    private void writeBlocks(Path path, List<SourceRange> ranges) throws Exception
    {
        try (BufferedWriter output = Files.newBufferedWriter(path, StandardCharsets.UTF_8))
        {
            output.write(
                "block,initialized,loaded,file_offset,length,min_address,max_address," +
                "address_space,description\n");
            for (SourceRange range : ranges)
            {
                output.write(csv(range.blockName()) + "," + range.initialized() + "," +
                    range.loaded() + "," + range.fileOffset() + "," + range.length() + "," +
                    range.minAddress() + "," + range.maxAddress() + "," +
                    csv(range.minAddress().getAddressSpace().getName()) + "," +
                    csv(range.description()) + "\n");
            }
        }
    }

    private int writeRelocations(Path path) throws Exception
    {
        int count = 0;
        Memory memory = currentProgram.getMemory();
        try (BufferedWriter output = Files.newBufferedWriter(path, StandardCharsets.UTF_8))
        {
            output.write(
                "index,address,address_segment,address_offset,status,type,values," +
                "original_bytes,memory_bytes\n");
            Iterator<Relocation> iterator = currentProgram.getRelocationTable().getRelocations();
            while (iterator.hasNext())
            {
                Relocation relocation = iterator.next();
                Address address = relocation.getAddress();
                if (!(address instanceof SegmentedAddress))
                    throw new IllegalStateException("MZ relocation is not segmented: " + address);
                SegmentedAddress segmented = (SegmentedAddress) address;
                byte[] memoryBytes = new byte[2];
                if (memory.getBytes(address, memoryBytes) != memoryBytes.length)
                    throw new IOException("unable to read relocation memory at " + address);
                output.write(count + "," + address + "," + segmented.getSegment() + "," +
                    segmented.getSegmentOffset() + "," + relocation.getStatus() + "," +
                    relocation.getType() + "," + csv(values(relocation.getValues())) + "," +
                    hex(relocation.getBytes() == null ? new byte[0] : relocation.getBytes()) +
                    "," + hex(memoryBytes) + "\n");
                count++;
            }
        }
        return count;
    }

    private int writeEntryPoints(Path path) throws Exception
    {
        int count = 0;
        try (BufferedWriter output = Files.newBufferedWriter(path, StandardCharsets.UTF_8))
        {
            AddressIterator iterator =
                currentProgram.getSymbolTable().getExternalEntryPointIterator();
            while (iterator.hasNext())
            {
                output.write(iterator.next().toString());
                output.write("\n");
                count++;
            }
        }
        return count;
    }

    @Override
    protected void run() throws Exception
    {
        String[] args = getScriptArgs();
        if (args.length != 5)
            throw new IllegalArgumentException(
                "usage: ExportMzAttestation.java OUTPUT_DIR RAW_SIZE HEADER_SIZE DECLARED_SIZE NONCE");
        Path output = Path.of(args[0]).toAbsolutePath();
        int rawSize = unsigned(args[1]);
        int headerSize = unsigned(args[2]);
        int declaredSize = unsigned(args[3]);
        String exportNonce = args[4];
        if (!exportNonce.matches("[0-9a-f]{32}"))
            throw new IllegalArgumentException("export nonce must be 32 lowercase hex digits");
        if (rawSize <= 0 || headerSize < 28 || declaredSize < headerSize ||
            declaredSize > rawSize)
            throw new IllegalArgumentException("invalid MZ extents supplied by wrapper");
        Files.createDirectories(output);

        List<FileBytes> allFileBytes = currentProgram.getMemory().getAllFileBytes();
        if (allFileBytes.size() != 1)
            throw new IllegalStateException(
                "expected exactly one imported FileBytes record, got " + allFileBytes.size());
        FileBytes fileBytes = allFileBytes.get(0);
        if (fileBytes.getSize() != rawSize)
            throw new IllegalStateException(
                "FileBytes size mismatch: " + fileBytes.getSize() + " != " + rawSize);

        byte[] original = new byte[rawSize];
        byte[] modified = new byte[rawSize];
        if (fileBytes.getOriginalBytes(0, original) != rawSize ||
            fileBytes.getModifiedBytes(0, modified) != rawSize)
            throw new IOException("unable to read the complete FileBytes record");
        List<SourceRange> ranges = sourceRanges(fileBytes);
        writeBlocks(output.resolve("blocks.csv"), ranges);
        String defaultSpace = currentProgram.getAddressFactory().getDefaultAddressSpace().getName();
        byte[] headerMemory = snapshot(ranges, 0, headerSize, false, "HEADER");
        byte[] loadMemory = snapshot(
            ranges, headerSize, declaredSize - headerSize, true, defaultSpace);

        Files.write(output.resolve("filebytes-original.bin"), original);
        Files.write(output.resolve("filebytes-modified.bin"), modified);
        Files.write(output.resolve("header-memory.bin"), headerMemory);
        Files.write(output.resolve("load-memory.bin"), loadMemory);
        int relocationCount = writeRelocations(output.resolve("relocations.csv"));
        int entryPointCount = writeEntryPoints(output.resolve("entrypoints.txt"));

        Listing listing = currentProgram.getListing();
        try (BufferedWriter properties = Files.newBufferedWriter(
            output.resolve("program.properties"), StandardCharsets.UTF_8))
        {
            properties.write("schema_version=1\n");
            properties.write("export_nonce=" + exportNonce + "\n");
            properties.write("program_name=" + currentProgram.getName() + "\n");
            properties.write("executable_path=" + currentProgram.getExecutablePath() + "\n");
            properties.write("executable_sha256=" + currentProgram.getExecutableSHA256() + "\n");
            properties.write("executable_format=" + currentProgram.getExecutableFormat() + "\n");
            properties.write("language_id=" + currentProgram.getLanguageID() + "\n");
            properties.write(
                "compiler_spec_id=" + currentProgram.getCompilerSpec().getCompilerSpecID() + "\n");
            properties.write("image_base=" + currentProgram.getImageBase() + "\n");
            properties.write("default_address_space=" + defaultSpace + "\n");
            properties.write("filebytes_filename=" + fileBytes.getFilename() + "\n");
            properties.write("filebytes_size=" + fileBytes.getSize() + "\n");
            properties.write("filebytes_original_sha256=" + sha256(original) + "\n");
            properties.write("filebytes_modified_sha256=" + sha256(modified) + "\n");
            properties.write("header_memory_sha256=" + sha256(headerMemory) + "\n");
            properties.write("load_memory_sha256=" + sha256(loadMemory) + "\n");
            properties.write("header_size=" + headerSize + "\n");
            properties.write("declared_size=" + declaredSize + "\n");
            properties.write("load_module_size=" + loadMemory.length + "\n");
            properties.write("source_range_count=" + ranges.size() + "\n");
            properties.write("relocation_count=" + relocationCount + "\n");
            properties.write("external_entry_point_count=" + entryPointCount + "\n");
            properties.write(
                "function_count=" + currentProgram.getFunctionManager().getFunctionCount() + "\n");
            properties.write("instruction_count=" + listing.getNumInstructions() + "\n");
            properties.write("defined_data_count=" + listing.getNumDefinedData() + "\n");
            properties.write(
                "headless_analysis_timed_out=" + analysisTimeoutOccurred() + "\n");
        }
        println("Exported TH04 MZ database attestation to " + output);
        println("SHA-256=" + currentProgram.getExecutableSHA256() +
            " relocations=" + relocationCount + " entry-points=" + entryPointCount);
    }
}
