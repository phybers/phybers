# cython: language_level=3, embedsignature=True
# distutils: language=c++

from shutil import rmtree
from os.path import exists
from libcpp.string cimport string

cdef extern from "main.hpp":
    cdef int main_segmentation(unsigned short n_points, string subject_path, string subject_name,
                               string atlas_path, string atlas_inf, string output_dir, string indices_output_dir) except +

def segment(unsigned short n_points, fibers, idsubj, atlasdir, atlasInformation, final_bundles_dir, id_seg_result):
    cdef char * argv[6]
    args = (fibers.encode('utf8'), idsubj.encode('utf8'),
            atlasdir.encode('utf8'), atlasInformation.encode('utf8'),
            final_bundles_dir.encode('utf8'), id_seg_result.encode('utf8'))
    for i, py_string in enumerate(args):
        argv[i] = <char *> py_string
    if exists(final_bundles_dir):
        rmtree(final_bundles_dir)
    main_segmentation(n_points, argv[0], argv[1], argv[2], argv[3], argv[4], argv[5])
    return
