// In place segmentation function
void inPlaceSegmentationMethod(int bundleN,
	int percentage,
	void *pyBundleStart,
	void *pySelectedBundles,
	void *pyFiberValidator) {


	int *bundleStart = (int *) pyBundleStart;
	int *selectedBundles = (int *) pySelectedBundles;
	bool *fiberValidator = (bool *) pyFiberValidator;
	
	int i, j;

	float step = 100.0/percentage;

	for (i=0; i<bundleN; i++)
		if (selectedBundles[i])
			for (j=0; j*step<bundleStart[i+1]-bundleStart[i]; j++)
				fiberValidator[bundleStart[i] + ( (int) (step*j))] = true;
}
