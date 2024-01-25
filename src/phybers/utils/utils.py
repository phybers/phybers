# -*- coding: utf-8 -*-
"""Utils Module
"""
import os
import re
from shutil import rmtree
from typing import Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from .fiberstools import getBundleSize, fiber_lens, mesures_to_dataframe
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
        if p.is_dir():
            rmtree(str(p))
        if not p.parent.exists():
            os.makedirs(str(p.parent))


_p1 = re.compile(r'^.*\.bundles$')


def read_bundle(file_in: str, points: int = 0) -> list:
    """
    Read tractography in bundles format.

    Parameters
    ----------
    file_in : str
        Path to read of the tractography dataset file in *bundles* format.

    Returns
    -------
    List where each position contains a NumPy array representing the 3D coordinates of a brain fiber.

    """
    if _p1.match(file_in):
        file_in += 'data'
    with open(file_in, 'rb') as f:
        data = np.fromfile(f, dtype=np.float32)
    if points > 0:
        return data.reshape(-1, points * 3 + 1)[:, 1:].reshape(-1, points, 3)
    else:
        start = 0
        fibers = []
        size = data.size
        u32_data = data.view(np.uint32)
        while start < size:
            f_size = u32_data[start] * 3
            start += 1
            end = start + f_size
            fibers.append(data[start:end].reshape(-1, 3))
            start = end
        return fibers


_MINF_TEMPLATE = """attributes = {{
    'binary' : 1,
    'bundles' : {},
    'byte_order' : 'DCBA',
    'curves_count' : {},
    'data_file_name' : '*.bundlesdata',
    'format' : 'bundles_1.0',
    'space_dimension' : 3
}}
"""


def write_bundle(file_out: str, points: list, buffer_size= 1_048_576)  -> None:
    """
    Write tractography in *bundles* format.

    Parameters
    ----------
    file_out : str
        Path to save of the tractography dataset file in *bundles* format.
    points : list
        List where each position contains a NumPy array representing the 3D coordinates of a brain fibers.

    Returns
    -------
    None

    """
    if not _p1.match(file_out):
        file_out += '.bundles'
    if isinstance(points, np.ndarray) and points.ndim == 3:
        nfibers, npoints, _ = points.shape
        data = np.empty((nfibers, npoints * 3 + 1), np.float32)
        data.view(np.uint32)[:, 0] = npoints
        data[:, 1:] = points.reshape(-1, npoints * 3)
        with open(file_out + 'data', 'wb') as f:
            data.tofile(f)
    else:
        nfibers = len(points)
        buffer = bytearray(buffer_size * 4)
        u32_buffer = memoryview(buffer).cast('I')
        f32_buffer = memoryview(buffer).cast('f')
        start = 0
        with open(file_out + 'data', 'wb') as f:
            for fiber in points:
                assert isinstance(fiber, np.ndarray)
                end = 1 + fiber.size + start
                if end > buffer_size:
                    f.write(buffer[:start * 4])
                    start = 0
                    end = 1 + fiber.size + start
                u32_buffer[start] = fiber.shape[0]
                f32_buffer[start + 1:end] = fiber.flat[:]  # type: ignore
                start = end
            f.write(buffer[:start * 4])
    with open(file_out, 'wt') as f:
        f.write(_MINF_TEMPLATE.format(['points', 0], nfibers))


def deform(deform_file: str, file_in: str, file_out: str) -> None:
    """
    Transforms a tractography file to another space using a non-linear deformation image file.

    Parameters
    ----------
    deform_file : str
        Deformation image (image in NIfTI format containing the deformations).
    file_in : str
        Input tractography dataset in bundles format.
    file_out : str
        Path to the transformed tractography dataset.

    Returns
    -------
    None

    Notes
    -----
    This function generates the following files in the specified directory:

    Tractography : bundles files
        Tractography dataset that has been transformed into the MNI space.

    """
    check_input_path(deform_file, ext='nii')
    check_input_path(file_in)
    check_output_path(file_out, ext='bundles')
    _deform(deform_file, file_in, file_out)


def sampling(file_in: str, file_out: str, npoints: int = 21) -> None:
    """
    Performs a fiber sampling by recalculating their points using a specified number of equidistant points.

    Parameters
    ----------
    file_in : str
        Tractography dataset file in *bundles* format.
    file_out : str
        Path to save the tractography dataset sampled at n equidistant points.
    npoints : str
        Number of sampling points (n). Default: *21*.

    Returns
    -------
    None

    Notes
    -----
    This function generates the following files in the specified directory:

    Tractography : bundles files
        Tractography dataset sampled at n equidistant points in *bundles* format

    """
    check_input_path(file_in, ext="bundles")
    check_output_path(file_out, ext="bundles")
    _sampling(file_in, file_out, npoints)


def intersection (file1_in: str, file2_in: str, dir_out: str,
                  distance_thr: float = 10.0) -> Tuple[float, float]:
    """
    Calculates a similarity measure between two sets of brain fibers (fiber clusters or segmented bundles).
    The similarity measure yields a value between *0* and *100%*.

    Parameters
    ----------
    file1_in : str
        Path of the first fiber bundle.
    file2_in : str
        Path of the second fiber bundle.
    dir_out : str
        Directory name to store all the results generated by the algorithm.
    distance_thr : float
        Distance threshold in *mm* used to consider similar two fibers, default: *10*.

    Returns
    -------
    Tuple : [float, float]
        `[float, float]`, The first value indicates the percentage of intersection of the first set of fibers compared to the second set of fibers,
        and the second value indicates the reverse scenario, intersection of the second set of fibers compared to the first set of fibers.
    
    Notes
    -----
    This function generates three tractography dataset files in the ouput directory, as follows:

    *fiber1-fiber2.bundles/fiber1-fiber2.bundlesdata*: 
      Containing the fibers that are considered similar (or intersecting) for both fascicles.
    *only_fiber1.bundles/only_fiber1.bundlesdata*: 
      Containing the fibers that are only in the first fascicle.
    *only_fiber2.bundles/only_fiber2.bundlesdata*: 
      Containing the fibers that are only in the second fascicle.

    """
    p1 = 0
    p2 = 0

    check_output_path(dir_out, dir=True)
    outfile = os.path.join(dir_out,'distance_matrix.txt')
    check_output_path(outfile)

    _intersection(file1_in, file2_in, outfile)

    ar=open(outfile,'rt')
    t=ar.readlines();ar.close()
    m=len(t)
    n=len(t[0].split('\t')[:-1])

    M = np.zeros((m,n),dtype = 'float32')

    for i in range(m):
        fila=t[i][:-1].split('\t')[:-1]
        for j in range(n):
            M[i,j]=float(fila[j])

    F_under_th=np.where( M < distance_thr) 
        
    xp1=list(set(F_under_th[0]))
    yp2=list(set(F_under_th[1]))

    p1=(len(xp1)/getBundleSize(file1_in))*100 
    p2=(len(yp2)/getBundleSize(file2_in))*100 

    bun1 = np.asarray(read_bundle(file1_in))
    bun2 = np.asarray(read_bundle(file2_in))

    bun1_bun2 = np.concatenate((bun1[xp1], bun2[yp2]), axis=0) 
    write_bundle(os.path.join(dir_out,'fiber1-fiber2.bundles'),list(bun1_bun2))

    ind_bun1 = list(range(len(bun1)))
    ind_bun2 = list(range(len(bun2)))

    xp_sup = list(set(ind_bun1) - set(xp1))
    yp_sup = list(set(ind_bun2) - set(yp2))

    bun1 = np.asarray(read_bundle(file1_in))[xp_sup]
    bun2 = np.asarray(read_bundle(file2_in))[yp_sup]

    write_bundle(os.path.join(dir_out,'only_fiber1.bundles'),list(bun1))
    write_bundle(os.path.join(dir_out,'only_fiber2.bundles'),list(bun2))


    return (p1,p2)


def postprocessing(dir_in: str) -> pd.DataFrame:
    """
    Sets of algorithms that can be applied on the results of clustering and segmentation algorithms.

    Parameters
    ----------
    dir_in : str
        Root directory where all segmentation or clustering algorithm results are stored.

    Returns
    -------
    pd.DataFrame
        `pd.DataFrame`, contains the following list of keys: `size`: number of fibers in the bundle,
        `len`: centroid length per bundle, `intra_mean`: mean intra-bundle Euclidean distance.
    
    """

    if not os.path.exists(dir_in):
        print('Directory does not exist!\nTo execute this function, you must first run an algorithm from the clustering module.')
        
   
    in_centroides=os.path.join(dir_in,'centroids','centroids.bundles')
    in_clusters_directory=os.path.join(dir_in,'final_bundles')

    dir_mensures  =  os.path.join(dir_in, 'outputs', 'mensures')

    if not os.path.exists(dir_mensures):
        os.makedirs(dir_mensures)

    # Fibers Lens and Fibers Size
    txt_lens = ''
    txt_sizes = ''

    centroides=read_bundle(in_centroides)
    for i in range(len(centroides)):
        txt_lens += str(fiber_lens(centroides[i]))+'\n'
        txt_sizes += str(getBundleSize(os.path.join(in_clusters_directory,str(i)+'.bundles')))+'\n'

    with open(os.path.join(dir_mensures, 'lens.txt'), 'w') as file:
        file.write(txt_lens)

    with open(os.path.join(dir_mensures, 'sizes.txt'), 'w') as file:
        file.write(txt_sizes)

    # - Distancia intra-clúster mínima, Distancia intra promedio, Rij y DBindex

    _postprocessing(in_centroides, in_clusters_directory,
                    os.path.join(dir_mensures, 'm'), 21)

    return mesures_to_dataframe(dir_mensures)


