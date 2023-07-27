// Copyright (C) 2019  Andrea Vázquez Varela

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

/* segmentation.cpp
Authors:  
    Narciso López López
    Andrea Vázquez Varela
Creation date: 24-10-2018 
Last update: 01-11-2019
*/

#include <sys/stat.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <omp.h>
#include <string.h>

#define min(a, b) (((a) < (b)) ? (a) : (b))

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
int discard_center(float *subject_data, float *atlas_data,unsigned short int ndata_fiber, 
    float threshold, unsigned int fiber_index, unsigned int fatlas_index) {
    unsigned int fpoint = (fiber_index*ndata_fiber)+31; //Point of fiber, 31 is the middle of the fiber
    unsigned int apoint = (fatlas_index*ndata_fiber)+31; //Atlas point, 31 is the middle of the fiber

    float ed = euclidean_distance(subject_data[fpoint-1],subject_data[fpoint],subject_data[fpoint+1],
                                  atlas_data[apoint-1],atlas_data[apoint],atlas_data[apoint+1]);
    if (ed>(threshold*threshold)) return 1;
    else return 0;
}

int discard_extremes(float *subject_data, float *atlas_data, unsigned short int ndata_fiber,
             float threshold, int *is_inverted, unsigned int fiber_index, unsigned int fatlas_index) {
    unsigned int fpoint1 = fiber_index*ndata_fiber;	//Point 0 of fiber
    unsigned int apoint1 = fatlas_index*ndata_fiber;	//Atlas point 0
    unsigned int fpoint21 = fpoint1+62;		//Last point on the fiber
    unsigned int apoint21 = apoint1+62;		//Last point on the fiber
    float first_points_ed_direct = euclidean_distance(subject_data[fpoint1], subject_data[fpoint1+1], subject_data[fpoint1+2],
                                                      atlas_data[apoint1], atlas_data[apoint1+1], atlas_data[apoint1+2]);
    float first_point_ed_flip = euclidean_distance(subject_data[fpoint1], subject_data[fpoint1+1], subject_data[fpoint1+2],
                                                   atlas_data[apoint21-2], atlas_data[apoint21-1], atlas_data[apoint21]);
    float first_points_ed = min(first_points_ed_direct, first_point_ed_flip);

    if (first_points_ed>(threshold*threshold)) return 1;
    else{
        float last_points_ed;
        if (first_points_ed_direct<first_point_ed_flip) {
            (*is_inverted) = 0;
            last_points_ed = euclidean_distance(subject_data[fpoint21-2], subject_data[fpoint21-1], subject_data[fpoint21],
                                                atlas_data[apoint21-2], atlas_data[apoint21-1], atlas_data[apoint21]);
        }
        else {
            (*is_inverted) = 1;
            last_points_ed = euclidean_distance(subject_data[fpoint21-2], subject_data[fpoint21-1], subject_data[fpoint21],
                                                atlas_data[apoint1], atlas_data[apoint1+1], atlas_data[apoint1+2]);
        }
        if (last_points_ed>(threshold*threshold)) return 1;
        else return 0;
    }
}

int discard_four_points(float *subject_data, float *atlas_data, unsigned short int ndata_fiber, float threshold, 
int is_inverted, unsigned int fiber_index, unsigned int fatlas_index) {
    unsigned short int points[4] = {3,7,13,17};
    unsigned short int inv = 3;
    //#pragma parallel for
    for (unsigned int i = 0; i< 4;i++){
        unsigned int point_fiber = (ndata_fiber*fiber_index) + (points[i]*3); //Mult by 3 dim
        unsigned int point_atlas = (ndata_fiber*fatlas_index)+ (points[i]*3);
        unsigned int point_inv_a = (ndata_fiber*fatlas_index)+ (points[inv]*3);
        float ed;
        if (!is_inverted){
            ed = euclidean_distance(subject_data[point_fiber],subject_data[point_fiber+1], subject_data[point_fiber+2],
                                    atlas_data[point_atlas],atlas_data[point_atlas+1], atlas_data[point_atlas+2]);}
        else{
            ed = euclidean_distance(subject_data[point_fiber],subject_data[point_fiber+1], subject_data[point_fiber+2],
                                    atlas_data[point_inv_a],atlas_data[point_inv_a+1], atlas_data[point_inv_a+2]);}

        if (ed>(threshold*threshold)) return 1;
        inv--;
    }
    return 0;
}

float discarded_21points (float *subject_data, float *atlas_data, unsigned short int ndata_fiber,
                        float threshold, int is_inverted, unsigned int fiber_index, unsigned int fatlas_index) {
    unsigned short int inv = 20;
    float ed;
    float max_ed = 0;
    for (unsigned short int i = 0; i<21; i++){
        unsigned int fiber_point = (ndata_fiber*fiber_index)+(i*3);
        unsigned int atlas_point = (ndata_fiber*fatlas_index)+(i*3);
        unsigned int point_inv = (ndata_fiber*fatlas_index)+(inv*3);
        if (!is_inverted){
            ed = euclidean_distance_norm(subject_data[fiber_point],subject_data[fiber_point+1], subject_data[fiber_point+2],
                                         atlas_data[atlas_point],atlas_data[atlas_point+1], atlas_data[atlas_point+2]);}
        else{
            ed = euclidean_distance_norm(subject_data[fiber_point],subject_data[fiber_point+1], subject_data[fiber_point+2],
                                         atlas_data[point_inv],atlas_data[point_inv+1], atlas_data[point_inv+2]);}

        if (ed>threshold) return -1;
        if (ed >= max_ed)
            max_ed = ed;
        inv--;
    }
    //After pass the comprobation of euclidean distance, will be tested with the lenght factor
    unsigned int fiber_pos = (ndata_fiber*fiber_index);
    unsigned int atlas_pos = (ndata_fiber*fatlas_index);
    float length_fiber1 = euclidean_distance_norm(subject_data[fiber_pos],subject_data[fiber_pos+1], subject_data[fiber_pos+2],
                                                  subject_data[fiber_pos+3],subject_data[fiber_pos+4], subject_data[fiber_pos+5]);
    float length_fiber2 = euclidean_distance_norm(atlas_data[atlas_pos],atlas_data[atlas_pos+1], atlas_data[atlas_pos+2],
                                                  atlas_data[atlas_pos+3],atlas_data[atlas_pos+4], atlas_data[atlas_pos+5]);
    float fact = length_fiber2 < length_fiber1 ? ((length_fiber1-length_fiber2)/length_fiber1) : ((length_fiber2-length_fiber1)/length_fiber2);
    fact = (((fact + 1.0f)*(fact + 1.0f))-1.0f);
    fact = fact < 0.0f ? 0.0f : fact;

    if ((max_ed+fact) >= threshold)
        return -1;
    else
        return max_ed;
}

void freeme(int * assignment){
    free(assignment);
}

int * initialized_array(int size, int value){
    int * new_array = (int *) malloc(size * sizeof(int));
    for (int i = 0; i < size; i++)
        new_array[i] = value;
    return new_array;
}

int * parallel_segmentation(float *atlas_data, float *subject_data, unsigned short int ndata_fiber, 
                            float threshold, unsigned int atlas_size, unsigned int subject_size) {
    int * assignment = initialized_array(subject_size,-1);
    unsigned int nunProc = omp_get_num_procs();
    omp_set_num_threads(nunProc);
#pragma omp parallel
{
#pragma omp for schedule(auto) nowait
        for (unsigned int i = 0; i < subject_size; i++) {
            float ed_i = 500;
            int assignment_i = -1;
            for (unsigned int j = 0; j < atlas_size; j++) {
                int is_inverted, is_discarded;
                float ed = -1;
                unsigned int bundle = j;
                //First test: discard_centers++; discard centroid
                is_discarded = discard_center(subject_data, atlas_data, ndata_fiber, threshold, i, j);
                if (is_discarded == 1) continue;
                //Second test: discard by the extremes
                is_discarded = discard_extremes(subject_data, atlas_data, ndata_fiber, threshold, &is_inverted, i, j);
                if (is_discarded == 1) continue;
                //Third test: discard by four points
                is_discarded = discard_four_points(subject_data, atlas_data, ndata_fiber, threshold, is_inverted, i, j);
                if (is_discarded == 1) continue;
                ed = discarded_21points(subject_data, atlas_data, ndata_fiber, threshold, is_inverted, i, j);
                if (ed != -1) {
                    if (ed < ed_i) {
                        ed_i = ed;
                        assignment_i = bundle;
                    }
                }
            }
            if (assignment_i!=-1)
                assignment[i]=assignment_i;
        }
    }
    return assignment;
}



int * segmentation(unsigned int n_points, float *subject_data, float *atlas_data, float threshold,
                    unsigned int nfibers_subject, unsigned int nfibers_atlas){

    //Number of coord of each fiber
    unsigned short int ndata_fiber = n_points*3;

    int *assignment = parallel_segmentation(atlas_data,subject_data,ndata_fiber,threshold, nfibers_atlas, nfibers_subject);

    unsigned int count = 0;
    for (unsigned int i = 0; i< nfibers_subject;i++){
        if (assignment[i]!= -1)
            count++;
    }

    return assignment;
}