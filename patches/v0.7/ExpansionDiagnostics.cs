using System;
using System.IO;
using System.Threading.Tasks;

namespace PKHeXMAUI;

/// <summary>Stores managed crashes only on-device; no analytics upload or personal data collection.</summary>
public static class ExpansionDiagnostics
{
    private static bool registered;
    private static readonly object Gate = new();
    private static string Folder => Path.Combine(FileSystem.AppDataDirectory, "ExpansionDiagnostics");
    private static string Log => Path.Combine(Folder, "latest.log");

    public static void Register()
    {
        if (registered) return;
        registered = true;
        AppDomain.CurrentDomain.UnhandledException += (_, e) =>
            Record(e.ExceptionObject as Exception ?? new Exception("Unhandled runtime issue"), "Unhandled");
        TaskScheduler.UnobservedTaskException += (_, e) =>
            Record(e.Exception, "Unobserved Task");
    }

    public static void Record(Exception ex, string operation)
    {
        try
        {
            lock (Gate)
            {
                Directory.CreateDirectory(Folder);
                File.AppendAllText(Log, DateTimeOffset.UtcNow.ToString("O") +
                    " [" + operation + "]" + Environment.NewLine + ex + Environment.NewLine);
                if (new FileInfo(Log).Length > 512000)
                {
                    string all = File.ReadAllText(Log);
                    File.WriteAllText(Log, all[(all.Length / 2)..]);
                }
            }
        }
        catch { /* Crash logger must never crash the app. */ }
    }

    public static string? GetLog() => File.Exists(Log) ? Log : null;
}
