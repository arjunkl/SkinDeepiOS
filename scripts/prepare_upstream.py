#!/usr/bin/env python3
"""Prepare a pinned idTech4A++ checkout for the compile-only iOS gate.

The source checkout is ephemeral. Every rewrite is anchor-checked so upstream
drift fails explicitly instead of silently producing a different build.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("engine_root", type=Path)
    args = parser.parse_args()

    cmake = args.engine_root / "Q3E/src/main/jni/skindeep/CMakeLists.txt"
    text = cmake.read_text(encoding="utf-8")

    text = replace_once(
        text,
        'set(DHEWM3BINARY "skindeep") # dhewm3',
        'if(CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '    set(DHEWM3BINARY "SkinDeepCore")\n'
        'else()\n'
        '    set(DHEWM3BINARY "skindeep") # dhewm3\n'
        'endif()',
        "static core target name",
    )

    text = replace_once(
        text,
        'if(APPLE)\n\tset(os "macosx")',
        'if(CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '\tset(os "ios")\n'
        'elseif(APPLE)\n'
        '\tset(os "macosx")',
        "iOS operating-system identity",
    )

    text = replace_once(
        text,
        'if(NOT AROS AND NOT ANDROID)\n\tfind_package(X11 REQUIRED)',
        'if(NOT AROS AND NOT ANDROID AND NOT CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '\tfind_package(X11 REQUIRED)',
        "X11 exclusion",
    )

    text = regex_once(
        text,
        r'\telseif\(APPLE\)\n\t\tadd_definitions\(-DMACOS_X=1\).*?'
        r'\n\telseif\(WIN32\)',
        '\telseif(APPLE)\n'
        '\t\tadd_definitions(-DMACOS_X=1)\n'
        '\t\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '\t\t\tadd_definitions(-DIOS=1 -D__IOS__=1 -DNOSTEAM=1)\n'
        '\t\telse()\n'
        '\t\t\tmessage(FATAL_ERROR "This overlay supports iOS, not the macOS bundle path")\n'
        '\t\tendif()\n'
        '\telseif(WIN32)',
        "Apple compiler branch",
    )

    text = regex_once(
        text,
        r'elseif\(APPLE\)\n\tset\(OSX_RESOURCE_FILES.*?\nelseif\(WIN32\)',
        'elseif(APPLE)\n'
        '\t# Platform entry points arrive in Milestone 2. A static archive may\n'
        '\t# retain unresolved platform symbols without pretending to launch.\n'
        '\tset(src_sys_base)\n'
        '\tset(src_sys_core)\n'
        'elseif(WIN32)',
        "iOS platform source boundary",
    )

    text = replace_once(
        text,
        'if(ANDROID)\n\tadd_library(${DHEWM3BINARY} SHARED',
        'if(CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '\tadd_library(${DHEWM3BINARY} STATIC\n'
        '\t\t${src_core}\n'
        '\t\t${src_sys_base}\n'
        '\t\t${src_sys_core}\n'
        '\t)\n'
        'elseif(ANDROID)\n'
        '\tadd_library(${DHEWM3BINARY} SHARED',
        "static library target",
    )

    cmake.write_text(text, encoding="utf-8")

    qgl = args.engine_root / "Q3E/src/main/jni/skindeep/renderer/qgl.h"
    qgl_text = qgl.read_text(encoding="utf-8")
    qgl_text = replace_once(
        qgl_text,
        '#include <SDL_opengl.h>',
        '#if defined(__IOS__)\n'
        '#include <OpenGLES/ES3/gl.h>\n'
        '#include <OpenGLES/ES3/glext.h>\n'
        '#else\n'
        '#include <SDL_opengl.h>\n'
        '#endif',
        "iOS OpenGL ES 3 headers",
    )
    qgl.write_text(qgl_text, encoding="utf-8")
    print(f"Prepared {cmake}")


if __name__ == "__main__":
    main()
