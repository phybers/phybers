import collections
import numpy as np
from os import path
from dipy.segment.clustering import ClusterMapCentroid
from . import clustering
from .bundleTools import write_bundle


def clusters_fibers21p(results: ClusterMapCentroid, final_bundles_dir, infile):
    for i, cluster in enumerate(results.clusters):
        bcust = [infile[j] for j in cluster.indices]
        write_bundle(path.join(final_bundles_dir, f'{i}.bundles'), bcust)

def save_clusters(dataset, clusters, filename):
    """
    Generate output file for clusters, the output file consists of
    the index to which cluster each element in the dataset(streamlines)
    belongs to, an index of -1 indicates that the element isnt assigned anywhere
    """
    output_array = -1*np.ones(len(dataset), np.int32)
    for cluster in clusters:
        output_array[cluster.indices] = cluster.id
    np.savetxt(X=output_array, fname=filename, delimiter='\n', fmt='%d')

def save_clusters_centroids(clusters, filename):
    with open(filename,"w") as file:
        for cluster in clusters:
            file.write(f"{cluster.centroid} \n")

def save_join_clusters_fibers(results, filename):
    with open(filename,"w") as file:
        for clusters_names in results:
            for name in clusters_names:
                text = name + "-" + " ".join(map(str, clusters_names[name].indices)) + "\n"
                file.write(text)

def load_clusters(dataset, filename, not_assigned=False):
    """
    From file where each line is the id of the cluster to which each streamline belongs
    generate a dipy ClusterMapCentroid to use
    """

    cls_dict = collections.defaultdict(list)
    with open(filename, 'r') as f:
        for i,id in enumerate(f):
            id = int(id)
            cls_dict[id].append(i)

    no_clusters = cls_dict.pop(-1)
    clusters = clustering.clusters_to_clustermap(list(cls_dict.values()), dataset, cls_dict.keys())

    if not_assigned:
        return clusters, no_clusters
    else:
        return clusters
