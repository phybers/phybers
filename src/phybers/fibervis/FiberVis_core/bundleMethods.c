#include "bundleMethods.h"

// #include "AtlasBasedParallelSegmentation.c"


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
	float * positions = (float *) pyPositions;
	float * normals = (float *) pyNormals;
	int * colors = (int *) pyColors;

	unsigned int * ebo = (unsigned int *) pyEbo;
	int * fibersize = (int *) pyFiberSize;

	int * bundlestart = (int *) pyBundleStart;

	// open bundledata file
	FILE *fp;
	fp = fopen(filePath, "rb");

	// read data
	unsigned index = 0;
	int k, i, j;
	float normal[3] = {1.0, 1.0, 1.0};
	float norma = 1.0;

	for (i=1; i<nBundles; i++) {
		for (j=bundlestart[i-1]; j<bundlestart[i]; j++) {
			fread(&fibersize[j], sizeof(int), 1, fp);
			fread(positions, sizeof(float), fibersize[j]*3, fp);

			for (k=0; k<fibersize[j] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = positions[k*3+3] - positions[ k*3 ];
				normal[1] = positions[k*3+4] - positions[k*3+1];
				normal[2] = positions[k*3+5] - positions[k*3+2];
				norma = (float)sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

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


/// based in http://www.trackvis.org/docs/?subsect=fileformat
trkHeader readTrkHeader(char * filePath) {	
	FILE *fp;
	fp = fopen(filePath, "rb");

	trkHeader headerBuffer;
	fread(&headerBuffer, 1, sizeof(trkHeader), fp);

	fseek(fp, 0L, SEEK_END);
	fclose(fp);

	return headerBuffer;
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
	float * points = (float *) pyPoints;
	float * normals = (float *) pyNormals;

	unsigned int * ebo = (unsigned int *) pyEbo;
	int * fibersize = (int *) pyFiberSize;

	float * scalars = (float *) pyScalars;
	float * properties = (float *) pyProperties;

	unsigned pointPack = 3+nScalars;
	int i, j, k;

	// open trk file
	FILE *fp;
	fp = fopen(filePath, "rb");
	fseek(fp, headerSize, SEEK_SET);

	unsigned index = 0;
	float normal[3] = {1.0, 1.0, 1.0};
	float norma = 1.0;

	if (nScalars == 0 && nProperties == 0) {
		for (i=0; i<curvesCount; i++) {
			fread(&fibersize[i], sizeof(int), 1, fp);
			fread(points, sizeof(float), fibersize[i]*3, fp);

			for (k=0; k<fibersize[i] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = points[k*3+3] - points[ k*3 ];
				normal[1] = points[k*3+4] - points[k*3+1];
				normal[2] = points[k*3+5] - points[k*3+2];
				norma = (float) sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

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
	else if (nScalars != 0 && nProperties == 0) {
		for (i=0; i<curvesCount; i++) {
			fread(&fibersize[i], sizeof(int), 1, fp);
			for(j=0; j<fibersize[i]; j++) {
				fread(points+j*pointPack, sizeof(float), 3, fp);
				fread(scalars+j*nScalars, sizeof(float), nScalars, fp);
			}
			scalars += fibersize[i]*nScalars;

			for (k=0; k<fibersize[i] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = points[k*3+3] - points[ k*3 ];
				normal[1] = points[k*3+4] - points[k*3+1];
				normal[2] = points[k*3+5] - points[k*3+2];
				norma = (float) sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

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
	else if (nScalars == 0 && nProperties != 0) {
		for (i=0; i<curvesCount; i++) {
			fread(&fibersize[i], sizeof(int), 1, fp);
			fread(points, sizeof(float), fibersize[i]*3, fp);
			fread(properties, sizeof(float), nProperties, fp);
			properties += nProperties;

			for (k=0; k<fibersize[i] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = points[k*3+3] - points[ k*3 ];
				normal[1] = points[k*3+4] - points[k*3+1];
				normal[2] = points[k*3+5] - points[k*3+2];
				norma = (float) sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

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
	else {
		for (i=0; i<curvesCount; i++) {
			fread(&fibersize[i], sizeof(int), 1, fp);
			for(j=0; j<fibersize[i]; j++) {
				fread(points+j*pointPack, sizeof(float), 3, fp);
				fread(scalars+j*nScalars, sizeof(float), nScalars, fp);
			}
			fread(properties, sizeof(float), nProperties, fp);

			scalars += fibersize[i]*nScalars;
			properties += nProperties;

			for (k=0; k<fibersize[i] - 1; k++) {
				*(ebo++) = index++;

				normal[0] = points[k*3+3] - points[ k*3 ];
				normal[1] = points[k*3+4] - points[k*3+1];
				normal[2] = points[k*3+5] - points[k*3+2];
				norma = (float) sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);

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
}





void vec3MultiplyBy4x4Matrix(float * vec3, float * mat4, float * tmpPlaceHolder) {
	tmpPlaceHolder[0] = vec3[0]*mat4[0] + vec3[1]*mat4[1] + vec3[2]*mat4[2]  + mat4[3];
	tmpPlaceHolder[1] = vec3[0]*mat4[4] + vec3[1]*mat4[5] + vec3[2]*mat4[6]  + mat4[7];
	tmpPlaceHolder[2] = vec3[0]*mat4[8] + vec3[1]*mat4[9] + vec3[2]*mat4[10] + mat4[11];

	vec3[0] = tmpPlaceHolder[0];
	vec3[1] = tmpPlaceHolder[1];
	vec3[2] = tmpPlaceHolder[2];
}
