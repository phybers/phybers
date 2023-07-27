#ifndef ATLASBASEDPARALLELSEGMENTATION_H
#define ATLASBASEDPARALLELSEGMENTATION_H

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
#include <stdbool.h>
#include <sys/stat.h>
#include <string.h>

// #include "functions.h"


#ifndef min
#define min(a,b) \
	({ __typeof__ (a) _a = (a); \
	   __typeof__ (b) _b = (b); \
	   _a < _b ? _a : _b; })
#endif

float sqrt7(float x);


float euclidean_distance(float x1, float y1, float z1, float x2, float y2, float z2);


/*Calculate the euclidean distance between two 3d points normalized*/
float euclidean_distance_norm(float x1, float y1, float z1, float x2, float y2, float z2);


/*Return true when the fiber is discarded measuring the distance in central points*/
bool discard_center(float *subjectData, float *atlasData, unsigned short int nDataFiber,
					unsigned char threshold, unsigned int fiberIndex, unsigned int fatlasIndex);


bool discard_extremes(
		float *subjectData, 
		float *atlasData, 
		unsigned short int nDataFiber,
		unsigned char threshold, 
		bool *isInverted, 
		unsigned int fiberIndex, 
		unsigned int fatlasIndex);


bool discard_four_points(
		float *subject_data, 
		float *atlas_data, 
		unsigned short int ndata_fiber,
		unsigned char threshold, 
		bool is_inverted, 
		unsigned int fiber_index, 
		unsigned int fatlas_index);


float discarded_21points(
		float *subjectData, 
		float *atlasData, 
		unsigned short int nDataFiber, 
		unsigned char threshold, 
		bool isInverted, 
		unsigned int fiberIndex, 
		unsigned int fatlasIndex);

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
		void *pyAssignment);


void AtlasBasedSegmentationExportbundlesdata(
		char * filePath,
		int bundleN,
		void * pyBundlesSelected,
		void * pyFiberSize,
		void * pyPoints,
		int fiberN,
		void * pyFiberValidator);


void reSampleBundle(
		void * pyInPoints, 
		void * pyInFiberSize, 
		int curvesCount, 
		void * pyOutPoints, 
		int newFiberSize);

int * segmentation(unsigned int n_points, float *subject_data, float *atlas_data, float threshold,
				unsigned int nfibers_subject, unsigned int nfibers_atlas);

#endif