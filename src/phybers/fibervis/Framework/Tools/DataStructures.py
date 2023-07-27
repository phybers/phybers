import numpy as np
# import Framework.CExtend.cfuncs as cfuncs
from ...FiberVis_core import ROIsSegmentationQueryOctree, ROIsSegmentationPopulateAndDefragmentPool

from .performance import *


class OctreePointBased:
	OT_NODE_CAPACITY = 256

	def __init__(self, points, fiberSizes):
		print('Building Octree...')
		self.vertex = points
		self.treeCount = 0
		self.root = 0
		self.pool = None
		self.vertexIdxPool = None

		x = self.vertex[0::3]
		y = self.vertex[1::3]
		z = self.vertex[2::3]

		xmin, xmax = x.min(),x.max()
		ymin, ymax = y.min(),y.max()
		zmin, zmax = z.min(),z.max()

		radius = np.array([(xmax-xmin)/2, (ymax-ymin)/2, (zmax-zmin)/2], dtype=np.float32) * 1.005
		center = radius + np.array([xmin, ymin, zmin], dtype=np.float32)

		self.CPopulateAndDefragment(points.size, center, radius)

		self.createVertex2Fiber(fiberSizes)


	# @timeit
	def CPopulateAndDefragment(self, vertexSize, center, radius):
		poolSize = int(vertexSize/self.OT_NODE_CAPACITY*4.4 + 1)

		dt = np.dtype([	('children', np.uint32, (8,)),
						('numberOfElements', np.uint32, (1,)),
						('contentElements', np.uint32, (1,)),
						('radius', np.float32, (3,)),
						('center', np.float32, (3,))])

		self.pool = np.empty(poolSize, dtype=dt)
		self.vertexIdxPool = np.empty(self.vertex.size//3, dtype=np.uint32)

		n = ROIsSegmentationPopulateAndDefragmentPool(
			self.pool,
			poolSize,
			self.vertex,
			self.vertex.size,
			center,
			radius,
			self.vertexIdxPool)

		# n = cfuncs.ROIsSegmentationPopulateAndDefragmentPool(
		# 	self.pool.ctypes.data,
		# 	poolSize,
		# 	self.vertex.ctypes.data,
		# 	self.vertex.size,
		# 	center.ctypes.data,
		# 	radius.ctypes.data,
		# 	self.vertexIdxPool.ctypes.data)

		self.pool = np.array(self.pool[:n], copy=True)


	def createVertex2Fiber(self, fiberSizes):
		self.vertexIdx2FiberIdx = np.empty(self.vertexIdxPool.size, dtype=np.int32)

		offset = 0
		for i in range(len(fiberSizes)):
			self.vertexIdx2FiberIdx[offset:offset+fiberSizes[i]] = i
			offset += fiberSizes[i]

	def queryCollision(self, queryPackage, result):
		ROIsSegmentationQueryOctree(len(queryPackage),
									queryPackage,
									self.pool,
									self.vertexIdxPool,
									self.vertexIdx2FiberIdx,
									self.vertex,
									result,
									result.shape[1])

		# cfuncs.ROIsSegmentationQueryOctree(	len(queryPackage),
		# 									queryPackage.ctypes.data,
		# 									self.pool.ctypes.data,
		# 									self.vertexIdxPool.ctypes.data,
		# 									self.vertexIdx2FiberIdx.ctypes.data,
		# 									self.vertex.ctypes.data,
		# 									result.ctypes.data,
		# 									result.shape[1])
