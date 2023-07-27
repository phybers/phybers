# Copyright (C) 2019  Andrea Vázquez Varela

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 30/10/2019
#Last update: 06/03/2020

# # import os
# import ctypes
# # import time
# import numpy as np

# _seg = ctypes.CDLL('Framework/CExtend/segmentation_clust_v1.2/segmentation.so')

# _seg.segmentation.argtypes = (ctypes.c_uint, ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float), ctypes.c_float, ctypes.c_uint,ctypes.c_uint)


# #The result value is a list whose indices are the indices of small clusters, each index contains the index of it's large_cluster reassignment
# def segmentation(nPoints,threshold, large_centroids,small_centroids,nfibers_subject,nfibers_atlas):
# 	global _seg

# 	ncentroids = len(small_centroids)
# 	flt_sc = np.asarray(small_centroids).ravel()
# 	flt_lc = np.asarray(large_centroids).ravel()
# 	sc_array = (ctypes.c_float * len(flt_sc))()
# 	lc_array = (ctypes.c_float * len(flt_lc))()
# 	sc_array[:] = flt_sc
# 	lc_array[:] = flt_lc


# 	_seg.segmentation.restype = ctypes.POINTER(ctypes.c_int)
# 	result = _seg.segmentation(ctypes.c_uint(nPoints), sc_array, lc_array,
# 			ctypes.c_float(threshold),ctypes.c_uint(nfibers_subject),ctypes.c_uint(nfibers_atlas))
# 	result_list = result[:ncentroids]
# 	_seg.freeme(result)
# 	return(result_list)