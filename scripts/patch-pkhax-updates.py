#!/usr/bin/env python3
"""Patch the pinned santacrab2/PKHeXMAUI source for Gen7 Expansion PKHaX UI.

This script is run at build time and fails fast if upstream code no longer
matches the expected version. The original source is not modified upstream.
"""
import argparse
from pathlib import Path

def replace_once(source: str, old: str, new: str, context: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{context}: expected one matching source span, found {count}")
    return source.replace(old, new, 1)

def apply(path: Path, patch):
    original = path.read_text(encoding="utf-8-sig")
    changed = patch(original)
    if changed == original:
        raise RuntimeError(f"Patch made no changes: {path}")
    path.write_text(changed, encoding="utf-8")
    print("Patched:", path)

def patch_settings_xaml(src: str) -> str:
    old = '<Picker x:Name="SaveVersionPicker" Title="Current Save" SelectedIndexChanged="applynewsave"></Picker>'
    new = old + """
        <!-- Expansion fork: persistent toggle, kept outside original reflection-based property grid. -->
        <VerticalStackLayout Padding="14,10" Spacing="8">
            <Label Text="PKHaX Mode" FontSize="20" FontAttributes="Bold" />
            <Grid ColumnDefinitions="*,Auto" ColumnSpacing="12">
                <Label Grid.Column="0"
                       Text="PKHaX: unlock Pokémon, move, item and ability choices"
                       VerticalOptions="Center" LineBreakMode="WordWrap" />
                <Switch x:Name="PKHaXSwitch" Grid.Column="1"
                        VerticalOptions="Center" Toggled="OnPKHaXToggled" />
            </Grid>
            <Label FontSize="12" TextColor="Orange"
                   Text="OFF: regular filtered editing. ON: allow edits that may be illegal or unsupported in game. Always back up your save." />
            <Label FontSize="12"
                   Text="Original PKHeX.MAUI update prompts are disabled for this Gen7 Expansion fork." />
        </VerticalStackLayout>"""
    return replace_once(src,old,new,"Settings XAML")

def patch_settings_cs(src: str) -> str:
    src = replace_once(src,
                       "public partial class PKHeXSettings : ContentPage\n{\n",
                       "public partial class PKHeXSettings : ContentPage\n{\n    private bool _initializingPKHaX = true;\n",
                       "Settings class")
    src = replace_once(src,
                       "InitializeComponent();",
                       "InitializeComponent();\n        _initializingPKHaX = true;\n        PKHaXSwitch.IsToggled = ExpansionSettings.PKHaXMode;\n        _initializingPKHaX = false;",
                       "Initialize PKHaX switch")
    key = "    private void applynewsave(object sender, EventArgs e)\n"
    on_changed = """    private async void OnPKHaXToggled(object sender, ToggledEventArgs e)
    {
        if (_initializingPKHaX || ExpansionSettings.PKHaXMode == e.Value)
            return;

        ExpansionSettings.PKHaXMode = e.Value;
        // Invalidate filtered data for Moves and other tabs, not just PK Editor.
        MainPage.RefreshPKHaXDataSources();
        await DisplayAlertAsync("PKHaX Mode",
            e.Value
                ? "PKHaX enabled. Additional Pokémon, moves, items and abilities are now selectable. Legality warnings remain enabled. Use a copy of your save."
                : "PKHaX disabled. Legal/normal filtered choices will return when you open the PK Editor.",
            "OK");
    }

"""
    return replace_once(src,key,on_changed+key,"Settings change handler")

def patch_main_cs(src: str) -> str:
    src=replace_once(src,
        "public partial class MainPage : ContentPage\n{\n",
        "public partial class MainPage : ContentPage\n{\n    private bool _appliedPKHaXMode;\n",
        "Main class")
    src=replace_once(src,
        "        GameInfo.FilteredSources = new FilteredGameDataSource(sav, GameInfo.Sources);\n        datasourcefiltered = GameInfo.FilteredSources;",
        "        RefreshPKHaXDataSources();",
        "Main constructor source")
    src=replace_once(src,
        "        InitializeComponent();\n        var OpenTrash",
        "        InitializeComponent();\n        _appliedPKHaXMode = ExpansionSettings.PKHaXMode;\n        var OpenTrash",
        "Main PKHaX mode initialization")
    src=replace_once(src,
        "        CheckForUpdate();",
        "        // Original PKHeX.MAUI update prompt intentionally disabled in this Expansion fork.",
        "Disable original update check")
    old_appear = """    protected override void OnAppearing()
    {
        if (!FirstLoad)
        {
            applymainpkinfo(pk);
            checklegality();
        }
    }
"""
    new_appear = """    /// <summary>Refresh all PKHaX-backed picker lists without changing the loaded save.</summary>
    public static void RefreshPKHaXDataSources()
    {
        GameInfo.FilteredSources = new FilteredGameDataSource(sav, GameInfo.Sources, ExpansionSettings.PKHaXMode);
        datasourcefiltered = GameInfo.FilteredSources;
    }

    protected override void OnAppearing()
    {
        if (_appliedPKHaXMode != ExpansionSettings.PKHaXMode)
        {
            SkipTextChange = true;
            RefreshPKHaXDataSources();
            specieslabel.ItemSource = (IList)datasourcefiltered.Species;
            helditempicker.ItemSource = (IList)datasourcefiltered.Items;
            _appliedPKHaXMode = ExpansionSettings.PKHaXMode;
            SkipTextChange = false;
        }
        if (!FirstLoad)
        {
            applymainpkinfo(pk);
            checklegality();
        }
    }
"""
    src=replace_once(src,old_appear,new_appear,"Main OnAppearing and refresh")

    src=replace_once(src,
        "        abilitySource = [.. GameInfo.FilteredSources.GetAbilityList(pkm.PersonalInfo)];",
        "        abilitySource = ExpansionSettings.PKHaXMode\n            ? [.. GameInfo.FilteredSources.Abilities]\n            : [.. GameInfo.FilteredSources.GetAbilityList(pkm.PersonalInfo)];",
        "PK editor ability picker")
    src=replace_once(src,
        "            abilitySource = [.. GameInfo.FilteredSources.GetAbilityList(pk.PersonalInfo)];",
        "            abilitySource = ExpansionSettings.PKHaXMode\n                ? [.. GameInfo.FilteredSources.Abilities]\n                : [.. GameInfo.FilteredSources.GetAbilityList(pk.PersonalInfo)];",
        "Species change ability picker")
    src=replace_once(src,
        "        abilitypicker.SelectedIndex = pkm.AbilityNumber == 4? 2: pkm.AbilityNumber-1;",
        """        if (ExpansionSettings.PKHaXMode)
            abilitypicker.SelectedItem = abilitySource.FirstOrDefault(z => z.Value == pkm.Ability);
        else
            abilitypicker.SelectedIndex = pkm.AbilityNumber == 4 ? 2 : pkm.AbilityNumber - 1;""",
        "Load selected unrestricted ability")
    src=replace_once(src,
        "            abilitypicker.SelectedIndex = pk.AbilityNumber == 4 ? 2 : pk.AbilityNumber-1;",
        """            if (ExpansionSettings.PKHaXMode)
                abilitypicker.SelectedItem = abilitySource.FirstOrDefault(z => z.Value == pk.Ability);
            else
                abilitypicker.SelectedIndex = pk.AbilityNumber == 4 ? 2 : pk.AbilityNumber - 1;""",
        "Select new species ability")
    src=replace_once(src,
        """        if (!SkipTextChange)
        {
            pk.SetAbilityIndex(abilitypicker.SelectedIndex);
        }""",
        """        if (!SkipTextChange && abilitypicker.SelectedIndex >= 0)
        {
            if (ExpansionSettings.PKHaXMode)
            {
                if (abilitypicker.SelectedItem is not ComboItem selected)
                    return;
                pk.Ability = selected.Value;
                if (pk.AbilityNumber is not (1 or 2 or 4))
                    pk.AbilityNumber = 1;
            }
            else
            {
                pk.SetAbilityIndex(abilitypicker.SelectedIndex);
            }
            checklegality();
        }""",
        "Apply PKHaX unrestricted ability")
    begin = src.find("    private async Task<bool> IsUpdateAvailable()")
    end = src.find("    private void applyPID(",begin)
    if begin<0 or end<0 or end<=begin:
        raise RuntimeError("Cannot locate upstream update-check methods")
    src = src[:begin] + """    // The original app's GitHub update check is irrelevant to this custom Gen7 Expansion fork.
    // Do not query original releases or show a forced update alert.
    public void CheckForUpdate() { }

""" + src[end:]
    return src

def patch_attacks(src: str) -> str:
    old="""        movlist = [];
        LegalMoveSource<ComboItem> p = new(new LegalMoveComboSource());
        p.ChangeMoveSource(datasourcefiltered.Moves);
        p.ReloadMoves(new LegalityAnalysis(pkm));
        foreach(var move in p.Display.DataSource)
        {
            var valid = p.Info.CanLearn((ushort)move.Value);
            movlist.Add(new MoveDisplay(move, valid));
        }
"""
    new="""        movlist = [];
        if (ExpansionSettings.PKHaXMode)
        {
            // PKHaX deliberately shows moves without learnset/legality filtering.
            movlist = datasourcefiltered.Moves.Select(move => new MoveDisplay(move, true)).ToList();
        }
        else
        {
            LegalMoveSource<ComboItem> p = new(new LegalMoveComboSource());
            p.ChangeMoveSource(datasourcefiltered.Moves);
            p.ReloadMoves(new LegalityAnalysis(pkm));
            foreach(var move in p.Display.DataSource)
            {
                var valid = p.Info.CanLearn((ushort)move.Value);
                movlist.Add(new MoveDisplay(move, valid));
            }
        }
"""
    return replace_once(src,old,new,"Move legality filter")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",default="PKHeXMAUI",type=Path)
    args=parser.parse_args()
    root=args.root
    exp = root/"Settings"/"ExpansionSettings.cs"
    if exp.exists():
        raise RuntimeError(f"Expected a pristine pinned PKHeX.MAUI checkout: {exp} already exists")
    exp.write_text("""namespace PKHeXMAUI;

/// <summary>Persistent source-filtering mode for the Aqua-0 Gen7 Expansion fork.</summary>
public static class ExpansionSettings
{
    private const string PreferenceKey = "PKHaXMode";
    public static bool PKHaXMode
    {
        get => Preferences.Default.Get(PreferenceKey, false);
        set => Preferences.Default.Set(PreferenceKey, value);
    }
}
""",encoding="utf-8")
    apply(root/"Settings"/"PKHeXSettings.xaml",patch_settings_xaml)
    apply(root/"Settings"/"PKHeXSettings.xaml.cs",patch_settings_cs)
    apply(root/"pktabs"/"PKTab.xaml.cs",patch_main_cs)
    apply(root/"pktabs"/"AttacksTab.xaml.cs",patch_attacks)
    print("PKHaX switch + ability/move filtering + disabled upstream update checks patched successfully.")

if __name__=="__main__":
    main()
