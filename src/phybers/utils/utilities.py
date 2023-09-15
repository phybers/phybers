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
from .FibersTools import getBundleSize, fiber_lens, Stadistics_txt_toxlsx
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

    Tractography : bundles file
        Tractography dataset that has been transformed into the MNI space.

    Examples
    --------
    To test `deform()`,  download the data from the `link deform <https://www.dropbox.com/sh/ncu8sf1ifwz4wpv/AACDzOXEdSrf8kBaWrbjfEPla?dl=1>`_.
    Then, open a Python terminal and run the following commands.

    >>> from phybers.utils import deform
    >>> deform( deform_file = 'defnolineal.nii', file_in = 'fibers.bundles', file_out = 'fibers_MNI.bundles' )

    Note: Make sure to replace the file paths with the actual paths to your data and directories.
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
        Tractography dataset file in *'.bundles'* format.
    file_out : str
        Path to save the sub-sampled fibers.
    atlas_dir : str
        Bundle atlas, with bundles in separated files, sampled at 21 equidistant points. The bundle atlases provided are in same folders.
    npoints : str
        number of sampling points (n). Default: *21*.

    Returns
    -------
    None

    Notes
    -----
    This function generates the following files in the specified directory:

    Tractography : bundles file
        Tractography dataset sampled at n equidistant points.

    Examples
    --------
    To test `sampling()`,  download the data from the `link sampling <https://www.dropbox.com/sh/9tfxseo8uh68b32/AAAn56Xgiw7KhL2ILmkN6A23a?dl=1>`_.
    Then, open a Python terminal and run the following commands.

    >>> from phybers.utils import sampling
    >>> sampling ( file_in = 'sub_01.bundles', file_out = 'sub_01_21points.bundles', npoints = 21 )

    Note: Make sure to replace the file paths with the actual paths to your data and directories.
    """
    check_input_path(file_in, ext="bundles")
    check_output_path(file_out, ext="bundles")
    _sampling(file_in, file_out, npoints)


def inter2bundles(file1_in: str, file2_in: str, dir_out: str,
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
        Path to save the distance matrix
    distance_thr : float
        Distance threshold in millimeters used to consider similar two fibers, default: *10*.

    Returns
    -------
    Tuple : [float, float]
        `[float, float]`, The first value indicates the percentage of intersection of the first set of fibers compared to the second set of fibers,
        and the second value indicates the reverse scenario, intersection of the second set of fibers compared to the first set of fibers.

    Examples
    --------
    To test `intersection()`, download the data from the `link intersection <https://www.dropbox.com/sh/dt196k65v03eh9m/AABKRW7ad2ssB0N_dpjqK4Dha?dl=1>`_.
    The provided data is identical, therefore a *100%* intersection is expected.
    Then, open a Python terminal and run the following commands.

    >>> from phybers.utils import intersection
    >>> result_inter=intersection ( file1_in = 'fib1.bundles', file2_in = 'fib2.bundles', dir_out = 'inter_result', distance_thr = 10.0 )
    >>> print(' intersection fibers1 with fibers2 ', result_inter [0] )
    >>> print(' intersection fibers2 with fibers1 ', result_inter [1] )

    Note: Make sure to replace the file paths with the actual paths to your data and directories.
    """


    labelsb1 = os.path.split(file1_in)[1]  # m - rows
    labelsb2 = os.path.split(file2_in)[1]  # num - columns


    p1 = 0
    p2 = 0

    str_out = labelsb1.split('.')[0]+'-'+labelsb2.split('.')[0]

    check_output_path(dir_out, dir=True)
    outfile = os.path.join(dir_out,str_out+'.txt')
    check_output_path(outfile)

    # computes the distance matrix between two fiber bundles.
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

    F_under_th=np.where( M < distance_thr) # fibers with at least 1 other fiber has distance under the threshold
    xp1=list(set(F_under_th[0]))
    yp2=list(set(F_under_th[1]))

    p1=(len(xp1)/getBundleSize(file1_in))*100 #fiber bundle 1 intersection percentage
    p2=(len(yp2)/getBundleSize(file2_in))*100 #fiber bundle 2 intersection percentage

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
        `pd.DataFrame`, contains the following list of keys: 'id_bundle': bundle identifier, 'sizes': number of fibers in the bundle,
        'lens': centroid length per bundle, 'intra_min': manimum intra-bundle Euclidean distance and intra_mean': mean intra-bundle Euclidean distance.

    Examples
    --------
    To test postprocessing(), download the data from the provided link, or execute it on the results of a clustering or segmentation algorithm.
    Then, open a Python terminal and run the following commands.


    >>> from phybers.utils import postprocessing
    >>> df = postprocessing ( dir_in = str )

    Note: Make sure to replace the file paths with the actual paths to your data and directories.
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
    centroides=read_bundle(in_centroides)
    for i in range(len(centroides)):
        txt_lens += str(fiber_lens(centroides[i]))+"\n"
        txt_sizes += str(getBundleSize(in_clusters_directory+'/'+str(i)+".bundles"))+"\n"

    with open(os.path.join(stadisticsFolder, 'lens.txt'), 'w') as file:
        file.write(txt_lens)

    with open(os.path.join(stadisticsFolder, 'sizes.txt'), 'w') as file:
        file.write(txt_sizes)

    # - Distancia intra-clúster mínima, Distancia intra promedio, Rij y DBindex

    _postprocessing(in_centroides, in_clusters_directory,
                    os.path.join(stadisticsFolder, 'mensure'), 21)

    # Dataframe
    Stadistics_txt_toxlsx(stadisticsFolder)

    return pd.read_excel(stadisticsFolder+'/stadistics.xlsx')


_p1 = re.compile(r'^.*\.bundles$')


def read_bundle(fp: str, npoints: int = 0) -> None:
    """
    Read bundles file.

    Parameters
    ----------
    file_in : str
        Tractography dataset file in *'.bundles'* format.
    npoints : str
        Path to save the sub-sampled fibers.


    Returns
    -------
    None

    Notes
    -----
    This function generates the following files in the specified directory:

    Tractography : bundles
        Tractography dataset sampled at n equidistant points.

    Examples
    --------
    To test `read_bundle()`,  download the data from the `link provided <https://www.dropbox.com/sh/9tfxseo8uh68b32/AAAn56Xgiw7KhL2ILmkN6A23a?dl=1>`_.
    Then, open a Python terminal and run the following commands.

    >>> from phybers.utils import sampling
    >>> sampling ( file_in = 'sub_01.bundles', file_out = 'sub_01_21points.bundles', npoints = 21 )

    Note: Make sure to replace the file paths with the actual paths to your data and directories.
    """
    if _p1.match(fp):
        fp += 'data'
    with open(fp, 'rb') as f:
        data = np.fromfile(f, dtype=np.float32)
    if npoints > 0:
        return data.reshape(-1, npoints * 3 + 1)[:, 1:].reshape(-1, npoints, 3)
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


def write_bundle(file_out: str, points, buffer_size=1_048_576)  -> None:
    """
    Write bundles file.

    Parameters
    ----------
    file_out : str
        Tractography dataset file in *'.bundles'* format.
    points : list
        Tractography dataset sampled at n equidistant points.

    Returns
    -------
    None

    Notes
    -----
    This function generates the following files in the specified directory:

    Tractography : bundles
        Tractography dataset sampled at n equidistant points.

    Examples
    --------
    To test `write_bundle()`,  download the data from the `link provided <https://www.dropbox.com/sh/9tfxseo8uh68b32/AAAn56Xgiw7KhL2ILmkN6A23a?dl=1>`_.
    Then, open a Python terminal and run the following commands.

    >>> from phybers.utils import sampling
    >>> sampling(dir_in='sub_01.bundles', file_out='sub_01_21points.bundles', npoints=21)

    Note: Make sure to replace the file paths with the actual paths to your data and directories.
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
