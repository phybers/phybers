#ifndef FFCLUST_H
#define FFCLUST_H

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

#include "functions.h"

int * segmentation(unsigned int n_points, float *subject_data, float *atlas_data, float threshold,
				unsigned int nfibers_subject, unsigned int nfibers_atlas);

#endif