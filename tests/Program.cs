using System.Security.Cryptography;
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
var bag = sav.Inventory;
var charmPocket = bag.GetPouch(InventoryType.KeyItems);
if (charmPocket.GiveItem(bag, 632, 1) != 1)
    throw new InvalidOperationException("Failed to add Shiny Charm as exactly one Key Item.");
bag.CopyTo(sav);
var output = sav.Write().ToArray();
if (output.Length < 200_000)
    throw new InvalidOperationException("USUM save output unexpectedly short.");

// Blank template saves may not carry the metadata required by SaveUtil auto-detection.
// A real imported main must pass SaveUtil detection; this synthetic test reopens as SAV7USUM.
// Gen7 reads intentionally zero the signature in the supplied backing buffer.
// Parse ONLY a dedicated clone, never the signed bytes we will export.
if (output.Length != SaveUtil.SIZE_G7USUM)
    throw new InvalidOperationException("Incorrect USUM raw main file size.");
const int signatureOffset = 0x6C100;
const int signatureLength = MemeCrypto.SaveFileSignatureLength;
static void CheckGen7SignedBytes(byte[] data)
{
    if (!MemeCrypto.VerifyMemeData(
            data.AsSpan(signatureOffset, signatureLength),
            out var decoded, MemeKeyIndex.PokedexAndSaveFile))
        throw new InvalidOperationException("The USUM MemeCrypto signature is invalid.");
    var checksumTableHash = SHA256.HashData(data.AsSpan(data.Length - 0x200, 0x150));
    if (decoded.Length < checksumTableHash.Length ||
        !decoded.AsSpan(0, checksumTableHash.Length).SequenceEqual(checksumTableHash))
        throw new InvalidOperationException("The signed SHA256 checksum-table hash differs.");
}
CheckGen7SignedBytes(output);
var expectedSigned = (byte[])output.Clone();
var inspectionCopy = (byte[])output.Clone();
var parsed = SaveUtil.GetSaveFile(inspectionCopy);
var readable = parsed as SAV7USUM ?? new SAV7USUM(inspectionCopy);
if (!output.AsSpan().SequenceEqual(expectedSigned))
    throw new InvalidOperationException("Export bytes were accidentally mutated by parsing.");
CheckGen7SignedBytes(output);
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
if (!readable.Inventory.GetPouch(InventoryType.KeyItems).HasItem(632))
    throw new InvalidOperationException("Shiny Charm not persisted in Key Items.");
Console.WriteLine("PASS: Shiny Charm ID 632, quantity 1 in the Key Items pocket.");
Console.WriteLine("PASS: Gen7 RSA signature+SHA256 table intact before AND after inspection of isolated copy.");
