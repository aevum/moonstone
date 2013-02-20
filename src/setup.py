# -*- coding: utf-8 -*-
#
# Moonstone is platform for processing of medical images (DICOM).
# Copyright (C) 2009-2011 by Neppo Tecnologia da Informação LTDA
# and Aevum Softwares LTDA
#
# This file is part of Moonstone.
#
# Moonstone is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
import glob
import locale
import shutil
import fnmatch
from distutils.core import setup
from setuptools import find_packages
import ConfigParser
import extensions

config = ConfigParser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.getcwd(), "resources", "moonstone.conf")))
config_dir = ".{0}".format(config.get("moonstone", "name_unix"))

extensions.register_file(os.path.abspath(os.path.join(os.getcwd(), "moonstone/ilsa/resources/plugin.conf")))
registered_plugins = [plugin.module_name for plugin in extensions.get()]

if sys.platform == "win32":
    import py2exe

    # If run without args, build executables, in quiet mode.
    if len(sys.argv) == 1:
        sys.argv.append("py2exe")
        sys.argv.append("-q")
    Executable = lambda x, *y, **z: x
    setup_requires = ["py2exe"]
elif sys.platform == "linux2":
    import cx_Freeze
    from cx_Freeze import setup, Executable

    setup_requires = ["cx_Freeze"]
elif sys.platform == "darwin":
    import py2app

    Executable = lambda x, *y, **z: x
    setup_requires = ["py2app"]
else:
    print("Error in buld!")
    sys.exit()


locale.setlocale(locale.LC_ALL, "")
try:
    sys.setappdefaultencoding("utf-8")
except AttributeError:
    try:
        reload(sys)
        sys.setdefaultencoding("utf-8")
    except LookupError:
        pass

if sys.version_info[0] == 3:
    extra_args = dict(use_2to3=True)
else:
    extra_args = dict()

long_description = """\
Moonstone is a platform for analysis, processing and visualization
medical image (DICOM) multiplatform (Unix-like, Mac OSX, Windows)
written in Python and using libraries of GDCM/VTK/ITK For image
processing, and distributed on a free license (GPL, LGPL).
"""

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: Healthcare Industry",
    "License :: OSI Approved :: GNU Lesser General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python :: 2.7",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

def get_moonstone_packages():
    return find_packages()

def get_moonstone_all_packages():
    fls = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(os.curdir,
                                                             "moonstone")):
        for filename in fnmatch.filter(filenames, "*.py"):
            fileui = os.path.join(dirpath, filename)
            if not os.access(fileui, os.R_OK):
                raise IOError("Can not access the file {0}" \
                        .format(fileui))
            fileui = fileui.replace("%s%s" % (os.curdir, os.sep), "")
            fileui = fileui.replace("%s" % os.sep, ".")
            fileui = fileui.replace(".py", "")
            fileui = fileui.replace(".__init__", "")
            fls.append(fileui)
    return fls

def get_include_modules():
    inc = [
        "encodings.utf_8",
        "vtk", "vtkgdcm", "gdcm", "extensions", "yaml", "sqlobject", "icu",
        "PySide.QtCore", "PySide.QtGui", "PySide.QtOpenGL", "multiprocessing.heap"
    ] + registered_plugins
    return inc

def get_package_modules():
    return [
        "encodings",
    ]

def get_scripts():
    if os.name == "posix":
        return [os.path.join("resources", "scripts", "moonstone")]
    return [os.path.join("resources", "scripts", "moonstone.bat")]

def get_data_files():
    data_files = []

    data_path_src = os.curdir
    data_path_dst = os.curdir
    data_files.append((data_path_src,
                       ["AUTHORS", "ChangeLog", "CONTRIBUTORS", "COPYING",
                        "FAQ", "INSTALL", "README", "THANKS", "TODO",]))

    data_path_src = os.path.join("resources")
    data_path_dst = os.path.join("resources")
    data_files.append((data_path_dst,
                      [os.path.join(data_path_src, "logging.conf"),]))
    data_files.append((data_path_dst,
                      [os.path.join(data_path_src, "moonstone.conf"),]))
    data_files.append((data_path_dst,
                      [os.path.join(data_path_src, "hounsfield.yaml"),]))

    data_path_src = os.path.join("resources")
    data_path_dst = os.path.join(os.path.expanduser("~"), config_dir,
                                 "resources")
    data_files.append((data_path_dst,
                      [os.path.join(data_path_src, "logging.conf"),]))

    data_path_src = os.path.join("resources", "log")
    data_path_dst = os.path.join("resources", "log")
    data_files.append((data_path_dst, []))

    data_path_src = os.path.join("resources", "log")
    data_path_dst = os.path.join(os.path.expanduser("~"), config_dir, "log")
    data_files.append((data_path_dst, []))

    data_path_src = os.path.join("moonstone", "ilsa", "resources")
    data_path_dst = os.path.join("resources", "ilsa")
    data_files.append((data_path_dst, [os.path.join(data_path_src, "plugin.conf"),]))

    data_path_src = os.path.join("moonstone", "ilsa", "resources")
    data_path_dst = os.path.join(os.path.expanduser("~"), config_dir,
                                 "resources", "ilsa")
    data_files.append((data_path_dst,
                      [os.path.join(data_path_src, "plugin.conf"),]))
    
    locale = os.path.join("resources", "locale")
    try:
        langs = [i for i in os.listdir(locale) \
                 if os.path.isdir(os.path.join(locale, i))]
    except OSError:
        langs = []
    for lang in langs:
        listFiles = []
        diretory = os.path.join("resources", "locale", lang, "LC_MESSAGES")
        mo = os.path.join("resources", "locale", lang,
                          "LC_MESSAGES", "moonstone.mo")
        if os.path.isfile(mo):
           listFiles.append(mo)
        qm = os.path.join("resources", "locale", lang,
                          "LC_MESSAGES", "moonstone.qm")
        if os.path.isfile(qm):
            listFiles.append(qm)
        data_files.append((diretory, listFiles))
    return data_files

def get_include_files():
    include_files = []

    data_path_src = os.curdir
    data_path_dst = os.curdir
    filelist = ["AUTHORS", "ChangeLog", "CONTRIBUTORS", "COPYING",
                "FAQ", "INSTALL", "README", "THANKS", "TODO",]
    for fl in filelist:
        include_files.append((os.path.join(data_path_src, fl),
                           os.path.join(data_path_dst, fl)))

    data_path_src = os.path.join("resources")
    data_path_dst = os.path.join("resources")
    filelist = ["logging.conf",]
    for fl in filelist:
        include_files.append((os.path.join(data_path_src, fl),
                           os.path.join(data_path_dst, fl)))

    data_path_src = os.path.join("resources", "log")
    data_path_dst = os.path.join("resources", "log")
    filelist = []
    for fl in filelist:
        include_files.append((os.path.join(data_path_src, fl),
                           os.path.join(data_path_dst, fl)))

    data_path_src = os.path.join("moonstone", "ilsa", "resources")
    data_path_dst = os.path.join("resources", "ilsa")
    filelist = ["plugin.conf"]
    for fl in filelist:
        include_files.append((os.path.join(data_path_src, fl),
                           os.path.join(data_path_dst, fl)))

    data_path_src = os.path.join("moonstone", "ilsa", "resources")
    data_path_dst = os.path.join("resources", "ilsa")
    filelist = ["plugin.conf"]
    for fl in filelist:
        include_files.append((os.path.join(data_path_src, fl), 
                           os.path.join(data_path_dst, fl)))


    locale = os.path.join("resources", "locale")
    try:
        langs = [i for i in os.listdir(locale) \
                 if os.path.isdir(os.path.join(locale, i))]
    except OSError:
        langs = []
    for lang in langs:
        listFiles = []
        data_path_src = os.path.join("resources", "locale", lang, "LC_MESSAGES")
        data_path_dst = os.path.join("resources", "locale", lang, "LC_MESSAGES")
        mo = os.path.join("resources", "locale", lang,
                          "LC_MESSAGES", "moonstone.mo")
        if os.path.isfile(mo):
           include_files.append((mo, mo))
        qm = os.path.join("resources", "locale", lang,
                          "LC_MESSAGES", "moonstone.qm")
        if os.path.isfile(qm):
            include_files.append((qm, qm))
    return include_files

def run():
    setup(name="Moonstone",
          version="0.4",
          url="http://www.moonstonemedical.org/",
          download_url="http://www.moonstonemedical.org/downloads/",
          license="GNU Lesser General Public License (LGPL)",
          description="""Moonstone is platform for processing of """
                      """medical images (DICOM).""",
          long_description=long_description,
          classifiers=classifiers,
          platforms=["Many"],
          packages=get_moonstone_packages(),
          scripts=get_scripts(),
          options={
            "py2exe": {
                "compressed": 1,
                "optimize": 2,
                "bundle_files": 3,
                "ascii": 1,
                "excludes": [
                    "pywin",
                    "pywin.debugger",
                    "pywin.debugger.dbgcon",
                    "pywin.dialogs",
                    "pywin.dialogs.list",
                ],
                "includes": get_include_modules(),
                "packages": get_package_modules(),
            },
            "build_exe": {
                "compressed": 1,
                "optimize": 2,
                "includes": get_include_modules(),
                "packages": get_package_modules(),
                "include_files": get_include_files(),
                "create_shared_zip": 1,
                "include_in_shared_zip": get_include_files(),
                "icon": os.path.join(os.curdir, "resources", "ui", "qt",
                                     "static", "default", "icon", "120x120",
                                     "moonstone.png"),
            },
            "py2app": {
                "compressed": 1,
                "optimize": 2,
                "argv_emulation": 0,
                "includes": get_include_modules() + get_moonstone_all_packages(),
                "packages": get_package_modules(),
                "resources": ["AUTHORS", "ChangeLog", "CONTRIBUTORS", "COPYING",
                              "FAQ", "INSTALL", "README", "THANKS", "TODO",],
                "iconfile": os.path.join(os.curdir, "resources", "ui", "qt",
                                         "static", "default", "icon",
                                         "macicons", "moonstone.icns"),
                "plist": {
                    "CFBundleName": "Moonstone",
                    "CFBundleShortVersionString": "0.4.0", # must be in X.X.X format
                    "CFBundleGetInfoString": "Moonstone 0.4",
                    "CFBundleExecutable": "Moonstone",
                    "CFBundleIdentifier": "org.moonstone.Moonstone",
                },
            },
          },
          zipfile=None,
          windows=[
            {
                "script": "moonstone.pyw",
                "icon_resources": [
                    (1, os.path.join(os.curdir, "resources", "ui", "qt",
                                     "static", "default", "icon", "winicons",
                                     "moonstone.ico"))
                ],
            },
          ],
          data_files=get_data_files(),
          executables=[
              Executable(
                 "moonstone.py",
                 copyDependentFiles=1,
                 icon=os.path.join(os.curdir, "resources", "ui", "qt",
                                   "static", "default", "icon", "120x120",
                                   "moonstone.png"),
              )
          ],
          app=["moonstone_macosx.py"],
          package_data={
            "py2app.apptemplate": [
                "prebuilt/main-i386",
                "prebuilt/main-ppc",
                "prebuilt/main-x86_64",
                "prebuilt/main-ppc64",
                "prebuilt/main-fat",
                "prebuilt/main-fat3",
                "prebuilt/main-intel",
                "prebuilt/main-universal",
                "lib/__error__.sh",
                "lib/site.py",
                "src/main.c",
            ],
            "py2app.bundletemplate": [
                "prebuilt/main-i386",
                "prebuilt/main-ppc",
                "prebuilt/main-x86_64",
                "prebuilt/main-ppc64",
                "prebuilt/main-fat",
                "prebuilt/main-fat3",
                "prebuilt/main-intel",
                "prebuilt/main-universal",
                "lib/__error__.sh",
                "lib/site.py",
                "src/main.m",
            ],
          },
          entry_points={
            "distutils.commands": [
                "py2app = py2app.build_app:py2app",
            ],
            "distutils.setup_keywords": [
                "app = py2app.build_app:validate_target",
                "plugin = py2app.build_app:validate_target",
            ],
            "console_scripts": [
                "py2applet = py2app.script_py2applet:main",
            ],
            "py2app.converter": [
                "xib          = py2app.converters.nibfile:convert_xib",
                "datamodel    = py2app.converters.coredata:convert_datamodel",
                "mappingmodel = py2app.converters.coredata:convert_mappingmodel",
            ],
            "py2app.recipe": [
            ]
          },
          setup_requires=setup_requires,
          **extra_args
    )
    
    if sys.platform == "win32":
        from platinfo import PlatInfo
        pi = PlatInfo()
        if pi.os == "win64":
            missingLibsDir = os.path.join(os.getcwd(),
                "resources",
                "packaging",
                "windows",
                "missing-libs64"
            )
        else:
            missingLibsDir = os.path.join(os.getcwd(),
                                 "resources",
                                 "packaging",
                                 "windows",
                                 "missing-libs"
                                 )
        for lib in os.listdir(missingLibsDir):
            shutil.copy2(os.path.join(missingLibsDir, lib),
                         os.path.join(os.getcwd(), "dist") )
        if os.path.exists(os.path.join(os.getcwd(), "dist", "tcl")):
            shutil.rmtree(os.path.join(os.getcwd(), "dist", "tcl"))
        if os.path.exists(os.path.join(os.getcwd(), "dist", "C:MinGW")):
            shutil.rmtree(os.path.join(os.getcwd(), "dist", "C:MinGW"))
        if os.path.exists(os.path.join(os.getcwd(), "dist", "C:mingw64")):
            shutil.rmtree(os.path.join(os.getcwd(), "dist", "C:mingw64"))
        if os.path.exists(os.path.join(os.getcwd(), "dist", "tk85.dll")):
            os.remove(os.path.join(os.getcwd(), "dist", "tk85.dll"))
        if os.path.exists(os.path.join(os.getcwd(), "dist", "tcl85.dll")):
            os.remove(os.path.join(os.getcwd(), "dist", "tcl85.dll"))            


# Commands:
# ./setup.py clean -a
# ./setup.py build
# ./setup.py py2exe
# ./setup.py install -c -O2
# ./setup.py sdist --formats=bztar, gztar, tar, zip, ztar
# ./setup.py bdist --formats=rpm, gztar, bztar, ztar, tar, wininst, zip
if __name__ == "__main__":
    run()
