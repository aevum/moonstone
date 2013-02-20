#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generates template file internationalization Qt interface.
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
from optparse import OptionParser

__version__ = 0.1


class UpdateTsFile(object):
    """Generates template file internationalization Qt interface

    Usage:
    >>> from update_ts_file import UpdateTsFile
    >>> utf = UpdateTsFile('/project/src', '/project/locale')
    >>> utf.update()
    """
    _tsname = "moonstone.ts"
    _pylupdate4 = "/usr/bin/pylupdate4 {infiles} -ts {tsfile}"
    _src = os.path.join(os.pardir, "src", "moonstone")
    _dst = os.path.join(os.pardir, "src", "resources", "locale")

    def __init__(self, src=None, dst=None):
        """Generates template file internationalization Qt interface

        Keyword arguments:
        src -- path of the file/directory from code Python
        dst -- target path, if null then the default path will be `_dst`
        """
        self.src = self._src if src is None else src
        self.dst = self._dst if dst is None else dst

    def __isfile(self, src):
        """Forehead, separates and returns the list of files"""
        if not os.access(src, os.R_OK):
            raise IOError("Can not access the file {0}".format(src))
        filepy = []
        if src.lower().endswith('.py'):
            filepy.append(src)
        else:
            raise ValueError("Parameters can be a file")
        return {'py': filepy}

    def __isdir(self, src):
        """Forehead, separates and returns the list of files in directory"""
        if not os.access(src, os.X_OK):
            raise IOError("Can not access the directory {0}".format(src))
        filepy = []
        for dirpath, dirnames, filenames in os.walk(src):
            for filename in fnmatch.filter(filenames, "*.py"):
                filepy.append(os.path.join(dirpath, filename))
        return {'py': filepy}

    def __ts(self, files):
        """Generate template file internationalization Qt interface"""
        choice = "y"
        dst = os.path.join(self.dst, self._tsname)
        if os.path.exists(dst):
            choice = raw_input("Want to replace this file {0}? " \
                "[(y)es,(n)o/(c)ancel] ".format(dst))
            choice = choice.lower()
        if choice in ("n", "no", "c", "cancel"):
            return
        print " + generating {0} to {1}".format(self.src, dst)
        infiles = ' '.join(files['py'])
        exc = self._pylupdate4.format(infiles=infiles, tsfile=dst)
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

    def update(self):
        """creates or updates the model of internationalization from
        Python code.
        """
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
            self.__ts(files)
        else:
            raise IOError("Invalid directory {0}".format(self.dst))


def main(sysargs):
    """Run the class UpdateTsFile arguments from the command line"""
    usage = "Usage: %prog [options] [file | directory] [directory]"
    parse = OptionParser(usage=usage, version="%prog {0}".format(__version__))
    parse.add_option("-t", "--template", dest="template", action="store_true",
            help="generates and update template file (.ts) [default]")
    options, args = parse.parse_args(sysargs)
    if options.template:
        utf = UpdateTsFile(*args[1:3])
        utf.update()
    else:
        parse.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
