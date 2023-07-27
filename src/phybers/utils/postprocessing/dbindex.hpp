/* main.cpp
   Authors:
   Narciso López López
   Andrea Vázquez Varela
   Last update: 15-02-2020 */

#ifndef DBINDEX_HPP
#define DBINDEX_HPP

#include <vector>
#include <iostream>
#include <cstring>
#include <omp.h>
#include <sstream>
#include <algorithm>
#include <fstream>
#include <ctime>

using namespace std;

#ifdef __linux__
	#include "dirent.h"
#elif _WIN32
	#include "win_dirent.h"
#endif

#ifndef S_IRWXU
	#define S_IRWXU (S_IRUSR | S_IWUSR | S_IXUSR)
#endif

#ifndef S_IRWXG
	#define S_IRWXG (S_IRGRP | S_IWGRP | S_IXGRP)
#endif

#ifdef _WIN32
    int mkdir(const char *path, int mode);
#endif

void write_results(float val, vector<float> &intra_dists, vector<float> &sums, vector<float> &intra_meandists,vector< vector<float> > &inter_dists, string name);
char * str_to_char_array(string s);
/*Read .bundles files and return (by reference) a vector with the datas*/
vector<float> read_bundles(string path, unsigned short int ndata_fiber) ;
vector<string> get_bundle_files(string path);
float sqrt7(float x);
/*Calculate the euclidean distance between two 3d points normalized*/
float euclidean_distance_norm(float x1, float y1, float z1, float x2, float y2, float z2);
float euclidean_21points_mean (vector<float> &bundle_data,unsigned int fiber_index1, unsigned int fiber_index2,short int ndata_fiber);
float euclidean_21points_max (vector<float> &bundle_data,unsigned int fiber_index1, unsigned int fiber_index2,short int ndata_fiber);
struct max_mean_pair
{
    float max;
    float mean;
};
struct max_mean_pair intra_dist_max_mean(vector<float> &fibers, unsigned short int ndata_fiber);
int main (int argc, char *argv[]);

#endif