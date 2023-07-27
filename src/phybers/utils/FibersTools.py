#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as N
import pandas as pd
import regex

#%%
def read_bundle( infile ):
  """ Read Bundles File.
  """
  points = []
  bun_file = infile + 'data'
  os.path.getsize( bun_file )
  bytes = os.path.getsize( bun_file )
  num = bytes / 4

  num_count = 0
  f = open( bun_file , 'rb')
  while num_count < num:
    p = N.frombuffer( f.read( 4 ), dtype=N.int32 )[ 0 ] # numero de puntos de la fibra
    vertex = N.frombuffer( f.read( p * 3 * 4 ), dtype=N.float32 ).reshape( -1, 3 ) # lee coordenadas fibra
    points.append( vertex )
    num_count = num_count + 1 + ( p * 3 )

  f.close()

  return points


def write_bundle( outfile, points ):
  """ Write bundles File.
  """
  #write bundles file
  f = open( outfile + 'data','wb' )
  ncount = len( points )
  for i in range( ncount ):
    f.write(N.array( [ len( points[ i ] ) ], N.int32 ).tobytes() )
    f.write( points[ i ].ravel().tostring() )

  f.close()

  # write minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""
  open( outfile, 'w' ).write(minf % ( [ 'points', 0 ], ncount ) )


_curves_count_p = regex.compile(r"\s*'curves_count'\s*:\s*(\d+),")
def getBundleSize( bundlefile ):
  """ Get Bundles Size from file.
  """
  #get center names from bundle file
  with open(bundlefile, 'rt') as f:
      m = _curves_count_p.search(f.read())
      if m:
         return int(m.group(1))
      else:
         raise Exception

def fiber_lens(fiber):
    """
    Find the length of a fiber.
    """
    final_len = 0
    for i in range(fiber.shape[0]-1):
        current_lens = N.linalg.norm(fiber[i,:] - fiber[i+1,:])
        final_len+=current_lens
    return final_len


def Stadistics_txt_toxlsx(dirstad):
    """Create Dataframe from statistical measures: sizes, lens, intra_means,intra_min and Ri_dbindex.
    """
    tam  = []
    with open(dirstad+"/sizes.txt", "r") as file:
        for i in file:
            tam.append(int(i[:-1]))

    larg  = []
    with open(dirstad+"/lens.txt", "r") as file:
        for i in file:
            larg.append(round(float(i[:-1]),2))


    intra_mean  = []
    with open(dirstad+"/mensure_intra_means_dists.txt", "r") as file:
        for i in file:
            intra_mean.append(round(float(i.split(" ")[1][:-1]),2))

    Ri_db  = []
    with open(dirstad+"/mensure_Ri_db.txt", "r") as file:
        for i in file:
            Ri_db.append(round(float(i.split(" ")[1][:-1]),2))


    data= {'sizes':tam,'lens':larg,'intra_mean':intra_mean,'Ri_db':Ri_db }

    df_data = pd.DataFrame(data, columns = ['sizes','lens','intra_mean','Ri_db'])

    df_data.to_excel(dirstad+'/stadistics.xlsx')
