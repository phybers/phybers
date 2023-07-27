# -*- coding: utf-8 -*-
import sys, os
import numpy as N
from time import time
from scipy import sparse



#class with Average Link Analisys vars
class WeightedGraph():


  def __init__( self, V, edges, weights ):

    self.V = V
    self.E = len( edges )
    self.edges = edges
    self.weights = weights


def createfffGraphFromFile( graphfile ):

  #read graph file and create fff graph
  inFile = open( graphfile, 'r' )
  line = inFile.readline()
  l = line.split()
  V = int( l[ 0 ] )
  E = int( l[ 1 ] )
  edges = N.zeros( [ E, 2 ], 'i' )
  weights = N.zeros( [ E, 1 ], 'f' )
  print ('edges: ', E, ' vertices: ', V)

  count = 0
  while True:

    line = inFile.readline()
    if line == '': break
    l = line.split()
    edges[ count, 0 ] = int( l[ 0 ] )
    edges[ count, 1 ] = int( l[ 1 ] )
    weights[ count ] = float( l[ 2 ] )
    count += 1
  inFile.close()
  G = WeightedGraph( V, edges, weights )
  return G


#class with Average Link Analisys vars
class CenterWForestVars():


  def __init__( self, wforestFile ):

    f = open( wforestFile, 'r' )

    #number of Wforest nodes
    self.V = int( f.readline() )
    #list of node father
    self.fa = []
    #list of node child indexes (two)
    self.ch = []

    for v in range( self.V ):

      line = f.readline()
      line = line.split()
      self.fa.append( int( line[ 0 ] ) )
      child = [ int( line[ 1 ] ), int( line[ 2 ] ) ]
      self.ch.append( child )

    f.close()
    #number of white matter parcels
    self.Vg = 0
    #points not included in the Weighted Forest (without connectivity)
    self.singles = []
    #number of parcels included in the Weighted Forest (clusterized)
    self.VV = 0
    #number of trees
    self.top = []
    #final top nodes of partition
    self.finalcl = []
    #singles additional nodes after partition
    self.singles2 = []
    #final clusters
    self.clusters = []

  def get_descendents( self, v ):

    v = int( v )
    if ( v >= 0 and v <= self.V - 1 ):

      if ( self.ch[ v ][ 0 ] == -1 and self.ch[ v ][ 1 ] == -1 ):

        return [ v ]

      else:

        descendent = [ v ]

        for c in self.ch[ v ]:

          temp = self.get_descendents( c )

          for q in temp:

            descendent.append( q )

      return descendent


##for clusterizeCentersMaxdist.py
def createSparceScipyMatrixFromfffGraph( graphfile ):

  G = createfffGraphFromFile( graphfile )
  V = G.V
  edges = G.edges
  weights = G.weights
  mat = sparse.lil_matrix( ( V, V ) )
  for ind in range( len( edges ) ):

    ed = edges[ ind ]
    i = ed[ 0 ]
    j = ed[ 1 ]
    mat[ i,j ] = weights[ ind ].item()
  return mat


#calculate max and mean distances within cluster nodes
#(clusters are connected components of the tree and not singles)
def calculate_top_dist( WFV, data, top, maxdist ):

  #number of default clusters
  #(connected components of the tree and not singles)
  defcl = len( top )
  dist_data  = N.zeros( defcl ) # max
  for i in range( defcl ):

    t = top[ i ]
    maxd = calculate_node_dist( WFV, data, t, maxdist )
    dist_data[ i ] = maxd
  return dist_data

#calculate max and mean distances within cluster nodes
#(clusters are connected components of the tree and not singles)
def calculate_top_dist_nomatrix( WFV, sparse_mat, top, minaff ):

  #number of default clusters
  #(connected components of the tree and not singles)
  defcl = len( top )
  dist_data  = N.zeros( defcl ) # max
  for i in range( defcl ):

    t = top[ i ]
    mind = calculate_node_dist_nomatrix( WFV, sparse_mat, t, minaff )
    dist_data[ i ] = mind
  return dist_data

#calculate max and mean distances within cluster nodes
#(clusters are connected components of the tree and not singles)
def calculate_node_dist( WFV, data, node, maxdist ):

  maxd = 0.0
  if ( WFV.ch[ node ][ 0 ] != -1 and WFV.ch[ node ][ 1 ] != -1 ):

    #get all cluster nodes
    s = WFV.get_descendents( node )
    s.remove( node )
    ss = N.array( s )
    #identify leaves
    ind_s = N.where( ss < WFV.Vg )[ 0 ]
    s = ss[ ind_s ]
    for s1 in range( len( s ) ):

      a = s[ s1 ]
      for s2 in range( s1 + 1, len( s ) ):

        b = s[ s2 ]
        val = data[ a ][ b ]
        if val > maxd:

          maxd = val
        if maxd > maxdist:

          return val
  return maxd

#(clusters are connected components of the tree and not singles)
def calculate_node_dist_nomatrix( WFV, sparse_mat, node, minaff ):

  #node = WFV.top(1)
  mind = 100.0
  if ( WFV.ch[ node ][ 0 ] != -1 and WFV.ch[ node ][ 1 ] != -1 ):

    #get all cluster nodes
    s = WFV.get_descendents( node )
    s.remove( node )
    ss = N.array( s )
    #identify leaves
    ind_s = N.where( ss < WFV.Vg )[ 0 ]
    s = ss[ ind_s ]
    for s1 in range( len( s ) ):

      a = s[ s1 ]
      #get all edges indexes who have the node
      for s2 in range( s1 + 1, len( s ) ):

        b = s[ s2 ]
        val = sparse_mat[ a, b ]
        if val < mind:

          mind = val
        if mind <= minaff:

          return mind
  return mind


def create_partition_from_finalcl( WFV, finalcl ):

  clusters = []
  for f in finalcl:

    if ( WFV.ch[ f ][ 0 ] != -1 and WFV.ch[ f ][ 1 ] != -1 ): #not single

      s = WFV.get_descendents( f )
      s.remove( f )
      ss = N.array( s )
      #identify leaves
      ind_s = N.where( ss < WFV.Vg )[ 0 ]
      s = ss[ ind_s ]
      nodelist = list( s )
    else:

      nodelist = [ f ]
    clusters.append( nodelist )

  WFV.clusters = clusters

def wforest_partition_maxdist_from_graph( wforestfile,
                                       maxdist,
                                       add_singles = False,
                                       graphfile = '',
                                       var: float = 3600 ):

  WFV = CenterWForestVars( wforestfile )
  nomatrix=True
  #number of vertices of the graph (fiber centers)
  Vg = 0
  while ( Vg < len( WFV.ch ) and \
                         WFV.ch[ Vg ][ 0 ] == -1 and WFV.ch[ Vg ][ 1 ] == -1  ):

    Vg = Vg + 1

  singles = []
  for v in range( Vg ):

    if WFV.fa[ v ] == v:
      singles.append( v )
  #
  #number of centers included in the Weighted Forest (clusterized)
  VV = Vg - len( singles )
  #
  #number of trees
  top = []
  for v in range( Vg, WFV.V ):

    if WFV.fa[ v ] == v:

      top.append( v )
  #store WFV data
  WFV.Vg = Vg
  WFV.singles = singles
  WFV.VV = VV
  WFV.top = top

  #calculate maximum values of distances to evaluate clusters
  #print("maxdist type: ")
  print(maxdist)
  print(type(maxdist))
  max_cldist = float(maxdist) * 1.0         #maximum distance within a cluster
  max_meancldist = float(maxdist) * 1.0      #mean distance within a cluster
  #minimum affinity within a cluster
  print(type(-max_cldist))
  print(type(max_cldist))
  print(type(var))
  min_claff = N.exp( -max_cldist * max_cldist / float(var) );
  #mean affinity within a cluster
  min_meanclaff = N.exp( -max_meancldist * max_meancldist / float(var) );

  #---------------------------------------------
  #information of distance within clusters
  if nomatrix:

    #convert fffgraph to scipy sparse matrix
    sparse_mat = createSparceScipyMatrixFromfffGraph( graphfile )
    dist_data = calculate_top_dist_nomatrix( WFV, sparse_mat, top, min_claff )
  #else:

    #mat = aims.read( all_centers_distmat )
    #data = mat.arraydata()[ 0 ][ 0 ]
    #calculate distance data
    #dist_data = calculate_top_dist( WFV, data, top, max_cldist )

  count_divide = 0 #tmp
  singles2b = []
  #review only non-tight clusters
  defcl = len( top )
  finalcl = []
  top2 = []

  for i in range( defcl ):

    maxd = dist_data[ i ]
    divide = False
    if nomatrix:

      if maxd <= min_claff: #maxd in the minimum affinity

        divide = True

    if divide:

       #add top chidren to divide queue
      count_divide += 1 #tmp
      t = top[ i ]
      children = WFV.ch[ t ]
      if ( children[ 0 ] != -1 or children[ 1 ] != -1 ):

        for chi in children:

          if chi >= Vg:

            top2.append( chi )
          else:

            singles2b.append( chi )
    else:

      finalcl.append( top[ i ] )

  #analisys queue
  queue = []
  #add all trees in queue
  for i in range( len( top2 ) ):

    queue.append( top2[ i ] )

  singles2 = []
  #perform analisys
  while len( queue ) > 0:

    ind = queue[ 0 ]
    queue.remove( ind )
    if nomatrix:

      maxd = calculate_node_dist_nomatrix( WFV,
                                           sparse_mat,
                                           ind,
                                           min_claff )


    children = WFV.ch[ ind ]
    #if maxd > max_cldist and meand > max_meancldist:
    divide = False
    if nomatrix:

      if maxd <= min_claff: #maxd in the minimum affinity

        divide = True

    if divide:

      count_divide += 1 #tmp
      #must divide
      if ( WFV.ch[ Vg ][ 0 ] != -1 and WFV.ch[ Vg ][ 1 ] != -1 ):

        for chi in children:

          if chi >= Vg:

            queue.append( chi )
          else:

            singles2b.append( chi )
      else:

        singles2.append( ind )
    else:

      if ( WFV.ch[ Vg ][ 0 ] != -1 and WFV.ch[ Vg ][ 1 ] != -1 ):

        finalcl.append( ind )
      else:

        singles2.append( ind )

  WFV.singles2 = singles2 + singles2b
  WFV.finalcl_singles = singles + singles2 + singles2b
  WFV.finalcl_notsingles = finalcl
  WFV.finalcl = finalcl + WFV.finalcl_singles
  print ('total singles num = ', len( WFV.finalcl_singles ))
  print ('not single clusters = ', len( WFV.finalcl_notsingles ))
  print ('total clusters = ', len( WFV.finalcl ))
  #tmp
  print ('count divide = ', count_divide)

  if add_singles == True:

    create_partition_from_finalcl( WFV, WFV.finalcl )
  else:

    create_partition_from_finalcl( WFV, WFV.finalcl_notsingles )
  return WFV
