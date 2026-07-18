cmake_minimum_required(VERSION 3.25)
project(SkinDeepiOS LANGUAGES C CXX OBJC OBJCXX)

if(NOT CMAKE_SYSTEM_NAME STREQUAL "iOS")
    message(FATAL_ERROR "This compile gate must target CMAKE_SYSTEM_NAME=iOS")
endif()

option(SKINDEEP_BUILD_ENGINE_ARCHIVE "Build the pinned idTech4A++ core" ON)
option(SKINDEEP_BUILD_BOOTSTRAP_APP "Build the native iOS bootstrap app" ON)
option(SKINDEEP_BUILD_ENGINE_LINK_PROBE "Link the core into an iOS executable" OFF)

if(SKINDEEP_BUILD_ENGINE_ARCHIVE)
    if(NOT DEFINED ENGINE_ROOT)
        message(FATAL_ERROR "Pass -DENGINE_ROOT=/absolute/path/to/idTech4A++")
    endif()

    get_filename_component(ENGINE_ROOT "${ENGINE_ROOT}" ABSOLUTE)
    set(JNI_ROOT "${ENGINE_ROOT}/Q3E/src/main/jni")
    set(SKINDEEP_ROOT "${JNI_ROOT}/skindeep")

    if(NOT EXISTS "${SKINDEEP_ROOT}/CMakeLists.txt")
        message(FATAL_ERROR "Skin Deep source is missing at ${SKINDEEP_ROOT}")
    endif()

    set(DIII4A_DEPEND_LIBRARY_PATH "${JNI_ROOT}/deplibs")
    set(DIII4A_DEPEND_INCLUDE_PATH "${JNI_ROOT}/depincs")
    set(DIII4A_DEPEND_COMMON_PATH "${JNI_ROOT}/common")

    set(CORE ON CACHE BOOL "Build engine core" FORCE)
    set(D3XP ON CACHE BOOL "Hard-link Skin Deep gameplay code" FORCE)
    set(HARDLINK_GAME ON CACHE BOOL "Do not build a runtime game dylib" FORCE)
    set(DEDICATED OFF CACHE BOOL "Do not build a server" FORCE)
    set(SDL2 ON CACHE BOOL "Use SDL2 headers" FORCE)
    set(ONATIVE OFF CACHE BOOL "Never tune for the CI host" FORCE)

    if(SKINDEEP_BUILD_ENGINE_LINK_PROBE)
        foreach(dependency SDL_ROOT OGG_ROOT VORBIS_ROOT)
            if(NOT DEFINED ${dependency} OR NOT EXISTS "${${dependency}}/CMakeLists.txt")
                message(FATAL_ERROR "The engine link probe requires -D${dependency}=/path/to/source")
            endif()
        endforeach()
        if(NOT EXISTS "${JNI_ROOT}/deplibs/libjpeg/CMakeLists.txt")
            message(FATAL_ERROR "The bundled libjpeg CMake project is missing")
        endif()
        set(SDL_SHARED OFF CACHE BOOL "Build no SDL dylib" FORCE)
        set(SDL_STATIC ON CACHE BOOL "Build static SDL" FORCE)
        set(SDL_TEST OFF CACHE BOOL "Build no SDL tests" FORCE)
        set(SDL_INSTALL OFF CACHE BOOL "Do not install SDL" FORCE)
        set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build static media dependencies" FORCE)
        set(BUILD_STATIC_LIBS ON CACHE BOOL "Build bundled static media libraries" FORCE)
        set(BUILD_TESTING OFF CACHE BOOL "Build no dependency tests" FORCE)
        set(INSTALL_DOCS OFF CACHE BOOL "Install no dependency documentation" FORCE)
        set(INSTALL_PKG_CONFIG_MODULE OFF CACHE BOOL "Install no pkg-config files" FORCE)
        set(INSTALL_CMAKE_PACKAGE_MODULE ON CACHE BOOL "Generate the Ogg package metadata" FORCE)
        set(SKINDEEP_LINKABLE_IOS ON CACHE BOOL "Include the POSIX/SDL system layer" FORCE)
        add_subdirectory("${SDL_ROOT}" sdl2 EXCLUDE_FROM_ALL)
        add_subdirectory("${OGG_ROOT}" ogg EXCLUDE_FROM_ALL)
        # Vorbis 1.3.7 ships a FindOgg module that looks only for an installed
        # archive. Seed its cache variables with the in-tree target instead.
        set(OGG_INCLUDE_DIR "${OGG_ROOT}/include" CACHE PATH "In-tree Ogg headers" FORCE)
        set(OGG_LIBRARY ogg CACHE STRING "In-tree Ogg target" FORCE)
        if(NOT TARGET Ogg::ogg)
            message(FATAL_ERROR "The in-tree Ogg project did not create Ogg::ogg")
        endif()
        add_subdirectory("${VORBIS_ROOT}" vorbis EXCLUDE_FROM_ALL)
        add_subdirectory("${JNI_ROOT}/deplibs/libjpeg" libjpeg EXCLUDE_FROM_ALL)
        # The bundled JPEG static target otherwise contains only an object
        # generator expression, which Xcode 16 does not materialize as an
        # archive. A native source forces the expected libtool phase.
        target_sources(jpeg_static PRIVATE ios/JPEGArchiveAnchor.c)
    endif()

    add_subdirectory("${SKINDEEP_ROOT}" skindeep)

    if(NOT TARGET SkinDeepCore)
        message(FATAL_ERROR "The prepared upstream tree did not create SkinDeepCore")
    endif()

    target_compile_features(SkinDeepCore PRIVATE cxx_std_11)
    target_compile_definitions(SkinDeepCore PRIVATE
        __IOS__=1
        __IPHONEOS__=1
        IOS=1
        NOSTEAM=1
    )

    if(SKINDEEP_BUILD_ENGINE_LINK_PROBE)
        add_executable(SkinDeepEngineLinkProbe MACOSX_BUNDLE
            ios/SkinDeepEngineLinkProbe.mm
            ios/SkinDeepSystem.mm
        )
        target_compile_features(SkinDeepEngineLinkProbe PRIVATE cxx_std_17)
        target_compile_definitions(SkinDeepEngineLinkProbe PRIVATE
            __IOS__=1
            __IPHONEOS__=1
            IOS=1
            NOSTEAM=1
            GLES_SILENCE_DEPRECATION=1
        )
        target_include_directories(SkinDeepEngineLinkProbe PRIVATE
            "${SKINDEEP_ROOT}"
            "${CMAKE_CURRENT_BINARY_DIR}/skindeep"
            "${SDL_ROOT}/include"
        )
        target_link_libraries(SkinDeepEngineLinkProbe PRIVATE
            SkinDeepCore
            skindeep_idlib
            SDL2main
            SDL2-static
            "-framework Foundation"
            "-framework UIKit"
            "-framework CoreGraphics"
            "-framework QuartzCore"
            "-framework OpenGLES"
            "-framework OpenAL"
            z
        )
        add_dependencies(SkinDeepEngineLinkProbe jpeg_static)
        set_target_properties(SkinDeepEngineLinkProbe PROPERTIES
            MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/ios/Info.plist.in"
            XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED "NO"
            XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED "NO"
            XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "org.skindeep.ios.engine-link-probe"
            XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2"
        )
    endif()
endif()

if(SKINDEEP_BUILD_BOOTSTRAP_APP)
    add_executable(SkinDeepBootstrap MACOSX_BUNDLE
        ios/SkinDeepBootstrap.mm
    )
    target_compile_features(SkinDeepBootstrap PRIVATE cxx_std_17)
    target_compile_definitions(SkinDeepBootstrap PRIVATE GLES_SILENCE_DEPRECATION=1)
    target_link_libraries(SkinDeepBootstrap PRIVATE
        "-framework Foundation"
        "-framework UIKit"
        "-framework CoreGraphics"
        "-framework QuartzCore"
        "-framework OpenGLES"
    )
    set_target_properties(SkinDeepBootstrap PROPERTIES
        MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/ios/Info.plist.in"
        XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED "NO"
        XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED "NO"
        XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "org.skindeep.ios.bootstrap"
        XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2"
    )
endif()
