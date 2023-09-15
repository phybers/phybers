# Overview of Phybers
Phybers is a Python library that shared several tools for cerebral tractography analysis. With the aim of improving its usability, the library has been separated into 4 primary modules:
*Segmentation*, *Clustering*, *Utils* and *Visualization*. To find details about the usage of each module, please refer to the [Phybers documentation][pageweb]

## Prerequisites for installation
Phybers can be executed on both Windows and Ubuntu platforms. It has been tested on both OS with Python 3.9 and 3.11 versions.
For running on Windows, make sure you have Microsoft Visual C++ 14.0 or a later version installed, which can be found at the [Visual Studio Website](https://visualstudio.microsoft.com/visual-cpp-build-tools)

## Installation
To install Phybers, it is recommended to create a Python environment. If you are using Anaconda, follow the instructions below for Windows and Ubuntu, respectively:

1. Open a terminal and execute the following command to create a new Python environment, where "environment_name" is the name you want for your environment, and "x.x" corresponds to the Python version you wish to use:

>``` conda create -n environment_name python=x.x```

2. To activate the environment, run:

>``` conda activate environment_name```

3. To deactivate the environment when you are finished, run:
   
>``` conda deactivate```

To install the Phybers package, activate the environment and run the following command:

>``` pip install phybers```


[pageweb]: <https://phybers.github.io/phybers/>
