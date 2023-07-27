# cython: language_level=3, embedsignature=True
# distutils: language=c

cdef extern from "fiberDistanceMax2bun.h":
    cdef int main(int argc, char *argv[])

def intersection(dir_fib1="", dir_fib2="", outdir=""):
    cdef char * argv[4]
    args = (b'', dir_fib1.encode('utf8'), dir_fib2.encode('utf8'), outdir.encode('utf8'))
    for i, py_string in enumerate(args):
        argv[i] = <char *> py_string
    main(4, argv)
    return
