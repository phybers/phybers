#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd

_minf = """attributes = {
    'binary' : 1,
    'bundles' : %s,
    'byte_order' : 'DCBA',
    'curves_count' : %s,
    'data_file_name' : '*.bundlesdata',
    'format' : 'bundles_1.0',
    'space_dimension' : 3
}"""


#%%
def read_bundle( infile ):
    """
    Read Bundles File.
    """
    points = []
    bun_file = infile + 'data'
    os.path.getsize( bun_file )
    bytes = os.path.getsize( bun_file )
    num = bytes / 4
    num_count = 0
    f = open( bun_file , 'rb')
    while num_count < num:
        p = np.frombuffer( f.read( 4 ), dtype=np.int32 )[ 0 ] # Numero de puntos de la fibra.
        vertex = np.frombuffer( f.read( p * 3 * 4 ), dtype=np.float32 ).reshape( -1, 3 ) # Lee coordenadas fibra.
        points.append( vertex )
        num_count = num_count + 1 + ( p * 3 )
    f.close()
    return points

def write_bundle( outfile, points ):
    """ Write bundles File.
    """
    f = open( outfile + 'data','wb' )
    ncount = len( points )
    for i in range( ncount ):
        f.write(np.array([len(points[i])], np.int32).tostring())  # type: ignore
        f.write(points[i].ravel().tostring())
    f.close()
    # write minf file
    open( outfile, 'w' ).write(_minf % ( [ 'points', 0 ], ncount ) )

def getBundleSize( bundlefile ):
    """ Get Bundles Size from file.
    """
    # Get center names from bundle file.
    ns = dict()
    exec(compile(open( bundlefile ).read(), bundlefile, 'exec'), ns)
    size = ns[ 'attributes' ][ 'curves_count' ]
    return  size

def fiber_lens(fiber):
    """
    Find the length of a fiber.
    """
    final_len = 0
    for i in range(fiber.shape[0]-1):
        current_lens = np.linalg.norm(fiber[i,:] - fiber[i+1,:])
        final_len+=current_lens
    return final_len


def Stadistics_txt_toxlsx(dirstad):
    """Create Dataframe from statistical measures: sizes, lens, intra_means,intra_min and Ri_dbindex.
    """
    with open(dirstad+"sizes.txt", "r") as file:
        tam = [int(i[:-1]) for i in file]

    with open(dirstad+"lens.txt", "r") as file:
        larg = [round(float(i[:-1]), 2) for i in file]

    with open(dirstad+"mensure_intra_dists.txt", "r") as file:
        intra_max = [round(float(i.split(" ")[1][:-1]), 2) for i in file]

    with open(dirstad+"mensure_intra_means_dists.txt", "r") as file:
        intra_mean = [round(float(i.split(" ")[1][:-1]), 2) for i in file]

    with open(dirstad+"mensure_Ri_db.txt", "r") as file:
        Ri_db = [round(float(i.split(" ")[1][:-1]), 2) for i in file]

    data= {'sizes':tam,'lens':larg,'intra_max':intra_max,'intra_mean':intra_mean,'Ri_db':Ri_db }
    df_data = pd.DataFrame(data, columns = ['sizes','lens','intra_max','intra_mean','Ri_db'])
    df_data.to_excel(dirstad+'stadistics.xlsx')
