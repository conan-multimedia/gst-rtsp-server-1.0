from conans import ConanFile, CMake, tools, Meson
import os

class GstrtspserverConan(ConanFile):
    name = "gst-rtsp-server"
    version = "1.14.4"
    description = "RTSP server based on GStreamer"
    url = "https://github.com/conan-multimedia/gst-rtsp-server-1.0"
    homepage = "https://github.com/GStreamer/gst-rtsp-server"
    license = "GPLv2+"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = ("gstreamer-1.0/1.14.4@conanos/dev","gst-plugins-base-1.0/1.14.4@conanos/dev",
                "gst-plugins-good-1.0/1.14.4@conanos/dev","gst-plugins-bad-1.0/1.14.4@conanos/dev",
                "gobject-introspection/1.58.0@conanos/dev","glib/2.58.0@conanos/dev",
                "libffi/3.3-rc0@conanos/dev")
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = "gst-rtsp-server-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PATH':'%s/bin:%s'%(self.deps_cpp_info["gobject-introspection"].rootpath, os.getenv("PATH")),
                'LD_LIBRARY_PATH':'%s/lib'%(self.deps_cpp_info["libffi"].rootpath),
                }):

                meson = Meson(self)
                meson.configure(
                    defs={ 'disable_introspection':'false', 'examples' : 'true',
                           'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
                         },
                    source_dir = '%s'%(os.getcwd()),
                    build_dir= '%s/builddir'%(os.getcwd()),
                    pkg_config_paths=[ '%s/lib/pkgconfig'%(self.deps_cpp_info["gstreamer-1.0"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gst-plugins-base-1.0"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gst-plugins-good-1.0"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gst-plugins-bad-1.0"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gobject-introspection"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["glib"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
                                      ]
                                )
                meson.build(args=['-j4'])
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

