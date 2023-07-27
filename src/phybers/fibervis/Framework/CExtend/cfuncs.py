import ctypes
import os

os.add_dll_directory(os.path.abspath("./Framework/CExtend/"))

funcs_lib = ctypes.windll.LoadLibrary(os.path.abspath("./Framework/CExtend/bundleCFunctions.so"))

# ------------------------ BUNDLES OBJECT------------------------
# Bundles read function
readBundleFile = funcs_lib.readBundleFile

readBundleFile.argtypes = (
		ctypes.c_char_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_int)

# Fiber trk read function
readTrkHeader = funcs_lib.readTrkHeader

readTrkHeader.argtypes = (
	ctypes.c_char_p,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p)

readTrkHeader.restypes = ctypes.c_int


readTrkBody = funcs_lib.readTrkBody

readTrkBody.argtypes = (
	ctypes.c_char_p, 
	ctypes.c_int, 
	ctypes.c_int, 
	ctypes.c_int, 
	ctypes.c_void_p, 
	ctypes.c_void_p, 
	ctypes.c_void_p, 
	ctypes.c_void_p, 
	ctypes.c_int, 
	ctypes.c_void_p,
	ctypes.c_void_p)

# Fiber tck read function
readTckHeader = funcs_lib.readTckHeader

readTckHeader.argtypes = (
	ctypes.c_char_p, 
	ctypes.c_void_p, 
	ctypes.c_void_p, 
	ctypes.c_void_p)

readTckHeader.restypes = ctypes.c_int

readTckBody = funcs_lib.readTckBody

readTckBody.argtypes = (
	ctypes.c_char_p, 
    ctypes.c_int, 
    ctypes.c_void_p, 
    ctypes.c_void_p, 
    ctypes.c_void_p, 
    ctypes.c_void_p, 
    ctypes.c_int)

applyMatrix = funcs_lib.applyMatrix

applyMatrix.argtypes = (
	ctypes.c_void_p,
	ctypes.c_int,
	ctypes.c_void_p)

reCalculateNormals = funcs_lib.reCalculateNormals

reCalculateNormals.argtypes = (
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_int)


# # Points to color, normal and element buffer
createVBOAndEBOFromPoints = funcs_lib.createVBOAndEBOFromPoints

createVBOAndEBOFromPoints.argtypes = (
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_int)


# ------------------------ SEGMENTATION INPLACE ------------------------
inPlaceSegmentationMethod = funcs_lib.inPlaceSegmentationMethod
# inPlaceSegmentationMethod = funcs_lib.reservoirSamplingMethod
# inPlaceSegmentationMethod = funcs_lib.reservoirSamplingMethodOpti

inPlaceSegmentationMethod.argtypes = (
	ctypes.c_int,
	ctypes.c_int,
	ctypes.c_void_p,
	ctypes.c_void_p,
	ctypes.c_void_p)

# ------------------------ ROIs SEGMENTATION ------------------------
# Segmentation ROIs - populate octree pool
ROIsSegmentationPopulateAndDefragmentPool = funcs_lib.ROIsSegmentationPopulateAndDefragmentPool

ROIsSegmentationPopulateAndDefragmentPool.argtypes = (
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p)

ROIsSegmentationPopulateAndDefragmentPool.restypes = ctypes.c_uint


# Segmentation ROIs - query octree
ROIsSegmentationQueryOctree = funcs_lib.queryTree

ROIsSegmentationQueryOctree.argtypes = (
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_int)


# Creating of EBO with validator array
ROISegmentationCreateEBO = funcs_lib.createEBO

ROISegmentationCreateEBO.argtypes = (
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_int)

ROISegmentationCreateEBO.restypes = ctypes.c_int

# Export bundlesdata file ROISegmentation
ROISegmentationExportbundlesdata = funcs_lib.ROISegmentationExportbundlesdata

ROISegmentationExportbundlesdata.argtypes = (
		ctypes.c_char_p,
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p)

# ------------------------ ATLAS BASED SEGMENTATION ------------------------

AtlasBasedSegmentation = funcs_lib.AtlasBasedParallelSegmentation

AtlasBasedSegmentation.argtypes = (
		ctypes.c_void_p,			# float *atlas_data				vector with all the 3d points for the atlas
		ctypes.c_int,				# unsigned int atlas_data_size	size of the vector with all the points for the atlas
		ctypes.c_void_p,			# float *subject_data 			vector with all the 3d points for the subject
		ctypes.c_int,				# unsigned int subject_data_size 	size of the vector with all the points for the subject
		ctypes.c_int,				# unsigned short int ndata_fiber	number of points per fiber (*3) so 21 points = 63
		ctypes.c_void_p,			# unsigned char *thresholds		vector with the thresholds for each fascicle on the atlas
		ctypes.c_void_p,			# unsigned int *bundle_of_fiber	vector of atlas_points_size with id for the fascicle that correspondence
		ctypes.c_void_p)			# unsigned char *assignment 		size nfibers_subject. And all data set to 254 - result vector

# Export bundlesdata file AtlasBasedSegmentation
AtlasBasedSegmentationExportbundlesdata = funcs_lib.AtlasBasedSegmentationExportbundlesdata

AtlasBasedSegmentationExportbundlesdata.argtypes = (
		ctypes.c_char_p,
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_void_p)

# Re sample a database to have n points per fiber
reSampleBundle = funcs_lib.reSampleBundle

reSampleBundle.argtypes = (
		ctypes.c_void_p,
		ctypes.c_void_p,
		ctypes.c_int,
		ctypes.c_void_p,
		ctypes.c_int)


