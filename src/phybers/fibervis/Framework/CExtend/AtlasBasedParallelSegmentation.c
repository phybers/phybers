/*
Authors:
	Narciso López López
	Andrea Vázquez Varela
	Ignacio Osorio Wallace
Last update: 5-12-2018 */

#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


#ifndef min
#define min(a,b) \
	({ __typeof__ (a) _a = (a); \
	   __typeof__ (b) _b = (b); \
	   _a < _b ? _a : _b; })
#endif

float sqrt7(float x){
	unsigned int i = *(unsigned int*) &x;
	i  += 127 << 23;	// adjust bias
	i >>= 1;	// approximation of square root
	return *(float*) &i;
}


float euclidean_distance(float x1, float y1, float z1, float x2, float y2, float z2){
	return ((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2));
}


/*Calculate the euclidean distance between two 3d points normalized*/
float euclidean_distance_norm(float x1, float y1, float z1, float x2, float y2, float z2){
	return sqrt7((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2));
}


/*Return true when the fiber is discarded measuring the distance in central points*/
bool discard_center(float *subjectData, float *atlasData, unsigned short int nDataFiber,
					unsigned char threshold, unsigned int fiberIndex, unsigned int fatlasIndex){

	unsigned int fpoint = (fiberIndex*nDataFiber)+31; //Point of fiber, 31 is the middle of the fiber
	unsigned int apoint = (fatlasIndex*nDataFiber)+31; //Atlas point, 31 is the middle of the fiber

	float ed = euclidean_distance(subjectData[fpoint-1], subjectData[fpoint], subjectData[fpoint+1],
									atlasData[apoint-1], atlasData[apoint], atlasData[apoint+1]);
	
	if (ed>(threshold*threshold)) return true;
	else return false;
}


bool discard_extremes(
		float *subjectData, 
		float *atlasData, 
		unsigned short int nDataFiber,
		unsigned char threshold, 
		bool *isInverted, 
		unsigned int fiberIndex, 
		unsigned int fatlasIndex){

	unsigned int fpoint1 = fiberIndex*nDataFiber;	//Point 0 of fiber
	unsigned int apoint1 = fatlasIndex*nDataFiber;	//Atlas point 0
	unsigned int fpoint21 = fpoint1+62;		//Last point on the fiber
	unsigned int apoint21 = apoint1+62;		//Last point on the fiber
	float first_points_ed_direct = euclidean_distance(subjectData[fpoint1], subjectData[fpoint1+1], subjectData[fpoint1+2],
														atlasData[apoint1], atlasData[apoint1+1], atlasData[apoint1+2]);
	float first_point_ed_flip = euclidean_distance(subjectData[fpoint1], subjectData[fpoint1+1], subjectData[fpoint1+2],
													atlasData[apoint21-2], atlasData[apoint21-1], atlasData[apoint21]);
	float first_points_ed = min(first_points_ed_direct, first_point_ed_flip);

	if (first_points_ed>(threshold*threshold)) return true;
	else {
		float last_points_ed;
		if (first_points_ed_direct<first_point_ed_flip) {
			(*isInverted) = false;
			last_points_ed = euclidean_distance(subjectData[fpoint21-2], subjectData[fpoint21-1], subjectData[fpoint21],
												atlasData[apoint21-2], atlasData[apoint21-1], atlasData[apoint21]);
		}
		else {
			(*isInverted) = true;
			last_points_ed = euclidean_distance(subjectData[fpoint21-2], subjectData[fpoint21-1], subjectData[fpoint21],
												atlasData[apoint1], atlasData[apoint1+1], atlasData[apoint1+2]);
		}
		if (last_points_ed>(threshold*threshold)) return true;
		else return false;
	}
}


bool discard_four_points(
		float *subject_data, 
		float *atlas_data, 
		unsigned short int ndata_fiber,
		unsigned char threshold, 
		bool is_inverted, 
		unsigned int fiber_index, 
		unsigned int fatlas_index){

	unsigned short int points[4] = {3,7,13,17};
	unsigned short int inv = 3;
	unsigned int point_fiber, point_atlas, point_inv_a;
	float ed;

	//#pragma parallel for
	for (unsigned int i = 0; i< 4;i++){
		point_fiber = (ndata_fiber*fiber_index) + (points[i]*3); //Mult by 3 dim
		point_atlas = (ndata_fiber*fatlas_index)+ (points[i]*3);
		point_inv_a = (ndata_fiber*fatlas_index)+ (points[inv]*3);

		if (!is_inverted){
			ed = euclidean_distance(subject_data[point_fiber],subject_data[point_fiber+1], subject_data[point_fiber+2],
									atlas_data[point_atlas],atlas_data[point_atlas+1], atlas_data[point_atlas+2]);}
		else{
			ed = euclidean_distance(subject_data[point_fiber],subject_data[point_fiber+1], subject_data[point_fiber+2],
									atlas_data[point_inv_a],atlas_data[point_inv_a+1], atlas_data[point_inv_a+2]);}

		if (ed>(threshold*threshold)) return true;
		inv--;
	}
	return false;
}


float discarded_21points(
		float *subjectData, 
		float *atlasData, 
		unsigned short int nDataFiber, 
		unsigned char threshold, 
		bool isInverted, 
		unsigned int fiberIndex, 
		unsigned int fatlasIndex){

	unsigned short int inv = 20;
	float ed;
	float max_ed = 0;
	unsigned int fiber_point, atlas_point, point_inv;

	for (unsigned short int i = 0; i<21; i++) {
		fiber_point = (nDataFiber*fiberIndex)+(i*3);
		atlas_point = (nDataFiber*fatlasIndex)+(i*3);
		point_inv = (nDataFiber*fatlasIndex)+(inv*3);
		if (!isInverted){
			ed = euclidean_distance_norm(subjectData[fiber_point],subjectData[fiber_point+1], subjectData[fiber_point+2],
										atlasData[atlas_point],atlasData[atlas_point+1], atlasData[atlas_point+2]);}
		else{
			ed = euclidean_distance_norm(subjectData[fiber_point],subjectData[fiber_point+1], subjectData[fiber_point+2],
										atlasData[point_inv],atlasData[point_inv+1], atlasData[point_inv+2]);}

		if (ed>threshold) return -1;
		if (ed >= max_ed)
			max_ed = ed;
		inv--;
	}

	//After pass the comprobation of euclidean distance, will be tested with the lenght factor
	unsigned int fiber_pos = (nDataFiber*fiberIndex);
	unsigned int atlas_pos = (nDataFiber*fatlasIndex);
	float length_fiber1 = euclidean_distance_norm(subjectData[fiber_pos], subjectData[fiber_pos+1], subjectData[fiber_pos+2],
													subjectData[fiber_pos+3], subjectData[fiber_pos+4], subjectData[fiber_pos+5]);
	float length_fiber2 = euclidean_distance_norm(atlasData[atlas_pos], atlasData[atlas_pos+1], atlasData[atlas_pos+2],
													atlasData[atlas_pos+3], atlasData[atlas_pos+4], atlasData[atlas_pos+5]);
	float fact = length_fiber2 < length_fiber1 ? ((length_fiber1-length_fiber2)/length_fiber1) : ((length_fiber2-length_fiber1)/length_fiber2);
	fact = (((fact + 1.0f)*(fact + 1.0f))-1.0f);
	fact = fact < 0.0f ? 0.0f : fact;

	if ((max_ed+fact) >= threshold)
		return -1;
	else
		return max_ed;
}

/*
float *atlasData				vector with all the 3d points for the atlas
unsigned int atlasDataSize		size of the vector with all the points for the atlas
float *subjectData 				vector with all the 3d points for the subject
unsigned int subjectDataSize 	size of the vector with all the points for the subject
unsigned short int nDataFiber	number of points per fiber (*3) so 21 points = 63
unsigned char *thresholds		vector with the thresholds for each fascicle on the atlas
unsigned int *bundleOfFiber		vector of atlas_points_size with id for the fascicle that correspondence
unsigned char *assignment 		size nfibersSubject. And all data set to 254 - result vector
*/
void AtlasBasedParallelSegmentation(
		void *pyAtlasData, 
		unsigned int atlasDataSize, 
		void *pySubjectData, 
		unsigned int subjectDataSize, 
		unsigned short int nDataFiber,	
		void *pyThresholds, 
		void *pyBundleOfFiber, 
		void *pyAssignment){

	float * atlasData = (float *) pyAtlasData;
	float *subjectData = (float *) pySubjectData;
	unsigned char *thresholds = (unsigned char *) pyThresholds;
	unsigned char *bundleOfFiber = (unsigned char *) pyBundleOfFiber;
	unsigned char *assignment = (unsigned char *) pyAssignment;

	unsigned int nfibersSubject = subjectDataSize/nDataFiber;
	unsigned int nfibersAtlas = atlasDataSize/nDataFiber;

	unsigned int nunProc = omp_get_num_procs();
	omp_set_num_threads(nunProc);

#pragma omp parallel
	{

#pragma omp for schedule(auto) nowait
		for (unsigned long i = 0; i < nfibersSubject; i++) {
			float ed_i = 500;
			unsigned char assignment_i = 254;
			for (unsigned int j = 0; j < nfibersAtlas; j++) {
				bool isInverted, isDiscarded;
				float ed = -1;
				unsigned char b = bundleOfFiber[j];

				//First test: discard_centers++; discard centroid
				isDiscarded = discard_center(subjectData, atlasData, nDataFiber, thresholds[b], i, j);
				if (isDiscarded) continue;

				//Second test: discard by the extremes
				isDiscarded = discard_extremes(subjectData, atlasData, nDataFiber, thresholds[b], &isInverted, i, j);
				if (isDiscarded) continue;

				//Third test: discard by four points
				isDiscarded = discard_four_points(subjectData, atlasData, nDataFiber, thresholds[b], isInverted, i, j);
				if (isDiscarded) continue;

				ed = discarded_21points(subjectData, atlasData, nDataFiber, thresholds[b], isInverted, i, j);
				if (ed != -1) {

					if (ed < ed_i) {
						ed_i = ed;
						assignment_i = b;
					}
				}
			}
			if (assignment_i!=254) {
				assignment[i]=assignment_i;
			}

		}
	}
}


void AtlasBasedSegmentationExportbundlesdata(
		char * filePath,
		int bundleN,
		void * pyBundlesSelected,
		void * pyFiberSize,
		void * pyPoints,
		int fiberN,
		void * pyFiberValidator) {

	unsigned char * bundlesSelected = (unsigned char *) pyBundlesSelected;
	int * fiberSize = (int *) pyFiberSize;
	float * points = (float *) pyPoints;
	unsigned char * fiberValidator = (unsigned char *) pyFiberValidator;

	// open bundledata file
	FILE *fp;
	fp = fopen(filePath, "wb");
	int i, j, offset, b;

	for (i=0; i<bundleN; i++) {
		offset = 0;
		b = bundlesSelected[i];

		for (j=0; j<fiberN; j++) {
			if (fiberValidator[j] == b) {
				fwrite(fiberSize+j, sizeof(int), 1, fp);
				fwrite(points+offset, sizeof(GLfloat), fiberSize[j]*3, fp);
			}

			offset += fiberSize[j]*3;
		}
	}

	 fclose(fp);
}


void reSampleBundle(
		void * pyInPoints, 
		void * pyInFiberSize, 
		int curvesCount, 
		void * pyOutPoints, 
		int newFiberSize) {

	GLfloat * inPoints = (GLfloat *) pyInPoints;
	int * inFiberSize = (int *) pyInFiberSize;
	GLfloat * outPoints = (GLfloat *) pyOutPoints;

	unsigned int inPointOffset = 0, outPointsOffset = 0;

	for(int k=0; k<curvesCount; inPointOffset += inFiberSize[k++]*3, outPointsOffset += newFiberSize*3) {
		int fSize = 1;

		*(outPoints + outPointsOffset  ) = *(inPoints+inPointOffset  );
		*(outPoints + outPointsOffset+1) = *(inPoints+inPointOffset+1);
		*(outPoints + outPointsOffset+2) = *(inPoints+inPointOffset+2);

		float fiberlength = 0;
		float acc_length[*(inFiberSize+k)];
		acc_length[0] = 0;

		for(int j=0; j<*(inFiberSize+k)-3; j++) {
			fiberlength += sqrt(pow(*(inPoints+inPointOffset+(j*3)  ) - *(inPoints+inPointOffset+(j*3)  +3),2) +
								pow(*(inPoints+inPointOffset+(j*3)+1) - *(inPoints+inPointOffset+(j*3)+1+3),2) +
								pow(*(inPoints+inPointOffset+(j*3)+2) - *(inPoints+inPointOffset+(j*3)+2+3),2));

			acc_length[j + 1] = fiberlength;
		}
		float step = fiberlength / (float)(newFiberSize-1);
		float currentLength = step;

		int currentInd = 0;

		float lengthtmp = fiberlength - step*0.5;

		while ( currentLength < lengthtmp) {
			if (acc_length[currentInd] < currentLength) {
				while (acc_length[currentInd] < currentLength) {
					currentInd++;
				}
				currentInd--;
			}

			float fact = (currentLength - acc_length[currentInd])/(acc_length[currentInd + 1] - acc_length[currentInd]);
			if ( fact > 0.000001 ) {
				*(outPoints + outPointsOffset + fSize*3    ) = (*(inPoints+inPointOffset + (int)(currentInd + 1)*3    ) - *(inPoints+inPointOffset + (int)currentInd*3    ))*fact + *(inPoints+inPointOffset + (int)currentInd*3    );
				*(outPoints + outPointsOffset + fSize*3 + 1) = (*(inPoints+inPointOffset + (int)(currentInd + 1)*3 + 1) - *(inPoints+inPointOffset + (int)currentInd*3 + 1))*fact + *(inPoints+inPointOffset + (int)currentInd*3 + 1);
				*(outPoints + outPointsOffset + fSize*3 + 2) = (*(inPoints+inPointOffset + (int)(currentInd + 1)*3 + 2) - *(inPoints+inPointOffset + (int)currentInd*3 + 2))*fact + *(inPoints+inPointOffset + (int)currentInd*3 + 2);
				fSize++;
			}
			else {
				*(outPoints + outPointsOffset + fSize*3    ) = *(inPoints+inPointOffset + (int)currentInd*3    );
				*(outPoints + outPointsOffset + fSize*3 + 1) = *(inPoints+inPointOffset + (int)currentInd*3 + 1);
				*(outPoints + outPointsOffset + fSize*3 + 2) = *(inPoints+inPointOffset + (int)currentInd*3 + 2);
				fSize++;
			}

			currentLength += step;
		}

		*(outPoints + outPointsOffset + fSize*3) = *(inPoints+inPointOffset + (*(inFiberSize + k) - 1)*3);
		*(outPoints + outPointsOffset + fSize*3 + 1) = *(inPoints+inPointOffset + (*(inFiberSize + k) - 1)*3 + 1);
		*(outPoints + outPointsOffset + fSize*3 + 2) = *(inPoints+inPointOffset + (*(inFiberSize + k) - 1)*3 + 2);
		fSize++;
	}
}