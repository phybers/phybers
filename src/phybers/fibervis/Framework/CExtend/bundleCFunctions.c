#include "stdio.h"
#include "math.h"
#include <stdbool.h>
#include "string.h"
#include "stdlib.h"

#ifdef __APPLE__
#include <OpenGL/gl3.h>
#else
#include <GL/gl.h>
#endif

#include "ROISegmentationCFunctions.c"
#include "AtlasBasedParallelSegmentation.c"
#include "InPlaceSegmentation.c"
// #include "ReservoirSampling.c"


// C function for fast read of bundle files
void readBundleFile(char * filePath, 
	void * pyPositions, 
	void * pyNormals, 
	void * pyColors, 
	void * pyEbo, 
	void * pyFiberSize, 
	void * pyBundleStart, 
	int curvesCount, 
	int nBundles) {

	// parse inputs
	GLfloat * positions = (GLfloat *) pyPositions;
	GLfloat * normals = (GLfloat *) pyNormals;
	GLint * colors = (GLint *) pyColors;

	GLuint * ebo = (GLuint *) pyEbo;
	int * fibersize = (int *) pyFiberSize;

	int * bundlestart = (int *) pyBundleStart;

	// open bundledata file
	FILE *fp;
	fp = fopen(filePath, "rb");

	// read data
	unsigned k, index = 0, i, j;
	GLfloat normal[3] = {1.0, 1.0, 1.0};
	GLfloat norma = 1.0;

	for (i=1; i<nBundles; i++) {
		for (j=bundlestart[i-1]; j<bundlestart[i]; j++) {
			fread(&fibersize[j], sizeof(int), 1, fp);
			fread(positions, sizeof(GLfloat), fibersize[j]*3, fp);

			for (k=0; k<fibersize[j] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = positions[k*3+3] - positions[ k*3 ];
				normal[1] = positions[k*3+4] - positions[k*3+1];
				normal[2] = positions[k*3+5] - positions[k*3+2];
				norma = sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

				*(normals++) = normal[0]/norma;
				*(normals++) = normal[1]/norma;
				*(normals++) = normal[2]/norma;

				*(colors++) = (i-1);
			}

			*(ebo++) = index++;
			*(ebo++) = 0xFFFFFFFF;

			*(colors++) = (i-1);

			*(normals++) = normal[0]/norma;
			*(normals++) = normal[1]/norma;
			*(normals++) = normal[2]/norma;
			positions += fibersize[j]*3;
		}
	}

	fclose(fp);
}


void createVBOAndEBOFromPoints(void * pyPositions, 
	void * pyNormals, 
	void * pyColors, 
	void * pyEbo, 
	void * pyFiberSize, 
	void * pyBundleStart, 
	int curvesCount, 
	int nBundles) {

	// parse inputs
	GLfloat * positions = (GLfloat *) pyPositions;
	GLfloat * normals = (GLfloat *) pyNormals;
	GLint * colors = (GLint *) pyColors;

	GLuint * ebo = (GLuint *) pyEbo;
	int * fibersize = (int *) pyFiberSize;

	int * bundlestart = (int *) pyBundleStart;

	// read data
	unsigned k, index = 0, i, j;
	GLfloat normal[3] = {1.0, 1.0, 1.0};
	GLfloat norma = 1.0;

	for (i=1; i<nBundles; i++) {
		for (j=bundlestart[i-1]; j<bundlestart[i]; j++) {

			for (k=0; k<fibersize[j] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = positions[k*3+3] - positions[ k*3 ];
				normal[1] = positions[k*3+4] - positions[k*3+1];
				normal[2] = positions[k*3+5] - positions[k*3+2];
				norma = sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

				*(normals++) = normal[0]/norma;
				*(normals++) = normal[1]/norma;
				*(normals++) = normal[2]/norma;

				*(colors++) = (i-1);
			}

			*(ebo++) = index++;
			*(ebo++) = 0xFFFFFFFF;

			*(colors++) = (i-1);

			*(normals++) = normal[0]/norma;
			*(normals++) = normal[1]/norma;
			*(normals++) = normal[2]/norma;
			positions += fibersize[j]*3;
		}
	}
}


struct trkHeader {
	char id_string[6];					// ID string for track file. The first 5 characters must be "TRACK".
	short int dim[3];					// Dimension of the image volume.
	float voxel_size[3];				// Voxel size of the image volume.
	float origin[3];					// Origin of the image volume. This field is not yet being used by TrackVis. That means the origin is always (0, 0, 0).
	short int n_scalars;				// Number of scalars saved at each track point (besides x, y and z coordinates).
	char scalar_name[10][20];			// Name of each scalar. Can not be longer than 20 characters each. Can only store up to 10 names.
	short int n_properties;				// Number of properties saved at each track.
	char property_name[10][20];			// Name of each property. Can not be longer than 20 characters each. Can only store up to 10 names.
	float vox_to_ras[4][4];				// 4x4 matrix for voxel to RAS (crs to xyz) transformation. If vox_to_ras[3][3] is 0, it means the matrix is not recorded. This field is added from version 2.
	char reserved[444];					// Reserved space for future version.
	char voxel_order[4];				// Storing order of the original image data. Explained here.
	char pad2[4];						// Paddings.
	float image_orientation_patient[6]; // Image orientation of the original image. As defined in the DICOM header.
	char pad1[2];						// Paddings.
	unsigned char invert_x;				// Inversion/rotation flags used to generate this track file. For internal use only.
	unsigned char invert_y;				// As above.
	unsigned char invert_z;				// As above.
	unsigned char swap_xy;				// As above.
	unsigned char swap_yz;				// As above.
	unsigned char swap_zx;				// As above.
	int n_count;						// Number of tracks stored in this track file. 0 means the number was NOT stored.
	int version;						// Version number. Current version is 2.
	int hdr_size;						// Size of the header. Used to determine byte swap. Should be 1000.
};										// 1000 bits total
typedef struct trkHeader trkHeader;


	/// based in http://www.trackvis.org/docs/?subsect=fileformat
int readTrkHeader(char * filePath, 
	void * pyVoxelSize,
	void * pyNScalars, 
	void * pyNProperties, 
	void * pyVox2RasMat,
	void * pyNCount, 
	void * pyFileSize, 
	void * pyHeaderSize) {
	
	float * voxelSize = (float *) pyVoxelSize;
	int * nScalars = (int*) pyNScalars;
	int * nProperties = (int*) pyNProperties;
	float * vox2RasMat = (float *) pyVox2RasMat;
	int * nCount = (int*) pyNCount;
	int * headerSize = (int*) pyHeaderSize;

	unsigned long * fileSize = (unsigned long *) pyFileSize;
	
	FILE *fp;
	fp = fopen(filePath, "rb");

	trkHeader headerBuffer;
	fread(&headerBuffer, 1, sizeof(trkHeader), fp);

	fseek(fp, 0L, SEEK_END);
	*fileSize = ftell(fp);
	fclose(fp);

	// copie the important data
	for (int i=0; i<3; i++) voxelSize[i] = headerBuffer.voxel_size[i];
	*nScalars = headerBuffer.n_scalars;
	*nProperties = headerBuffer.n_properties;
	for (int i=0; i<4; i++) for(int j=0; j<4; j++) * (vox2RasMat + i*4 + j) = headerBuffer.vox_to_ras[i][j];
	*nCount = headerBuffer.n_count;
	*headerSize = headerBuffer.hdr_size;

	*fileSize = *fileSize - headerBuffer.hdr_size;

	// Check that the file corresponds with a fiber file
	if (strcmp(headerBuffer.id_string, "TRACK") != 0) return -1;
	if (headerBuffer.hdr_size != 1000) return -1;
	return 0;
}


void readTrkBody(char * filePath, 
	int headerSize, 
	int nScalars,
	int nProperties,
	void * pyPoints, 
	void * pyNormals, 
	void * pyEbo, 
	void * pyFiberSize, 
	int curvesCount, 
	void * pyScalars,
	void * pyProperties) {

	// parse inputs
	GLfloat * points = (GLfloat *) pyPoints;
	GLfloat * normals = (GLfloat *) pyNormals;

	GLuint * ebo = (GLuint *) pyEbo;
	int * fibersize = (int *) pyFiberSize;

	float * scalars = (float *) pyScalars;
	float * properties = (float *) pyProperties;

	unsigned i, j, pointPack = 3+nScalars;

	// open trk file
	FILE *fp;
	fp = fopen(filePath, "rb");
	fseek(fp, headerSize, SEEK_SET);

	//////////////////////////////////////////////////////////////////////////////
	void readPoints() {
		fread(points, sizeof(GLfloat), fibersize[i]*3, fp);
	}

	void readPointsScalars() {
		for(j=0; j<fibersize[i]; j++) {
			fread(points+j*pointPack, sizeof(GLfloat), 3, fp);
			fread(scalars+j*nScalars, sizeof(float), nScalars, fp);
		}
		scalars += fibersize[i]*nScalars;
	}

	void readPointsProperties() {
		fread(points, sizeof(GLfloat), fibersize[i]*3, fp);
		fread(properties, sizeof(float), nProperties, fp);
		properties += nProperties;
	}

	void readPointsScalarsProperties() {
		for(j=0; j<fibersize[i]; j++) {
			fread(points+j*pointPack, sizeof(GLfloat), 3, fp);
			fread(scalars+j*nScalars, sizeof(float), nScalars, fp);
		}
		fread(properties, sizeof(float), nProperties, fp);

		scalars += fibersize[i]*nScalars;
		properties += nProperties;
	}

	void (*readData_i) ();

	if (nScalars == 0 && nProperties == 0) readData_i = readPoints;
	else if (nScalars != 0 && nProperties == 0) readData_i = readPointsScalars;
	else if (nScalars == 0 && nProperties != 0) readData_i = readPointsProperties;
	else readData_i = readPointsScalarsProperties;
	//////////////////////////////////////////////////////////////////////////////

	unsigned k, index = 0;
	GLfloat normal[3] = {1.0, 1.0, 1.0};
	GLfloat norma = 1.0;

	for (i=0; i<curvesCount; i++) {
		fread(&fibersize[i], sizeof(int), 1, fp);
		readData_i();

		for (k=0; k<fibersize[i] - 1; k++) {
			*(ebo++) = index++;

			normal[0] = points[k*3+3] - points[ k*3 ];
			normal[1] = points[k*3+4] - points[k*3+1];
			normal[2] = points[k*3+5] - points[k*3+2];
			norma = sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

			*(normals++) = normal[0]/norma;
			*(normals++) = normal[1]/norma;
			*(normals++) = normal[2]/norma;
		}

		*(ebo++) = index++;
		*(ebo++) = 0xFFFFFFFF;

		*(normals++) = normal[0]/norma;
		*(normals++) = normal[1]/norma;
		*(normals++) = normal[2]/norma;
		points += fibersize[i]*3;
	}
}


// Based in https://mrtrix.readthedocs.io/en/latest/getting_started/image_data.html?highlight=format#tracks-file-format-tck
// and https://github.com/scilus/fibernavigator/blob/master/src/dataset/Fibers.cpp
int readTckHeader(char * filePath, 
	void * pyNCount, 
	void * pyFileSize, 
	void * pyHeaderSize) {

	int * nCount = (int*) pyNCount;
	unsigned long * fileSize = (unsigned long *) pyFileSize;
	int * headerSize = (int*) pyHeaderSize;

	FILE *fp;
	fp = fopen(filePath, "rb");

	// tmp the fixed size n
	int n = 1000;
	char headerSizeFound = 0, countFound = 0;
	char * headerBuffer = (char*) malloc(n*sizeof(char));

	do {
		fread(headerBuffer, n, sizeof(char), fp);

		if (strstr(headerBuffer, "file:") != NULL) {
			sscanf(strstr(headerBuffer, "file:"), "file: . %d", headerSize);
			headerSizeFound = 1;
		}

		if (strstr(headerBuffer, "count:") != NULL) {
			sscanf(strstr(headerBuffer, "count:"), "count: %d", nCount);
			countFound = 1;
		}

	} while (strstr(headerBuffer, "END") == NULL);


	fseek(fp, 0L, SEEK_END);
	*fileSize = ftell(fp);
	fclose(fp);

	if (countFound != 1 || headerSizeFound != 1)
		return -1;

	*fileSize = *fileSize - *headerSize;

	return 0;
}

void readTckBody(char * filePath, 
	int headerSize, 
	void * pyPoints, 
	void * pyNormals, 
	void * pyEbo, 
	void * pyFiberSize, 
	int curvesCount) {

	// parse inputs
	GLfloat * points = (GLfloat *) pyPoints;
	GLfloat * normals = (GLfloat *) pyNormals;

	GLuint * ebo = (GLuint *) pyEbo;
	int * fibersize = (int *) pyFiberSize;

	// open tck file
	FILE *fp;
	fp = fopen(filePath, "rb");
	fseek(fp, headerSize, SEEK_SET);

	unsigned index = 0;
	GLfloat normal[3] = {1.0, 1.0, 1.0};
	GLfloat norma = 1.0;

	float tmpVertex[3];

	for (unsigned i=0; i<curvesCount; i++) {
		for(fread(tmpVertex, 3, sizeof(float), fp); *(unsigned int*)tmpVertex != 0x7fc00000/* && tmpVertex[0] != INF*/; fread(tmpVertex, 3, sizeof(float), fp)) {
			memcpy(points+fibersize[i]*3, tmpVertex, sizeof(float)*3);

			fibersize[i]++;
		}

		for (unsigned k=0; k<fibersize[i] - 1; k++) {
			*(ebo++) = index++;

			normal[0] = points[k*3+3] - points[ k*3 ];
			normal[1] = points[k*3+4] - points[k*3+1];
			normal[2] = points[k*3+5] - points[k*3+2];
			norma = sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

			*(normals++) = normal[0]/norma;
			*(normals++) = normal[1]/norma;
			*(normals++) = normal[2]/norma;
		}

		*(ebo++) = index++;
		*(ebo++) = 0xFFFFFFFF;

		*(normals++) = normal[0]/norma;
		*(normals++) = normal[1]/norma;
		*(normals++) = normal[2]/norma;
		points += fibersize[i]*3;
	}
}


void vec3MultiplyBy4x4Matrix(GLfloat * vec3, float * mat4, float * tmpPlaceHolder) {
	tmpPlaceHolder[0] = vec3[0]*mat4[0] + vec3[1]*mat4[1] + vec3[2]*mat4[2]  + mat4[3];
	tmpPlaceHolder[1] = vec3[0]*mat4[4] + vec3[1]*mat4[5] + vec3[2]*mat4[6]  + mat4[7];
	tmpPlaceHolder[2] = vec3[0]*mat4[8] + vec3[1]*mat4[9] + vec3[2]*mat4[10] + mat4[11];

	vec3[0] = tmpPlaceHolder[0];
	vec3[1] = tmpPlaceHolder[1];
	vec3[2] = tmpPlaceHolder[2];
}


void applyMatrix(void * pyPoints,
	int pointsSize,
	void * pyMatrix) {
	GLfloat * points = (GLfloat *) pyPoints;
	float * matrix = (float *) pyMatrix;

	float tmp[3];

	for (unsigned i=0; i<pointsSize; i+= 3) 
		vec3MultiplyBy4x4Matrix(points+i, matrix, tmp);
}


void reCalculateNormals(
		void * pyPoints,
		void * pyNormals,
		void * pyFiberSize,
		int curvesCount) {

	GLfloat * points = (GLfloat *) pyPoints;
	GLfloat * normals = (GLfloat *) pyNormals;
	int * fibersize = (int *) pyFiberSize;

	GLfloat normal[3] = {1.0, 1.0, 1.0};
	GLfloat norma = 1.0;

	for (unsigned i=0; i<curvesCount; i++) {
		for (unsigned j=0; j<fibersize[i]-1; j++) {
			normal[0] = points[j*3+3] - points[ j*3 ];
			normal[1] = points[j*3+4] - points[j*3+1];
			normal[2] = points[j*3+5] - points[j*3+2];
			norma = sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

			*(normals++) = normal[0]/norma;
			*(normals++) = normal[1]/norma;
			*(normals++) = normal[2]/norma;
		}

		*(normals++) = normal[0]/norma;
		*(normals++) = normal[1]/norma;
		*(normals++) = normal[2]/norma;
		points += fibersize[i]*3;
	}
}