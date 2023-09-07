# cython: language_level=3, embedsignature=True
# distutils: language=c++

cdef extern from "distances.hpp":
    cdef int fDM_main(char *fp_input, char *fp_output)
    cdef int gAGFDM_main(char *fp_input, char *fp_output, float maxdist) except +
    cdef int gALHCFGF_main(char * fp_input, char * fp_output)

def fiberDistanceMax(fp_input: str, fp_output: str):
    fp_input_c = fp_input.encode('utf8')
    fp_output_c = fp_output.encode('utf8')
    fDM_main(<char *>fp_input_c, <char *>fp_output_c)
    return

def getAffinityGraphFromDistanceMatrix(fp_input: str, fp_output: str, max_distance: float):
    fp_input_c = fp_input.encode('utf8')
    fp_output_c = fp_output.encode('utf8')
    gAGFDM_main(<char *>fp_input_c, <char *>fp_output_c, max_distance)
    return

def getAverageLinkHCFromGraphFile(fp_input: str, fp_output: str):
    fp_input_c = fp_input.encode('utf8')
    fp_output_c = fp_output.encode('utf8')
    if gALHCFGF_main(<char *>fp_input_c, <char *>fp_output_c):
        raise OSError("Error reading file.")
    return
