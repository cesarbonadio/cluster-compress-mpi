#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 Rómulo Rodríguez <rodriguezrjrr@gmail.com>

This file is part of super-compress.

super-compress is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

super-compress is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""

import bz2
import getopt
import os
import sys
import zlib
import subprocess
from mpi4py import MPI


class SuperCompressAbs(object):
    """
    implementación Abstracta de interfaz de compresión.
    """

    options = ''
    """
    Opciones extras en formato corto de getopt.
    """

    long_options = []
    """
    Lista de opciones extras en formato largo de getopt.
    """

    def __init__(self, in_file, out_path, **kwargs):
        self._in_file = in_file
        self._out_path = out_path
        self._parts = int(kwargs.get('-p', kwargs.get('--parts', '2')))
        self._bty = int(kwargs.get('-b', kwargs.get('--bs', '4096')))
        self._file_hs = {}
        self._file_o = {}
        self._in_file_size = os.path.getsize(self._in_file)
        self._size_of_part = int(self.in_file_size / self.parts)

    @property
    def in_file(self):
        return self._in_file

    @property
    def bytes_pre_read(self):
        return self._bty

    @property
    def in_file_size(self):
        return self._in_file_size

    @property
    def out_path(self):
        return self._out_path

    @property
    def parts(self):
        return self._parts

    @property
    def size_of_part(self):
        return self._size_of_part

    def open_in_file(self, part):
        """
        Apertura del archivo en una parte específica.

        :params part: Número de partes.
        """
        if part in self._file_hs and self._file_hs[part] is not None:
            return
        fileh = open(self.in_file, 'rb')
        offset = self.size_of_part * (part - 1)
        fileh.seek(offset)
        self._file_hs[part] = fileh

    def close_in_file(self, part):
        """
        Cierre del archivo en una parte específica.

        :params part: Número de parte de archivo.
        """
        self._file_hs[part].close()
        self._file_hs[part] = None

    def read_in_file(self, part, byt):
        """
        Lectura de una parte del archivo.

        :params part: Número de parte de archivo.
        :params byt: Cantidad máxima de bytes a leer.

        :returns: bytes leidos de la parte del archivo.
        """
        return self._file_hs[part].read(byt)

    def open_out_file(self, part):
        """
        Apertura de escritura de una parte.

        :params part: Número de parte.
        """
        if part in self._file_o and self._file_o[part] is not None:
            return
        base_path = os.path.abspath(self.out_path)
        if not os.path.exists(base_path):
            try:
                os.mkdir(base_path)
            except:
                pass
        path = os.path.join(os.path.abspath(self.out_path), str(part))
        fileh = open(path, 'wb')
        self._file_o[part] = fileh

    def close_out_file(self, part):
        """
        Cierre de escritura de una parte.

        :params part: Número de parte.
        """
        self._file_o[part].close()
        self._file_o[part] = None

    def write_out_file(self,part, data):
        """
        Escritura de una parte.

        :params part: Número de parte.
        :params data: Datos a escribir.
        """
        self._file_o[part].write(data)

    def run(self):
        """
        implementación del compresor
        """
        raise Exception("Requerida la implementación de este Método.")


class SuperCompressObjCompressor(SuperCompressAbs):
    """
    Implementación que hace uso de objetos compresores.
    """

    options = 'l:'
    long_options = ["level="]
    compressor_class = None
    """
    Clase o función que genera el objeto compresor
    """
    default_lavel = None
    """
    Nivel por defecto de compresión
    """

    def __init__(self, in_file, out_path, **kwargs):
        self._level = int(kwargs.get('-l', kwargs.get('--level',
                                                      self.default_lavel)))
        if self._level > 9 or self._level < 0:
            raise Exception('El valor de level deve de estar entre 0 y 9')
        super(SuperCompressObjCompressor, self).__init__(in_file,
                                                         out_path,
                                                         **kwargs)
    @property
    def level(self):
        return self._level

    def make_compressor(self):
        """
        Generación de un objeto compresor.
        """
        if self.compressor_class is None:
            raise Excpetion("Es requerida la definición de compressor_class")
        return self.compressor_class(self.level)

    def run(self):
        comm = MPI.COMM_WORLD
        req = MPI.Request
        n_procs = comm.Get_size()
        my_rank = comm.Get_rank()

        if my_rank + 1  > self.parts:
            return 0

        for c_part in range(self.parts):
            part = c_part
            while part > n_procs - 1:
                part = part - n_procs
            if my_rank == part:
                print(my_rank,part)
                self._compress_part(c_part + 1)
        return 0

    def _compress_part(self, part):
        """
        Para comprimir cada parte.
        """
        compressor = self.make_compressor()
        self.open_in_file(part)
        self.open_out_file(part)
        bty_count = 0
        is_last_part = part == self.parts
        while bty_count < self.size_of_part:
            byt_req = self.bytes_pre_read
            if not is_last_part and bty_count + byt_req >= self.size_of_part:
                byt_req = self.size_of_part - bty_count
            part_data = self.read_in_file(part, byt_req)
            data_size = len(part_data)
            bty_count += data_size
            c_data = compressor.compress(part_data)
            self.write_out_file(part, c_data)
        remain = compressor.flush()
        self.write_out_file(part, remain)
        self.close_out_file(part)
        self.close_in_file(part)


class SuperCompressZlib(SuperCompressObjCompressor):
    """
    Imprementación que usa zlib
    """

    compressor_class = zlib.compressobj
    default_lavel = '6'


class SuperCompressBz2(SuperCompressObjCompressor):
    """
    Imprementación que usa bz2
    """

    compressor_class = bz2.BZ2Compressor
    default_lavel = '9'


class SuperCompress:
    """
    Implementación de metodos de control del programa principal
    """

    _cls_progrmas = {
        'super_zlib': SuperCompressZlib,
        'super_bz2': SuperCompressBz2
    }
    """
    Mapeo de implementaciones.
    """

    @classmethod
    def create(cls, *args):
        """
        Entrada principal
        """
        args_list = list(args)
        #print('lista de argumentos: {0}'.format(args_list[0]))
        program_name = os.path.basename(args_list.pop(0))
        if '-h' in args_list or '--help' in args_list:
            cls.usage(program_name)
            return 0
        if len(args_list) < 2:
            cls.usage(program_name)
            return 10
        in_file = args_list.pop(0)
        out_path = args_list.pop(0)

        try:
            cls_program = cls.get_cls_program(program_name)
            cls.verify_in_file(in_file)
        except Exception as exce:
            print('Error entrada: %s' % exce)
            return 11

        return cls.run(cls_program, in_file, out_path, args_list)

    @classmethod
    def get_cls_program(cls, program_name):
        """
        Obtiene la implementación correspondiente al mapeo.
        """
        if program_name not in cls._cls_progrmas:
            raise Exception('Programa %s no implementado' % program_name)
        return cls._cls_progrmas[program_name]

    @classmethod
    def usage(cls, name):
        """
        """
        print("Uso del comando %s:" % name)
        print("    %s in_file out_path [otps]" % name)
        print("")
        print("    in_file: Path del archivo a comprimir.")
        print("    in_file: Directorio de salida.")
        print("    otps:    Opciones.")
        print("")
        print("Opciones:")
        print("    -p, --parts Número de archivos a generar.")
        print("    -l, --level Nivel de compreción.")
        print("    -l, --level Nivel de compreción.")
        print("    -b, --bs    Número de bytes a procesar por lectura.")
        print("")


    @classmethod
    def verify_in_file(cls, in_file):
        """
        Verificación de existencia de archiv de entrada
        """
        assert os.path.isfile(in_file) and os.access(in_file, os.R_OK), \
            "Archivo %s no existe o no se puede leer" % in_file

    @classmethod
    def run(cls, cls_program, in_file, out_path, args_list):
        """
        Crea y corre la implementacion del compresor.
        """
        options = 'b:p:' + cls_program.options
        long_options = cls_program.long_options
        long_options.append('parts=')
        long_options.append('bs=')
        opts, args = getopt.getopt(args_list, options, long_options)
        kwargs = dict(opts)
        try:
            program = cls_program(in_file, out_path, **kwargs)
            return program.run()
        except Exception as exce:
            pass
	    #print('Error de programa: %s' % exce)
            #return 12
		


if __name__ == '__main__':
    args = sys.argv
    sys.exit(SuperCompress.create(*args))
