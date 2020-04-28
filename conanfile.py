import os
from conans import ConanFile, CMake, tools


class LibrealuvcConan(ConanFile):
    name = "librealuvc"
    version = "1.0.1"
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
    generators = "cmake", "cmake_find_package"

    def source(self):
        self.run("git clone https://github.com/dbuller/librealuvc.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("librealuvc/CMakeLists.txt", "project(librealuvc LANGUAGES CXX C)",
                              '''project(librealuvc LANGUAGES CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
       build_type = self.settings.build_type
       self._cmake = CMake(self, build_type=build_type)
       self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
       if self.settings.os == "Windows" and self.options.shared:
           self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
       self._cmake.configure(source_folder="librealuvc")
       self._cmake.build()

    def package(self):
        #self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include/librealuvc",
                  src="librealuvc/include/librealuvc")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["librealuvc"]
