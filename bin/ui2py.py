#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generates Python code from Qt interface and resources files.
# Copyright (C) 2009-2010 by Neppo Tecnologia da Informação LTDA
#
# This file is part of Moonstone.
#
# Moonstone is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
import fnmatch
import optparse

__version__ = 0.2


class Ui2Py(object):
    """Generates Python code from Qt interface and resources files

    Usage:
    >>> from ui2py import Ui2Py
    >>> ui2py = Ui2Py('/project/ui/main.ui', '/project/py_ui')
    >>> ui2py.generate()
    """
    PYUIC4 = "/usr/bin/pyuic4 -x -o {dst} {src}"
    PYRCC4 = "/usr/bin/pyrcc4 -name resources_rc -o {dst} {src}"
    PYSIDEUIC = "/usr/bin/pyside-uic -x -o {dst} {src}"
    PYSIDERCC4 = "/usr/bin/pyside-rcc -name resources_rc -o {dst} {src}"
    GENERATE = {0: (PYUIC4, PYRCC4), 1: (PYSIDEUIC, PYSIDERCC4)}
    DST = "widget"

    def __init__(self, src, dst=None, gnt=0):
        """Generates Python code from Qt interface and/or resources
        files or directories containing files Qt.

        Keyword arguments:
        src -- path of the file/directory from Qt interface/resources files
        dst -- target path, if null then the default path will be 'widget'
        gnt -- program generate the file (.py), if null then the default PySide
        """
        self.src = src
        self.dst = os.path.join(os.curdir, Ui2Py.DST) if dst is None else dst
        (self.uic, self.rcc) = Ui2Py.GENERATE.get(gnt)

    def __isfile(self, src):
        """Forehead, separates and returns the list of files"""
        if not os.access(src, os.R_OK):
            raise IOError("Can not access the file {0}".format(src))
        ui = []
        qrc = []
        if src.lower().endswith('.ui'):
            ui.append(src)
        elif src.lower().endswith('.qrc'):
            qrc.append(src)
        else:
            raise ValueError("Parameters can be a file")
        return {'ui': ui, 'qrc': qrc}

    def __isdir(self, src):
        """Forehead, separates and returns the list of files in directory"""
        if not os.access(src, os.X_OK):
            raise IOError("Can not access the directory {0}".format(src))
        ui = []
        for dirpath, dirnames, filenames in os.walk(src):
            for filename in fnmatch.filter(filenames, "*.ui"):
                fileui = os.path.join(dirpath, filename)
                if not os.access(fileui, os.R_OK):
                    raise IOError("Can not access the file {0}" \
                            .format(fileui))
                ui.append(fileui)
        qrc = []
        for dirpath, dirnames, filenames in os.walk(src):
            for filename in fnmatch.filter(filenames, "*.qrc"):
                fileqrc = os.path.join(dirpath, filename)
                if not os.access(fileqrc, os.R_OK):
                    raise IOError("Can not access the file {0}" \
                            .format(fileqrc))
                qrc.append(fileqrc)
        return {'ui': ui, 'qrc': qrc}

    def __ui(self, files):
        """Generates Python code from Qt interface"""
        choice = "y"
        for fl in files:
            py = fl.split(os.sep)[-1].replace(".ui", "_ui.py")
            dst = os.path.join(self.dst, py)
            sfl = os.path.split(fl)[-1]
            sdst = os.path.split(dst)[-1]
            if choice not in ("all", "none"):
                if os.path.exists(dst):
                    choice = raw_input("Want to replace this file {0}? " \
                        "[(y)es/(n)o/(c)ancel/(all)/(none)] ".format(sdst))
                    choice = choice.lower()
            if choice in ("c", "cancel"):
                break
            elif choice in ("n", "no", "none"):
                continue
            print " + generating {0} to {1}".format(sfl, sdst)
            exc = self.uic.format(src=fl, dst=dst)
            try:
                os.system(exc)
            except OSError, e:
                print "Failed to generate {0}".format(self.dst)

    def __qrc(self, files):
        """Generates Python code from Qt resource"""
        choice = "y"
        for fl in files:
            py = fl.split(os.sep)[-1].replace(".qrc", "_rc.py")
            dst = os.path.join(self.dst, py)
            sfl = os.path.split(fl)[-1]
            sdst = os.path.split(dst)[-1]
            if choice not in ("all", "none"):
                if os.path.exists(dst):
                    choice = raw_input("Want to replace this file {0}? " \
                        "[(y)es/(n)o/(c)ancel/(all)/(none)] ".format(sdst))
                    choice = choice.lower()
            if choice in ("c", "cancel"):
                break
            elif choice in ("n", "no", "none"):
                continue
            print " + generating {0} to {1}".format(sfl, sdst)
            exc = self.rcc.format(src=fl, dst=dst)
            try:
                os.system(exc)
            except OSError, e:
                print "Failed to generate {0}".format(self.dst)

    def getfiles(self):
        """It makes checking the files/directory and return a dictionary"""
        files = []
        if os.path.isfile(self.src):
            files = self.__isfile(self.src)
        elif os.path.isdir(self.src):
            files = self.__isdir(self.src)
        else:
            raise ValueError("Parameters can be a directory or a file")
        return files

    def generate(self):
        """Generates the code from the python files checked"""
        if not os.path.exists(self.dst):
            try:
                os.makedirs(self.dst)
            except IOError, e:
                raise IOError("Can not create the directory {0}" \
                        .format(self.dst))
        if os.path.isdir(self.dst):
            if not os.access(self.dst, os.W_OK):
                raise IOError("Can not access the directory {0}" \
                        .format(self.dst))
            files = self.getfiles()
            _Strategy(self.__ui, 'ui').action(files['ui'])
            _Strategy(self.__qrc, 'qrc').action(files['qrc'])
        else:
            raise IOError("Invalid directory {0}".format(self.dst))


class _Strategy(object):
    """Implements the strategy design pattern"""
    def __init__(self, action, label):
        self.action = action
        self.label = label


def main(args):
    """Run the class Ui2Py arguments from the command line"""
    parser = optparse.OptionParser(
        usage="Usage: %prog [options] <ui-file|directory> <directory>",
        version="%prog {0}".format(__version__))
    parser.add_option("-0", "--pyuic4", 
                      action="store_const", dest="generate", const=0, default=0, 
                      help="Generates the file (.py) through pyuic4 [default]")
    parser.add_option("-1", "--pyside-uic", 
                      action="store_const", dest="generate", const=1,
                      help="Generates the file (.py) through pyside-uic")
    parser.add_option("-d", "--default",
                      action="store_true", dest="default", default=True,
                      help="Loading default configure")
    parser.add_option("-p", "--plugin",
                      action="store", dest="plugin", 
                      help="Generates the file (.py) is plugin")
    (options, args) = parser.parse_args()
    if not args:
        if options.plugin:
            plugin = options.plugin
            os.path.join(os.path.abspath(os.pardir))
            plugindir = os.path.join(os.path.abspath(os.pardir), "src", 
                                     "moonstone", "ilsa", "plugins", plugin) 
            if not os.path.isdir(plugindir):
                parser.error("Plugin {0} not exists".format(plugin))            
            src = os.path.abspath(os.path.join(plugindir, "resources", "ui", "qt"))
            dst = os.path.abspath(os.path.join(plugindir, "gui", "qt", "widget"))
            args.insert(1, src)
            args.insert(2, dst)
        elif options.default:
            src = os.path.join(os.path.abspath(os.pardir), "src", "resources",
                               "ui", "qt")
            dst = os.path.join(os.path.abspath(os.pardir), "src", "moonstone",
                               "gui", "qt", "widget")
            args.insert(1, src)
            args.insert(2, dst)
        else:
            parser.error("Invalid parameter")
    elif len(args) > 2:
        parser.error("Invalid parameter")
    ui2py = Ui2Py(*args, gnt=options.generate)
    ui2py.generate()


if __name__ == "__main__":
    main(sys.argv)
