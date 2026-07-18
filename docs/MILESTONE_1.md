# Milestone 1 — ARM64 iOS compile foundation

## Goal

Produce a real `iphoneos`/ARM64 static archive containing the Skin Deep engine
and its gameplay module. The game module is hard-linked; no runtime `dlopen`
path is part of this gate.

## Pinned source

- Repository: `glKarin/com.n0n3m4.diii4a`
- Commit: `c600f9a5c935494d43f264a336b3b46538d569b4`
- Skin Deep tree: `Q3E/src/main/jni/skindeep`

The workflow fetches only source and dependency headers needed by this gate.

## Passing evidence

A passing run must provide all of the following:

1. CMake configures with `CMAKE_SYSTEM_NAME=iOS`, `iphoneos`, and `arm64`.
2. `SkinDeepCore` and `skindeep_idlib` compile with the Apple device SDK.
3. The combined archive reports ARM64 through `lipo`.
4. The archive contains a Skin Deep game-module symbol such as `gameLocal` or
   `GetGameAPI`.
5. GitHub Actions uploads the archive, architecture evidence, symbol evidence,
   and pinned upstream commit.

## Explicitly outside this milestone

- An `.app` or `.ipa`
- Signing, installation, or physical-device execution
- OpenGL ES context creation or shader conversion
- Audio, filesystem, lifecycle, touch, gyro, or controllers
- Commercial Skin Deep data

