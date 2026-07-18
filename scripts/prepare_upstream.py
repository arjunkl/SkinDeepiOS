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
        'if(DIII4A)\n\tset(JPEG_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libjpeg/libjpeg")\n'
        '\tset(JPEG_LIBRARY "jpeg")',
        'if(DIII4A)\n\tset(JPEG_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libjpeg/libjpeg")\n'
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS" AND TARGET jpeg)\n'
        '\t\tset(JPEG_LIBRARY jpeg)\n'
        '\telse()\n'
        '\t\tset(JPEG_LIBRARY "jpeg")\n'
        '\tendif()',
        "static JPEG target",
    )

    text = replace_once(
        text,
        'if(DIII4A)\n\tset(OGG_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libogg/include")\n'
        '\tset(OGG_LIBRARIES "ogg")',
        'if(DIII4A)\n\tset(OGG_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libogg/include")\n'
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS" AND TARGET ogg)\n'
        '\t\tset(OGG_LIBRARIES ogg)\n'
        '\telse()\n'
        '\t\tset(OGG_LIBRARIES "ogg")\n'
        '\tendif()',
        "static Ogg target",
    )

    text = replace_once(
        text,
        'if(DIII4A)\n\tset(VORBIS_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libvorbis/include")\n'
        '\tset(VORBIS_LIBRARIES "vorbis")',
        'if(DIII4A)\n\tset(VORBIS_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libvorbis/include")\n'
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS" AND TARGET vorbis)\n'
        '\t\tset(VORBIS_LIBRARIES vorbis)\n'
        '\telse()\n'
        '\t\tset(VORBIS_LIBRARIES "vorbis")\n'
        '\tendif()',
        "static Vorbis target",
    )

    text = replace_once(
        text,
        'if(DIII4A)\n\tset(VORBISFILE_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libvorbis/include")\n'
        '\tset(VORBISFILE_LIBRARIES "vorbisfile")',
        'if(DIII4A)\n\tset(VORBISFILE_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/libvorbis/include")\n'
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS" AND TARGET vorbisfile)\n'
        '\t\tset(VORBISFILE_LIBRARIES vorbisfile)\n'
        '\telse()\n'
        '\t\tset(VORBISFILE_LIBRARIES "vorbisfile")\n'
        '\tendif()',
        "static Vorbisfile target",
    )

    text = replace_once(
        text,
        'if(DIII4A)\n\tset(OPENAL_INCLUDE_DIR "${DIII4A_DEPEND_INCLUDE_PATH}/openal")\n'
        '\tset(OPENAL_LIBRARY "openal")',
        'if(DIII4A)\n\tset(OPENAL_INCLUDE_DIR "${DIII4A_DEPEND_INCLUDE_PATH}/openal")\n'
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '\t\tset(OPENAL_LIBRARY "-framework OpenAL")\n'
        '\telse()\n'
        '\t\tset(OPENAL_LIBRARY "openal")\n'
        '\tendif()',
        "Apple OpenAL framework",
    )

    text = replace_once(
        text,
        'if(DIII4A)\n\tset(CURL_FOUND True)\n'
        '\tset(CURL_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/curl/include")\n'
        '\tset(CURL_LIBRARY "curl")\nendif()',
        'if(DIII4A)\n'
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS")\n'
        '\t\tset(CURL_FOUND False)\n'
        '\t\tset(CURL_LIBRARY "")\n'
        '\telse()\n'
        '\t\tset(CURL_FOUND True)\n'
        '\t\tset(CURL_INCLUDE_DIR "${DIII4A_DEPEND_LIBRARY_PATH}/curl/include")\n'
        '\t\tset(CURL_LIBRARY "curl")\n'
        '\tendif()\nendif()',
        "disable curl on iOS",
    )

    text = replace_once(
        text,
        '\tset(SDL2_LIBRARY "SDL2")',
        '\tif(CMAKE_SYSTEM_NAME STREQUAL "iOS" AND TARGET SDL2-static)\n'
        '\t\tset(SDL2_LIBRARY SDL2-static)\n'
        '\telse()\n'
        '\t\tset(SDL2_LIBRARY "SDL2")\n'
        '\tendif()',
        "static SDL target",
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
        '\tif(SKINDEEP_LINKABLE_IOS)\n'
        '\t\tset(src_sys_base\n'
        '\t\t\tsys/cpu.cpp\n'
        '\t\t\tsys/threads.cpp\n'
        '\t\t\tsys/events.cpp\n'
        '\t\t\tsys/sys_local.cpp\n'
        '\t\t\tsys/posix/posix_net.cpp\n'
        '\t\t\tsys/posix/posix_main.cpp\n'
        '\t\t)\n'
        '\t\tset(src_sys_core sys/glimp.cpp)\n'
        '\telse()\n'
        '\t\t# The compile-only gate intentionally retains unresolved platform symbols.\n'
        '\t\tset(src_sys_base)\n'
        '\t\tset(src_sys_core)\n'
        '\tendif()\n'
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
        '#ifndef GL_VERTEX_ARRAY\n'
        '#define GL_VERTEX_ARRAY 0x8074\n'
        '#endif\n'
        '#ifndef GL_COLOR_ARRAY\n'
        '#define GL_COLOR_ARRAY 0x8076\n'
        '#endif\n'
        '#ifndef GL_MODULATE\n'
        '#define GL_MODULATE 0x2100\n'
        '#endif\n'
        '#ifndef GL_DECAL\n'
        '#define GL_DECAL 0x2101\n'
        '#endif\n'
        '#ifndef GL_ADD\n'
        '#define GL_ADD 0x0104\n'
        '#endif\n'
        '#ifndef GL_MODELVIEW\n'
        '#define GL_MODELVIEW 0x1700\n'
        '#endif\n'
        '#ifndef GL_PROJECTION\n'
        '#define GL_PROJECTION 0x1701\n'
        '#endif\n'
        '#ifndef GL_ALL_ATTRIB_BITS\n'
        '#define GL_ALL_ATTRIB_BITS 0xFFFFFFFF\n'
        '#endif\n'
        '#ifndef GL_POLYGON\n'
        '#define GL_POLYGON 0x0009\n'
        '#endif\n'
        '#ifndef GL_QUADS\n'
        '#define GL_QUADS 0x0007\n'
        '#endif\n'
        '#ifndef GL_STENCIL_INDEX\n'
        '#define GL_STENCIL_INDEX 0x1901\n'
        '#endif\n'
        '#ifndef GL_POLYGON_OFFSET_LINE\n'
        '#define GL_POLYGON_OFFSET_LINE 0x2A02\n'
        '#endif\n'
        '#ifndef GL_LINE\n'
        '#define GL_LINE 0x1B01\n'
        '#endif\n'
        '#ifndef GL_FILL\n'
        '#define GL_FILL 0x1B02\n'
        '#endif\n'
        '#ifndef GL_SMOOTH\n'
        '#define GL_SMOOTH 0x1D01\n'
        '#endif\n'
        '#ifndef GL_ALPHA_TEST\n'
        '#define GL_ALPHA_TEST 0x0BC0\n'
        '#endif\n'
        '#ifndef GL_COLOR_LOGIC_OP\n'
        '#define GL_COLOR_LOGIC_OP 0x0BF2\n'
        '#endif\n'
        '#ifndef GL_TEXTURE_GEN_S\n'
        '#define GL_TEXTURE_GEN_S 0x0C60\n'
        '#define GL_TEXTURE_GEN_T 0x0C61\n'
        '#define GL_TEXTURE_GEN_R 0x0C62\n'
        '#define GL_TEXTURE_GEN_Q 0x0C63\n'
        '#endif\n'
        '#ifndef GL_S\n'
        '#define GL_S 0x2000\n'
        '#define GL_T 0x2001\n'
        '#define GL_R 0x2002\n'
        '#define GL_Q 0x2003\n'
        '#endif\n'
        '#ifndef GL_TEXTURE_GEN_MODE\n'
        '#define GL_TEXTURE_GEN_MODE 0x2500\n'
        '#endif\n'
        '#ifndef GL_OBJECT_PLANE\n'
        '#define GL_OBJECT_PLANE 0x2501\n'
        '#define GL_EYE_PLANE 0x2502\n'
        '#endif\n'
        '#ifndef GL_OR\n'
        '#define GL_OR 0x1507\n'
        '#endif\n'
        '#ifndef GL_STACK_OVERFLOW\n'
        '#define GL_STACK_OVERFLOW 0x0503\n'
        '#define GL_STACK_UNDERFLOW 0x0504\n'
        '#endif\n'
        '#ifndef GL_COLOR_INDEX\n'
        '#define GL_COLOR_INDEX 0x1900\n'
        '#endif\n'
        '#ifndef GL_ALPHA8\n'
        '#define GL_ALPHA8 0x803C\n'
        '#endif\n'
        '#ifndef GL_LUMINANCE8\n'
        '#define GL_LUMINANCE8 0x8040\n'
        '#endif\n'
        '#ifndef GL_LUMINANCE8_ALPHA8\n'
        '#define GL_LUMINANCE8_ALPHA8 0x8045\n'
        '#endif\n'
        '#ifndef GL_INTENSITY8\n'
        '#define GL_INTENSITY8 0x804B\n'
        '#endif\n'
        '#ifndef GL_RGB5\n'
        '#define GL_RGB5 0x8050\n'
        '#endif\n'
        '#ifndef GL_TEXTURE_BORDER_COLOR\n'
        '#define GL_TEXTURE_BORDER_COLOR 0x1004\n'
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

    jpeg_config = (
        args.engine_root
        / "Q3E/src/main/jni/deplibs/libjpeg/libjpeg/jconfig.h"
    )
    jpeg_config.write_text(
        "#pragma once\n"
        "#define HAVE_PROTOTYPES 1\n"
        "#define HAVE_UNSIGNED_CHAR 1\n"
        "#define HAVE_UNSIGNED_SHORT 1\n"
        "#define HAVE_STDDEF_H 1\n"
        "#define HAVE_STDLIB_H 1\n",
        encoding="utf-8",
    )
    print(f"Prepared {cmake}")


if __name__ == "__main__":
    main()
