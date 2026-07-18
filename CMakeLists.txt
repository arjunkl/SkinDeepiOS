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
        if(NOT DEFINED SDL_ROOT OR NOT EXISTS "${SDL_ROOT}/CMakeLists.txt")
            message(FATAL_ERROR "The engine link probe requires -DSDL_ROOT=/path/to/SDL2")
        endif()
        set(SDL_SHARED OFF CACHE BOOL "Build no SDL dylib" FORCE)
        set(SDL_STATIC ON CACHE BOOL "Build static SDL" FORCE)
        set(SDL_TEST OFF CACHE BOOL "Build no SDL tests" FORCE)
        set(SDL_INSTALL OFF CACHE BOOL "Do not install SDL" FORCE)
        set(SKINDEEP_LINKABLE_IOS ON CACHE BOOL "Include the POSIX/SDL system layer" FORCE)
        add_subdirectory("${SDL_ROOT}" sdl2 EXCLUDE_FROM_ALL)
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
            SDL2-static
            "-framework Foundation"
            "-framework UIKit"
            "-framework CoreGraphics"
            "-framework QuartzCore"
            "-framework OpenGLES"
            "-framework OpenAL"
            z
        )
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
