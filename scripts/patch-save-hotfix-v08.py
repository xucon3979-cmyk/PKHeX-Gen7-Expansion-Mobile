#!/usr/bin/env python3
"""v0.8 hotfix — preserve signed save buffers and validate Gen7 inventory edits.

Applied after the v0.4 and v0.7 patches against a pinned upstream commit.
Fails immediately if the expected source is missing rather than silently
producing an unprotected APK.
"""
from pathlib import Path
import argparse, shutil

def replace_once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise RuntimeError(f"{label}: expected 1 match; got {count}")
    return text.replace(old,new,1)

def patch_file(path, callback):
    original=path.read_text(encoding="utf-8-sig")
    result=callback(original)
    if result==original: raise RuntimeError(f"Empty patch: {path}")
    path.write_text(result,encoding="utf-8")
    print("Hotfixed:",path)

def patch_picker(s):
    # FileUtil.GetSupportedFile eventually invokes SAV7USUM(Memory<byte>).
    # That constructor clears the MemeCrypto signature of its backing byte[]
    # IN PLACE. The raw byte[] must therefore be isolated from the parser.
    s=replace_once(s,
        "var obj = FileUtil.GetSupportedFile(input,Path.GetExtension(pkfile.FileName),sav);",
        "var obj = FileUtil.GetSupportedFile((byte[])input.Clone(),Path.GetExtension(pkfile.FileName),sav);",
        "Protect exact imported bytes from parser side effects")
    return s

def patch_items(s):
    s=replace_once(s,
        "    private void GiveAll_Clicked(object? sender, EventArgs? e)\n    {",
        '''    private async void GiveAll_Clicked(object? sender, EventArgs? e)
    {
        if (SAV is SAV7USUM)
        {
            await DisplayAlertAsync("Unsafe Inventory Action",
                "Give All can add incompatible story/key items to an Expansion save. " +
                "Add Shiny Charm as one Key Item manually.", "OK");
            return;
        }''',
        "Disable USUM Give All")
    s=replace_once(s,
        "    private void ModifyAll_Clicked(object? sender, EventArgs? e)\n    {",
        '''    private async void ModifyAll_Clicked(object? sender, EventArgs? e)
    {
        if (SAV is SAV7USUM)
        {
            await DisplayAlertAsync("Unsafe Inventory Action",
                "Modify All is disabled for USUM to avoid invalid item quantities. " +
                "Edit the quantity of individual items instead.", "OK");
            return;
        }''',
        "Disable USUM Modify All")
    marker="    private async void SaveItemsClicked(object sender, EventArgs e)\n    {\n"
    validation='''    private void ValidateUSUMItems()
    {
        // InventoryItem7 stores a 10-bit ID and count, but physical Key Items
        // are capped at 1 (or 2 for the story Z-Ring). The original mobile
        // editor did not enforce either the count or pocket rules.
        for (int p = 0; p < pouches.Pouches.Count; p++)
        {
            var pocket = pouches.Pouches[p];
            var used = new System.Collections.Generic.HashSet<int>();
            int occupied = 0;
            foreach (var entry in SourceList[p])
            {
                int itemId = Array.IndexOf(itemlist, entry.name);
                if (itemId <= 0) continue;
                if (itemId > SAV.MaxItemID || itemId > 1023 || !pocket.CanContain((ushort)itemId))
                    throw new System.IO.InvalidDataException(
                        $"Item #{itemId} cannot be stored in the {pocket.Type} pocket.");
                if (!int.TryParse(entry.count, out int itemCount))
                    throw new System.IO.InvalidDataException(
                        $"Item #{itemId} has an invalid quantity.");
                int maximum = pouches.GetMaxCount(pocket.Type, itemId);
                if (itemCount < 1 || itemCount > maximum)
                    throw new System.IO.InvalidDataException(
                        $"Item #{itemId} in {pocket.Type} must have quantity 1 to {maximum}. " +
                        "Shiny Charm belongs in Key Items with quantity 1.");
                if (!used.Add(itemId))
                    throw new System.IO.InvalidDataException(
                        $"Item #{itemId} is duplicated in {pocket.Type}.");
                occupied++;
            }
            if (occupied > pocket.Items.Length)
                throw new System.IO.InvalidDataException(
                    $"Too many items in {pocket.Type}: {occupied}/{pocket.Items.Length}.");
        }
    }

    private async void SaveItemsClicked(object sender, EventArgs e)
    {
        if (SAV is SAV7USUM)
        {
            try { ValidateUSUMItems(); }
            catch (Exception ex)
            {
                await DisplayAlertAsync("Safe Save — Inventory Rejected",
                    ex.Message + "\\nNo changes have been applied to the save.", "OK");
                return;
            }
        }
'''
    s=replace_once(s,marker,validation,"Validate Gen7 items before committing inventory")
    # Guard against invalid or overly numerous slots for other games too.
    s=replace_once(s,
        "                pouch.Items[ctr] = item;",
        '''                if (ctr >= pouch.Items.Length)
                    throw new System.IO.InvalidDataException("The inventory pocket is full.");
                pouch.Items[ctr] = item;''',
        "Prevent inventory buffer overrun")
    return s

def patch_export(s):
    # Never retain an unverified candidate as a valid pre-export snapshot.
    s=replace_once(s,
      '            ExpansionSaveSafety.Backup(payload, sav.Metadata.FileName ?? "main", "Pre-export");\\n            ExpansionSaveSafety.VerifyExport(sav, payload);',
      '            ExpansionSaveSafety.VerifyExport(sav, payload);\\n            ExpansionSaveSafety.Backup(payload, sav.Metadata.FileName ?? "main", "Pre-export");',
      "Verify Gen7 export BEFORE creating candidate backup")
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path("PKHeXMAUI"))
    root=ap.parse_args().root
    dest=root/"Services/ExpansionSaveSafety.cs"
    if not dest.exists(): raise RuntimeError("v0.7 Safe Save missing")
    shutil.copyfile("patches/v0.8/ExpansionSaveSafety.cs",dest)
    patch_file(root/"pktabs/PKTab.xaml.cs",patch_picker)
    patch_file(root/"SaveEditors/Items.xaml.cs",patch_items)
    patch_file(root/"AppShell.xaml.cs",patch_export)
    print("v0.8: isolated import+export byte arrays; protected Gen7 signature and inventory.")

if __name__=="__main__":
    main()
