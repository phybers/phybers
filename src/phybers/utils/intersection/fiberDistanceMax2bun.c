#include "fiberDistanceMax2bun.h"

int main(int argc, char *argv[])
{
   if(argc==4)
   {
    struct bundle f1;
    struct bundle f2;
    f1=read_bundle(argv[1]);
    f2=read_bundle(argv[2]);
    int i,j,cont=1;
    float** m = (float**) malloc (f1.nfibers*sizeof(float*));
    for(i=0;i<f1.nfibers;i++)
	m[i] = (float*) malloc(f2.nfibers*sizeof(float));

    m=fiberDistanceMax2bun(f1,f2);

    FILE *fw;
    fw = fopen(argv[3],"wb");


    for(i=0;i<f1.nfibers;i++)
    {
        for(j=0;j<f2.nfibers;j++)
        {

            fprintf(fw, "%f\t",sqrt(*(m[i]+j)));

            if(j==f2.nfibers-1)
            {
                fprintf(fw, "\n");
            }
        }
     //   cont++;
    }

    fclose(fw);


   }
   else{printf("Cantidad invalida de argumentos\n");}

   return 0;
}
