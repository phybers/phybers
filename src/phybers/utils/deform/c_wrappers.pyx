# cython: language_level=3, embedsignature=True
# distutils: language=c

cdef extern from "main.h":
    cdef int main(int argc, char *argv[])

def deform(imgdef="", infile="", outfile=""):
    cdef char * argv[4]
    args = (b'', imgdef.encode('utf8'), infile.encode('utf8'), outfile.encode('utf8'))
    for i, py_string in enumerate(args):
        argv[i] = <char *> py_string
    main(4, argv)
    return
