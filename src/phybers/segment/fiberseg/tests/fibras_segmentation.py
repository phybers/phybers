"""! @brief Testing"""
##
# @mainpage Fibers segmentation wrapper
#
# @section description_main Description
# An example of the segmentation code for fibers.
#
# @brief Example Python program with Doxygen style comments.
#
#Imports
from subprocess import run
#Global Constants
## Number of points.
npoints = "21"
## Fibers .bundles path.
fibrasdir = "../../data/subjects/118225/118225.bundles"
## Subject ID.
idsubj =  "118225"
## Atlas directory path.
atlasdir="../../data/atlas_flargas/bundles"
## Atlas info file.
atlasIformation = "../../data/atlas_flargas/atlas_info.txt"
## Output directory path for the segmentated fascicles for the subject.
seg_resul = "../../result/seg_result" # Aquí se guardan los fascículos segmentados para el sujeto.
## Output directory path for the index of the original fibers for each detected fascicle.
id_seg_result = "../../result/idseg_result" # Aquí se guardan los índices  de las fibras originales para cada fascículo detectado.

run(["./main", npoints, fibrasdir, idsubj, atlasdir, atlasIformation, seg_resul, id_seg_result])

