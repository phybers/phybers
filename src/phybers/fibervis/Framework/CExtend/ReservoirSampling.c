#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

// In place segmentation function
void reservoirSamplingMethod(int bundleN,
	int percentage,
	void *pyBundleStart,
	void *pySelectedBundles,
	void *pyFiberValidator) {


	int *bundleStart = (int *) pyBundleStart;
	int *selectedBundles = (int *) pySelectedBundles;
	bool *fiberValidator = (bool *) pyFiberValidator;

	double k_d = 0;
	for (int i=0; i<bundleN; i++)
		if (selectedBundles[i])
			k_d += (bundleStart[i+1]-bundleStart[i])/100.0*percentage;

	int k = ceil(k_d);

	unsigned int *R = (unsigned int*) malloc(k*sizeof(unsigned int));

	int b_init=-1, i=0, i_init=0;
	while (i<k) {
		b_init++;

		if (selectedBundles[b_init]) {
			while (i_init<bundleStart[b_init+1] && i<k)
				R[i++] = i_init++;
		}
		else
			i_init += bundleStart[b_init+1]-bundleStart[b_init];
	}

	if (i_init==bundleStart[b_init+1]) b_init++;
	i=k;
	srand(time(0));

	while (b_init<bundleN) {
		if (selectedBundles[b_init]) {
			while (i_init<bundleStart[b_init+1]) {
				i++;
				int j = rand()%i;

				if (j<k)
					R[j] = i_init;
				i_init++;
			}

		}
		else
			i_init += bundleStart[b_init+1]-bundleStart[b_init];
		b_init++;
	}

	for (i=0; i<k; i++)
		fiberValidator[R[i]] = true;

	free(R);
}











// In place segmentation function
void reservoirSamplingMethodOpti(int bundleN,
	int percentage,
	void *pyBundleStart,
	void *pySelectedBundles,
	void *pyFiberValidator) {


	int *bundleStart = (int *) pyBundleStart;
	int *selectedBundles = (int *) pySelectedBundles;
	bool *fiberValidator = (bool *) pyFiberValidator;

	double k_d = 0;
	for (int i=0; i<bundleN; i++)
		if (selectedBundles[i])
			k_d += (bundleStart[i+1]-bundleStart[i])/100.0*percentage;

	int k = k_d;

	unsigned int *R = (unsigned int*) malloc(k*sizeof(unsigned int));

	int b_init=-1, i=0, i_init=0;
	while (i<k) {
		b_init++;

		if (selectedBundles[b_init]) {
			while (i_init<bundleStart[b_init+1] && i<k)
				R[i++] = i_init++;
		}
		else
			i_init += bundleStart[b_init+1]-bundleStart[b_init];
	}

	if (i_init==bundleStart[b_init+1]) b_init++;
	i=k;
	srand(time(0));
	double W = exp(log((double)rand() / (double)RAND_MAX)/k);
	printf("W:%.6f\n", W);

	/////////////////////////////////////////////////////////
	int offset = floor(log((double)rand() / (double)RAND_MAX)/log(1-W)) + 1;
	printf("next in %d\n", offset);

	while (b_init<bundleN) {
		printf("bundle: %d\n",b_init);
		if (selectedBundles[b_init]) {
			while (i_init+offset<bundleStart[b_init+1]) {
				printf("i_init: %d \t offset: %d\n", i_init,offset);
				i_init += offset;
				R[rand()%k] = i_init;
				W = exp(log((double)rand() / (double)RAND_MAX)/k);
				offset = floor(log((double)rand() / (double)RAND_MAX)/log(1.0-W)) + 1;
			}

			offset -= bundleStart[b_init+1]-i_init;
			i_init = bundleStart[b_init+1];
		}
		else
			i_init += bundleStart[b_init+1]-bundleStart[b_init];
		b_init++;
	}

	for (i=0; i<k; i++)
		fiberValidator[R[i]] = true;

	free(R);
}