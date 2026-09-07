#pragma option -WX -zCSHARED -k-

/*
 * Zero-code SHARED alignment translation unit.
 *
 * snd_mmd_resident itself must compile without -WX to reproduce its two
 * distinct RETF paths.  The original following SHARED contribution still
 * starts on a word boundary.  TC4J emits a word-aligned SHARED SEGDEF for this
 * empty translation unit and no LEDATA; TLINK therefore restores that layout
 * boundary without adding authored code or embedding a target byte.
 *
 * The target byte in the resulting one-byte gap is tracked separately as
 * padding.  This source intentionally does not claim or emit that byte.
 */
