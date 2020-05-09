#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan recipe package for librealuvc
"""
from conans import ConanFile, CMake, tools

class LibrealuvcConan(ConanFile):
    name = "librealuvc"

    version = "0.0.4"
    license = "http://www.apache.org/LICENSE.txt"
    author = "darren.buller@ultraleap.com"
    url = "https://github.com/DarrenBuller/conan-librealuvc"
    description = "This library provides a portable backend to UVC-compliant cameras and other" \
                  "USB devices (e.g. motion sensors), with support for UVC Extension Units." \
                  "It is a modified version of the backend code from the IntelRealSense/librealsense" \
                  "library."
    settings = "os", "compiler", "build_type", "arch"
    requires = "opencv/4.1.1@conan/stable"  # , "libusb/1.0.23@bincrafters/stable"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": True,
                       "fPIC": True,
                       "opencv:shared": True,
                       "opencv:ffmpeg": False,
                       "opencv:tiff": False,
                       "opencv:protobuf": False}
    exports = "LICENSE"
    generators = "cmake_paths"

    def source(self):
        self.run("git clone --branch develop-conan-integration-test --depth 1 https://github.com/DarrenBuller/librealuvc.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("librealuvc/CMakeLists.txt", "project(librealuvc LANGUAGES CXX C)",
                              '''project(librealuvc LANGUAGES CXX C)
#set(BUILD_WITH_CONAN ON)                              
#if(EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo_multi.cmake)
#  include(${CMAKE_BINARY_DIR}/conanbuildinfo_multi.cmake)
#else()
#  include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
#endif()
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
message(STATUS "CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}")
set(OpenCV_DIR ${CONAN_OPENCV_ROOT})
#conan_basic_setup(TARGETS)''')

    def config_options(self):
        """Remove fPIC option on Windows platform
        """
        if self.settings.os == "Windows":
            del self.options.fPIC


    def configure_cmake(self):
        """Create CMake instance and execute configure step
        """
        build_type = "None"
        if(self.settings.os == "Windows" and self.options.shared):
            """Force release mode because debug dll fails unresolved linker errors
            """
            build_type = "Release"

        cmake = CMake(self, build_type=build_type)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.configure(source_folder="librealuvc")
        return cmake

    def build(self):
        """Configure, build and install FlatBuffers using CMake.
        """
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        self.copy("*.h", dst="include/librealuvc",
                  src="librealuvc/include/librealuvc")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.so.*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["librealuvc"]
