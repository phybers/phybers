#ifndef BUNDLETOOLS_H_INCLUDED
#define BUNDLETOOLS_H_INCLUDED

#include <stdint.h>

struct bundle {
    int32_t nfibers;
    int32_t* npoints;
    float** points;
    };

char* masdata(char* bunfile);
struct bundle read_bundle(char* bunfile);
//char* int2string(int32_t si);
char* int2STR(int32_t si);
void write_bundle(char* outfile, int32_t nfibers, int32_t* npoints, float** points);
struct bundle sliceFiber( struct bundle fibras, int sliceNum);
//int32_t string2int(char* si);
float** fiberDistanceMax(struct bundle f);
struct bundle bundleSampler(struct bundle fibras, float sampler, int modo);//modo=0 para porcentaje y modo=1 numero de fibras

#endif // BUNDLETOOLS_H_INCLUDED
