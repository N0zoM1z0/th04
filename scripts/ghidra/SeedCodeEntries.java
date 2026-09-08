// Seed the DOS COM entry before headless auto-analysis.
//@author N0zoM1z0
//@category TH04

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;

public class SeedCodeEntries extends GhidraScript
{
    @Override
    protected void run() throws Exception
    {
        String[] args = getScriptArgs();
        if (args.length < 1)
            throw new IllegalArgumentException(
                "usage: SeedCodeEntries.java ENTRY_ADDRESS [CODE_ADDRESS...]");
        for (int index = 0; index < args.length; index++)
        {
            Address entry = toAddr(args[index]);
            if (!currentProgram.getMemory().contains(entry))
                throw new IllegalStateException(
                    "code seed is outside imported memory: " + entry);
            if (index == 0)
                currentProgram.getSymbolTable().addExternalEntryPoint(entry);
            disassemble(entry);
            if (getFunctionAt(entry) == null)
                createFunction(entry, index == 0 ? "entry" : null);
            println("Seeded code entry at " + entry);
        }
    }
}
