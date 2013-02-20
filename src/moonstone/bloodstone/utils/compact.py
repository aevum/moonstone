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

import zipfile, os
import threading


from Crypto.Cipher import AES
import struct, tempfile, random
from data import load_vtis_from_yaml_file

class Zipper():
    key = "6140e766dc2020bb995c62d40d6f12a8"
    originalKey = "6140e766dc2020bb995c62d40d6f12a8"
    def __init__(self):
        self._lock = threading.Lock() 

    def start(self, outputFile):
        try :
            self._lock.acquire()
            self._outputFile = outputFile 
            self._zipf = zipfile.ZipFile(outputFile, "w", compression=zipfile.ZIP_DEFLATED )
            self._canceled = False
        finally:
            self._lock.release()
        
    def finish(self):
        self._zipf.close()
        
    def cancel(self):
        try :
            self._lock.acquire()
            self._canceled = True
            self._zipf.close()
            self._zipf = None
            os.remove(self._outputFile)
        finally:
            self._lock.release()
         
    def recursive_zip(self, file, root=None):
        if not root:
            root = os.path.basename(file)
        if os.path.isfile(file):
            try :
                self._lock.acquire()
                if self._canceled:
                    return False
                self._zipf.write(os.path.join(file), root)
            finally:
                self._lock.release()
        
        elif os.path.isdir(file):
            for next in os.listdir(file):
                realpath = os.path.join(file, next)
                arcpath = os.path.join(root, next)
                if not self.recursive_zip(realpath, arcpath):
                    return False
        return True
     
    
     
def encryptFile(input_path, key):
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(input_path)
    chunksize= 1024
    out_file = tempfile.NamedTemporaryFile(delete=False)

    with open(input_path, 'rb') as infile:
        with open(out_file.name, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))
    return out_file.name

def decryptFile(in_filename, key):
    try:
        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            chunksize= 1024
            decryptor = AES.new(key, AES.MODE_CBC, iv)
            out_filename = tempfile.NamedTemporaryFile(delete=False)
            with open(out_filename.name, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))
        
                outfile.truncate(origsize)
                
        load_vtis_from_yaml_file(out_filename.name)
        return out_filename.name
    except:
        return ""

