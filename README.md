# Overview of Phybers
Phybers is a Python library that shared several tools for cerebral tractography analysis. With the aim of improving its usability, the library has been separated into 4 primary modules:
`1. Segmentation`
`2. Clustering`
`3. Utils`
`4.Visualization`

## Work formats
MRI data in NIFTI format (`.nii`/`.nii.gz`) and cerebral tractography in `.bundles` format are taken as input/output by the segmentation, clustering, and utilities modules.
## Prerequisites for installation
Phybers can be executed on both Windows and Ubuntu platforms. It has been tested on both OS with Python 3.9 versions.
For running on Windows, make sure you have Microsoft Visual C++ 14.0 or a later version installed, which can be found at the [Visual Studio Website](https://visualstudio.microsoft.com/visual-cpp-build-tools)

To install Phybers on Windows, run the following command:
>```$ pip install phybers```

To install Phybers on Ubuntu, run the following command:
>```$ python3 -m pip install phybers```

[Pg2012]: <https://doi.org/10.1016/j.neuroimage.2012.02.071>
[LN2017]: <https://link.springer.com/article/10.1007/s12021-016-9316-7>
[An2019]: <https://doi.org/10.1109/ISBI.2019.8759208>
[cl2017]: <https://doi.org/10.3389/fninf.2017.00073>
[cl2022]: <https://doi.org/10.1016/j.neuroimage.2022.119550>
[va2020]: <https://doi.org/10.1016/j.neuroimage.2020.117070>
