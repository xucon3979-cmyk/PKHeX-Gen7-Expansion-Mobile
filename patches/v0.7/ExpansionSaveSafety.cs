using PKHeX.Core;
using System;
using System.IO;
using System.Linq;
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

    public static void VerifyExport(SaveFile original, byte[] bytes)
    {
        if (bytes.Length < 32)
            throw new InvalidDataException("Export is empty.");
        if (original is not SAV7USUM)
            return; // Original app validation applies to other generations.
        // Normal imported saves should be recognized automatically. Some valid saves
        // (and synthetic templates) lack the metadata needed for auto-detection.
        // If necessary, explicitly parse the known Gen7 save type and validate CRCs.
        var roundTrip = SaveUtil.GetSaveFile(bytes) as SAV7USUM ??
                        new SAV7USUM(bytes);
        if (!roundTrip.ChecksumsValid)
            throw new InvalidDataException("Export checksum error: " + roundTrip.ChecksumInfo);
        if (roundTrip.Data.Length != original.Data.Length)
            throw new InvalidDataException("Export length mismatch.");
    }
}
