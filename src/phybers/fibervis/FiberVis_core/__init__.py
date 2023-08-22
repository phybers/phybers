from typing import Callable
from array import array


readTrkHeader: Callable[[str], dict]
readTrkBody: Callable[[str], dict]
readTrk: Callable[[str], dict]
readBundle: Callable[[str, int, array, int], dict]
readTck: Callable[[str], dict]
applyMatrix: Callable[[array, array], None]
reCalculateNormals: Callable[[array, array, array, int], None]
inPlaceSegmentationMethod: Callable[[int, int, array, array, array], None]
ROIsSegmentationPopulateAndDefragmentPool: Callable[[array, int, array, int, array, array, array], int]
ROIsSegmentationQueryOctree: Callable[[int, array, array, array, array, array, array, int], None]
ROISegmentationCreateEBO: Callable[[int, array, array, array, int], int]
ROISegmentationExportBundlesdata: Callable[[str, int, array, array, array, array, array], None]
AtlasBasedSegmentation: Callable[[array, int, array, int, int, array, array, array], None]
AtlasBasedSegmentationExportbundlesdata: Callable[[str, int, array, array, array, int, array], None]
reSampleBundle: Callable[[array, array, int, array, int], None]
ffclust: Callable[[int, array, array, float, int, int], array]

from .FiberVis_core import readTrkHeader,\
    readTrkBody,\
    readTrk,\
    readBundle,\
    readTck,\
    applyMatrix,\
    reCalculateNormals,\
    inPlaceSegmentationMethod,\
    ROIsSegmentationPopulateAndDefragmentPool,\
    ROIsSegmentationQueryOctree,\
    ROISegmentationCreateEBO,\
    ROISegmentationExportBundlesdata,\
    AtlasBasedSegmentation,\
    AtlasBasedSegmentationExportbundlesdata,\
    reSampleBundle,\
    ffclust
