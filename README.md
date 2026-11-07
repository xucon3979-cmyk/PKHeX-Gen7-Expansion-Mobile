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
