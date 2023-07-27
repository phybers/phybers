# cython: language_level=3, embedsignature=True
# distutils: language=c++

cdef extern from "dbindex.hpp":
    cdef int main(int argc, char *argv[])

def postprocessing(in_centroides, in_clusters_directory, output_path, points):
    cdef char * argv[4]
    args = (b'', in_centroides.encode('utf8'),in_clusters_directory.encode('utf8'), output_path.encode('utf8'), str(points).encode('utf8'))
    for i, py_string in enumerate(args):
        argv[i] = <char *> py_string
    cdef int res = main(5, argv)
    print(f"Finalizo main, ouput: {res}")
    return res
