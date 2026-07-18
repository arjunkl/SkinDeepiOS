# SkinDeepiOS

Experimental iOS port work for **Skin Deep**, based on the open-source
[idTech4A++](https://github.com/glKarin/com.n0n3m4.diii4a) compatibility layer.

This repository contains engine and platform work only. It does not include
commercial Skin Deep game data. A legally owned copy of the game is required.

## Current status

Milestone 1 is a compile-only foundation. Its GitHub Actions gate pins an exact
idTech4A++ revision, compiles the Skin Deep engine and gameplay code into one
ARM64 iPhoneOS static archive, and publishes that archive with provenance.

Passing this gate proves only that the selected sources compile for the Apple
device ABI. It does **not** yet prove launch, rendering, audio, input, asset
loading, signing, installation, or gameplay.

## Milestone 1

Run the **Skin Deep iOS ARM64 Compile Gate** workflow. The output artifact is:

```text
SkinDeepCore-iphoneos-arm64/libSkinDeepCore.a
```

The workflow intentionally fetches no commercial data.

