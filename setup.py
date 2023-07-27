import numpy
from setuptools.command.build_ext import new_compiler  # type: ignore
from setuptools import setup, Extension, find_packages
from os.path import exists, getmtime
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()


if new_compiler().compiler_type == "msvc":
    openmp_compile = ["/openmp"]
    openmp_link = []
    fast_math = ["/fp:fast"]
else:
    openmp_compile = ["-fopenmp"]
    openmp_link = ["-fopenmp"]
    fast_math = ["-ffast-math"]

try:
    from Cython.Compiler import Options
    from Cython.Build import cythonize
    Options.fast_fail = True
    cython_ok = True
except ImportError:
    cython_ok = False

def is_up_to_date(c_path, cy_path):
    return getmtime(c_path) >= getmtime(cy_path)

def check_src(c_path):
    base, _ = c_path.rsplit('.', maxsplit=1)
    cy_path = base + ".pyx"
    if exists(c_path):
        if exists(cy_path):
            if is_up_to_date(c_path, cy_path):
                pass
            elif cython_ok:
                cythonize(cy_path)
            else:
                pass # Warning(f"Cython source {cy_path} is more recente than {language} source, but Cython is not present to update it")
    elif cython_ok:
        if exists(cy_path):
            cythonize(cy_path)
        else:
            raise RuntimeError(f"Both source file {c_path} and cython source file {cy_path} are missing.")
    else:
        raise RuntimeError(f"Source file {c_path} missing and Cython is not present.")
    return c_path

ffclust_ext = Extension(
    "phybers.clustering.ffclust.c_wrappers",
    sources=[
        check_src("./src/phybers/clustering/ffclust/c_wrappers.c"),
        "./src/phybers/clustering/ffclust/segmentation.c",
        "./src/phybers/clustering/ffclust/sliceFibers.c",
        "./src/phybers/clustering/ffclust/BundleTools.c"
    ],
    extra_compile_args=openmp_compile + fast_math,
    extra_link_args=openmp_link
)

hclust_ext = Extension(
    "phybers.clustering.hclust.c_wrappers",
    sources=[
        check_src("./src/phybers/clustering/hclust/c_wrappers.cpp"),
        "./src/phybers/clustering/hclust/distances.cpp",
        "./src/phybers/clustering/hclust/BundleTools.cpp"
    ]
)

segmentation_ext = Extension(
    "phybers.segment.fiberseg.c_wrappers",
    sources=[
        check_src("./src/phybers/segment/fiberseg/c_wrappers.cpp"),
        "./src/phybers/segment/fiberseg/main.cpp",
        "./src/phybers/segment/fiberseg/sliceFibers.cpp",
        "./src/phybers/segment/fiberseg/BundleTools.cpp"
    ],
    extra_compile_args=openmp_compile + fast_math,
    extra_link_args=openmp_link
)

deformHCPtoMNI_ext = Extension(
    "phybers.utils.deform.c_wrappers",
    sources=[
        check_src("./src/phybers/utils/deform/c_wrappers.c"),
        "./src/phybers/utils/deform/main.c",
        "./src/phybers/utils/deform/BundleTools.c"
    ],
)

fiberDistanceMax2bun_ext = Extension(
    "phybers.utils.intersection.c_wrappers",
    sources=[
        check_src("./src/phybers/utils/intersection/c_wrappers.c"),
        "./src/phybers/utils/intersection/fiberDistanceMax2bun.c",
        "./src/phybers/utils/intersection/BundleTools.c"
    ],
)

sliceFibers_ext = Extension(
    "phybers.utils.sampling.c_wrappers",
    sources=[
        check_src("./src/phybers/utils/sampling/c_wrappers.c"),
        "./src/phybers/utils/sampling/sliceFibers.c",
        "./src/phybers/utils/sampling/BundleTools.c"
    ],
)

postprocessing_ext = Extension(
    "phybers.utils.postprocessing.c_wrappers",
    sources=[
        check_src("./src/phybers/utils/postprocessing/c_wrappers.cpp"),
        "./src/phybers/utils/postprocessing/dbindex.cpp",
        "./src/phybers/utils/postprocessing/BundleTools.cpp"
    ],
    extra_compile_args=openmp_compile + fast_math,
    extra_link_args=openmp_link
)

fibervis_ext = Extension("phybers.fibervis.FiberVis_core.FiberVis_core",
                         sources=["./src/phybers/fibervis/FiberVis_core/FiberVis_core.c",
                                  "./src/phybers/fibervis/FiberVis_core/bundleMethods.c",
                                  "./src/phybers/fibervis/FiberVis_core/PointOctree.c",
                                  "./src/phybers/fibervis/FiberVis_core/AtlasBasedParallelSegmentation.c",
                                  "./src/phybers/fibervis/FiberVis_core/miscellaneous.c"],
                         include_dirs=[numpy.get_include()],
                         extra_compile_args=openmp_compile,
                         extra_link_args=openmp_link
)

setup(
    name="phybers",
    version="0.1.0b",
    description="Integration of multiple tractography and neural-fibers related tools and algorithms.",
    url="https://github.com/phybers/phybers",
    author="Gonzalo Sabat, L. Liset Gonzales, Alejandro Cofre",
    author_email="phybers.dmris@gmail.com",
    license="GNU",
    classifiers=['Development Status :: 4 - Beta'],
    install_requires=[
        "numpy",
        "dipy",
        "joblib",
        "matplotlib",
        "scikit-learn",
        "networkx",
        "pandas",
        "PyQt5",
        "PyOpenGL",
        "PyOpenGL_accelerate",
        "nibabel",
        "pydicom",
        "scikit-image",
        "scipy",
        "openpyxl",
        "regex"
    ],
    package_dir={'': "src"},
    packages=find_packages(where="./src", exclude=['phybers.fibervis_backup', 'phybers.phyexample']),
    ext_modules=[
        ffclust_ext,
        hclust_ext,
        segmentation_ext,
        deformHCPtoMNI_ext,
        fiberDistanceMax2bun_ext,
        sliceFibers_ext,
        postprocessing_ext,
        fibervis_ext
    ],
    include_package_data=True,
    package_data={
        "phybers.fibervis": ["shaders/*"],
        "phybers.fibervis.ui": ["Segmentations/*", "Settings/*", "*.ui"],
        "phybers.clustering.ffclust": ["*.jpg"],
        "phybers.clustering.hclust": ["data/*"],
        "phybers.segment": ["fiberseg/data/*"],
        "phybers.utils.intersection": ["data/Inter2bundles/*"],
        "phybers":["phyexample/*"]
    },
    exclude_package_data={'phybers.clustering': ["*.c", "*.cpp", "*.h", "*.hpp"]},
    include_dirs=[numpy.get_include()],
    zip_safe=False,
    entry_points={
        'gui_scripts': [
            'FiberVis = phybers.fibervis.FiberVis:main'
        ]
    },
    long_description=long_description,
    long_description_content_type='text/markdown'
)