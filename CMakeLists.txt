cmake_minimum_required(VERSION 3.25)
project(SkinDeepiOSCompileGate LANGUAGES C CXX OBJC OBJCXX)

if(NOT CMAKE_SYSTEM_NAME STREQUAL "iOS")
    message(FATAL_ERROR "This compile gate must target CMAKE_SYSTEM_NAME=iOS")
endif()

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
