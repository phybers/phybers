# cython: language_level=3, embedsignature=True
# distutils: language=c
import shutil
import os
from .bundleTools import write_bundle
from tempfile import mkdtemp
from collections.abc import Sequence

cdef extern from "segmentation.h":
    cdef int * segmentation(unsigned int n_points, char *subject_path, char *atlas_path, float threshold,
        char *output_directory, unsigned int nfibers_subject, unsigned int nfibers_atlas)

def seg(nPoints:int ,threshold:float , large_clusters_fibers: Sequence, small_clusters_fibers: Sequence , nfibers_subject: int, nfibers_atlas: int):
    cdef int * res
    cdef unsigned int n_small_clusters_fibers = len(small_clusters_fibers)

    #Create folders
    bundles_dir = mkdtemp()

    #Write file with the largest cluster's
    large_centroids_file = os.path.join(bundles_dir, "large_clusters.bundles")
    write_bundle(large_centroids_file, large_clusters_fibers)

    #Write file with the smallest cluster's
    small_centroids_file = os.path.join(bundles_dir, "small_clusters.bundles")
    write_bundle(small_centroids_file, small_clusters_fibers)

    ouputWorkDirectory = os.path.join(bundles_dir, 'result')

    py_byte_string_0 = small_centroids_file.encode('utf8')
    py_byte_string_1 = large_centroids_file.encode('utf8')
    py_byte_string_2 = ouputWorkDirectory.encode('utf8')

    res = segmentation(nPoints, <char *>py_byte_string_0, <char *>py_byte_string_1, threshold,
                       <char *>py_byte_string_2, nfibers_subject, nfibers_atlas)
    shutil.rmtree(bundles_dir)
    return <int[:n_small_clusters_fibers]>res

cdef extern from "sliceFibers.h":
    cdef int main(int argc, char *argv[])

def sliceFibers(fp_input: str, fp_output: str, point_count: int = 21):
    cdef char * argv[4]
    args = (b'', fp_input.encode('utf8'), fp_output.encode('utf8'), str(point_count).encode('utf8'))
    for i, py_string in enumerate(args):
        argv[i] = <char *> py_string
    main(4, argv)
    return
