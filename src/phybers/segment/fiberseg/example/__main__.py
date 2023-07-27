# -*- coding: utf-8 -*-
import os
from subprocess import run
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[0])

result_path = parent_path + "/result"

print("The result directory will be created in: " + result_path)
#Checking if the result directory exists. Else, the program won't run and an error while trying to run.

if os.path.exists(result_path):
    print("Target directory exists. Checking if executable file exists: ")
else:
    print("Target directory does not exist in path. Creating it: ")
    run(['mkdir', result_path])
    
    if os.path.exists(result_path):
        print("Target directory exists now. Checking if executable file exists: ")
    else: 
        print("Target directory still doesn't exist. Exiting...")
        exit()
        
# Checking if the main executable file exists. Else, the program compiles the .cpp file, so that it doesn't compile it everytime
# the main is run.       
if os.path.exists(pathname + "/../main"):
    print("Found executable file. Running segmentation executable file: ")
else:
    print("Executable file not found. Compiling main.cpp")
    run(['g++','-std=c++14','-O3', pathname + '/../main.cpp', '-o', pathname + '/../main', '-fopenmp', '-ffast-math'])
    if os.path.exists(pathname + "/../main"):
        print("main.cpp compiled. Running executable file: ")
    else: 
        print("Target directory still doesn't exist. Exiting")
        exit()

#Segmentation subprocess.run():

npoints = "21"
fibrasdir = pathname + "/../data/subjects/118225/118225.bundles"
idsubj =  "118225"
atlasdir = pathname + "/../data/atlas_flargas/bundles"
atlasIformation = pathname + "/../data/atlas_flargas/atlas_info.txt"
# Aquí se guardan los fascículos segmentados para el sujeto.
seg_resul = result_path + "/result"
# Aquí se guardan los índices  de las fibras originales para cada fascículo detectado.
id_seg_result = result_path + "/result"

run([ pathname + "/.././main", npoints, fibrasdir, idsubj, atlasdir, atlasIformation, seg_resul, id_seg_result])

