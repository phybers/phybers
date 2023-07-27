import sys
from .segment import fiberseg

if __name__ == "__main__":
    if len(sys.argv) == 6:
        fiber_input = sys.argv[1]
        idsubj = sys.argv[2]
        atlasdir = sys.argv[3]
        atlasInformation = sys.argv[4]
        result_path = sys.argv[5]
        fiberseg(fiber_input, idsubj, atlasdir, atlasInformation, result_path)
    else:
        print(fiberseg.__doc__)
