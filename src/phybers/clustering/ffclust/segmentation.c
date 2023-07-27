/* segmentation.cpp
Authors:
    Narciso López López
    Andrea Vázquez Varela
Creation date: 24-10-2018
Last update: 18-11-2018
*/

#include "segmentation.h"
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

/*Read .bundles files and return (by reference) a vector with the datas*/
float *read_bundles(char *bundles_path, unsigned short int ndata_fiber, unsigned int nfibers) {
    char extension[4]="data";
    size_t path_size = strlen(bundles_path);
    char * path = (char *) malloc(sizeof(char) * (path_size + 4 + 1));
    strcpy(path,bundles_path);
    strcat(path,extension);
    float *data = (float*) malloc (ndata_fiber * nfibers * sizeof(float));
    path[path_size + 4] = 0;
    FILE *fp = fopen(path, "rb");
    printf("%s\n", path);
    if (fp == NULL) {fputs ("File error opening file\n",stderr); exit (1);}
    fseek (fp, 0 , SEEK_END);
    long lSize = ftell(fp);                                // Get file size.
    unsigned int sfiber = sizeof(int32_t) + ndata_fiber*sizeof(float); // Size of a fiber (bytes).  // Add 1 element (uint32_t) because in .bundles/.bundlesdata format the first element of each fiber/centroid corresponds to the amount of points in the fiber/centroid. In this case that number should be always the same.
    float  * buffer = (float *) malloc(sizeof(float) * sfiber);
    unsigned int nFibers = (unsigned int)(lSize/(long)sfiber);                 // Number of fibers
    rewind(fp);
    unsigned int index = 0;
    for(unsigned int j = 0; j < (nFibers); ++j)    // Copy fibers.
    {
        size_t r = fread(buffer, sizeof(float), (ndata_fiber+1), fp);     // Skip the first element of each fiber/centroid (number of points).;
        if (r == -1)
            printf("error reading buffer data");
        for(int s = 1; s < ndata_fiber+1; ++s)
        {
            data[index]=buffer[s];
            index++;
        }
    }
    free(path);
    free(buffer);
    fclose(fp);
    return data;
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
                            float threshold, const int atlas_size, const int subject_size) {
                                 printf("Entra en parallel segmentation");
    int * assignment = initialized_array(subject_size,-1);
    unsigned int nunProc = omp_get_num_procs();
    omp_set_num_threads(nunProc);
        printf("\nEntra en la segmentación\n");
        printf("\nUmbral: %f\n",threshold);
    int i;
#pragma omp parallel
{
    #ifdef _MSC_VER
        #pragma omp for schedule(runtime) nowait
    #else
        #pragma omp for schedule(auto) nowait
    #endif
        for (i = 0; i < subject_size; i++) {
            float ed_i = 500;
            int assignment_i = -1;
            for (int j = 0; j < atlas_size; j++) {
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
    printf("Termina segmentación");
    return assignment;
}



int * segmentation(unsigned int n_points, char *subject_path, char *atlas_path, float threshold,
          char *output_directory, unsigned int nfibers_subject, unsigned int nfibers_atlas){
    double time_start_paralell, parallelFastCPUTime;

    //Number of coord of each fiber
    unsigned short int ndata_fiber = n_points*3;

    //Atlas data
    float *atlas_data = read_bundles(atlas_path, ndata_fiber, nfibers_atlas);
    //Subject data
    float *subject_data = read_bundles(subject_path, ndata_fiber,nfibers_subject);
    time_start_paralell = omp_get_wtime();
    int *assignment = parallel_segmentation(atlas_data,subject_data,ndata_fiber,threshold, (const int)nfibers_atlas, (const int)nfibers_subject);
    parallelFastCPUTime = omp_get_wtime() - time_start_paralell;

    unsigned int count = 0;
    for (unsigned int i = 0; i< nfibers_subject;i++){
        if (assignment[i]!= -1)
            count++;
    }
    free(atlas_data);
    free(subject_data);

    printf("Total segmented fibers: %d\n\n",count);
    printf("Execution time of algorithm: %f seconds\n",parallelFastCPUTime);
    return assignment;
}