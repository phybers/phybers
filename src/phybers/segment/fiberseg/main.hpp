/*# Copyright (C) 2019  Andrea Vázquez Varela

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

 main.cpp
Authors:
    Narciso López López
    Andrea Vázquez Varela
Last modification: 24-10-2018 */
#ifndef MAIN_H
#define MAIN_H


#include <iostream>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <fstream>
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <math.h>
#include <sys/stat.h>
#include <unordered_map>
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

using namespace std;

#ifdef _WIN32
    int mkdir(const char *path, int mode);
#endif

float sqrt7(float x);
float euclidean_distance(float x1, float y1, float z1, float x2, float y2, float z2);
/*Calculate the euclidean distance between two 3d points normalized*/
float euclidean_distance_norm(float x1, float y1, float z1, float x2, float y2, float z2);

/*Return true when the fiber is discarded measuring the distance in central points*/
bool discard_center(vector<float> &subject_data, vector<float> &atlas_data,unsigned short int ndata_fiber,
 unsigned char threshold, unsigned int fiber_index, unsigned int fatlas_index);

bool discard_extremes(vector<float> &subject_data, vector<float> &atlas_data,unsigned short int ndata_fiber,
             unsigned char threshold, bool &is_inverted, unsigned int fiber_index, unsigned int fatlas_index);

bool discard_four_points(vector<float> &subject_data, vector<float> &atlas_data, unsigned short int ndata_fiber, unsigned char threshold,
bool is_inverted, unsigned int fiber_index, unsigned int fatlas_index);

char * str_to_char_array(string s);

float discarded_21points (vector<float> &subject_data, vector<float> &atlas_data, unsigned short int ndata_fiber,
                unsigned char threshold, bool is_inverted, unsigned int fiber_index, unsigned int fatlas_index);


float euclidean_dist21 (vector<float> &atlas_data, unsigned int fiber1, unsigned int fiber2,unsigned short int ndata);

void write_indices(const std::string &path, vector<string> &names, const std::vector<std::vector<unsigned short int>> &ind);

/*Read .bundles files and return (by reference) a vector with the datas*/
void write_bundles(string subject_name, string output_path, vector<vector<unsigned short int>> &assignment,vector<string> &names ,int ndata_fiber,
                   vector<float> &subject_data);

/*Read .bundles files and return (by reference) a vector with the datas*/
vector<float> read_bundles(string path, unsigned short int ndata_fiber);

/*Get vector of bundles of the atlas*/
vector<float> get_atlas_bundles(string path, vector<string> names,unsigned short int ndata_fiber);

/*Read atlas information file*/
void read_atlas_info(string path, vector<string> &names, vector<unsigned char> &thres,
                     unsigned int &nfibers_atlas, vector<unsigned int> &fibers_per_bundle);

vector<unsigned int> atlas_bundle(vector<unsigned int> &fibers_per_bundle, unsigned int nfibers);

bool sort_by_length (float i,float j);

vector<float> calc_centroid(vector<float> &atlas_data,vector<unsigned int> &indices,unsigned short int ndata);


vector<vector<float>> get_centroids(vector<vector<float>> &atlas_data, unsigned short int ndata);

vector<unsigned short> parallel_segmentation(vector<float> &atlas_data, vector<float> &subject_data,
                                  unsigned short int ndata_fiber, vector<unsigned char> thresholds,
                                  vector<unsigned int> &bundle_of_fiber);

int main_segmentation(unsigned short int n_points, string subject_path, string subject_name, string atlas_path, string atlas_inf, string output_dir, string indices_output_dir);
#endif