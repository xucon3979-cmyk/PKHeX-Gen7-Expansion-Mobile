using PKHeX.Core;

// Programmatic save verification. Not a substitute for real ROM-hack save testing.
if (Gen7Expansion.MaxSpeciesID != 1025 ||
    Gen7Expansion.MaxMoveID != 920 ||
    Gen7Expansion.MaxAbilityID != 316 ||
    Gen7Expansion.MaxItemID != 1023)
    throw new InvalidOperationException("Unexpected Aqua-0 v1.0 Gen7 Expansion maximum IDs.");

var blank = BlankSaveFile.Get(GameVersion.US, "EXPANSION_TEST");
if (blank is not SAV7USUM sav)
    throw new InvalidOperationException("Could not initialize a USUM save.");
if (sav.MaxSpeciesID != 1025 || sav.MaxMoveID != 920 ||
    sav.MaxAbilityID != 316 || sav.MaxItemID != 1023)
    throw new InvalidOperationException("Gen7 Expansion limits are not active.");

var greninja = new PK7
{
    Species = 658,
    Form = 3, // Mega Greninja in Expansion
    Ability = 311,
    HeldItem = 515,
    Move1 = 920,
};
sav.SetBoxSlotAtIndex(greninja, 0, 0);
var output = sav.Write().ToArray();
if (output.Length < 200_000)
    throw new InvalidOperationException("USUM save output unexpectedly short.");

var parsed = SaveUtil.GetSaveFile(output);
if (parsed is not SAV7USUM readable)
    throw new InvalidOperationException("USUM synthetic save could not be reparsed.");
if (!readable.ChecksumsValid)
    throw new InvalidOperationException("USUM synthetic export checksum invalid: " + readable.ChecksumInfo);

var restored = readable.GetBoxSlotAtIndex(0, 0);
if (restored.Species != 658 || restored.Form != 3 ||
    restored.Ability != 311 || restored.HeldItem != 515 ||
    restored.Move1 != 920)
{
    throw new InvalidOperationException(
        $"Gen7 Expansion box data lost after save round-trip: " +
        $"{restored.Species} form {restored.Form}, ability {restored.Ability}, " +
        $"item {restored.HeldItem}, move {restored.Move1}");
}

Console.WriteLine("PASS: Aqua-0 v1.0 Expansion max IDs.");
Console.WriteLine("PASS: Synthetic USUM save roundtrip and checksums.");
Console.WriteLine("PASS: Mega Greninja form, custom ability, move, and item persisted.");
