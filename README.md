# dist-super-compress

Script en python para la compresión de un archivo generando N partes.

# USO

Uso del comando super_zlib:
    super_zlib in_file out_path [otps]

    in_file: Path del archivo a comprimir.
    in_file: Directorio de salida.
    otps:    Opciones.

Opciones:
    -p, --parts Número de archivos a generar.
    -l, --level Nivel de compreción (de 0 a 9).
    -b, --bs    Número de bytes a procesar por lectura.


# Ejemplo.

Cramos un archivo de ejemplo de 4G.

```
$ dd if=/dev/urandom of=/tmp/ejemplo_file count=4096 bs=1M
4096+0 records in
4096+0 records out
4294967296 bytes (4.3 GB, 4.0 GiB) copied, 104.676 s, 41.0 MB/s
$ ls -lh /tmp/ejemplo_file
-rw-r--r-- 1 user user 4.0G Dec  8 18:40 /tmp/ejemplo_file
$ md5sum /tmp/ejemplo_file
cfc3e98d0d8a5f4d2bb21bf33292d83f  /tmp/ejemplo_file
```

Si no has descargado el srcipt:

```
$ git clone https://gitlab.com/rodriguezrjrr/dist-super-compress.git
$ cd dist-super-compress
```

Compresión  usando zlib en 2 partes:

```
$ ./super_zlib /tmp/ejemplo_file /tmp/ejemplo_zlib
$ ls /tmp/ejemplo_zlib
1 2
```

Para comprovar:

```
$ for num in {1..2}; do pigz -d -c /tmp/ejemplo_zlib/$num; done | md5sum -
cfc3e98d0d8a5f4d2bb21bf33292d83f  -
```

Compresión  usando zlib en 20 partes:

```
$ ./super_zlib /tmp/ejemplo_file /tmp/ejemplo_zlib_20 -p 20
```

Compresión  usando zlib en 20 partes nivel 9:

```
$ ./super_zlib /tmp/ejemplo_file /tmp/ejemplo_zlib_20_9 -p 20 -l 9
```

Compresión  usando bz2 en 2 partes:

```
$ ./super_bz2 /tmp/ejemplo_file /tmp/ejemplo_bz2
```

Para comprovar:

```
$ for num in {1..2}; do bzip2 -d -c /tmp/ejemplo_bz2/$num; done | md5sum -
cfc3e98d0d8a5f4d2bb21bf33292d83f  -
```

Compresión  usando bz2 en 30 partes:

```
$ ./super_bz2 /tmp/ejemplo_file /tmp/ejemplo_bz2_30 -p 30
```


