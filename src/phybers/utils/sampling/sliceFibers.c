#include "sliceFibers.h"

int main(char* fp_input, char* fp_output, int point_count)
{ // 21 = 21 puntos
	struct bundle f1,f2;
	//struct bundle read_bundle(char* bunfile)

	//printf("%s\n%s\n%i\nok\n",argv[1],argv[2],string2int(argv[3]));
	printf("%s\n%s\n%i\nok\n", fp_input, fp_output, point_count);

	f1 = read_bundle(fp_input);

	//struct bundle sliceFiber( struct bundle fibras, int sliceNum)
	//f2= sliceFiber( f1, string2int(argv[3]));
	f2 = sliceFiber(f1, point_count);

	//void write_bundle(char* outfile, int32_t nfibers, int32_t* npoints, float** points)
	write_bundle(fp_output, f2.nfibers, f2.npoints, f2.points);

	int k;
        for(k=0;k<f2.nfibers;k++)
        {
    	    float *a = f2.points[k];
	    free(a);
        }

        //free(f1.npoints);
        //free(f1.points);
	free(f2.npoints);
	free(f2.points);
	k;
        for(k=0;k<f1.nfibers;k++)
        {
    	    float *a = f1.points[k];
	    free(a);
        }
	free(f1.npoints);
	free(f1.points);

	return 0;
}
