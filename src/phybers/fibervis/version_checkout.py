# python version
import sys

print (sys.version)

# import pydicom
# # import nibabel.nicom.dicomwrappers

# # data = nibabel.nicom.dicomwrappers.wrapper_from_file('D:/Codes/UDEC/Database/DICOM/AHUMADA DONOSO/AHUMADA DONOSO 2/fat_fraction_2.dcm')

# file = 'D:/Codes/UDEC/Database/DICOM/AHUMADA DONOSO/AHUMADA DONOSO 2/fat_fraction_2.dcm'

# ds = pydicom.dcmread(file)

# # print(help(ds))

# # for elem in ds.elements():
# # 	print(elem)

# data = ds.pixel_array

# print('data.shape:', data.shape)

# print(help(ds))

# j-bundlesStart[i] == Math.ceil(j/step)

# import numpy as np

# size = 300
# percentage = 20
# step = 100.0/percentage

# array1 = np.zeros(size, dtype=np.int8)
# array2 = np.empty(size, dtype=np.int8)

# for j in range(int(size/step)):
# 	array1[(int) (step*j)] = 1

# rango = np.arange(int(size/step))


# for i in range(rango.size-1):
# 	for j in range(rango[i], rango[i+1]):


# print((array1==1).sum())

# for (j=0; j*step<bundleStart[i+1]-bundleStart[i]; j++)
# 				fiberValidator[bundleStart[i] + ( (int) (step*j))] = true;
