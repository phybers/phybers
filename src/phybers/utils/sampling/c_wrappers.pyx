# cython: language_level=3, embedsignature=True
# distutils: language=c

cdef extern from "sliceFibers.h":
    cdef int main(char* fp_input, char* fp_output, int point_count)

def sliceFibers(fp_input: str, fp_output: str, point_count: int = 21):
    fp_input_c = fp_input.encode('utf8')
    fp_output_c = fp_output.encode('utf8')
    main(<char *>fp_input_c, <char *>fp_output_c, point_count)
    return
