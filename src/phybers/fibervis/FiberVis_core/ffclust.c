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

#include "ffclust.h"

#define min(a, b) (((a) < (b)) ? (a) : (b))

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
