#!/usr/bin/env python3
"""Apply Expansion v0.7 additions after the existing v0.4 PKHaX patch.

Works only against pinned santacrab2 PKHeX.MAUI source. Refuses unmatched patches.
"""
from pathlib import Path
import argparse
import re
import shutil

def change(src, old, new, label):
    count=src.count(old)
    if count!=1:
        raise RuntimeError(f"{label}: expected 1 match, got {count}")
    return src.replace(old,new,1)

def edit(path, function):
    old=path.read_text(encoding="utf-8-sig")
    new=function(old)
    if old==new: raise RuntimeError(f"No edits: {path}")
    path.write_text(new,encoding="utf-8")
    print("Updated",path)

def settings_xaml(s):
    s=change(s,
      '            <Label FontSize="12" TextColor="Orange"',
      '''            <Grid ColumnDefinitions="*,Auto" ColumnSpacing="12">
                <Label Grid.Column="0" VerticalOptions="Center"
                       Text="Box legality markers (slower)" />
                <Switch x:Name="BoxLegalSwitch" Grid.Column="1"
                        Toggled="OnBoxLegalityToggled"/>
            </Grid>
            <Label FontSize="12" TextColor="Orange"''',
      "Add Box marker toggle")
    s=change(s,
      'Text="Original PKHeX.MAUI update prompts are disabled for this Gen7 Expansion fork." />',
      '''Text="Original PKHeX.MAUI update prompts are disabled for this Gen7 Expansion fork." />
            <Label Text="SAFE SAVE" FontSize="16" FontAttributes="Bold" Margin="0,10,0,0" />
            <Button Text="Restore save backup" Clicked="RestoreSaveBackupClicked"/>
            <Button Text="Export crash log" Clicked="ExportDiagnosticLogClicked"/>
            <Label Text="Backups are stored locally. Gen7 exports are checksum-checked before saving."
                   FontSize="12" TextColor="Gray"/>''',
      "Add Safe Save settings panel")
    return s

def settings_code(s):
    s=change(s,
      '        PKHaXSwitch.IsToggled = ExpansionSettings.PKHaXMode;',
      '''        PKHaXSwitch.IsToggled = ExpansionSettings.PKHaXMode;
        BoxLegalSwitch.IsToggled = ExpansionSettings.BoxLegalityIndicators;''',
      "Set marker toggle value")
    marker='    private void applynewsave(object sender, EventArgs e)\n'
    handlers='''    private void OnBoxLegalityToggled(object sender, ToggledEventArgs e)
    {
        ExpansionSettings.BoxLegalityIndicators = e.Value;
    }

    private async void RestoreSaveBackupClicked(object sender, EventArgs e)
    {
        try
        {
            var list = ExpansionSaveSafety.GetBackups();
            if (list.Count == 0)
            {
                await DisplayAlertAsync("Safe Save", "No backups stored on this device yet.", "OK");
                return;
            }
            var labels = list.Select((b, i) =>
                $"{i+1}. {b.CreatedAt:yyyy-MM-dd HH:mm} - {b.Label} ({b.Bytes / 1024} KB)").ToArray();
            var selected = await DisplayActionSheetAsync("Recover Save", "Cancel", null, labels);
            var idx = System.Array.IndexOf(labels, selected);
            if (idx < 0) return;
            bool confirm = await DisplayAlertAsync("Confirm Restore",
                "Load this backup in the editor? Your source file is never overwritten.", "Restore", "Cancel");
            if (!confirm) return;
            var restore = ExpansionSaveSafety.Restore(list[idx]);
            App.Current!.Windows[0].Page = new AppShell(restore);
            await DisplayAlertAsync("Recovered", "Backup loaded. Use Export Save to create a restored main file.", "OK");
        }
        catch (System.Exception error)
        {
            ExpansionDiagnostics.Record(error, "Backup Restore");
            await DisplayAlertAsync("Restore Failed", error.Message, "OK");
        }
    }

    private async void ExportDiagnosticLogClicked(object sender, EventArgs e)
    {
        try
        {
            var log = ExpansionDiagnostics.GetLog();
            if (log is null)
            {
                await DisplayAlertAsync("Log", "No crash or error log available.", "OK");
                return;
            }
            await using var stream = new System.IO.MemoryStream(System.IO.File.ReadAllBytes(log));
            var result = await FileSaver.Default.SaveAsync("PKHeX-Expansion-CrashLog.txt", stream,
                System.Threading.CancellationToken.None);
            if (!result.IsSuccessful)
                throw result.Exception ?? new System.InvalidOperationException("Unable to export crash log");
            await DisplayAlertAsync("Log", "The crash log has been exported.", "OK");
        }
        catch (System.Exception error)
        {
            await DisplayAlertAsync("Log Error", error.Message, "OK");
        }
    }

'''
    return change(s,marker,handlers+marker,"Add Safe Save event handlers")

def models(s):
    before='    public static bool PKHaXMode\n'
    if before not in s:raise RuntimeError("Missing v0.4 ExpansionSettings base")
    return s[:s.rfind("}")] + '''    public static bool BoxLegalityIndicators
    {
        get => Preferences.Default.Get("BoxLegalityIndicators", false);
        set => Preferences.Default.Set("BoxLegalityIndicators", value);
    }
''' + s[s.rfind("}"):]

def editor(s):
    s=change(s,
       '        var input = File.ReadAllBytes(pkfile.FullPath);',
       '''        byte[] input;
        await using (var fileStream = await pkfile.OpenReadAsync())
        {
            using var buffer = new MemoryStream();
            await fileStream.CopyToAsync(buffer);
            input = buffer.ToArray();
        }''',
       "Read Android SAF file stream")
    s=change(s,
       'FileUtil.GetSupportedFile(input,Path.GetExtension(pkfile.FullPath),sav)',
       'FileUtil.GetSupportedFile(input,Path.GetExtension(pkfile.FileName),sav)',
       "Get filename from Android file picker")
    s=change(s,
       '            case SaveFile s: opensavefile(s, pkfile.FullPath); return;',
       '''            case SaveFile s:
                try
                {
                    ExpansionSaveSafety.Backup(input, pkfile.FileName, "Imported-original");
                    opensavefile(s, pkfile.FileName);
                }
                catch (Exception ex)
                {
                    ExpansionDiagnostics.Record(ex, "Import Save");
                    await DisplayAlertAsync("Safe Save", "Cannot back up this save; import cancelled: " + ex.Message, "OK");
                }
                return;''',
       "Backup original save on open")
    s=change(s,
       '        var forms = FormConverter.GetFormList(pkm.Species, str.types, str.forms, GameInfo.GenderSymbolUnicode, pkm.Context);',
       '''        var forms = FormConverter.GetFormList(pkm.Species, str.types, str.forms, GameInfo.GenderSymbolUnicode, pkm.Context);
        if (pkm is PK7 && pkm.PersonalInfo.FormCount > forms.Length)
        {
            var list = forms.ToList();
            for (int i = list.Count; i < pkm.PersonalInfo.FormCount; i++)
                list.Add($"Expansion Form {i}");
            forms = list.ToArray();
        }''',
       "Add missing Expansion form labels")
    s=patch_editor_sprites(s, "Editor main view")
    return s

def patch_editor_sprites(s, name):
    pat=r'spriteurl = (pkm|pk)\.Species == 0\s*\?\s*"a_egg\.png"\s*:\s*\$"a_\{\1\.Species\}[^\n]*?\.png";'
    out,num=re.subn(pat,lambda m:"spriteurl = ExpansionSprites.Editor("+m.group(1)+");",s)
    if num<1: raise RuntimeError(f"{name}: cannot find sprite key builder")
    print(f"{name}: replaced {num} sprite paths")
    return out

def box(s):
    s=change(s,
       '        url = pk9.Species == 0 ? "" : $"a_{pkm.Species}{((pkm.Form > 0 && !NoFormSpriteSpecies.Contains(pkm.Species)) ? $"_{pkm.Form}" : "")}.png";',
       '        url = ExpansionSprites.Box(pkm);',
       "Switch to shiny/form-aware Box sprite")
    s=change(s,
       '        legal = !new LegalityAnalysis(pk9).Valid;',
       '        legal = ExpansionSettings.BoxLegalityIndicators && !new LegalityAnalysis(pk9).Valid;',
       "Avoid heavy Box legality work by default")
    s=change(s,
       '        species = $"{(Species)pk9.Species}";',
       '        species = pk9.Form == 0 ? $"{(Species)pk9.Species}" : $"{(Species)pk9.Species} (Form {pk9.Form})";',
       "Display custom form in Box")
    return s

def shell(s):
    return change(s,
       '''        await using var LiveStream = new MemoryStream(sav.Write(flags).ToArray());
        var result = await FileSaver.Default.SaveAsync(sav.Metadata.FileName??"", LiveStream, CancellationToken.None);''',
       '''        byte[] payload;
        try
        {
            // Write/Finalize checksums on a clone: preserve original in-memory save.
            payload = sav.Clone().Write(flags).ToArray();
            ExpansionSaveSafety.Backup(payload, sav.Metadata.FileName ?? "main", "Pre-export");
            ExpansionSaveSafety.VerifyExport(sav, payload);
        }
        catch (Exception ex)
        {
            ExpansionDiagnostics.Record(ex, "Export Save");
            await DisplayAlertAsync("Safe Save",
                "Export blocked because backup or Gen7 checksum validation failed: " + ex.Message, "OK");
            return;
        }
        await using var LiveStream = new MemoryStream(payload);
        var result = await FileSaver.Default.SaveAsync(sav.Metadata.FileName ?? "main", LiveStream, CancellationToken.None);''',
       "Back up and verify exported save")

def app(s):
    return change(s,"        InitializeComponent();",
       "        ExpansionDiagnostics.Register();\n        InitializeComponent();",
       "Register crash diagnostics")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("PKHeXMAUI"))
    args=parser.parse_args()
    root=args.root
    assets=[]
    for folder in ("SVSprites","NonShinySprites","ShinySprites","ExpansionForms"):
        base=root/"Resources"/"Images"/folder
        if base.exists(): assets.extend(f.name.lower() for f in base.glob("*.png"))
    spritefile=Path("patches/v0.7/ExpansionSprites.cs.in").read_text(encoding="utf-8")
    if "a_658.png" not in assets or "b_658.png" not in assets: raise RuntimeError("Upstream sprite packages missing")
    spritefile=change(spritefile,"        // GENERATED_SPRITE_MANIFEST",
                      ",\n".join('        "'+name+'"' for name in sorted(set(assets))),"Sprite manifest placeholder")
    (root/"Services").mkdir(exist_ok=True)
    (root/"Services"/"ExpansionSprites.cs").write_text(spritefile,encoding="utf-8")
    for name in ("ExpansionSaveSafety.cs","ExpansionDiagnostics.cs"):
        shutil.copyfile(Path("patches/v0.7")/name,root/"Services"/name)
    edit(root/"Settings/ExpansionSettings.cs",models)
    edit(root/"Settings/PKHeXSettings.xaml",settings_xaml)
    edit(root/"Settings/PKHeXSettings.xaml.cs",settings_code)
    edit(root/"pktabs/PKTab.xaml.cs",editor)
    for p in ("AttacksTab","MetTab","StatsTab","Cosmeticstab","OTTab"):
        edit(root/"pktabs"/(p+".xaml.cs"),lambda src:patch_editor_sprites(src,p))
    edit(root/"boxtab/BoxTab.xaml.cs",box)
    edit(root/"AppShell.xaml.cs",shell)
    edit(root/"App.xaml.cs",app)
    print("Expansion v0.7 patches complete:",len(assets),"offline Pokémon sprite resources.")

if __name__=="__main__":
    main()
