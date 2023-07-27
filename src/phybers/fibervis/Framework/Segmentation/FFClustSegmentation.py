from .SegmentationHandler import *

from sklearn.cluster import MiniBatchKMeans
import multiprocessing as mp
from scipy import sparse
from functools import partial
# import Framework.CExtend.segmentation as seg
from ...FiberVis_core import ffclust, reSampleBundle
import networkx as nx

import random

num_proc = mp.cpu_count()

def kmeans(points,k):
	kmeans = MiniBatchKMeans(n_clusters=k,random_state=0)
	sm = sparse.csr_matrix(points)
	return kmeans.fit_predict(sm)

def parallel_kmeans(fibers,points,ks):
	# selected_points = np.array(list(list(f[i] for f in fibers) for i in points))

	selected_points = np.swapaxes(fibers.reshape(-1,21,3),0,1)[points,:,:]

	pool = mp.Pool(num_proc)
	results = pool.starmap(kmeans,zip(selected_points,ks))
	pool.close()
	return results

def mapping(point_clusters,r):
	fibers_map = {}
	for i in range(r[0],r[1],1):
		key = "_".join(str(point_clusters[p][i]) for p in range(len(point_clusters)))
		if key not in fibers_map:
			fibers_map[key] = [i]
		else:
			fibers_map[key].append(i)
	return fibers_map

def merge_maps(maps):
	final_map = {}
	for map in maps:
		for key, val in map.items():
			if key not in final_map:
				final_map[key] = val
			else:
				final_map[key].extend(val)
	return final_map

def parallel_mapping(point_clusters,ranges):

	partial_mapping = partial(mapping,point_clusters)
	pool = mp.Pool(num_proc)
	results = pool.map(partial_mapping, ranges)
	pool.close()
	fiber_clusters = merge_maps(results)
	return fiber_clusters

def get_ranges(nfibers):
	total_len = nfibers
	len_groups, rest = divmod(total_len, num_proc)
	return list((n, min(n + len_groups, total_len)) for n in range(0, total_len, len_groups))

def is_inverted(f1,f2):
	dist_00 = np.linalg.norm(f1[0]-f2[0])
	dist_020 = np.linalg.norm(f1[0]-f2[20])
	if dist_00 > dist_020:
		return True
	else:
		return False

def align_fibers(bundle):
	new_fibers = [bundle[0]]
	f1 = bundle[0]
	for f2 in bundle[1:]:
		if is_inverted(f1,f2):
			new_fibers.append(f2[::-1])
		else:
			new_fibers.append(f2)
	return np.asarray(new_fibers)

def centroid_mean_align(bundle):
	fibers = align_fibers(bundle)
	return np.asarray(sum(fibers)/len(fibers))

def parallel_reassignment(fibers,fiber_clusters,central_index,thr):
	size_filter = 5
	large_clusters,small_clusters,large_indices,small_indices,large_centroids,small_centroids = [], [], [], [], [], []
	###########
	fibers_idx = []
	small_idx = []
	###########
	small_indices = []
	for key,indices in fiber_clusters.items():
		if len(indices) > size_filter:
			large_indices.append(int(key.split("_")[central_index]))
			c = [fibers[i] for i in indices]
			large_clusters.append(c)
	###########
			fibers_idx.append(indices)
	###########

			large_centroids.append(centroid_mean_align(c))
		else:
			small_indices.append(int(key.split("_")[central_index]))
			c = [fibers[i] for i in indices]
			small_clusters.append(c)
	###########
			small_idx.append(indices)
	###########
			small_centroids.append(centroid_mean_align(c))
	result = ffclust(21, np.asarray(small_centroids).ravel(), np.asarray(large_centroids).ravel(),
			thr,len(small_centroids),len(large_centroids))
	reassignment = result[:len(small_centroids)]
	# reassignment = seg.segmentation(21,thr, large_centroids,small_centroids,len(small_centroids), len(large_centroids))
	count = 0
	num_fibers_reass = 0
	num_discarded = 0
	for small_index,large_index in enumerate(reassignment):
		fibers = small_clusters[small_index]
		fibers_idx_tmp = small_idx[small_index]

		if int(large_index)!=-1:
			large_clusters[large_index].extend(fibers)
	###########
			fibers_idx[large_index].extend(fibers_idx_tmp)
	###########
			num_fibers_reass += len(fibers)
			count+=1
		else:
			if len(fibers)>2:
				recover_cluster = small_clusters[small_index]
				large_clusters.append(recover_cluster)
	###########
				fibers_idx.append(fibers_idx_tmp)
	###########
				large_indices.append(small_indices[small_index])
			else:
				num_discarded +=1
	return large_clusters,large_indices, fibers_idx

def get_groups(clusters,central_index,fiber_index):
	groups = {}
	for i,cluster in enumerate(clusters):
		index = central_index[i]
		if index not in groups:
			groups[index] = [[cluster],[fiber_index[i]]]
		else:
			groups[index][0].append(cluster)
			groups[index][1].append(fiber_index[i])
	return groups

def matrix_dist(streamlines, get_max=True, get_mean=False):
	x = np.asarray(streamlines)
	distances = ((np.stack((x,x[:,::-1]))[:,None]-x[:,None])**2).sum(axis=4)
	if get_max and get_mean:
		max_distances = np.sqrt(distances.max(axis=3).min(axis=0))
		mean_distances = np.sqrt(distances.mean(axis=3).min(axis=0))
		return max_distances, mean_distances
	elif get_max:
		return np.sqrt(distances.max(axis=3).min(axis=0))
	elif get_mean:
		return  np.sqrt(distances.mean(axis=3).min(axis=0))
	else:
		print('error, should return atleast one matrix')

def create_graph(centroids,thr):
	matrix_dist_ = matrix_dist(centroids, get_max=True)
	matrix_dist_[matrix_dist_>thr] = 0
	G = nx.from_numpy_matrix(matrix_dist_)
	return G

def join(thr,group):
	centroids = [centroid_mean_align(c) for c in group[0]]
	graph = create_graph(centroids,thr)
	cliques = sorted(nx.find_cliques(graph), key=len, reverse=True)
	visited = {}
	new_clusters,new_centroids = [] ,[]
	new_clusters_fiber_idx = []
	for clique in cliques:
		new_cluster = []
		new_cluster_idx = []
		for node in clique:
			# print(node)
			if node not in visited:
				cluster = group[0][node]
				cluster_idx = group[1][node]
				new_cluster.extend(cluster)
				new_cluster_idx.extend(cluster_idx)
				visited[node] = True
		if len(new_cluster)>0:
			new_clusters.append(new_cluster)
			new_centroids.append(centroid_mean_align(new_cluster))
			############################
			new_clusters_fiber_idx.append(new_cluster_idx)
			############################
	# print(len(visited))
	return new_clusters,new_centroids,new_clusters_fiber_idx

def parallel_join(fiber_clusters,cluster_indices,fiber_indices,thr):
	groups = get_groups(fiber_clusters,cluster_indices,fiber_indices)
	# print('groups', groups)
	partial_join = partial(join,thr)
	pool = mp.Pool(num_proc)
	results = pool.map(partial_join, [g for key,g in groups.items()])
	# print('len de groups: ',len(groups) , ' len results: ', len(results))
	pool.close()
	new_clusters,new_centroids = [], []
	new_clusters_fiber_idx = []
	for clust,centroids,fiber_idx in results:
		new_clusters.extend(clust)
		new_clusters_fiber_idx.extend(fiber_idx)
		new_centroids.extend([c] for c in centroids)
	# print('len new_clusters:', len(new_clusters), '   ', len(new_centroids))
	return new_clusters,new_centroids,new_clusters_fiber_idx

class FFClustSegmentation(SegmentationHandler):
	# fibers = IO.read_bundles(args.infile)
	# clusters,centroids,log = clustering.fiber_clustering(fibers,args.points,args.ks,args.thr_seg,args.thr_join)



	def __init__(self, bundle, shaderDict):
		super().__init__(bundle, shaderDict)

		self.segmentationIdentifier = SegmentationTypes.FFClust

		self.fileName = 'FFclust' # temporal

		self.alpha = 0.8

		self.clusters = []

		# Default values:
		self.selected_points = list((0,3,10,17,20))		# Points to be used in map clustering
		self.ks = list((300, 200, 200, 200, 300))		# Number of clusters to be used for each point in K-Means for map
		self.thr_seg = 6								# Minimum threshold for segmentation
		self.thr_join = 6								# Minimum threshold for join

		self.colorTableTexture = None
		self.color = np.array([0.5,0.5,0.5,2.0], dtype=np.float32).reshape((1,4))
		self._loadColorTexture()

		self.configFiberValidator()

		# Creates VBOs & an EBO, then populates them with the point, normal and color data. The elements data goes into the EBO
		self._loadBuffers()
		self.buildVertex2Fiber()
		self.vboAndLinkVertex2Fiber()

		# Check if bundle has fixed point size per fiber (21 vertex per fiber)
		if (self.fiberSizes != 21).sum():
			print('Resampling...')
			self.fixedPoints = np.empty(self.curvescount*self.fiberLengthTimes3, dtype=np.float32)
			reSampleBundle(
				self.points,
				self.fiberSizes,
				self.curvescount,
				self.fixedPoints,
				self.fiberLengthTimes3//3)

			print('Done.')
		else:
			self.fixedPoints = self.points

		self.fixedPoints = self.fixedPoints.reshape(self.curvescount,21,3)

		# self.segmentedBundles = []
		# self.validBundles = []

		self.boundingbox = BoundingBox(shaderDict, self, bundle.boundingbox.dims, bundle.boundingbox.center)
		print('Maximum number of clusters: ', np.iinfo(np.uint16).max)


	def segmentMethod(self):
		print('SEGMENTATION')
		point_clusters = parallel_kmeans(self.fixedPoints,self.selected_points,self.ks)
		fiber_clusters_map = parallel_mapping(point_clusters,get_ranges(self.curvescount))
		central_index = int((len(self.selected_points) - 1)/2)
		fiber_clusters,cluster_indices,fibers_idx = parallel_reassignment(self.fixedPoints,fiber_clusters_map,central_index,self.thr_seg)
		final_clusters,centroids,final_fibers_idx = parallel_join(fiber_clusters,cluster_indices,fibers_idx,self.thr_join)

		self.clusters = final_fibers_idx

		self.fiberValidator[:self.curvescount] = len(self.clusters)

		for index,fibers in enumerate(final_fibers_idx):
			self.fiberValidator[fibers] = index

		self.updateColor(len(final_fibers_idx))
		self.updateColorTexture()

		print(len(self.clusters))
		print(len(final_clusters))


	def updateFiberValidator(self):
		glActiveTexture(GL_TEXTURE1)
		glBindTexture(GL_TEXTURE_2D, self.validFiberTexture)

		glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, *self.validFiberTexDims, GL_RED_INTEGER, GL_UNSIGNED_SHORT, self.fiberValidator)



	def defaultFiberValidator(self):
		return np.zeros(self.validFiberTexDims[1]*self.validFiberTexDims[0], dtype=np.uint16)


	def configFiberValidator(self):
		maxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < self.curvescount:
			raise ValueError('Fiber data set to big for GPU, need to change render mode...')
		self.validFiberTexDims = (maxTexDim, int(math.ceil(self.curvescount/maxTexDim)))
		# self. validFiberTexDims = findIntegersMultiplierFor(self.curvescount, maxTexDim)

		self.fiberValidator = self.defaultFiberValidator()

		self.validFiberTexture = glGenTextures(1)

		glActiveTexture(GL_TEXTURE1)

		glBindTexture(GL_TEXTURE_2D, self.validFiberTexture)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

		bgColor = np.array([1,1,1,1], dtype=np.float32)
		glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, bgColor)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_R16UI, self.validFiberTexDims[0], self.validFiberTexDims[1], 0, GL_RED_INTEGER, GL_UNSIGNED_SHORT, self.fiberValidator)







	def _loadColorTexture(self):
		''' It generates a texture (if not already). Then makes the texture0 the active one and loads the color table as a 1D texture.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''
		maxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < len(self.color):
			raise ValueError('To many bundles inside the atlas... Color texture not big enought.')
		self.validBundleColorTexDims = findIntegersMultiplierFor(len(self.color), maxTexDim)
		print(self.validBundleColorTexDims)

		if self.colorTableTexture == None:
			self.colorTableTexture = glGenTextures(1)

		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.colorTableTexture)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

		bgColor = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
		glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, bgColor)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		# glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, 1, 0, GL_RGBA, GL_FLOAT, self.atlas.colorTable.flatten())
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, *self.validBundleColorTexDims, 0, GL_RGBA, GL_FLOAT, self.color.flatten())


	def updateColor(self, n_of_clusters):
		self.color = np.empty((n_of_clusters+1,4), dtype=np.float32)
		self.color[-1] = [0.5,0.5,0.5,2.0]

		for i in range(n_of_clusters):
			self.color[i] = [random.random(), random.random(), random.random(), 2.0]


	def updateColorTexture(self):
		maxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < len(self.color):
			raise ValueError('To many bundles inside the atlas... Color texture not big enought.')
		self.validBundleColorTexDims = findIntegersMultiplierFor(len(self.color), maxTexDim)
		print(self.validBundleColorTexDims)

		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.colorTableTexture)

		# glTexImage1D(GL_TEXTURE_2D, 0, GL_RGBA, len(self.atlas.bundlesNames)+1, 0, GL_RGBA, GL_FLOAT, self.atlas.colorTable.flatten())
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, *self.validBundleColorTexDims, 0, GL_RGBA, GL_FLOAT, self.color.flatten())


	def _loadBuffers(self):
		''' It generates a VAO, VBO and EBO.
		It populates them with the vertex, normal and colors (the VBO), also the elements (the EBO).

		It finishes when the buffers are linked with attributes on the vertex shader.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		# Reference for vbos, ebos and attribute ptrs
		self.vao = glGenVertexArrays(1)
		glBindVertexArray(self.vao)

		# self.ebo = glGenBuffers(1)

		# VBO positions
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])

		positionAttribute =	self.shader[0].attributeLocation('vertexPos')
		glEnableVertexAttribArray(positionAttribute)
		glVertexAttribPointer(positionAttribute,3, GL_FLOAT, GL_FALSE, 0, None)

		# VBO normals
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[1])

		normalAttribute =	self.shader[0].attributeLocation('vertexNor')
		glEnableVertexAttribArray(normalAttribute)
		glVertexAttribPointer(normalAttribute,	3, GL_FLOAT, GL_FALSE, 0, None)

		# EBO
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)


	def loadUniforms(self):
		super().loadUniforms()

		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('notAssigned'), len(self.clusters))

		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('colorTable'), 0)
		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('fiberValidator'), 1)
