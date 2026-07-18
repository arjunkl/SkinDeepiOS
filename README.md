# SkinDeepiOS

Experimental iOS port work for **Skin Deep**, based on the open-source
[idTech4A++](https://github.com/glKarin/com.n0n3m4.diii4a) compatibility layer.

This repository contains engine and platform work only. It does not include
commercial Skin Deep game data. A legally owned copy of the game is required.

## Current status

Milestone 1 compiles the pinned Skin Deep engine and hard-linked gameplay code
into an ARM64 iPhoneOS archive. Milestone 2 adds a native iOS platform
bootstrap and launches it in a clean simulator to validate UIKit lifecycle,
sandbox storage, and OpenGL ES 3 context creation.

The bootstrap is deliberately not described as an engine launch: attaching
the idTech runtime, SDL lifecycle, shaders, audio, and input remains future
work.

## Milestone 1

Run the **Skin Deep iOS ARM64 Compile Gate** workflow. The output artifact is:

```text
SkinDeepCore-iphoneos-arm64/libSkinDeepCore.a
```

The workflow intentionally fetches no commercial data.

## Milestone 2

Run the **Skin Deep iOS Simulator Bootstrap** workflow. Its artifact contains:

```text
SkinDeepBootstrap-simulator/
  SkinDeepBootstrap.app.zip
  bootstrap.json
  bootstrap.log
  bootstrap.png
```

See [`docs/MILESTONE_2.md`](docs/MILESTONE_2.md) for the exact proof boundary.
