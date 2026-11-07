# PKHeX Gen7 Expansion Mobile — original PKHeX.MAUI interface

This integration **uses the existing** [santacrab2/PKHeXMAUI](https://github.com/santacrab2/PKHeXMAUI) **app as the UI base**, including its existing 5-tab Pokémon editor (Main, Met, Stats, Moves, Cosmetic), flyout menu, Box/Party views, many save-editing tools, and packaged Pokémon/item sprites. It is NOT a new simplified interface and is NOT a patch to the user's compiled APK.

**Core:** [Aqua-0/PKHeX v1.0](https://github.com/Aqua-0/PKHeX/releases/tag/v1.0), `PKHeX.Core` substituted at source/build time instead of the original NuGet package.

**Original mobile source pinned at:** `a6f7cfb78e1c96155baa67660fd7ae97895e375f` (GPL-3.0).
**Expansion Core pinned:** `v1.0` (GPL-3.0).

## Building from source (GitHub Actions)
Go to **Actions > Build PKHeX.MAUI Gen7 Expansion (original UI)**, or inspect the latest push run. If both jobs pass, download the APK from **Artifacts**.

The workflow checks out the two upstream repositories, invokes `scripts/prepare-pkhex-maui.ps1`, builds a standalone Android Debug APK, and verifies its process stays alive for ~17 seconds on an Android emulator.

- The fork uses package ID `org.pkhex.gen7expansion.maui` so it can coexist with the original PKHeX.MAUI.
- The original UI already contains regular/shiny/form sprite resources; avoid online-only sprite lookup.
- The original developer explicitly warns that their unmodified app does not support ROM hacks. The Aqua-0 Core replacement is an experimental attempt to add Gen7 Expansion support. **A successful build or startup check does not prove that editing a modded save is safe.**
- Some original tools use precompiled `PKHeX.Core.AutoMod.dll` and `PKHeX.Core.Injection.dll`; they may be incompatible with the replacement Core and require source updates.
- Never replace your only save: use a backup of the decrypted `main` and test import/export before trusting it.

## Why not modify the .apk directly?
An Android .apk is an already-compiled and signed package. Changing the PKHeX.Core engine and the underlying save structures reliably requires rebuilding the available GPL source code, not just renaming/unzipping the APK.
