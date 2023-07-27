import functools
import sklearn.cluster
import numpy as np
from dipy.segment.clustering import ClusterCentroid, ClusterMapCentroid, Clustering
from joblib import Parallel, delayed
from .bundleTools import write_bundle
from . import processing as processing
from . import metric as metric
from . import utils as utils
from .c_wrappers import seg as segmentation



def cluster_kmeans(x, k,random_state=0):
    kmeans = sklearn.cluster.MiniBatchKMeans(n_clusters=k,
                                             random_state=random_state)
    return kmeans.fit_predict(x), kmeans

def parallel_points_clustering(X, ks, n_jobs=-1, backend='threading'):
    """
    Compute MiniBatchKMeans for each point according to cluster size
    Do in parallel, conserve clusterers object.
    """
    results = Parallel(n_jobs=n_jobs, backend=backend)(delayed(cluster_kmeans)(x, k) for x, k in zip(X, ks))
    labels, clusterers = list(map(list, zip(*results)))
    labels = np.array(labels).T
    return labels, clusterers

def map_clustering(labels):
    """
    Create groups based on the labels that composed each element

    @arg labels: List of lists, each element in the dataset
    has m features, then
    if each feature has an associated label each element is the
    collection of such labels, in this case the labels come from
    a previous clustering step performed in each feature.
    """

    labels_it = map(tuple, labels)
    clusters = []
    d = {}

    # For every element check its label
    # if its new then create a new cluster
    # else assign to the cluster that has all elements with the
    # same label
    for i, label in enumerate(labels_it):
        if label in d:
            clusters[d[label]].append(i)
        else:
            clusters.append([i])
            d[label] = len(d)
    return clusters

def split_fibers(fibers,points):
    return np.array(np.split(fibers, len(points), axis=1))[:,:,0]

# Wrapper for dipy given that we have clusters and not centroids.
def clusters_to_clustermap(clusters, fibers, ids=None):
    """
    Wrapper for dipy clustering interface
    @arg clusters : list of lists representing the clusters, each
    inner list contains the index of the elements in the dataset that
    conform this cluster.

    @arg fibers : dataset
    """

    cluster_map = ClusterMapCentroid(fibers)
    if ids:
        for i, cluster in zip(ids, clusters):
            # Compute a centroid as a mean of its elements.

            centr = fibers[cluster].mean(axis=0)
            c = ClusterCentroid(centroid=centr,
                                id=i, indices=cluster,
                                refdata=fibers)
            cluster_map.add_cluster(c)
        return cluster_map
    for i, cluster in enumerate(clusters):
        # Compute a centroid as a mean of its elements.
        centr = fibers[cluster].mean(axis=0)
        c = ClusterCentroid(centroid=centr,
                                                    id=i, indices=cluster,
                                                    refdata=fibers)
        cluster_map.add_cluster(c)
    return cluster_map

def get_groups(labels, ngroups):
    groups = [[] for i in range(ngroups)]
    for i, l in enumerate(labels):
        groups[l].append(i)
    return groups


def small_clusters_reassignment(clusters,min_size_filter, max_size_filter,input_dir, threshold,refdata):
    """
    Write .bundles .bundlesdata of small (< 1 fiber) and long centroids (> 1 fiber) of clusters.
    """
    small_clusters = clusters.get_small_clusters(max_size_filter)
    large_clusters = clusters.get_large_clusters(min_size_filter)
    small_centroids = np.asarray([x.centroid for x in small_clusters])
    large_centroids = np.asarray([x.centroid for x in large_clusters])
    reassignment = segmentation(21 ,threshold, large_centroids,small_centroids,len(small_centroids), len(large_centroids))

    count = 0
    num_fibers_reass = 0
    num_discarded = 0
    # Reassign small clusters to large clusters.
    for small_index,large_index in enumerate(reassignment):
        fibers = small_clusters[small_index].indices
        if int(large_index)!=-1:
            # Hacer bucle para reasignar todas las fibras.
            for fiber in fibers:
                centroid = large_clusters[large_index].centroid
                f = small_clusters[small_index].refdata[fiber]
                large_clusters[large_index].assign(id_datum=fiber, features= small_clusters[small_index].refdata[fiber])
                num_fibers_reass += 1
            metric.recalc_centroid(large_clusters[large_index].indices, refdata)
            count+=1
        else:
            if len(fibers)>2:
                recover_cluster = small_clusters[small_index]
                large_clusters.append(recover_cluster)
            else:
                num_discarded +=1
    return large_clusters

# Classes for use with dipy ClusteringMap objects.
class MapClustering(Clustering):
    # Must return ClusterMap object
    # So we wrap our function around this
    def cluster(self, fibers, labels):
        clusters = map_clustering(labels)
        return clusters_to_clustermap(clusters, fibers)

def joinable_clusters(clique, visited):
    """
    Visits the nodes of a clique and returns nodes that are not visited.
    In the clustering, the nodes represent the centroids of the clusters.
    """
    clusters_ids = []
    for node in clique:
        # Some clusters may be joined already.
        if not visited[node]:
            clusters_ids.append(node)
            visited[node] = True
    return clusters_ids

def clique_join(clusters, refdata, joined_bundles_dir, ident_clusters, object_dir, threshold):
    """
    Returns a list of new clusters(dipy.clustering.ClusterCentroid container)
    based on computing the distance between centroids and using this matrix as input
    to finding cliques, distances greater than the specified threshold are ignored.
    """

    try:
        from networkx import from_numpy_array, find_cliques # type: ignore
    except ImportError:
        from networkx import from_numpy_matrix as from_numpy_array, find_cliques # type: ignore
    centroids = np.asarray([x.centroid for x in clusters])

    max_dists = metric.matrix_dist(centroids, get_max=True)

    max_dists[max_dists > threshold] = 0 # type: ignore
    network = from_numpy_array(max_dists)
    cliques = sorted(find_cliques(network), key=len, reverse=True)

    visited = np.zeros(len(centroids), np.bool_)
    new_clusters = []
    cluster_names = []
    map_cluster_names = {}
    for clique in cliques:
        # Each clique is potentially a cluster.
        clusters_ids = joinable_clusters(clique, visited)
        if not clusters_ids:
            continue
        # Need to copy indices to preserve number of streamlines, no idea why.
        ob = ClusterCentroid(centroid=clusters[clusters_ids[0]].centroid,
                             indices=clusters[clusters_ids[0]].indices[:],
                             refdata=clusters[clusters_ids[0]].refdata)
        # Node value indexes into centroids.
        if (len(clusters_ids)) > 1:
            for idx in clusters_ids[1:]:
                for index in clusters[idx].indices:
                    ob.assign(id_datum=index, features=refdata[index])
            ob.centroid = metric.recalc_centroid(ob.indices,refdata)
        new_clusters.append(ob)

        string_ids = ""
        for idx in clusters_ids:
            index_cluster = ident_clusters[str(clusters[idx].indices)]
            string_ids = string_ids + str(index_cluster)+"c"
        cluster_names.append(string_ids)
    for i,cluster in enumerate(new_clusters):
        map_cluster_names[cluster_names[i]] = cluster
    return map_cluster_names

def parallel_group_join_clique(clusters, groups, refdata,joined_bundles_dir,final_centroids_dir,ident_clusters,object_dir,thr_join):
    """
    Same as group_join_clique, using multiprocessing.dummy.Pool for threading
    Return clusters after distributing them in groups and joining with both distances and
    cliques inside those groups.

    groups: Each group if a list of indices of clusters which are in that group.
    """
    import multiprocessing.dummy

    final_clusters = ClusterMapCentroid(refdata)
    ind = 0
    pool_input = []
    for group in groups:
        cls = [clusters[i] for i in group]
        pool_input.append(cls)

    p = multiprocessing.dummy.Pool()
    func=functools.partial(clique_join, refdata=refdata, joined_bundles_dir=joined_bundles_dir,
                           ident_clusters=ident_clusters, object_dir=object_dir, threshold=thr_join)
    results = p.map(func, pool_input)

    final_output_filename = object_dir + '/final_clusters.txt'
    utils.save_join_clusters_fibers(results=results, filename=final_output_filename)

    final_centroids = []
    i = 0
    for cluster_names in results:
        for name in cluster_names:
            cluster = cluster_names[name]
            join_bundles_file = joined_bundles_dir+"/"+str(i)+".bundles"
            i+=1
            c = np.asarray(cluster[:])
            final_centroids.append(cluster.centroid)
            write_bundle(join_bundles_file,c)

    write_bundle(final_centroids_dir + '/centroids.bundles',np.asarray(final_centroids))

    for new_clusters in results:
        for k in new_clusters:
            new_clusters[k].id = ind
            ind += 1
            final_clusters.add_cluster(new_clusters[k])

    return final_clusters
