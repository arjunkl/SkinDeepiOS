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

    text = replace_once(
        text,
        'if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_C_COMPILER_ID STREQUAL "Clang")',
        'if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_C_COMPILER_ID MATCHES "^(Apple)?Clang$")',
        "AppleClang compiler identity",
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
        '#ifndef APIENTRY\n'
        '#define APIENTRY\n'
        '#endif\n'
        '#ifndef APIENTRYP\n'
        '#define APIENTRYP APIENTRY *\n'
        '#endif\n'
        'typedef double GLdouble;\n'
        'typedef double GLclampd;\n'
        '#include <SDL_opengl_glext.h>\n'
        '#ifndef GL_TEXTURE_COORD_ARRAY\n'
        '#define GL_TEXTURE_COORD_ARRAY 0x8078\n'
        '#endif\n'
        '#ifndef GL_MODULATE\n'
        '#define GL_MODULATE 0x2100\n'
        '#endif\n'
        '#ifndef GL_MODELVIEW\n'
        '#define GL_MODELVIEW 0x1700\n'
        '#endif\n'
        '#else\n'
        '#include <SDL_opengl.h>\n'
        '#endif',
        "iOS OpenGL ES 3 headers",
    )
    qgl.write_text(qgl_text, encoding="utf-8")

    string_cpp = args.engine_root / "Q3E/src/main/jni/skindeep/idlib/Str.cpp"
    string_text = string_cpp.read_text(encoding="utf-8")
    string_text = replace_once(
        string_text,
        '#if !defined(__ANDROID__) //karin: using vsnprintf directly on Android\n'
        '#undef _vsnprintf\n'
        '#endif\n'
        '\tret = _vsnprintf( dest, size-1, fmt, argptr );\n'
        '#if !defined(__ANDROID__) //karin: using vsnprintf directly on Android\n'
        '#define _vsnprintf\tuse_idStr_vsnPrintf\n'
        '#endif',
        '#if defined(__IOS__)\n'
        '#undef vsnprintf\n'
        '#undef _vsnprintf\n'
        '\tret = ::vsnprintf( dest, size-1, fmt, argptr );\n'
        '#define vsnprintf\tuse_idStr_vsnPrintf\n'
        '#define _vsnprintf\tuse_idStr_vsnPrintf\n'
        '#else\n'
        '#if !defined(__ANDROID__) //karin: using vsnprintf directly on Android\n'
        '#undef _vsnprintf\n'
        '#endif\n'
        '\tret = _vsnprintf( dest, size-1, fmt, argptr );\n'
        '#if !defined(__ANDROID__) //karin: using vsnprintf directly on Android\n'
        '#define _vsnprintf\tuse_idStr_vsnPrintf\n'
        '#endif\n'
        '#endif',
        "iOS vsnprintf portability",
    )
    string_cpp.write_text(string_text, encoding="utf-8")
    print(f"Prepared {cmake}")


if __name__ == "__main__":
    main()
