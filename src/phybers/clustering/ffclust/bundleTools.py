import numpy as N
import os

_minf = """attributes = {{
    'binary' : 1,
    'bundles' : {},
    'byte_order' : 'DCBA',
    'curves_count' : {},
    'data_file_name' : '*.bundlesdata',
    'format' : 'bundles_1.0',
    'space_dimension' : 3
}}"""

def read_bundle( infile ):
    points = []
    bun_file = infile + 'data'
    os.path.getsize( bun_file )
    bytes = os.path.getsize( bun_file )
    num = bytes / 4

    num_count = 0
    with open(bun_file,'rb') as f:
        while num_count < num:
            # numero de puntos de la fibra
            p = N.frombuffer(f.read(4), 'i' )[ 0 ]
            vertex = N.frombuffer( f.read( p * 3 * 4 ), 'f' ).reshape( -1, 3 ) # lee coordenadas fibra
            points.append( vertex )
            #num_# commentunt = num_count + 1 + ( p * 3 )
            num_count = num_count + 1 + ( p * 3 )
    return points

def write_bundle( outfile, points ):
    #write bundles file
    f = open( outfile + 'data','wb' )
    ncount = len( points )
    for i in range( ncount ):
            f.write(N.array( [ len( points[ i ] ) ], N.int32 ).tobytes() )
            f.write( points[ i ].ravel().tobytes() )
    f.close()
    # wrtie minf file
    open( outfile, 'w' ).write(_minf.format([ 'points', 0 ], ncount))
