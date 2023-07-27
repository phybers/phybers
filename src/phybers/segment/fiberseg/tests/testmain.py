## @package segmentation
# Documentation for the segmentation __main__.py file.
#
# @mainpage Segmentation module
# @brief Fibers segmentation based on a multi-subject atlas. It's purpose is clasifying subject fibers in function of a multisubject-fascicle atlas.
# \tableofcontents
# @section description_main How to run
# You can run the segmentation module by typing the following on console:
#
# ```python3 -m segmentation <npoints> <fibrasdir> <idsubj> <atlasdir> <atlasInformation> <result_path>```
#

# Imports
import sys
import os
from subprocess import run
from pathlib import Path

print(len(locals()))
pathname = os.path.dirname(__file__)


#Global Constants
## Number of points.
npoints = sys.argv[1]
## Fibers .bundles path.
fibrasdir = sys.argv[2]
## Subject ID.
idsubj = sys.argv[3]
## Atlas directory path.
atlasdir = sys.argv[4]
## Atlas info file.
atlasInformation = sys.argv[5]
## Output directory path for the segmentated fascicles for the subject.
result_path = sys.argv[6]

aux = str(Path(result_path).parents[0])

if os.path.exists(result_path):
    print("Target directory exists.")
else:
    print("Target directory does not exist in path. Creating it: ")
    run(['mkdir', aux + '/result'])
    
    if os.path.exists(result_path):
        print("Target directory has been created successfully.")

    else: 
        print("Target directory still doesn't exist. Exiting...")
        exit()

seg_resul = result_path + "/seg_bundles"
run(['mkdir', seg_resul])
id_seg_result = result_path + "/id_txt_seg"
run(['mkdir', id_seg_result])


## Output directory path for the index of the original fibers for each detected fascicle.

#Functions
 
if os.path.exists(pathname + "/main"):
    print("Found executable file. Running segmentation executable file: ")
else:
    print("Executable file not found. Compiling main.cpp")
    run(['g++','-std=c++14','-O3', pathname + '/main.cpp', '-o', pathname + '/main', '-fopenmp', '-ffast-math'])
    if os.path.exists(pathname + "/main"):
        print("main.cpp compiled. Running executable file: ")
    else: 
        print("Executable file still not found. Exiting")
        exit()



run([pathname + "/./main", npoints, fibrasdir, idsubj, atlasdir, atlasInformation, seg_resul, id_seg_result])

