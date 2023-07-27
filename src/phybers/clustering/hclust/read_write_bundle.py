import numpy as N
import os

def read_bundle( infile ):
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

  #write bundles file
  with open( outfile + 'data','wb' ) as f:
    ncount = len( points )
    for i in range( ncount ):
      f.write(N.array( [ len( points[ i ] ) ], N.int32 ).tobytes() )
      f.write( points[ i ].ravel().tobytes() )

  # write minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""
  with open( outfile, 'w' ) as f:
    f.write(minf % ( [ 'points', 0 ], ncount ) )


def write_bundle2( outfile, points,label ):

  #write bundles file
  f = open( outfile + 'data','wb' )
  ncount = len( points )
  for i in range( ncount ):
    f.write(N.array( [ len( points[ i ] ) ], N.int32 ).tostring() )
    f.write( points[ i ].ravel().tostring() )

  f.close()

  # write minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""
  open( outfile, 'w' ).write(minf % ( [ label, 0 ], ncount ) )

def getBundleNames( bundlefile ):

  #get center names from bundle file
  ns = dict()
  execfile( bundlefile, ns )
  bunlist = ns[ 'attributes' ][ 'bundles' ]
  centers_num = len( bunlist ) / 2
  labels = []
  for i in range( centers_num ):

    ind = i * 2
    labels.append( bunlist[ ind ] )
  return labels

def getBundleSize( bundlefile ):

  #get center names from bundle file
  ns = dict()
  exec(compile(open( bundlefile ).read(), bundlefile, 'exec'), ns)
  size = ns[ 'attributes' ][ 'curves_count' ]
  return  size

def read_bundle_severalbundles( infile ):

  points = []
  bun_file = infile + 'data'
  os.path.getsize( bun_file )
  bytes = os.path.getsize( bun_file )
  num = bytes / 4

  ns = dict()
  execfile( infile, ns )
  bundlescount = ns[ 'attributes' ][ 'bundles' ]
  curvescount = ns[ 'attributes' ][ 'curves_count' ]
  bunnames = []
  bunstart = []
  bun_num = len( bundlescount ) / 2
  count = 0
  for i in range( bun_num ):

    bunnames.append( bundlescount[ count ] )
    count = count + 1
    bunstart.append( bundlescount[ count ] )
    count = count + 1
    points.append( [] )

  bun_size = []
  if len( bunstart ) > 1:

    for b in range( len( bunstart ) - 1 ):

      bun_size.append( bunstart[ b + 1 ] - bunstart[ b ] )
    bun_size.append( curvescount - bunstart[ b + 1 ] )
  else:

    bun_size.append( curvescount )
  num_count = 0
  f = open( bun_file )
  bun_count = 0
  num_count_bundle = 0
  while num_count < num:

    p = N.frombuffer( f.read( 4 ), 'i' )[ 0 ]
    vertex = N.frombuffer( f.read( p * 3 * 4 ), 'f' ).reshape( -1, 3 )
    points[ bun_count ].append( vertex )
    #print num_count, p, bun_count, num_count_bundle
    num_count_bundle = num_count_bundle + 1
    if num_count_bundle == bun_size[ bun_count ]:
      bun_count = bun_count + 1
      num_count_bundle = 0
    num_count = num_count + 1 + ( p * 3 )

  f.close()
  return points, bunnames


def write_bundle_severalbundles( outfile, points, bundles = [] ):

  #write bundles file
  f = open( outfile + 'data','w' )
  ncount = 0
  for i in range( len( points ) ):

    size = len( points[ i ] )
    ncount = ncount + size
    bun = points[ i ]
    for i in range( size ):

      f.write( N.array( [ len( bun[ i ] ) ], N.int32 ).tostring() )
      f.write( bun[ i ].ravel().tostring() )
  f.close()
  # wrtie minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""

  bundles_list = []
  ind = 0
  for i in range( len( points ) ):

    if bundles == []:

      bundles_list.append( str( i ) )
    else:

      bundles_list.append( bundles[ i ] )
    bundles_list.append( ind )
    #print i, ' : len= ', len(points[i])
    ind = ind + len( points[ i ] )

  bundlesstr = '['
  l = len( bundles_list ) / 2
  for i in range( l - 1 ):

    ind = i*2
    bundlesstr += ' \'' + bundles_list[ ind ] + '\', ' \
                        + str( bundles_list[ ind + 1 ] ) + ','
  bundlesstr += ' \'' + bundles_list[ ind + 2 ] + '\', ' \
                      + str( bundles_list[ ind + 3 ] ) + ' ]'

  open( outfile, 'w' ).write( minf % ( bundlesstr, ncount ) )

def make_hie (nuevohie,names):
	###################################################################################
	colores=['color 255 0 0', 'color 0 255 0', 'color 0 0 200', 'color 255 255 20',
	 'color 188 243 243', 'color 190 21 216', 'color 179 147 47', 'color 249 182 249',
	 'color 125 100 50', 'color 147 147 179', 'color 255 0 255', 'color 250 100 0',
	 'color 100 25 150', 'color 80 230 180', 'color 240 100 100', 'color 50 125 100',
	 'color 40 40 255', 'color 250 160 0', 'color 255 20 147', 'color 138 43 226',
	 'color 210 105 30', 'color 0 0 139', 'color 0 150 0', 'color 150 25 150',
	 'color 150 25 150', 'color 180 147 180', 'color 0 250 0', 'color 255 255 20',
	 'color 50 100 125', 'color 188 143 143', 'color 229 229 112', 'color 119 200 0',
	 'color 30 144 255', 'color 128 0 128', 'color 100 100 200', 'color 100 0 100',
	 'color 184 134 11', 'color 141 188 143', 'color 173 255 47', 'color 255 160 122',
	 'color 32 178 170', 'color 224 176 255', 'color 107 142 35', 'color 15 15 15',
	 'color 139 0 0', 'color 219 112 147', 'color 152 251 152', 'color 238 232 170',
	 'color 218 112 214', 'color 46 139 87', 'color 160 82 45', 'color 0 255 127',
	 'color 244 164 96', 'color 106 90 205', 'color 192 192 192', 'color 255 69 0',
	 'color 72 209 204', 'color 210 180 140', 'color 135 206 235', 'color 199 21 133',
	 'color 255 218 185', 'color 128 0 0', 'color 218 112 214', 'color 205 92 92',
	 'color 205 133 63', 'color 135 206 250', 'color 0 120 0', 'color 255 105 180',
	 'color 186 85 211', 'color 240 230 140', 'color 75 0 130', 'color 180 181 113',
	 'color 97 117 105', 'color 97 117 105', 'color 62 87 66', 'color 231 218 227',
	 'color 116 76 76', 'color 154 96 74', 'color 142 122 157', 'color 164 125 190',
	 'color 47 56 35', 'color 132 157 161', 'color 128 102 67', 'color 222 218 217',
	 'color 166 113 99', 'color 160 147 115', 'color 109 101 20', 'color 175 159 123',
	 'color 183 144 105', 'color 140 63 47',  'color 63 99 95', 'color 29 28 0',
	 'color 201 183 173', 'color 157 143 117', 'color 207 191 175', 'color 151 149 150',
	 'color 180 162 162', 'color 73 71 48', 'color 131 123 110', 'color 198 247 255',
	 'color 64 96 111', 'color 166 95 151', 'color 142 161 168', 'color 156 115 149',
	 'color 148 201 109', 'color 232 185 217', 'color 171 137 91', 'color 173 172 116',
	 'color 153 99 63', 'color 166 127 145', 'color 146 141 99', 'color 117 129 107',
	 'color 214 182 183', 'color 183 144 105', 'color 96 51 22', 'color 173 176 123',
	 'color 176 197 198', 'color 199 182 126', 'color 159 160 120', 'color 244 243 239',
	 'color 195 152 118', 'color 96 51 22', 'color 166 113 99', 'color 233 201 212',
	 'color 156 203 211', 'color 146 178 137', 'color 151 100 99', 'color 141 165 189',
	 'color 156 115 149', 'color 205 194 164', 'color 147 96 43', 'color 158 133 93',
	 'color 79 69 44', 'color 145 120 100', 'color 146 141 99', 'color 196 169 176',
	 'color 66 19 9', 'color 103 51 90', 'color 151 151 159', 'color 191 185 233',
	 'color 118 105 73', 'color 113 117 146', 'color 160 147 115', 'color 196 169 176',
	 'color 161 131 71', 'color 96 51 22', 'color 196 193 124', 'color 198 247 255',
	 'color 131 144 135', 'color 178 143 150', 'color 59 63 48', 'color 244 234 225',
	 'color 198 247 255', 'color 97 152 157', 'color 221 190 170', 'color 233 162 176',
	 'color 194 124 98', 'color 109 102 120', 'color 34 9 5', 'color 128 123 103',
	 'color 110 100 108', 'color 150 200 209', 'color 243 224 218', 'color 50 77 107',
	 'color 151 119 156', 'color 166 113 99', 'color 94 113 91', 'color 129 146 162',
	 'color 175 172 163', 'color 173 172 116', 'color 193 156 140', 'color 121 117 116',
	 'color 133 87 12', 'color 117 138 129', 'color 109 113 140', 'color 137 113 103',
	 'color 232 185 217', 'color 205 194 164', 'color 191 220 162', 'color 158 116 118',
	 'color 63 79 104', 'color 168 148 149', 'color 150 160 110', 'color 110 100 108',
	 'color 157 143 117', 'color 165 150 111', 'color 127 115 89', 'color 221 190 170',
	 'color 233 162 176', 'color 129 113 98', 'color 191 192 212', 'color 88 84 75',
	 'color 29 28 0', 'color 151 166 187', 'color 240 216 154', 'color 47 56 35',
	 'color 53 31 67', 'color 165 150 111', 'color 244 243 239', 'color 147 90 125',
	 'color 118 105 73', 'color 161 129 88', 'color 18 21 14', 'color 148 183 185',
	 'color 128 123 103', 'color 141 165 189', 'color 65 37 34', 'color 65 37 34',
	 'color 200 191 152', 'color 51 62 48', 'color 44 35 0', 'color 167 170 127',
	 'color 158 116 118', 'color 220 215 177', 'color 158 116 118', 'color 209 197 183',
	 'color 139 126 94', 'color 65 37 34', 'color 156 115 149', 'color 99 68 125',
	 'color 150 160 110', 'color 133 87 12', 'color 96 51 22', 'color 50 77 107',
	 'color 94 113 91', 'color 197 232 212', 'color 155 165 154', 'color 53 31 67',
	 'color 209 197 183', 'color 180 162 162', 'color 150 200 209', 'color 156 115 149',
	 'color 146 141 99', 'color 59 32 65', 'color 191 165 81', 'color 151 119 156',
	 'color 168 131 112', 'color 181 130 103', 'color 133 112 143', 'color 149 190 186',
	 'color 214 228 192', 'color 178 184 120', 'color 112 158 132', 'color 121 125 128',
	 'color 202 175 106', 'color 252 221 164', 'color 151 166 187', 'color 212 202 151',
	 'color 129 146 162', 'color 179 217 226', 'color 129 146 162', 'color 150 200 209',
	 'color 175 172 163', 'color 151 166 187', 'color 208 154 168', 'color 166 113 99']*35
	###################################################################################
	a=open(nuevohie+'.hie','w')
	a.write('# tree 1.0\n\n*BEGIN TREE hierarchy\ngraph_syntax RoiArg\n\n*BEGIN TREE fold_name\nname all\n\n')

	for i in range(len(names)):
		a.write('*BEGIN TREE fold_name\n')
		a.write('name  '+names[i]+'\n')
		a.write(colores[i]+'\n\n*END\n\n')
	a.write('*END\n\n*END')
	a.close()


def allFibersToOneBundle( bundlefile, bundlename = '1', mode = 0 ):

  ns = dict()
  execfile( bundlefile, ns )
  curves_count = ns[ 'attributes' ][ 'curves_count' ]
  if ( mode == 1 ):

    bunlist = ns[ 'attributes' ][ 'bundles' ]
    bundlename = bunlist[ 0 ]
  bundles = '[ \'' + bundlename + '\', 0 ]'
  # write minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""
  open( bundlefile, 'w' ).write( minf % ( bundles, curves_count ) )
