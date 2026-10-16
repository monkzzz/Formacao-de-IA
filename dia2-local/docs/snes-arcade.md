# Secret SNES arcade

Enter Up, Up, Down, Down, Left, Right, Left, Right, B, A outside text
fields to open the arcade. It automatically starts the supplied Zelda ROM at
`dist/roms/zelda.sfc`. Both ROM directories are ignored by Git. The original
file remains in `roms/`; a local serving copy is in `dist/roms/`.
If the serving copy is missing, a local `.sfc` or `.smc` picker (up to 16 MB)
is available. **Stop / choose another ROM** also opens this picker.

The isolated iframe loads the [EmulatorJS stable runtime](https://emulatorjs.org/docs/cdn/)
on demand using its documented [Snes9x configuration](https://emulatorjs.org/docs/systems/snes/).
Network access to `cdn.emulatorjs.org` is required. The emulator menu provides
input configuration and save-state options. Export saves before closing.
Escape or **Back to the lab** destroys the emulator frame and stops playback;
**Stop / choose another ROM** resets it. Game progress in memory is lost on exit.

Local Edge UI checks passed: code activation, lazy loading, file validation,
blob ROM configuration, Escape teardown, focus restoration, reopening, download
failure, retry, close button and a 375-pixel mobile layout. The runtime loader
was doubled in these initial checks. A subsequent real-runtime Edge check with
the supplied Zelda ROM passed: automatic loading, Snes9x game-start event,
visible game canvas and teardown on close. The boot screen was visually checked;
extended gameplay and save persistence have not been tested. Screenshots are
retained in ignored `artifacts/`.

Deployment includes `v3/snes.html`, `v3/snes.js`, `v3/snes.css`, both Konami
assets and `index.html`, with the entry page transferred last. Automatic Zelda
startup also requires the separate `roms/zelda.sfc` serving asset. Deployment
and public verification evidence is recorded separately under `reports/`,
preserving earlier release reports.

Release v3.4.0 is live. The [FTPS deployment record](../reports/release-3.4.0-ftp-deployment.json)
records seven verified uploads, with replaced assets backed up. Public Edge
verification passed automatic Zelda startup, the game-start event, visible canvas,
runtime teardown and the v3.4.0 footer. All 38 public static asset hashes matched
the local files, including the separately deployed ROM. This was a boot smoke
test; extended gameplay and save persistence remain untested.
