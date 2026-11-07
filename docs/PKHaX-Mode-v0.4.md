# PKHaX + update-notification modifications (v0.4.0)

This fork builds the **pinned original PKHeX.MAUI UI** with **Aqua-0 v1.0 PKHeX.Core**, preserving bundled Pokémon normal/shiny sprites and editor tabs.

**Settings → PKHeX Settings → PKHaX Mode** controls a persistent, default-off toggle.
- OFF: normal filtered Pokémon, moves, items, species-based abilities.
- ON: the Core's `FilteredGameDataSource(..., HaX: true)` is used for species, moves, item lists. The Ability picker offers all abilities within the save's max ID (including Aqua-0's custom Expansion abilities). Move learnset filtering is bypassed in the Move tab.
- On returning to the editor, lists are reloaded without discarding the loaded save. Existing legality warnings are **not** disabled.
- Turning OFF does **not** automatically revert any illegal edits already applied.

Original santacrab2/PKHeXMAUI release-check code is no longer called; its updater methods are disabled so the fork never prompts to update to an unrelated upstream release.

Source patch: `scripts/patch-pkhax-updates.py`, applied during `scripts/prepare-pkhex-maui.ps1`.

The GitHub workflow builds the app, signs the APK with a new ephemeral debug certificate and runs an Android emulator **startup smoke test**. That does not verify that saving modified Pokémon is safe. **Back up your decrypted `main` before testing**.

The new APK is signed with a different temporary debug key, so Android may reject installation over the old custom fork. If so, back up app-local files and uninstall old `org.pkhex.gen7expansion.maui` before installing v0.4.0.
