# Milestone 3 — engine executable link gate

## Goal

Move from a standalone static archive to an iPhoneOS executable that contains
the Skin Deep engine, hard-linked gameplay module, SDL runtime, and iOS system
path implementation.

This is initially a device-ABI link gate. Simulator execution follows after
all third-party runtime dependencies link without placeholder claims.

## Passing evidence

1. Build SDL 2.30.12 from pinned source for iPhoneOS ARM64.
2. Compile the POSIX/SDL idTech system layer for iOS.
3. Link `SkinDeepCore`, `skindeep_idlib`, and SDL into one application
   executable.
4. Verify `_main`, `_GetGameAPI`, and `_gameLocal` in that executable.
5. Upload the unsigned `.app` and architecture/symbol evidence.

## Explicitly outside this milestone

- Signing or physical-device execution
- Commercial Skin Deep data
- A claim that `common->Init` has executed successfully
- Rendering, audio, touch, gyro, or gameplay
