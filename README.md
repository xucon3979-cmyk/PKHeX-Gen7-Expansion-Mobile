# PKHeX Gen7 Expansion Mobile v0.8.0 — SAVE CORRUPTION FIX

**Tested signed APK (ZIP artifact):** https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42441363730/artifacts/13602121541

**Verified GitHub Actions run:** https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42441363730 — synthetic save signature, Shiny Charm, item and Pokémon data checks passed; APK compiled, signed and opened on Android 15 emulator.

**IMPORTANT:** Previous v0.7.0 exports can be corrupted. v0.8.0 fixes a confirmed in-place signature-clearing issue in Gen7 SaveUtil validation. The user's healthy game save was **not uploaded** to GitHub. No test on the user's live Ultra Sun Expansion save or Xiaomi 14 has been completed. Do not overwrite your last working `main`; test the candidate on a separate copy first.

**New fixes:** independent copies for import/export parsers; RSA MemeCrypto signature verification including SHA256 checksum table; safe backup created only after export verification; safer Key Items and Shiny Charm handling; disable USUM bulk Give All / Modify All. Existing PKHeX.MAUI UI, sprites and PKHaX are preserved.

[Read technical root cause and release cautions](docs/v0.8-save-corruption-hotfix.md).

**Signing caveat:** GitHub repository signing secrets are not set, so the ZIP contains an APK signed with a temporary Debug certificate. Android may require uninstalling your previous fork before installing, which deletes app-private backups. **Save your good `main` externally first.**

---

# Critical: v0.7.0 Gen7 save export corruption

**DO NOT use v0.7.0 to export Pokémon Ultra Sun/Ultra Moon saves.** A confirmed bug in the v0.7.0 verification step passed the signed output buffer directly into `SAV7USUM`, whose constructor erases the MemeCrypto signature *in place*. The exported `main` can then be rejected by the game.

A **v0.8.0 hotfix** is in development and includes a regression test for preserving the signed save, an independent RSA/checksum-table verification and safer Shiny Charm inventory constraints. Refer to [save hotfix details](docs/v0.8-save-corruption-hotfix.md). **Only install the hotfix after the build and Android smoke-test are green**.

Keep your original, game-working `main` separately. Do not overwrite it with a v0.7.0 export.

---

# PKHeX.MAUI Gen7 Expansion v0.7.0 — Full UI, Expansion, Safe Save, Android

**Latest signed APK (ZIP artifact):** https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42372147818/artifacts/13574186955

**Build and verification:** https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42372147818 — check that both `build` and `sign-and-smoke-test` are green before installing.

## What's new
- **v0.5:** Existing PKHaX switch with Expansion-capable species, forms, moves, abilities and items. Original Pokémon/Shiny sprites plus offline form-art fallback.
- **v0.6:** Automatic backup of each imported save, locally stored recovery list in Settings, and checksum/round-trip verification of Ultra Sun/Moon Expansion saves before export.
- **v0.7:** Android document-picker streaming, optional Box legality markers (off by default for faster browsing), private crash logs and a workflow that can use a persistent APK signing certificate via GitHub secrets.

Read [complete changes, setup and limitations](docs/v0.7-release-notes.md).

**Safety:** A Core synthetic Gen7 Expansion save test and an Android startup test are included. Editing an actual Pokémon Ultra Sun Expansion `main` has **not** yet been tested against a user-provided save. Use a copy. The workflow's temporary signing certificate cannot update an older Debug-signed installation in place.

---
## Earlier v0.4 release (archived)

# PKHeX Gen7 Expansion Mobile v0.4.0 — PKHaX Settings

**Download the tested signed Android APK (ZIP artifact):**

https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42367509587/artifacts/13571974623

Open the link (sign in to GitHub if needed), download the ZIP, extract `PKHeX-MAUI-Gen7Expansion-PKHaX-v0.4.0-Signed.apk`, and install it.

**Changes in v0.4.0**
- Settings → PKHeX Settings → **PKHaX Mode** toggle (off by default, persists).
- When enabled: unfiltered choices for species, moves, held items, and abilities within the save's supported IDs. Ability picker supports custom Gen7 Expansion abilities.
- When disabled: normal filtered choices return. This does **not** revert previously saved illegal changes.
- Disabled the original PKHeX.MAUI update checker, which was incorrectly prompting this expansion fork to update to upstream versions.
- Kept the original PKHeX.MAUI interface, Box/Party screens, editor tabs, and packaged Pokémon/Shiny sprites.

**Validation:** GitHub Actions run [42367509587](https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42367509587) passed the full .NET MAUI build, signing verification and Android 15 emulator startup test. No on-device Xiaomi 14 save-editing regression test has been performed.

**Install note:** This signed APK uses a new temporary Debug signing key. If Android reports a package-signature mismatch, back up any app-local data, uninstall the previous *Expansion fork* (`org.pkhex.gen7expansion.maui`) and install v0.4.0. Keep the original PKHeX.MAUI separately if desired.

**Save safety:** Test on a copy of your decrypted `main` and keep the original backup. PKHaX permits intentionally illegal data; game acceptance is not guaranteed.

**Implementation:** [patch script](scripts/patch-pkhax-updates.py) | [integration script](scripts/prepare-pkhex-maui.ps1) | [build workflow](.github/workflows/android-maui-expansion.yml).

---

# PKHeX Gen7 Expansion Mobile — PKHeX.MAUI Original Interface

## ✅ APK with original PKHeX.MAUI UI, sprites, and Gen7 Expansion core

The new experimental full-UI build was created from the public source **santacrab2/PKHeXMAUI** (pinned commit `a6f7cfb`) with **Aqua-0/PKHeX v1.0 PKHeX.Core** replacing the original NuGet engine. It preserves the original flyout menu, Main / Met / Stats / Moves / Cosmetic Pokémon editing tabs, Box / Party, and the bundled regular / shiny / form sprites.

**Installation artifact (signed APK, zipped by GitHub):** https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42361719267/artifacts/13569877645

**Verified:** .NET build successful; APK re-signed and signature verified; installed and opened on Android 15 x86_64 emulator; application remained running after the startup smoke test. **Not yet verified on Xiaomi 14 or with an Ultra Sun Expansion save file**.

**To install:** Open the artifact link while logged in to GitHub, download the ZIP, extract `PKHeX-MAUI-Gen7Expansion-OriginalUI-Signed.apk` and open that APK on Android. The package ID is `org.pkhex.gen7expansion.maui`; it installs alongside the original app. Keep an external backup of the `main` save.

**Important:** The original maintainer explicitly states that PKHeX.MAUI doesn't support ROM hacks; this is an experimental integration of an Expansion-aware core, not a guarantee of save editing safety. Some AutoMod / Injection features could still be incompatible.

**Build script:** `scripts/prepare-pkhex-maui.ps1`; **original UI build workflow:** `.github/workflows/android-maui-expansion.yml`; **signed APK test workflow:** `.github/workflows/android-maui-sign-test.yml`. The signed test workflow was necessary because the default build artifact did not contain a file named `*-Signed.apk`, although a standalone APK was built successfully.

---

## Legacy simplified prototype (deprecated)


An unofficial prototype using **Aqua-0/PKHeX tag v1.0 (Gen7 Expansion)** through a .NET 10 MAUI Android interface inspired by **kwsch/PKHeX.Mobile**.

## ✅ Android standalone APK: Startup crash fixed and emulator tested

**Verified new successful GitHub Actions run (build + emulator startup test):** https://github.com/xucon3979-cmyk/PKHeX-Gen7-Expansion-Mobile/actions/runs/42357732707

The fixed run has artifact **PKHeX-Gen7-Expansion-Android-Debug** containing:
- `org.pkhex.gen7expansion.mobile-Signed.apk` (the signed Debug APK to install)
- `org.pkhex.gen7expansion.mobile.apk` (unsigned build product; prefer the Signed APK)

Open the successful run -> **Artifacts** -> download artifact ZIP -> extract `org.pkhex.gen7expansion.mobile-Signed.apk` -> install on Android (enable “Install unknown apps” for your file browser if required). Sign-in to GitHub might be required to download Actions artifacts.

**Status:** APK compiled, ZIP/APK integrity checked, and **installed + launched successfully on an Android 15 x86_64 emulator**. The app remained alive after 16 seconds with no fatal startup messages. **Not yet tested on a physical Xiaomi 14, with Azahar, or with actual expansion save files.**

### Crash in first version (2026-11-07)
The old Debug APK from run 42356622710 could install but immediately crash. The Android log identified the cause:
`F monodroid: No assemblies found ... Assuming this is part of Fast Deployment. Exiting...`
The build now uses `EmbedAssembliesIntoApk=true` and `AndroidUseSharedRuntime=false` so the APK contains `PKHeX.Core` and the app assemblies, and adds an emulator startup test.
**Do not install the original 15 MB APK.** The fixed standalone APK is approximately 92 MB. As the Debug signing certificate may change between builds, uninstall the original app first; back up any app-local data before doing so.

## Source and build

Due to API upload limitations, the complete source is committed as a compressed XZ archive encoded in four numbered base64 files under `source-bundle/`. Each GitHub Actions run:
1. Concatenates `part-01.txt` through `part-04.txt`, decodes the archive, verifies SHA-256, extracts the MAUI project.
2. Checks out `Aqua-0/PKHeX` **v1.0** as the PKHeX.Core reference.
3. Applies .NET MAUI compatibility corrections found from the first compile (FlexLayout namespace, integer overload, logging provider, MAUI controls package).
4. Forces standalone Debug APK packaging with all .NET assemblies embedded.\n5. Compiles the Android Debug APK, uploads it, and smoke-tests launch on an Android emulator.

The source bundle SHA-256 after decoding: `f0b3ac5c648d056d6651cbc96e0cb90a3baf8847c903b581176fcdc4f68e74f7`.

Source directories after unpacking:
- `PKHeXExpansion.Mobile/Pages` — HomePage, Pokémon Editor, ID picker.
- `PKHeXExpansion.Mobile/Services` — SaveWorkspace, ExpansionCatalog.
- `PKHeXExpansion.Mobile/Controls` and `Platforms/Android`.
- `setup.ps1` and `build-android.ps1`.

The initial version is a **prototype rather than a 1:1 port**: sprites, QR support, advanced inventory, Mystery Gift, cross-generation transfers, and some other legacy features have not been implemented. It can potentially contain bugs in save export, UI, legality, or PK7 import/export.

## Important safety guidance

1. Always back up the original `main` save file outside the app.
2. Test on a **copy** of a decrypted Ultra Sun / Ultra Moon Expansion save.
3. Do not overwrite your only copy: export and re-open a test save first.
4. The app does **not** directly replace Azahar save data; you must import the exported file yourself.
5. Never assume the legality status of custom Expansion Pokémon has been fully validated.

## Sources and license

- https://github.com/kwsch/PKHeX.Mobile
- https://github.com/Aqua-0/PKHeX/releases/tag/v1.0

PKHeX and its modifications are GPL-3.0-or-later. Not an official release of either original project.
