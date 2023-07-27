# Overview of Phybers
Phybers is a Python library that shared several tools for cerebral tractography analysis. With the aim of improving its usability, the library has been separated into 4 primary modules:
### 1.	Segmentation Module
This module includes a white matter fiber bundle segmentation algorithm (**Guevara et al., 2012; Labra et al., 2017; Vázquez et al., 2019**) based on a multi-subject atlas, which we call **FiberSeg**. It aims to classify the subject fibers according to a multi-subject bundle atlas. The method uses as a measure of similarity between pairs of fibers the maximum Euclidean distance between corresponding points. We provide one atlas of deep white matter (DWM) bundles (**Guevara et al., 2012**) and one atlas of superficial white matter (SWM) bundles (**Roman et al., 2017**). <!--Furthermore, other atlases are available for downloading from the Phybers website, such as a new SWM bundle atlas (**Roman et al. , 2022**), and the DWM and SWM bundle atlas of (Zhang et al., 2018) in the format required by the segmentation algorithm. All the atlases are in the MNI space.
There will be two additional cerebral fiber segmentation algorithms added in future updates. The first one will use a cortical surface atlas (**López-López et al., 2020**), and the second one will utilize an anatomical regions atlas( **Hernan Hernández et al., 2023**).-->
### 2.	Clustering Module
The module comprises two algorithms for clustering cerebral fibers. The first algorithm, **FFClust** (Fast Fiber Clustering, **Vázquez et al., 2020**), is an intra-subject clustering algorithm based in K-means. The aims to identify compact and homogeneous fiber clusters in a large tractography dataset. The second algorithm, **HClust** (Hierarchical Clustering, **Roman et al., 2017, 2022**), is an automatic hierarchical method for identifying reproducible short association of tractography by using distance metrics between fibers, affinity graph and a threshold for dividing the dendrograma. This algorithm is computationally more costly than **FFClust**. However, **HClust** is better for grouping short associations, but **FFClust** is better for long associations. Users should evaluate which method is more convenient depending on their goal.
### 3.	Utilities Module
The module includes useful tools for reading/writing cerebral fibers, sampling 'n' equidistant points, and deforming cerebral fibers to the MNI space. Additionally, there are other tools for assessing the performance of segmentation and clustering algorithms. Some of these tools include determining the intersection between two sets of fibers, calculating intra/inter cluster distances, and computing the db Index metric.
### 4.	Visualization Module
This module contains a visualization algorithm called **FiberVis**. It includes a graphical user interface that allows users to simultaneously visualize multiple MRI slices/volumes in NIfTI format (`.nii`/`.nii.gz`), mesh in (`.mesh`) format, and tractography in (`.bundles`) and TRK formats. Additionally, it features a useful tool for real-time segmentation of cerebral tractography using manual positioning of ROIs.
## Work formats
MRI data in NIFTI format (`.nii`/`.nii.gz`) and cerebral tractography in `.bundles` format are taken as input/output by the segmentation, clustering, and utilities modules.
## Prerequisites for installation
Phybers can be executed on both Windows and Ubuntu platforms. It has been tested on both OS with Python 3.9 versions.
For running on Windows, make sure you have Microsoft Visual C++ 14.0 or a later version installed, which can be found at the [Visual Studio Website](https://visualstudio.microsoft.com/visual-cpp-build-tools)

To install Phybers on Windows, run the following command:
>```$ pip install phybers```

To install Phybers on Ubuntu, run the following command:
>```$ python3 –m pip install phybers```
