"""The utils subpackage is a compendium of tools used for both the pre-processing of a tractography as well as for evaluating the performance of the clustering and the segmentation. It includes 4 modules:
    1) deform
    2) sampling
    3) intersection
    4) postprocessing
"""
import os
import numpy as N
import pandas as pd
from typing import Tuple
from pathlib import Path
from . import FibersTools as fb
from .deform import deform as _deform
from .sampling import slice_fibers as _sampling
from .intersection import intersection as _intersection
from .postprocessing import postprocessing as _postprocessing


def check_input_path(in_file: str, ext="", dir=False):
    p = Path(in_file)
    if ext and ('.' not in p.name or p.name.rsplit('.', maxsplit=1)[1] != ext):
        raise ValueError(f"File {p.name} must have extension {ext}.")
    if dir and not p.is_dir():
        raise ValueError(f"Path {p} is not a directory.")
    if not p.exists():
        if dir:
            raise FileNotFoundError(f"Directory {p} not found.")
        else:
            raise FileNotFoundError(f"File {p} not found.")

def check_output_path(out_file: str, ext="", dir=False, overwrite=True):
    p = Path(out_file)
    if ext and ('.' not in p.name or p.name.rsplit('.', maxsplit=1)[1] != ext):
        raise ValueError(f"File {p.name} must have extension {ext}.")
    if dir:
        if p.exists():
            if not p.is_dir():
                raise ValueError(f"Path exist {p} but is not a directory.")
        else:
            os.makedirs(str(p))
    else:
        if p.exists() and not overwrite:
            raise ValueError(f"File {p} already exist and will not be deleted.")
        if not p.parent.exists():
            os.makedirs(str(p.parent))



def deform(deform_file: str, file_in: str, file_out: str):
    """! Transforms a tractography file to another space using a non-linear deformation file. The inputs for the deform function are:

        <ol>
            <li>**deform_file**: Deformation image. Has to be a .nii file.</li>
            <li>**indir**: Fiber input file.</li>
            <li>**outdir**: Result directory path.</li>
        </ol>
    """
    check_input_path(deform_file, ext='nii')
    check_input_path(file_in)
    check_output_path(file_out, ext='bundles')
    _deform(deform_file, file_in, file_out)


def sampling(dir_in: str, file_out: str, npoints: int = 21) -> None:
    """! Fiber sampling at n equidistant points. The inputs for the sampling function are:
        <ol>
            <li>**dir_in**: Fiber input file</li>
            <li>**npoints**: Number of points</li>
            <li>**file_out**: Result directory path.</li>
        </ol>
    """
    check_input_path(dir_in, ext="bundles")
    check_output_path(file_out, ext="bundles")
    _sampling(dir_in, file_out, npoints)


def inter2bundles(file1_in: str, file2_in: str, dir_out: str, distance_thr: float=10.0) -> Tuple[float, float]:
    """! computes the intersection percentage between two fiber bundles.. The inputs for the intersection function are:
        <ol>
            <li>**file1_in**: First fiber bundle file ".bundles".</li>
            <li>**file2_in**: Second fiber bundle file ".bundles".</li>
            <li>**dir_out**: Result directory path.</li>
            <li>**distance_thr**: TH_Dmax[mm]</li>
        </ol>
    """

    labelsb1 = os.path.split(file1_in)[1] #m - rows
    labelsb2= os.path.split(file2_in)[1]  #num - columns


    p1=0
    p2=0

    str_out = labelsb1.split('.')[0]+'-'+labelsb2.split('.')[0]


    outfile=os.path.join(dir_out,str_out+'.txt')

    #computes the distance matrix between two fiber bundles.
    _intersection(file1_in, file2_in, outfile)

    ar=open(outfile,'rt')
    t=ar.readlines();ar.close()
    m=len(t)
    n=len(t[0].split('\t')[:-1])

    M = N.zeros((m,n),dtype = 'float32')

    for i in range(m):
        fila=t[i][:-1].split('\t')[:-1]
        for j in range(n):
            M[i,j]=float(fila[j])

    F_under_th=N.where( M < distance_thr) # fibers with at least 1 other fiber has distance under the threshold
    xp1=list(set(F_under_th[0]))
    yp2=list(set(F_under_th[1]))

    p1=(len(xp1)/fb.getBundleSize(file1_in))*100 #fiber bundle 1 intersection percentage
    p2=(len(yp2)/fb.getBundleSize(file2_in))*100 #fiber bundle 2 intersection percentage

    return (p1,p2)


def postprocessing(dir_in: str) -> pd.DataFrame:
    ##THIS IS THE DOC WAAAA
    #
    """! Contains a set of algorithms that are applied on the results of clustering and segmentation algorithms.
        1) Fibers Lens (se calcula para el centroide del clúster)
        2) Fibers Size ( cantidad de fibras por clúster)
        3) Distancia intra-clúster mínima,  Distancia intra promedio y  Distancia intra máxima
        4) Rij
        5) DBindex

        <ol>
            <li>**dir_in**: Flies directory path.</li>
        </ol>
    """

    in_centroides=os.path.join(dir_in,'FinalCentroids','centroids.bundles')
    in_clusters_directory=os.path.join(dir_in,'FinalBundles')

    stadisticsFolder =  os.path.join(dir_in, 'stadistics')

    if not os.path.exists(dir_in):
        os.makedirs(dir_in)

    if not os.path.exists(stadisticsFolder):
        os.makedirs(stadisticsFolder)

    # Fibers Lens and Fibers Size
    txt_lens = ''
    txt_sizes = ''

#    stadisticsFolder =  os.path.join(dir_in, "stadistics")
    print(stadisticsFolder)

    if not os.path.exists(dir_in):
        os.makedirs(dir_in)
    if not os.path.exists(dir_in):
        os.makedirs(dir_in)
    centroides=fb.read_bundle(in_centroides)
    for i in range(len(centroides)):
        txt_lens += str(fb.fiber_lens(centroides[i]))+"\n"
        txt_sizes += str(fb.getBundleSize(in_clusters_directory+'/'+str(i)+".bundles"))+"\n"

    with open(os.path.join(stadisticsFolder, 'lens.txt'), 'w') as file:
        file.write(txt_lens)

    with open(os.path.join(stadisticsFolder, 'sizes.txt'), 'w') as file:
        file.write(txt_sizes)

    # - Distancia intra-clúster mínima, Distancia intra promedio, Rij y DBindex

    _postprocessing(in_centroides, in_clusters_directory,
                    os.path.join(stadisticsFolder, 'mensure'), 21)

    # Dataframe
    fb.Stadistics_txt_toxlsx(stadisticsFolder)

    return pd.read_excel(stadisticsFolder+'/stadistics.xlsx')