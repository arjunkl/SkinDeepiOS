# Milestone 2 — iOS platform bootstrap

## Goal

Produce and launch a real iOS application bundle before attaching the full
engine runtime. The app must prove that UIKit lifecycle, sandbox storage, and
an OpenGL ES 3 context work under the current Apple toolchain.

## Passing evidence

The **Skin Deep iOS Simulator Bootstrap** workflow must:

1. Build an unsigned `SkinDeepBootstrap.app` for the latest installed iOS
   Simulator runtime.
2. Boot a clean iPhone simulator, install the bundle, and launch it.
3. Create `Documents/SkinDeep/base` inside the app sandbox.
4. create and make current an OpenGL ES 3 context.
5. Write `Documents/bootstrap.json` containing the filesystem and graphics
   evidence.
6. Capture the running UI and upload the app, JSON, screenshot, and system log.

## Explicitly outside this milestone

- Calling `common->Init` or running the idTech frame loop
- SDL lifecycle integration
- Linking the device-only engine archive into the simulator app
- Loading or distributing commercial Skin Deep data
- Rendering Skin Deep shaders, audio, input, signing, or physical-device use

This boundary is intentional: it validates the native Apple platform seam and
the project's GLES 3.0 assumption without disguising a shell launch as an
engine launch.
