##
# @mainpage Hierarchical Clustering module
# @brief Brief HClust description.
# Descripción de HClust.
# \tableofcontents
# @subsection description_main How to run
# The hclust module is executed by running the following on console:
#
# > ```python3 -m hclust <dir_raw_tractography> <MaxDistance_Threshold> <maxdist> <var> <result_path>```
# Donde la definición de cada argumento se puede encontrar en el siguiente enlace: \ref hclust.main
# Where each argument's definition can be found in the following link: \ref hclust.main
#
#

import sys
from .mainHClust import hclust

if __name__ == "__main__":
    ## Path to the .bundles file that corresponds to the raw tractography.
    ## Ruta al archivo .bundles que corresponde a la tractografía.
    dir_raw_tractography = sys.argv[1]  # input format: ".bundles"

    ## Output directory path.
    ## Ruta del directorio de salida.
    result_path = sys.argv[2]

    #MaxDistance_Threshold="40" # variable threshold
    ## Maximum threshold of euclidian distance between pairs of fibers. 40 is recommended.
    ## Máximo umbral de distancia euclidiana entre pares de fibras. Se recomienda 40.
    MaxDistance_Threshold = int(sys.argv[3])  # variable threshold

    ## Maximum threshold of affinity, 30 is recommended.
    ## Máximo umbral de afinidad, se recomienda 30.
    maxdist = int(sys.argv[4])  # define usuario, se recomienda 30?

    ## Value related with the scale of similarity used. 3600 is recommended.
    ## Valor relacionado con la escala de similitud utilizada. Se recomienda 3600.
    var = int(sys.argv[5])  # define usuario, pero se recomienda usar 3600.


    hclust(dir_raw_tractography, result_path, MaxDistance_Threshold, maxdist, var)
