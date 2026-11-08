using PKHeX.Core;
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
namespace PKHeXMAUI;

/// <summary>Private, offline backups of imported and exported save files.</summary>
public static class ExpansionSaveSafety
{
    public sealed record BackupRecord(string Path, string Label, DateTime CreatedAt, long Bytes);
    private static string Folder => System.IO.Path.Combine(FileSystem.AppDataDirectory, "ExpansionSaveBackups");

    public static string Backup(byte[] bytes, string? source, string stage)
    {
        if (bytes.Length < 32)
            throw new InvalidDataException("Save file too small for safe backup.");
        Directory.CreateDirectory(Folder);
        string cleanName = new string(System.IO.Path.GetFileName(source ?? "main")
            .Where(c => char.IsLetterOrDigit(c) || c is '.' or '_' or '-').Take(40).ToArray());
        if (string.IsNullOrEmpty(cleanName)) cleanName = "main";
        string name = DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") +
                      "_" + stage + "_" + cleanName + ".pkbackup";
        string dest = System.IO.Path.Combine(Folder, name);
        string tmp = dest + ".partial";
        try
        {
            using (var fs = new FileStream(tmp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                fs.Write(bytes);
                fs.Flush(true);
            }
            File.Move(tmp, dest);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
        // Keep 20 most recent backups in private application storage.
        foreach (var old in Directory.GetFiles(Folder, "*.pkbackup")
                                .OrderByDescending(File.GetCreationTimeUtc).Skip(20))
        {
            try { File.Delete(old); } catch (IOException) { }
        }
        return dest;
    }

    public static System.Collections.Generic.IReadOnlyList<BackupRecord> GetBackups()
    {
        if (!Directory.Exists(Folder)) return [];
        return Directory.GetFiles(Folder, "*.pkbackup")
            .OrderByDescending(File.GetCreationTimeUtc)
            .Take(20)
            .Select(p => new BackupRecord(p, System.IO.Path.GetFileName(p),
                                         File.GetCreationTime(p), new FileInfo(p).Length))
            .ToArray();
    }

    public static SaveFile Restore(BackupRecord backup)
    {
        string full = System.IO.Path.GetFullPath(backup.Path);
        string safeFolder = System.IO.Path.GetFullPath(Folder) +
                            System.IO.Path.DirectorySeparatorChar;
        if (!full.StartsWith(safeFolder, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Invalid recovery path.");
        byte[] bytes = File.ReadAllBytes(full);
        SaveFile? restored = SaveUtil.GetSaveFile(bytes);
        if (restored is null)
            throw new InvalidDataException("This backup cannot be decoded as a game save.");
        if (restored is SAV7USUM && !restored.ChecksumsValid)
            throw new InvalidDataException("Backup checksums are invalid.");
        restored.Metadata.SetExtraInfo("main");
        return restored;
    }

    /// <summary>
    /// Validates the exact 0x6CC00-byte USUM raw main file, signed using MemeCrypto.
    /// A valid CRC table is not sufficient; the game also checks the RSA signature.
    /// </summary>
    public static void VerifyGen7Signature(ReadOnlySpan<byte> input)
    {
        if (input.Length != SaveUtil.SIZE_G7USUM)
            throw new InvalidDataException(
                $"USUM raw main must contain {SaveUtil.SIZE_G7USUM} bytes; got {input.Length}.");

        const int signatureOffset = 0x6C100;
        const int signatureSize = MemeCrypto.SaveFileSignatureLength; // 0x80
        const int checksumTableLength = 0x150;
        var signature = input.Slice(signatureOffset, signatureSize);
        var crcTable = input.Slice(input.Length - 0x200, checksumTableLength);
        if (!MemeCrypto.VerifyMemeData(
                signature, out var decoded, MemeKeyIndex.PokedexAndSaveFile))
            throw new InvalidDataException(
                "The USUM save's MemeCrypto signature is missing or invalid. Export blocked.");

        var sha = SHA256.HashData(crcTable);
        if (decoded.Length < sha.Length || !decoded.AsSpan(0, sha.Length).SequenceEqual(sha))
            throw new InvalidDataException(
                "The Gen7 signature does not match the checksum table. Export blocked.");
    }

    public static void VerifyExport(SaveFile original, byte[] bytes)
    {
        if (bytes.Length < 32)
            throw new InvalidDataException("Export is empty.");
        if (original is not SAV7USUM)
            return; // Original app validation applies to other generations.
        // Normal imported saves should be recognized automatically. Some valid saves
        // (and synthetic templates) lack the metadata needed for auto-detection.
        // If necessary, explicitly parse the known Gen7 save type and validate CRCs.
        // CRITICAL: SAV7USUM(Memory<byte>) clears the Gen7 MemeCrypto signature
        // IN PLACE when opening a save. NEVER pass the export payload itself to
        // SaveUtil.GetSaveFile or new SAV7USUM. That destroyed the signature in 0.7.0.
        VerifyGen7Signature(bytes);
        var independentCopy = (byte[])bytes.Clone();
        var roundTrip = SaveUtil.GetSaveFile(independentCopy) as SAV7USUM ??
                        new SAV7USUM(independentCopy);
        if (!roundTrip.ChecksumsValid)
            throw new InvalidDataException("Export checksum error: " + roundTrip.ChecksumInfo);
        if (roundTrip.Data.Length != original.Data.Length)
            throw new InvalidDataException("Export length mismatch.");
        // Verify again that no checking step touched the signed export bytes.
        VerifyGen7Signature(bytes);
    }
}
