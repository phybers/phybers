#ifndef DISTANCES_H
#define DISTANCES_H

#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <cstdlib>
#include <vector>
#include <climits>
#include <algorithm>
#include <ctime>
#include <iostream>
#include <iomanip>
#include <cmath>
#include "bundleTools.hpp"

int fDM_main(char *fp_input, char *fp_output);
int gAGFDM_main(char *fp_input, char *fp_output, float maxdist);
struct smax
{
    float value;
    int arg;
};
struct smax floatmax(std::vector<float> &dvector, int lenght);
int gALHCFGF_main(char *fp_input, char *fp_output);

#endif