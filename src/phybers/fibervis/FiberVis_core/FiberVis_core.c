#ifndef FIBERVIS_CORE_H
#define FIBERVIS_CORE_H

#include <Python.h>
#include <numpy/arrayobject.h>

#include "bundleMethods.h"
#include "miscellaneous.h"
#include "PointOctree.h"
#include "InPlaceSegmentationMethod.h"
#include "AtlasBasedParallelSegmentation.h"
// #include "ffclust.h"


//#include "test.h"

static PyObject* pyReCalculateNormals(PyObject* self, PyObject* args) {
	PyArrayObject* points;
	PyArrayObject* normals;
	PyArrayObject* fiberSizes;
	int n_count;

	if (!PyArg_ParseTuple(args,"OOOi",&points,&normals,&fiberSizes,&n_count))
		return NULL;

	float * points_p = (float *) PyArray_DATA(points);
	float * normals_p = (float *) PyArray_DATA(normals);
	int * fibersize = (int *) PyArray_DATA(fiberSizes);

	float normal[3] = {1.0, 1.0, 1.0};
	float norma = 1.0;

	for (int i=0; i<n_count; i++) {
		for (int j=0; j<fibersize[i]-1; j++) {
			normal[0] = points_p[j*3+3] - points_p[ j*3 ];
			normal[1] = points_p[j*3+4] - points_p[j*3+1];
			normal[2] = points_p[j*3+5] - points_p[j*3+2];
			norma = (float) sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

			*(normals_p++) = normal[0]/norma;
			*(normals_p++) = normal[1]/norma;
			*(normals_p++) = normal[2]/norma;
		}

		*(normals_p++) = normal[0]/norma;
		*(normals_p++) = normal[1]/norma;
		*(normals_p++) = normal[2]/norma;
		points_p += fibersize[i]*3;
	}

	return Py_None;
}

static PyObject* pyReadBundle(PyObject *self, PyObject* args) {
	char * fileDataPath;
	int n_count;
	PyArrayObject * bundlesInterval;
	int nBundles;

	if (!PyArg_ParseTuple(args, "siOi", &fileDataPath, &n_count, &bundlesInterval, &nBundles))
		return NULL;

	unsigned long fileSize;
	FILE *fp;
	fp = fopen(fileDataPath, "rb");
	fseek(fp, 0L, SEEK_END);
	fileSize = ftell(fp);
	fclose(fp);

	npy_intp dims[1];

	dims[0] = fileSize/4-n_count;
	PyObject* points = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	PyObject* normals = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	dims[0] /= 3;
	PyObject* color = PyArray_ZEROS(1,dims,NPY_INT32,0);

	dims[0] += n_count;
	PyObject* elements = PyArray_SimpleNew(1,dims,NPY_UINT32);
	dims[0] = n_count;
	PyObject* fiberSizes = PyArray_SimpleNew(1,dims,NPY_INT32);

	readBundleFile(fileDataPath,
			PyArray_DATA(points),
			PyArray_DATA(normals),
			PyArray_DATA(color),
			PyArray_DATA(elements),
			PyArray_DATA(fiberSizes),
			PyArray_DATA(bundlesInterval),
			n_count,
			nBundles);

	return Py_BuildValue("{s:S,s:S,s:S,s:S,s:S}",
							"points",points,
							"normals",normals,
							"color",color,
							"elements",elements,
							"fiberSizes",fiberSizes);
}


static PyObject* pyReadTrkHeader(PyObject* self, PyObject* args) {

	char * filePath;

	if (!PyArg_ParseTuple(args,"s", &filePath))
		return NULL;
	
	trkHeader header = readTrkHeader(filePath);


	char * headerToDict = "{s:s,s:[i,i,i],s:[f,f,f],s:[f,f,f],s:i,s:S,s:i,s:S,s:S,s:S,s:S,s:S,s:S,s:i,s:i,s:i}";
	PyObject *pyScalarNames = Py_BuildValue("[s,s,s,s,s,s,s,s,s,s]", header.scalar_name[0],header.scalar_name[1],header.scalar_name[2],header.scalar_name[3],header.scalar_name[4],header.scalar_name[5],header.scalar_name[6],header.scalar_name[7],header.scalar_name[8],header.scalar_name[9]);
	PyObject *pyPropertyNames = Py_BuildValue("[s,s,s,s,s,s,s,s,s,s]", header.property_name[0],header.property_name[1],header.property_name[2],header.property_name[3],header.property_name[4],header.property_name[5],header.property_name[6],header.property_name[7],header.property_name[8],header.property_name[9]);

	npy_intp dims[2];

	dims[0] = 3;
	PyObject *pyDim = PyArray_SimpleNew(1,dims,NPY_INT16);
	memcpy(PyArray_DATA(pyDim),header.dim,3*sizeof(int));
	PyObject *pyVoxelSize = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyVoxelSize),header.voxel_size,3*sizeof(float));
	PyObject *pyOrigin = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyOrigin),header.origin,3*sizeof(float));

	dims[0] = 4;
	dims[1] = 4;
	PyObject *pyVoxToRas = PyArray_SimpleNew(2,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyVoxToRas),header.vox_to_ras,16*sizeof(float));

	PyObject *pyVoxelOrder = PyArray_SimpleNew(1,dims,NPY_INT8);
	memcpy(PyArray_DATA(pyVoxelOrder),header.voxel_order,4*sizeof(char));

	PyObject *pyPad2 = PyArray_SimpleNew(1,dims,NPY_INT8);;
	memcpy(PyArray_DATA(pyPad2),header.pad2,4*sizeof(char));

	dims[0] = 6;
	PyObject *pyImageOrientationPatient = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyImageOrientationPatient),header.image_orientation_patient,6*sizeof(float));

	dims[0] = 2;
	PyObject *pyPad1 = PyArray_SimpleNew(1,dims,NPY_INT8);
	memcpy(PyArray_DATA(pyPad1),header.pad1,2*sizeof(char));

	return Py_BuildValue(headerToDict,
						"id_string", header.id_string,
						"dim", pyDim,
						"voxel_size", pyVoxelSize,
						"origin",pyOrigin,
						"n_scalars", header.n_scalars,
						"scalar_name", pyScalarNames,
						"n_properties", header.n_properties,
						"property_name", pyPropertyNames,
						"vox_to_ras", pyVoxToRas,
						"voxel_order", pyVoxelOrder,
						"pad2", pyPad2,
						"image_orientation_patient", pyImageOrientationPatient,
						"pad1", pyPad1,
						"n_count", header.n_count,
						"version", header.version,
						"hdr_size", header.hdr_size);
}


static PyObject* pyReadTrkBody(PyObject* self, PyObject* args) {
	char* filePath;

	if (!PyArg_ParseTuple(args,"s",&filePath))
		return NULL;

	unsigned long fileSize;
	FILE *fp;
	fp = fopen(filePath, "rb");

	trkHeader headerBuffer;
	fread(&headerBuffer, 1, sizeof(trkHeader), fp);

	fseek(fp, 0L, SEEK_END);
	fileSize = ftell(fp)-headerBuffer.hdr_size;
	fclose(fp);

	unsigned int size = (fileSize/4-headerBuffer.n_count*(headerBuffer.n_properties+1))*3/(3+headerBuffer.n_scalars);

	// Create numpy data
	npy_intp dims[2];
	dims[0] = size;
	PyObject* points = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	PyObject* normals = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	dims[0] = size/3;
	PyObject* color = PyArray_ZEROS(1,dims,NPY_INT32,0);

	dims[0] = size/3+headerBuffer.n_count;
	PyObject* elements = PyArray_SimpleNew(1,dims,NPY_UINT32);
	dims[0] = headerBuffer.n_count;
	PyObject* fiberSizes = PyArray_SimpleNew(1,dims,NPY_INT32);

	dims[0] = size/3*headerBuffer.n_scalars;
	PyObject* scalars = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	dims[0] = headerBuffer.n_count*headerBuffer.n_properties;
	PyObject* properties = PyArray_SimpleNew(1,dims,NPY_FLOAT32);


	// Read into the memory blocks
	readTrkBody(filePath, 
			headerBuffer.hdr_size, 
			headerBuffer.n_scalars,
			headerBuffer.n_properties,
			PyArray_DATA(points), 
			PyArray_DATA(normals), 
			PyArray_DATA(elements), 
			PyArray_DATA(fiberSizes), 
			headerBuffer.n_count, 
			PyArray_DATA(scalars),
			PyArray_DATA(properties));

	return Py_BuildValue("{s:S,s:S,s:S,s:S,s:S,s:S,s:S}",
							"points",points,
							"normals",normals,
							"color",color,
							"elements",elements,
							"fiberSizes",fiberSizes,
							"scalars",scalars,
							"properties",properties);
}

static PyObject* pyReadTrk(PyObject* self, PyObject* args) {
	char* filePath;

	if (!PyArg_ParseTuple(args,"s",&filePath))
		return NULL;

	unsigned long fileSize;
	FILE *fp;
	fp = fopen(filePath, "rb");

	trkHeader header;
	fread(&header, 1, sizeof(trkHeader), fp);

	fseek(fp, 0L, SEEK_END);
	fileSize = ftell(fp)-header.hdr_size;
	fclose(fp);

	unsigned int size = (fileSize/4-header.n_count*(header.n_properties+1))*3/(3+header.n_scalars);

	// Create numpy data
	// Header
	char * headerToDict = "{s:s,s:O,s:O,s:O,s:i,s:S,s:i,s:S,s:S,s:S,s:S,s:S,s:S,s:i,s:i,s:i}";
	PyObject *pyScalarNames = Py_BuildValue("[s,s,s,s,s,s,s,s,s,s]", header.scalar_name[0],header.scalar_name[1],header.scalar_name[2],header.scalar_name[3],header.scalar_name[4],header.scalar_name[5],header.scalar_name[6],header.scalar_name[7],header.scalar_name[8],header.scalar_name[9]);
	PyObject *pyPropertyNames = Py_BuildValue("[s,s,s,s,s,s,s,s,s,s]", header.property_name[0],header.property_name[1],header.property_name[2],header.property_name[3],header.property_name[4],header.property_name[5],header.property_name[6],header.property_name[7],header.property_name[8],header.property_name[9]);

	npy_intp dims[2];

	dims[0] = 3;
	PyObject *pyDim = PyArray_SimpleNew(1,dims,NPY_INT16);
	memcpy(PyArray_DATA(pyDim),header.dim,3*sizeof(int));
	PyObject *pyVoxelSize = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyVoxelSize),header.voxel_size,3*sizeof(float));
	PyObject *pyOrigin = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyOrigin),header.origin,3*sizeof(float));

	dims[0] = 4;
	dims[1] = 4;
	PyObject *pyVoxToRas = PyArray_SimpleNew(2,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyVoxToRas),header.vox_to_ras,16*sizeof(float));

	PyObject *pyVoxelOrder = PyArray_SimpleNew(1,dims,NPY_INT8);
	memcpy(PyArray_DATA(pyVoxelOrder),header.voxel_order,4*sizeof(char));

	PyObject *pyPad2 = PyArray_SimpleNew(1,dims,NPY_INT8);;
	memcpy(PyArray_DATA(pyPad2),header.pad2,4*sizeof(char));

	dims[0] = 6;
	PyObject *pyImageOrientationPatient = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	memcpy(PyArray_DATA(pyImageOrientationPatient),header.image_orientation_patient,6*sizeof(float));

	dims[0] = 2;
	PyObject *pyPad1 = PyArray_SimpleNew(1,dims,NPY_INT8);
	memcpy(PyArray_DATA(pyPad1),header.pad1,2*sizeof(char));

	// Body
	dims[0] = size;
	PyObject* points = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	PyObject* normals = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	dims[0] = size/3;
	PyObject* color = PyArray_ZEROS(1,dims,NPY_INT32,0);

	dims[0] = size/3+header.n_count;
	PyObject* elements = PyArray_SimpleNew(1,dims,NPY_UINT32);
	dims[0] = header.n_count;
	PyObject* fiberSizes = PyArray_SimpleNew(1,dims,NPY_INT32);

	dims[0] = size/3*header.n_scalars;
	PyObject* scalars = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	dims[0] = header.n_count*header.n_properties;
	PyObject* properties = PyArray_SimpleNew(1,dims,NPY_FLOAT32);


	// Read into the memory blocks
	readTrkBody(filePath, 
			header.hdr_size, 
			header.n_scalars,
			header.n_properties,
			PyArray_DATA(points), 
			PyArray_DATA(normals), 
			PyArray_DATA(elements), 
			PyArray_DATA(fiberSizes), 
			header.n_count, 
			PyArray_DATA(scalars),
			PyArray_DATA(properties));

	PyObject* pyHeader = Py_BuildValue(headerToDict,
							"id_string", header.id_string,
							"dim", pyDim,
							"voxel_size", pyVoxelSize,
							"origin",pyOrigin,
							"n_scalars", header.n_scalars,
							"scalar_name", pyScalarNames,
							"n_properties", header.n_properties,
							"property_name", pyPropertyNames,
							"vox_to_ras", pyVoxToRas,
							"voxel_order", pyVoxelOrder,
							"pad2", pyPad2,
							"image_orientation_patient", pyImageOrientationPatient,
							"pad1", pyPad1,
							"n_count", header.n_count,
							"version", header.version,
							"hdr_size", header.hdr_size);

	return Py_BuildValue("{s:S,s:S,s:S,s:S,s:S,s:S,s:S,s:S}",
							"header", pyHeader,
							"points",points,
							"normals",normals,
							"color",color,
							"elements",elements,
							"fiberSizes",fiberSizes,
							"scalars",scalars,
							"properties",properties);
}

// // Based in https://mrtrix.readthedocs.io/en/latest/getting_started/image_data.html?highlight=format#tracks-file-format-tck
// // and https://github.com/scilus/fibernavigator/blob/master/src/dataset/Fibers.cpp
static PyObject * pyReadTck(PyObject* self, PyObject* args) {
	char *filePath;

	if(!PyArg_ParseTuple(args, "s", &filePath))
		return NULL;

	int n_count;
	unsigned long fileSize;
	int headerSize;

	FILE *fp;
	fp = fopen(filePath, "rb");

	// tmp the fixed size n
	int n = 1000;
	char headerSizeFound = 0, countFound = 0;
	char * headerBuffer = (char*) malloc(n*sizeof(char));

	do {
		fread(headerBuffer, n, sizeof(char), fp);

		if (strstr(headerBuffer, "file:") != NULL) {
			sscanf(strstr(headerBuffer, "file:"), "file: . %d", &headerSize);
			headerSizeFound = 1;
		}

		if (strstr(headerBuffer, "count:") != NULL) {
			sscanf(strstr(headerBuffer, "count:"), "count: %d", &n_count);
			countFound = 1;
		}

	} while (strstr(headerBuffer, "END") == NULL);


	fseek(fp, 0L, SEEK_END);
	fileSize = ftell(fp) - headerSize;

	if (countFound != 1 || headerSizeFound != 1) {
		fclose(fp);
		return NULL;
	}

	// Read fibers
	unsigned long size = (fileSize-12-12*n_count)/4;

	npy_intp dims[1];
	dims[0] = size;
	PyObject* points = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	PyObject* normals = PyArray_SimpleNew(1,dims,NPY_FLOAT32);
	dims[0] = size/3;
	PyObject* color = PyArray_ZEROS(1,dims,NPY_INT32,0);

	dims[0] = size/3+n_count;
	PyObject* elements = PyArray_SimpleNew(1,dims,NPY_UINT32);
	dims[0] = n_count;
	PyObject* fiberSizes = PyArray_SimpleNew(1,dims,NPY_INT32);

	float * points_p = (float*) PyArray_DATA(points);
	float * normals_p = (float*) PyArray_DATA(normals);

	unsigned int * ebo = (unsigned int*) PyArray_DATA(elements);
	int * fibersize = (int *) PyArray_DATA(fiberSizes);

	// open tck file
	fseek(fp, headerSize, SEEK_SET);

	unsigned index = 0;
	float normal[3] = {1.0, 1.0, 1.0};
	float norma = 1.0;

	float tmpVertex[3];

	for (int i=0; i<n_count; i++) {
		for(fread(tmpVertex, 3, sizeof(float), fp); *(unsigned int*)tmpVertex != 0x7fc00000/* && tmpVertex[0] != INF*/; fread(tmpVertex, 3, sizeof(float), fp)) {
			memcpy(points_p+fibersize[i]*3, tmpVertex, sizeof(float)*3);

			fibersize[i]++;
		}

		for (int k=0; k<fibersize[i] - 1; k++) {
			*(ebo++) = index++;

			normal[0] = points_p[k*3+3] - points_p[ k*3 ];
			normal[1] = points_p[k*3+4] - points_p[k*3+1];
			normal[2] = points_p[k*3+5] - points_p[k*3+2];
			norma = (float) sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

			*(normals_p++) = normal[0]/norma;
			*(normals_p++) = normal[1]/norma;
			*(normals_p++) = normal[2]/norma;
		}

		*(ebo++) = index++;
		*(ebo++) = 0xFFFFFFFF;

		*(normals_p++) = normal[0]/norma;
		*(normals_p++) = normal[1]/norma;
		*(normals_p++) = normal[2]/norma;
		points_p += fibersize[i]*3;
	}


	fclose(fp);

	// return Py_BuildValue("(iii)",n_count, fileSize, headerSize);
	return Py_BuildValue("{s:i,s:S,s:S,s:S,s:S,s:S}",
							"n_count", n_count,
							"points",points,
							"normals",normals,
							"color",color,
							"elements",elements,
							"fiberSizes",fiberSizes);
}


static PyObject* pyApplyMatrix(PyObject * self, PyObject* args) {
	PyArrayObject * points;
	PyArrayObject * mat4;

	if (!PyArg_ParseTuple(args, "OO", &points, &mat4))
		return NULL;

	npy_intp size = PyArray_SIZE(points);

	float * points_p = (float *) PyArray_DATA(points);
	float * matrix4 = (float *) PyArray_DATA(mat4);

	float tmp[3];

	for (unsigned i=0; i<size; i+= 3) 
		vec3MultiplyBy4x4Matrix(points_p+i, matrix4, tmp);

	return Py_None;
}


//=======================================================================================================//
//-----------------------------------------In Place segmentation-----------------------------------------//

static PyObject* pyInPlaceSegmentationMethod(PyObject* self, PyObject* args) {
	int bundleN;
	int percentage;
	PyArrayObject* pyBundleStart;
	PyArrayObject* pySelectedBundles;
	PyArrayObject* pyFiberValidator;

	if (!PyArg_ParseTuple(args,"iiOOO",&bundleN,&percentage,&pyBundleStart,&pySelectedBundles,&pyFiberValidator))
		return NULL;

	inPlaceSegmentationMethod(bundleN,
							percentage,
							PyArray_DATA(pyBundleStart),
							PyArray_DATA(pySelectedBundles),
							PyArray_DATA(pyFiberValidator));


	return Py_None;
}

//=======================================================================================================//
//-------------------------------------------OCTREE segmentation-----------------------------------------//

static PyObject* pyROIsSegmentationPopulateAndDefragmentPool(PyObject* self, PyObject* args) {
	PyArrayObject* pool;
	int poolSize;
	PyArrayObject* vertices;
	int verticesSize;
	PyArrayObject* center;
	PyArrayObject* radius;
	PyArrayObject* verticesIdxPool;

	if (!PyArg_ParseTuple(args,"OiOiOOO",&pool,&poolSize,&vertices,&verticesSize,&center,&radius,&verticesIdxPool))
		return NULL;

	int n = ROIsSegmentationPopulateAndDefragmentPool(PyArray_DATA(pool),
														poolSize,
														PyArray_DATA(vertices),
														verticesSize,
														PyArray_DATA(center),
														PyArray_DATA(radius),
														PyArray_DATA(verticesIdxPool));

	return Py_BuildValue("I",n);
}

static PyObject* pyROIsSegmentationQueryOctree(PyObject* self, PyObject* args) {
	int n_rois;
	PyArrayObject* rois;
	PyArrayObject* pool;
	PyArrayObject* verticesIdxPool;
	PyArrayObject* verticesIdx2FiberIdx;
	PyArrayObject* vertices;
	PyArrayObject* results;
	int n_count;

	if (!PyArg_ParseTuple(args,"iOOOOOOi",&n_rois,&rois,&pool,&verticesIdxPool,&verticesIdx2FiberIdx,&vertices,&results,&n_count))
		return NULL;

	queryTree(n_rois,
			PyArray_DATA(rois),
			PyArray_DATA(pool),
			PyArray_DATA(verticesIdxPool),
			PyArray_DATA(verticesIdx2FiberIdx),
			PyArray_DATA(vertices),
			PyArray_DATA(results),
			n_count);

	return Py_None;
}

// I did not find where this function was being called, it might be deprecated
static PyObject* pyROISegmentationCreateEBO(PyObject* self, PyObject* args) {
	int a;
	PyArrayObject* b;
	PyArrayObject* c;
	PyArrayObject* d;
	int e;

	if (!PyArg_ParseTuple(args,"iOOOi",&a,&b,&c,&d,&e))
		return NULL;

	int f = createEBO(a,
					PyArray_DATA(b),
					PyArray_DATA(c),
					PyArray_DATA(d),
					e);

	return Py_BuildValue("i", f);
}

static PyObject* pyROISegmentationExportBundlesdata(PyObject* self, PyObject* args) {
	char* filePath;
	int n_bundles;
	PyArrayObject* bundlesStart;
	PyArrayObject* fiberSizes;
	PyArrayObject* bundleCount;
	PyArrayObject* points;
	PyArrayObject* fiberValidator;

	if (!PyArg_ParseTuple(args,"siOOOOO",&filePath,&n_bundles,&bundlesStart,&fiberSizes,&bundleCount,&points,&fiberValidator))
		return NULL;

	ROISegmentationExportbundlesdata(filePath,
									n_bundles,
									PyArray_DATA(bundlesStart),
									PyArray_DATA(fiberSizes),
									PyArray_DATA(bundleCount),
									PyArray_DATA(points),
									PyArray_DATA(fiberValidator));

	return Py_None;
}

static PyObject* pyAtlasBasedParallelSegmentation(PyObject* self, PyObject* args) {
	PyArrayObject* atlasData;
	unsigned int atlasDataSize;
	PyArrayObject* subjectData;
	unsigned int subjectDataSize;
	unsigned short int nDataFiber;
	PyArrayObject* thresholds;
	PyArrayObject* bundleOfFiber;
	PyArrayObject* assignment;

	if (!PyArg_ParseTuple(args,"OIOIHOOO",&atlasData,&atlasDataSize,&subjectData,&subjectDataSize,&nDataFiber,&thresholds,&bundleOfFiber,&assignment))
		return NULL;

	AtlasBasedParallelSegmentation(PyArray_DATA(atlasData),
								atlasDataSize,
								PyArray_DATA(subjectData),
								subjectDataSize,
								nDataFiber,
								PyArray_DATA(thresholds),
								PyArray_DATA(bundleOfFiber),
								PyArray_DATA(assignment));

	return Py_None;	
}

static PyObject* pyAtlasBasedSegmentationExportbundlesdata(PyObject* self, PyObject* args) {
	char* filePath;
	int bundleN;
	PyArrayObject* pyBundlesSelected;
	PyArrayObject* pyFiberSize;
	PyArrayObject* pyPoints;
	int fiberN;
	PyArrayObject* pyFiberValidator;

	if (!PyArg_ParseTuple(args,"siOOOiO",&filePath,&bundleN,&pyBundlesSelected,&pyFiberSize,&pyPoints,&fiberN,&pyFiberValidator))
		return NULL;

	AtlasBasedSegmentationExportbundlesdata(filePath,
										bundleN,
										PyArray_DATA(pyBundlesSelected),
										PyArray_DATA(pyFiberSize),
										PyArray_DATA(pyPoints),
										fiberN,
										PyArray_DATA(pyFiberValidator));

	return Py_None;
}

static PyObject* pyReSampleBundle(PyObject* self, PyObject* args) {
	PyArrayObject* pyInPoints;
	PyArrayObject * pyInFiberSize; 
	int curvesCount;
	PyArrayObject * pyOutPoints; 
	int newFiberSize;

	if (!PyArg_ParseTuple(args,"OOiOi",&pyInPoints,&pyInFiberSize,&curvesCount,&pyOutPoints,&newFiberSize))
		return NULL;

	reSampleBundle(PyArray_DATA(pyInPoints), 
				PyArray_DATA(pyInFiberSize), 
				curvesCount, 
				PyArray_DATA(pyOutPoints), 
				newFiberSize);

	return Py_None;
}

static PyObject* pyFfclust(PyObject* self, PyObject* args) {
	unsigned int n_points;
	PyArrayObject* small_centroids;
	PyArrayObject* large_centroids;
	float thr;
	unsigned int nfibers_subject;
	unsigned int nfibers_atlas;

	if (!PyArg_ParseTuple(args,"IOOfII",&n_points,&small_centroids,&large_centroids,&thr,&nfibers_subject,&nfibers_atlas))
		return NULL;

	int* result_c = segmentation(n_points,
							PyArray_DATA(small_centroids), 
							PyArray_DATA(large_centroids), 
							thr,
							nfibers_subject, 
							nfibers_atlas);

	npy_intp dims[1];
	dims[0] = nfibers_subject;
	PyArrayObject* result = PyArray_SimpleNew(1,dims,NPY_INT32);
	memcpy(PyArray_DATA(result),result_c,nfibers_subject);

	return result;
}


static PyMethodDef myMethods[] = {
	{"readTrkHeader", pyReadTrkHeader, METH_VARARGS, "Testing reading of trk file."},
	{"readTrkBody", pyReadTrkBody, METH_VARARGS, "Testing read of trk body file."},
	{"readTrk", pyReadTrk, METH_VARARGS, "Returns a dict with header and data"},
	{"readBundle", pyReadBundle, METH_VARARGS, "Returns a dict with header and data"},
	{"readTck", pyReadTck, METH_VARARGS, "Returns a dict with points data and n_count"},
	{"applyMatrix", pyApplyMatrix, METH_VARARGS, "Applies a mat4 to a set of points in 3D (on a numpy)."},
	{"reCalculateNormals", pyReCalculateNormals, METH_VARARGS, "Recalculates normals given the point, normals, fibersizes arrays and n_count."},
	{"inPlaceSegmentationMethod",pyInPlaceSegmentationMethod,METH_VARARGS,"In place segmentation for selected bundles and percentage selection"},
	{"ROIsSegmentationPopulateAndDefragmentPool",pyROIsSegmentationPopulateAndDefragmentPool,METH_VARARGS,"optimization methods"},
	{"ROIsSegmentationQueryOctree",pyROIsSegmentationQueryOctree,METH_VARARGS,"Query the octree with the rois"},
	{"ROISegmentationCreateEBO",pyROISegmentationCreateEBO,METH_VARARGS,"no idea if it is used."},
	{"ROISegmentationExportBundlesdata",pyROISegmentationExportBundlesdata,METH_VARARGS,"Exportation function"},
	{"AtlasBasedSegmentation",pyAtlasBasedParallelSegmentation,METH_VARARGS,"Segmentation of a dataset using an atlas."},
	{"AtlasBasedSegmentationExportbundlesdata",pyAtlasBasedSegmentationExportbundlesdata,METH_VARARGS,"Export function using fibervalidator vector."},
	{"reSampleBundle", pyReSampleBundle, METH_VARARGS, "Samples a bundle file to have a "},
	{"ffclust", pyFfclust, METH_VARARGS,"FFCLUST"},
	{NULL,NULL,0,NULL}
};


static struct PyModuleDef FiberVis_core = {
	PyModuleDef_HEAD_INIT,
	"FiberVis_core",
	"FiberVis tool module",
	-1,
	myMethods
};


PyMODINIT_FUNC PyInit_FiberVis_core(void) {
	/* Load `numpy` functionality. */
	import_array();

	return PyModule_Create(&FiberVis_core);
}

#endif