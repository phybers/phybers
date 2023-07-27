import logging
import time
import os
import numpy as np
import joblib
from .bundleTools import read_bundle
from .clustering import split_fibers, parallel_points_clustering, MapClustering,\
    small_clusters_reassignment, get_groups, parallel_group_join_clique
from ...utils import sampling
from .utils import clusters_fibers21p, save_clusters, save_clusters_centroids

def ffclust(file_in: str, dir_out: str, assign_thr: int=6, join_thr: int=6) -> bool:
    if isinstance(assign_thr, str):
        assign_thr = int(assign_thr)
    if isinstance(join_thr, str):
        join_thr = int(join_thr)

    points = np.array([0,3,10,17,20])
    ks = np.array([200,300,300,300,200])

    os.makedirs(dir_out, exist_ok=True)

    final_bundles21p_dir = os.path.join(dir_out, 'FinalBundles21p')
    os.makedirs(final_bundles21p_dir, exist_ok=True)

    final_centroids_dir = os.path.join(dir_out,'FinalCentroids')
    os.makedirs(final_centroids_dir, exist_ok=True)

    object_dir = os.path.join(dir_out, 'output')
    os.makedirs(object_dir, exist_ok=True)
    data=read_bundle(file_in)

    npf=0
    for i in range(len(data)-1):
        if len(data[i]) != len(data[i+1]):
            npf=21
            break


    if npf == 21:
        fibers21p = os.path.join(object_dir,'fiberorig_21p.bundles')
        sampling(file_in, fibers21p, 21)
        fibers = np.asarray(read_bundle(fibers21p))
    else:
        fibers = np.asarray(data)

    # New logging file each time, changing filemode to a should append instead.
    logging.basicConfig(filename=dir_out+'/info.log', filemode='w', level=logging.INFO)

    t1 = time.time()
    X = split_fibers(fibers[:,points,:],points)
    labels, clusterers = parallel_points_clustering(X=X, ks=ks)
    logging.info('Tiempo Kmeans: {}'.format(time.time() - t1))

    t1 = time.time()
    m = MapClustering()
    map_clusters = m.cluster(fibers, labels)
    logging.info('Tiempo Map: {}'.format(time.time() - t1))

    map_output_filename = os.path.join(object_dir, 'clusters_map.txt')
    save_clusters(dataset=fibers, clusters=map_clusters, filename=map_output_filename)

    with open(dir_out+'/stats.txt', 'w') as f:
        f.write('Number of clusters in map_clusters: {}\n'.format(len(map_clusters)))
        f.write('Number of fibers in map_clusters: {}\n'.format(sum(map_clusters.clusters_sizes())))

    for p,k, clusterer in zip(points, ks, clusterers):
        joblib.dump(clusterer, object_dir + '/clusterer-Point{}-k{}.pkl'.format(p,k))

    """Write .bundles .bundlesdata of small (< 1 fiber) and long centroids (> 1 fiber) of clusters
    and reassign small clasters to large clusters. Input:
    ouput: path of output file directory to write the clusters
    min_size_filter = minimum size to get the largest clusters
    max_size_filter = maximum size to get the clusters with only 1 fiber
    input_dir = path of the input dir that contains the results of segmetation/reassignation
    threshold = minimum distance for the segmentation's method
    """
    # Compenzando la reasignación.
    t1 = time.time()
    actual_clusters = small_clusters_reassignment(clusters=map_clusters,
                                                  min_size_filter=6,
                                                  max_size_filter=5,
                                                  input_dir = 'segmentation/bundles/result/parallelFastCPU',
                                                  threshold = assign_thr,
                                                  refdata = fibers)

    ident_clusters = dict()
    for i,c in enumerate(actual_clusters):
        ident_clusters[str(c.indices)] = i

    logging.info('Tiempo Segmentacion {}'.format(time.time() - t1))

    t1 = time.time()
    point_index = 10
    ngroups = ks[len(ks)//2]

    centroids = np.asarray([x.centroid for x in actual_clusters])
    centroids_points = centroids[:,point_index]
    clusterer=clusterers[len(points)//2]
    labels = clusterer.predict(centroids_points)

    groups = get_groups(labels, ngroups=ngroups)
    joined_clusters = parallel_group_join_clique(actual_clusters, groups, fibers,final_bundles21p_dir,final_centroids_dir,ident_clusters,object_dir,join_thr)


    final_clusters = joined_clusters
    final_centroids_filename = os.path.join(object_dir, 'final_centroids.txt')
    save_clusters_centroids(clusters=final_clusters, filename=final_centroids_filename)

    if npf == 21:
        final_bundles_dir = os.path.join(dir_out,'FinalBundles')
        os.makedirs(final_bundles_dir, exist_ok=True)
        clusters_fibers21p(final_clusters, final_bundles_dir, data)
    return True
