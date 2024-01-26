.. _doc-phybers:

Documentation
#############
Phybers is a Python library that provides several tools for brain tractography dataset analysis. 
With the aim of improving its usability, the library has been separated into 4 primary modules: :ref:`segment-doc`, :ref:`clustering-doc`, :ref:`utils-doc`, and :ref:`visualization-doc`. 
This section explains each of its modules, functions, and ``input/output`` arguments.

.. _segment-doc:

Segment
-------

This module incorporates a white matter fiber bundle segmentation algorithm based on a multi-subject atlas :cite:`PGuevara-2012, LabraN2017, Andrea-Vazquez-2019`, called FiberSeg.

.. automodule:: phybers.segment
    :members:


FiberSeg Description
~~~~~~~~~~~~~~~~~~~~

The FiberSeg uses as a measure of similarity between pairs of fibers the maximum Euclidean distance between corresponding points ( :math:`d_{ME}`), defined as:

.. math::
    \begin{equation}
    \label{eq:ecua1}
    d_{ME}(A,B) = \min(\max_{i}(|a_{i}-b_{i}|),\max_{i}(|a_{i}-b_{N_{p}-i}|)) \quad \qquad [1]
    \end{equation}

Where :math:`a_{i}` and :math:`b_{i}` represent the 3D coordinates of the points in fibers A and B, respectively, both having an equal number of points (:math:`N_{p}`) and in direct order. 
This implies that the points of fiber A are sequentially traversed as :math:`a_{i}` = [:math:`a_{1}`, :math:`a_{2}`, …, :math:`a_{N_{p}}`], 
and those of B are similarly defined: :math:`b_{i}` = [:math:`b_{1}`, :math:`b_{2}`, …, :math:`b_{N_{p}}`]. 
Therefore, the reverse order of fiber B is expressed as  :math:`b_{N_{p-i}}` = [ :math:`b_{N_{p}}`, :math:`b_{N_{p-1}}`, …, :math:`b_{1}`].

It aims to classify the subject fibers according to a multi-subject bundle atlas. The bundle atlas consists of a set of representative bundles and an information file.
The fibers of the atlas bundles are called centroids. The fibers of each subject are classified using a maximum :math:`d_{ME}` distance threshold for each bundle between the subject’s fibers and the atlas centroids.
The fibers are labeled with the closest atlas bundle, given that the distance is smaller than the distance threshold.

.. _atlases-download:

Atlases Download
~~~~~~~~~~~~~~~~

We provide one atlas of Deep White Matter (DWM) bundles :cite:`PGuevara-2012` and two atlases of Superficial White Matter (SWM) bundles, :cite:`Claudio-Roman-2017` and :cite:`Claudio-Roman-2022`. 
The following links provide access to these three atlases:

1. `Download DWM bundle atlas (Guevara et al. 2012) <https://www.dropbox.com/scl/fo/vy3j1bi56w07arzqnn8gc/h?rlkey=ngppw0xu4a5rbmx6sh0rtyg1o&dl=1>`_
2. `Download SWM bundle atlas (Claudio Roman et al. 2017) <https://www.dropbox.com/scl/fo/adjz3yx0pkw6nyekrpyta/h?rlkey=qpzulmnm86kn3a7zu02693t4z&dl=1>`_
3. `Download SWM bundle atlas (Claudio Roman et al. 2022) <https://www.dropbox.com/scl/fo/hperwxwe86ai334x41ee5/h?rlkey=sfgz7v34sls40x3wgntmnpa9y&dl=1>`_


In addition to these atlases, we have tested our algorithm with the atlas :cite:`Atlas-Fan-Zhang-2018`, which contains both  DWM and SWM bundle.
If you need this atlas in data ``bundles`` format, feel free to contact us via email.

.. autofunction:: fiberseg


.. _clustering-doc:

Clustering
----------

The module comprises two fiber clustering algorithms whole-brain tractography dataset, HClust (Clustering Hierarchical, :cite:`Claudio-Roman-2017, Claudio-Roman-2022`) 
and FFClust (Fast Fiber Clustering, :cite:`Andrea-Vazquez-2020`)


.. automodule:: phybers.clustering
    :members:


HClust Description
~~~~~~~~~~~~~~~~~~

HClust is an average-link hierarchical agglomerative clustering algorithm which allows finding bundles based on a pairwise fiber distance measure.
The algorithm calculates a distance matrix between all fiber pairs for a bundles dataset (:math:`d_{ij}`), by using the maximum of the Euclidean distance between fiber pairs (Equation [1]).
Then, it computes an affinity graph on the :math:`d_{ij}` matrix for the fiber pairs that have Euclidean distance below a maximum distance threshold (*fiber_thr*). 
The Affinity :cite:`ODonnell-2007` is given by the following equation:

.. math::
    \begin{equation}
    a_{ij} = e^{\frac{-d_{ij}}{\sigma^{2}}}
    \end{equation}

where :math:`d_{ij}` is the distance between the elements :math:`i` and :math:`j`, and :math:`\sigma` is a parameter that defines the similarity scale in *mm*.

From the affinity graph, the hierarchical tree is generated using an agglomerative average-link hierarchical clustering algorithm.
The tree is adaptively partitioned using a distance threshold (*partition_thr*). 

.. autofunction:: hclust


FFClust Description
~~~~~~~~~~~~~~~~~~~

FFClust is an intra-subject clustering algorithm aims to identify compact and homogeneous fiber clusters on a large tractography dataset.
The algorithm consists of four stages. The stage 1 applies Minibatch K-Means clustering on five fiber points, and it merges fibers sharing the same point clusters (map clustering) in stage 2.
Next, it reassigns small clusters to bigger ones (stage 3) considering distance of fibers in direct and reverse order.
Finally, at stage 4, the algorithm groups clusters sharing the central point and merges close clusters represented by their centroids.
The distance among fibers is defined as the maximum of the Euclidean distance between corresponding points.

.. autofunction:: ffclust

.. _utils-doc:

Utils
-----

The Utils module is a set of tools used for tractography dataset pre-processing and the analysis of brain fiber clustering and segmentation results. 
The module includes tools for reading and writing brain fiber files in bundles format, transform the fibers to a reference coordinate system based on a deformation field,
sampling of fibers at a defined number of equidistant points, calculation of intersection between sets of brain fibers, 
and tools for extracting measures and filtering fiber clusters or segmented bundles. 
We considered the extraction of measures such as size, mean length (in *mm*), and the distance between fibers of each cluster (or fascicle), in *mm*. The source code is mostly developed in C/C++.

.. automodule:: phybers.utils
    :members:

Deformation Description
~~~~~~~~~~~~~~~~~~~~~~~

The *deformation* sub-module transforms a tractography dataset file to another space using a nonlinear deformation file. 
The maps must be stored in ``NIfTI`` format, where the voxels contain the transformation to be applied to each voxel 3D space location.
*deformation* applies the transformation to the 3D coordinates of the fiber points. 
The *deformation* can be employed on the  Human Connectome Project (HCP) database :cite:`Glasser-2013` during the pre-processing stage before applying the segmentation algorithm.

.. autofunction:: deform


Sampling Description
~~~~~~~~~~~~~~~~~~~~

Tractography datasets are usually composed of a large number of 3D polylines with a variable number of points. 
The *sampling* sub-module performs a sampling of the fibers, recalculating their points using a defined number of equidistant points. 
The input data of the algorithm are the path of the tractography dataset file to be sampled, the output file with the fibers with n points, and the number of points (npoints). 
The *sampling* sub-module is used in the pre-processing stage of the segmentation and clustering algorithms.

.. autofunction:: sampling


Intersection Description
~~~~~~~~~~~~~~~~~~~~~~~~

The *intersection* sub-module calculates a similarity measure between two sets of brain fibers, that could be generated with other algorithms, such as fiber clustering (fiber clusters) and bundle
segmentation (segmented bundles). It uses a maximum distance threshold (in *mm*) to consider two fibers as similar. Both sets of fibers must be in the same space. First, an Euclidean distance matrix is calculated
between the fibers of the two sets. The number of fibers from one set that have a similar fiber in the other set are counted, for both sets. The similarity measure yields a value between *0* and *100 %*. 
The input data of the intersection algorithm are the two sets of fibers and the maximum distance threshold, while the output is the similarity percentage.

.. autofunction:: intersection


Postprocessing Description
~~~~~~~~~~~~~~~~~~~~~~~~~~

The PostProcessing sub-module contains a set of algorithms that can be applied to the results of clustering and segmentation algorithms. 
This algorithm constructs a Pandas library object (``Dataframe``), where each key corresponds to the name of the fiber set (cluster or segmented fascicle), 
followed by measures defined on the fiber set such as number of fibers (size), intra-fiber bundle distance (in *mm*) and mean length (in *mm*). 
It can be used to perform single or multiple feature filtering on the clustering or segmentation results. The input of the algorithm is the directory with the bundle sets to be 
analyzed, and the output is a Pandas Dataframe object with the calculated metrics.


.. autofunction:: postprocessing

Read and Write bundle Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The functions ``read_bundle()`` and ``write_bundle()`` allow reading and writing files in the ``'.bundles/bundlesdata'`` format, respectively. Below, their inputs and outputs are described.

.. autofunction:: read_bundle


.. autofunction:: write_bundle

.. _visualization-doc:

Visualization
-------------

The tractography dataset files can be rendered with lines or cylinders.
In the case of lines, the software loads the streamlines with a fixed normal per vertex, which correspond to the normalized direction for the particular segment of the streamline.
Furthermore, a phong lighting algorithm :cite:`ABrainVis` is implemented in a vertex shader to compute the color fetched for the streamline.
The MRI data is rendered by using specific shaders for slice visualization and volume rendering. Meshes can be displayed using points, wireframes or shaded triangles.
The user interface (GUI) allows viewing several objects simultaneously, performing camera operations (zoom, rotate and panning), modifying material properties (color and adding transparency)
and applying linear transformation on the brain tractography dataset.

 .. automodule:: phybers.fibervis
    :members:


Interactive 3D ROI-based fiber segmentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function enables users to extract bundles using 3D objects and labeled 3D images, creating a point-based data structure for fast queries, known as an Octree. 
It is based on storing points inside a bounding box with a capacity of N. When a node is filled, and a new point is added, the node subdivides its bounding box into eight new non-overlapping nodes, 
and the points are moved to the new nodes. The resulting selected fiber for each object can be used in logical mathematical operations (and, or, xor, not). 
This allows the use of multiple ROIs (Regions of Interest) to find fibers that connect specific areas while excluding others selected by different areas.

.. autofunction:: start_fibervis