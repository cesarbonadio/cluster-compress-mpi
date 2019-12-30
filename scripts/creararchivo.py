f= open("archivosupergrande","w+")
for i in range(1000000):
     f.write('esta es la linea {0} del archivo super grande\n'.format(i))
f.close()
