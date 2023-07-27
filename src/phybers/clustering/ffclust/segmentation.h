/* segmentation.h
Authors:
    Narciso López López
    Andrea Vázquez Varela
Creation date: 24-10-2018
Last update: 18-11-2018
*/
#ifndef SEGMANTATION_H
#define SEGMENTATION_H

#include <sys/stat.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <omp.h>
#include <string.h>
#include <stdint.h>

float sqrt7(float x);
float euclidean_distance(float x1, float y1, float z1, float x2, float y2, float z2);
/*Calculate the euclidean distance between two 3d points normalized*/
float euclidean_distance_norm(float x1, float y1, float z1, float x2, float y2, float z2);
/*Read .bundles files and return (by reference) a vector with the datas*/
float *read_bundles(char *bundles_path, unsigned short int ndata_fiber, unsigned int nfibers);
/*Return true when the fiber is discarded measuring the distance in central points*/
int discard_center(float *subject_data, float *atlas_data, unsigned short int ndata_fiber,
                   float threshold, unsigned int fiber_index, unsigned int fatlas_index);
int discard_extremes(float *subject_data, float *atlas_data, unsigned short int ndata_fiber,
                     float threshold, int *is_inverted, unsigned int fiber_index, unsigned int fatlas_index);
int discard_four_points(float *subject_data, float *atlas_data, unsigned short int ndata_fiber, float threshold,
                        int is_inverted, unsigned int fiber_index, unsigned int fatlas_index);
float discarded_21points(float *subject_data, float *atlas_data, unsigned short int ndata_fiber,
                         float threshold, int is_inverted, unsigned int fiber_index, unsigned int fatlas_index);
void freeme(int *assignment);
int *initialized_array(int size, int value);
int *parallel_segmentation(float *atlas_data, float *subject_data, unsigned short int ndata_fiber,
                           float threshold, const int atlas_size, const int subject_size);
int *segmentation(unsigned int n_points, char *subject_path, char *atlas_path, float threshold,
                  char *output_directory, unsigned int nfibers_subject, unsigned int nfibers_atlas);
#endif