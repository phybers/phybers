#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#include "main.h"
#include "nifti1.h"
#include "bundleTools.h"

#define MIN_HEADER_SIZE 348

int index_by_coord(int x, int y, int z, int w, int dimx, int dimy,int dimz,int dimw){

    return x + y*dimx + z* dimx*dimy + w* dimx*dimy*dimz;
}

int main(int argc, char *argv[])
{

    if(argc <= 3){
        printf("Invalid Arguments!\n");
        printf("Please write: acpc_dc2standard.nii dir_fibras.bundles dir_fibras_deform.bundles");
        exit(1);
    }
    //Leo el volumen .nii
    nifti_1_header atlas;
    int ret;
    FILE *fp;

    fp = fopen(argv[1], "rb");

    ret = fread(&atlas, MIN_HEADER_SIZE, 1, fp);

    ret = fseek(fp, (long)(atlas.vox_offset), SEEK_SET);

    float *data=(float *) malloc(sizeof(float) * atlas.dim[3]*atlas.dim[1]*atlas.dim[2]*atlas.dim[4]);

    ret = fread(data, sizeof(float), atlas.dim[3]*atlas.dim[1]*atlas.dim[2]*atlas.dim[4], fp);
    fclose(fp);


    struct bundle all_fibras;
    all_fibras = read_bundle(argv[2]);



    // new bundles to store the transformation
    float** points;
    points = (float**) malloc (all_fibras.nfibers*sizeof(float*));

    int32_t* npoints;
    npoints=(int32_t*) malloc(all_fibras.nfibers*sizeof(int32_t));


    struct bundle fas;

    fas.npoints=npoints;
    fas.points=points;
    fas.nfibers = all_fibras.nfibers;



    for(int i = 0; i < all_fibras.nfibers; i++){

        fas.npoints[i] = all_fibras.npoints[i];
        fas.points[i] = (float* )malloc((*(all_fibras.npoints+i))*3*sizeof(float));
        }

    for(int i=0;i<(all_fibras.nfibers);i++)
    {

        for(int k=0;k<(all_fibras.npoints[i]);k++) //Itero por los puntos de cada fibra
        {
            int x =      (int)(*(all_fibras.points[i]+(k*3)+0))/2;
            int y = 108- (int)(*(all_fibras.points[i]+(k*3)+1))/2;
            int z = 90 - (int)(*(all_fibras.points[i]+(k*3)+2))/2;

            int coord_0 = index_by_coord( x,  y,  z,  0, atlas.dim[1], atlas.dim[2],atlas.dim[3],atlas.dim[4]);
            int coord_1 = index_by_coord( x,  y,  z,  1, atlas.dim[1], atlas.dim[2],atlas.dim[3],atlas.dim[4]);
            int coord_2 = index_by_coord( x,  y,  z,  2, atlas.dim[1], atlas.dim[2],atlas.dim[3],atlas.dim[4]);

            float traslation_0 = data[coord_0];
            float traslation_1 = data[coord_1];
            float traslation_2 = data[coord_2];



        *(fas.points[i]+(k*3)+0) = *(all_fibras.points[i]+(k*3)+0) - traslation_0;
        *(fas.points[i]+(k*3)+1) = *(all_fibras.points[i]+(k*3)+1) + traslation_1;
        *(fas.points[i]+(k*3)+2) = *(all_fibras.points[i]+(k*3)+2) + traslation_2;

        }
    }

       write_bundle(argv[3], fas.nfibers, fas.npoints, fas.points);

       //Free Memory
       int k;

       for(k=0;k<all_fibras.nfibers;k++)
       {
       	float *a = all_fibras.points[k];
	    free(a);
	   }

       free(all_fibras.npoints);
       free(all_fibras.points);


       for(k=0;k<fas.nfibers;k++)
       {
       	float *a = fas.points[k];
	    free(a);
	   }

       free(fas.npoints);
       free(fas.points);

       free(data);

    return 0;
}
