'''
to-do:
	readColorFile
'''

from .VisualizationBaseObject import *
from .BoundingBox import BoundingBox
import os
import nibabel as nib
from .Tools.utilities import findIntegersMultiplierFor
from .Tools.Quaternion import Quaternion

from .Tools.performance import *
import math

# import Framework.CExtend.cfuncs as cfuncs
from ..FiberVis_core import readBundle, readTrk, applyMatrix, reCalculateNormals, readTck
from importlib_resources import files

_b_vs = files('phybers.fibervis.shaders').joinpath('bundle.vs')
_sfs_fs = files('phybers.fibervis.shaders').joinpath('standardFragmentShader.fs')
_c_vs = files('phybers.fibervis.shaders').joinpath('cylinder.vs')
_c_gs = files('phybers.fibervis.shaders').joinpath('cylinder.gs')
_q_glsl = files('phybers.fibervis.shaders').joinpath('quaternion.glsl')


class Bundle(VisualizationBaseObject):
	''' Class for drawing all kind of bundle files (currently implemented .bundle)
	'''

	def __init__(self, sPath, shaderDict, parent):
		''' Initialize a Bundle object.
		It copies references to the path and the gl program.
		Then it loads the information from the file (points, normals, etc).

		It prepares the color texture, then loads it.

		Sends the information to the GPU buffers.

		Initialize  all parameters.

		The drawable variable is set to True.

		Parameters
		----------
		sPath : str
			String containing path for the bundle file (.bundles)
		shaderProgram : GLInt
			Reference to the gl program containing all the shaders

		'''

		super().__init__(parent, shaderDict)
		self.nShader = 2
		self.identifier = VisualizationObject.Bundle

		self.path = sPath
		self.fileName = sPath.split('/')[-1]

		self.points = None
		self.normals = None
		self.color = None
		self.elements = None
		self.fiberSizes = None

		self.bundlesName = None
		self.bundlesStart = None
		self.curvescount = 0
		self.bundlesInterval = None

		# Read the vertex, fiber index and bundle index (self. points, fibers, bundles)
		self._readFibers()

		# Initialize the values on colorTable
		self.colorTable = None
		self._createColorTable()

		# Initialize of texture id and loading of self.colorTable into the GPU
		self.colorTableTexture = None
		self.validBundleColorTexDims = None
		self._loadColorTexture()

		# Load cylinder shader static data
		self.loadStaticUniforms()

		# Creates VBOs & an EBO, then populates them with the point, normal and color data. The elements data goes into the EBO
		self._loadBuffers()

		# Ready to draw
		self.drawable = True

		dims, center = self.calculateBoundingBoxDimCenter()

		self.boundingbox = BoundingBox(shaderDict, self, dims, center)

		print("Loading ready:\n\t", self.curvescount, " fibers.\n\t", len(self.bundlesName), " bundles.")


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		GL.glDeleteVertexArrays(self.nShader, self.vao)

		GL.glDeleteBuffers(3, self.vbo)
		GL.glDeleteBuffers(1, [self.ebo])

		GL.glDeleteTextures([self.colorTableTexture])

		self.clean = True


	def calculateBoundingBoxDimCenter(self):
		# We set the boundingbox parameters
		x = self.points[0::3]
		y = self.points[1::3]
		z = self.points[2::3]

		xmin, xmax = x.min(),x.max()
		ymin, ymax = y.min(),y.max()
		zmin, zmax = z.min(),z.max()

		dims = np.array([xmax-xmin, ymax-ymin, zmax-zmin], dtype=np.float32)
		center = np.array([xmin, ymin, zmin], dtype=np.float32)#+dims/2

		return dims, center

	# @averageTimeit
	@timeit
	def _readFibers(self):
		''' It reads the information from self.path file.
		Also calculates the normals and color attributes.
		Finally creates the ebo buffer.

		Allowed files: .bundles, .trk

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		extension = self.path.split('.')[-1]

		# Bundle file
		if extension == 'bundles':
			self._openBundle()

		# Trk file
		elif extension == 'trk':
			self._openTrk()

		# Tck file
		elif extension == 'tck':
			self._openTck()

		# Unsopported file
		else:
			raise TypeError('Unsupported file.', extension)


	def _openBundle(self):
		''' This function reads the dictionary from the .bundles file.
		It then creates the numpy array for points, normals, color, ebo (elements) and fiberSizes (for bundles with different fiber size).

		Then it calls a C function loaded using Ctypes, passing a pointer to the numpy's data. The arrays are populated in C.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		print('Opening bundle file {}'.format(self.path))


		bunFile = self.path + 'data'
		dataSize = os.path.getsize(bunFile)

		ns = dict()
		with open(self.path) as f:
			exec(f.read(), ns)

		bundlescount = ns[ 'attributes' ][ 'bundles' ]
		self.curvescount = ns[ 'attributes' ][ 'curves_count' ]

		self.bundlesName = bundlescount[::2]
		self.bundlesStart = bundlescount[1::2]

		# self.points = np.empty(dataSize//4-self.curvescount, dtype=np.float32)
		# self.normals = np.empty(dataSize//4-self.curvescount, dtype=np.float32)
		# self.color = np.empty((dataSize//4-self.curvescount)//3, dtype=np.int32)
		# self.elements = np.empty((dataSize//4-self.curvescount)//3+self.curvescount, dtype=np.uint32)
		# self.fiberSizes = np.empty(self.curvescount, dtype=np.int32)

		self.bundlesInterval = np.array(self.bundlesStart+[self.curvescount], dtype=np.int32)

		# cfuncs.readBundleFile(
		# 	bunFile.encode('utf-8'),
		# 	self.points.ctypes.data,
		# 	self.normals.ctypes.data,
		# 	self.color.ctypes.data,
		# 	self.elements.ctypes.data,
		# 	self.fiberSizes.ctypes.data,
		# 	self.bundlesInterval.ctypes.data,
		# 	self.curvescount,
		# 	self.bundlesInterval.size)

		data = readBundle(bunFile,self.curvescount,self.bundlesInterval,self.bundlesInterval.size)
		self.points = data['points']
		self.normals = data['normals']
		self.color = data['color']
		self.elements = data['elements']
		self.fiberSizes = data['fiberSizes']

	def _openTrk(self):
		'''

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		print('Opening trk file {}'.format(self.path))

		data = readTrk(self.path)

		self.points = data['points']
		self.normals = data['normals']
		self.color = data['color']

		self.elements = data['elements']
		self.fiberSizes = data['fiberSizes']

		voxelSize = data['header']['voxel_size']
		vox2RasMat = data['header']['vox_to_ras']

		self.curvescount = data['header']['n_count']
		self.bundlesName = [self.fileName]
		self.bundlesStart = [0]


		# cfuncs.readTrkHeader(self.path.encode('utf-8'),
		# 	voxelSize.ctypes.data,
		# 	nScalars.ctypes.data,
		# 	nProperties.ctypes.data,
		# 	vox2RasMat.ctypes.data,
		# 	nCount.ctypes.data,
		# 	fileSize.ctypes.data,
		# 	headerSize.ctypes.data)

		# self.curvescount = nCount[0]
		# self.bundlesName = [self.fileName]
		# self.bundlesStart = [0]

		# size = (fileSize//4-nCount*(nProperties+1))*3//(3+nScalars)


		# self.points = np.empty(size, dtype=np.float32)
		# self.normals = np.empty(size, dtype=np.float32)
		# self.color = np.zeros(size//3, dtype=np.int32)

		# self.elements = np.empty(size//3+self.curvescount, dtype=np.uint32)
		# self.fiberSizes = np.empty(nCount, dtype=np.int32)

		# scalars = np.empty(size//3*nScalars, dtype=np.float32)
		# properties = np.empty(nCount*nProperties, dtype=np.float32)


		# cfuncs.readTrkBody(self.path.encode('utf-8'),
		# 	headerSize,
		# 	nScalars,
		# 	nProperties,
		# 	self.points.ctypes.data,
		# 	self.normals.ctypes.data,
		# 	self.elements.ctypes.data,
		# 	self.fiberSizes.ctypes.data,
		# 	self.curvescount,
		# 	scalars.ctypes.data,
		# 	properties.ctypes.data)

		inverseVoxelSize = glm.scaleMatrix([1/voxelSize[0], 1/voxelSize[1], 1/voxelSize[2]])
		trkMat = np.matmul(vox2RasMat, inverseVoxelSize)
		halfVoxelSize = glm.translateMatrix(-voxelSize/2)
		trkMat = np.matmul(trkMat, halfVoxelSize)

		# cfuncs.applyMatrix(self.points.ctypes.data,
		# 	self.points.size,
		# 	trkMat.ctypes.data)
		applyMatrix(self.points, trkMat)

		normal = np.empty(3, dtype=np.float32)
		normal = self.points[:3] - self.points[3:6]
		normal /= np.linalg.norm(normal)

		if (normal-self.normals[:3]).max() >= 0.01:
			print('reCalculateNormals')

			# cfuncs.reCalculateNormals(
			# 	self.points.ctypes.data,
			# 	self.normals.ctypes.data,
			# 	self.fiberSizes.ctypes.data,
			# 	self.curvescount)
			reCalculateNormals(
							self.points,
							self.normals,
							self.fiberSizes,
							self.curvescount)


	def _openTck(self):

		print('Opening tck file {}'.format(self.path))

		data = readTck(self.path)

		self.curvescount = data['n_count']
		self.bundlesName = [self.fileName]
		self.bundlesStart = [0]

		self.points = data['points']
		self.normals = data['normals']
		self.color = data['color']

		self.elements = data['elements']
		self.fiberSizes = data['fiberSizes']





		# nCount = np.empty(1, dtype=np.int32)
		# fileSize = np.empty(1, dtype=np.uint)
		# headerSize = np.empty(1, dtype=np.int32)

		# cfuncs.readTckHeader(self.path.encode('utf-8'),
		# 	nCount.ctypes.data,
		# 	fileSize.ctypes.data,
		# 	headerSize.ctypes.data)

		# self.curvescount = nCount[0]
		# self.bundlesName = [self.fileName]
		# self.bundlesStart = [0]

		# size = int((fileSize[0]-12-12*self.curvescount)//4)

		# self.points = np.empty(size, dtype=np.float32)
		# self.normals = np.empty(size, dtype=np.float32)
		# self.color = np.zeros(size//3, dtype=np.int32)

		# self.elements = np.empty(size//3+self.curvescount, dtype=np.uint32)
		# self.fiberSizes = np.zeros(nCount, dtype=np.int32)

		# cfuncs.readTckBody(self.path.encode('utf-8'),
		# 	headerSize,
		# 	self.points.ctypes.data,
		# 	self.normals.ctypes.data,
		# 	self.elements.ctypes.data,
		# 	self.fiberSizes.ctypes.data,
		# 	self.curvescount)


		# trkObj = nib.streamlines.load(self.path)

		# self.curvescount = len(trkObj.streamlines)

		# # Just for now, cuz I dont know where to retrive information about bundles in a trk
		# self.bundlesName = [self.fileName]
		# self.bundlesStart = [0]

		# self.fiberSizes = np.array([i.shape[0] for i in trkObj.streamlines], dtype=np.int32)

		# size = self.fiberSizes.sum()
		# print(size*3)
		# self.points = np.concatenate(trkObj.streamlines).ravel()
		# self.normals = np.empty(size*3, dtype=np.float32)
		# self.color = np.empty(size, dtype=np.int32)

		# self.elements = np.empty(size+self.curvescount, dtype=np.uint32)

		# bun = np.array(self.bundlesStart+[self.curvescount], dtype=np.int32)

		# cfuncs.createVBOAndEBOFromPoints(
		# 	self.points.ctypes.data,
		# 	self.normals.ctypes.data,
		# 	self.color.ctypes.data,
		# 	self.elements.ctypes.data,
		# 	self.fiberSizes.ctypes.data,
		# 	bun.ctypes.data,
		# 	self.curvescount,
		# 	bun.size)




	def readColorFile(self, colorFile):
		pass


	def loadAndApplyMatrix(self, matrixFile):
		extension = matrixFile.split('.')[-1]

		# numpy matrix file
		if extension == 'npy':
			transform = Bundle.loadNumpyMatrix(matrixFile)

		# brain visa (trm) matrix file
		elif extension == 'trm':
			transform = Bundle.loadTrmMatrix(matrixFile)

		elif extension == 'txt':
			transform = Bundle.loadTxtMatrix(matrixFile)

		# Unsopported file
		else:
			raise TypeError('Unsupported matrix file.', extension)

		self.applyMatrix(transform)


	def applyMatrix(self, transform):
		applyMatrix(self.points,transform)
		# cfuncs.applyMatrix(self.points.ctypes.data,
		# 	self.points.size,
		# 	transform.ctypes.data)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[0])
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, self.points.nbytes, self.points)

		normal = np.empty(3, dtype=np.float32)
		normal = self.points[:3] - self.points[3:6]
		normal /= np.linalg.norm(normal)

		if (normal-self.normals[:3]).max() >= 0.01:
			reCalculateNormals(
							self.points,
							self.normals,
							self.fiberSizes,
							self.curvescount)
			# cfuncs.reCalculateNormals(
			# 	self.points.ctypes.data,
			# 	self.normals.ctypes.data,
			# 	self.fiberSizes.ctypes.data,
			# 	self.curvescount)

			GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[1])
			GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
				0,
				self.normals.nbytes,
				self.normals)

		dims, center = self.calculateBoundingBoxDimCenter()
		self.boundingbox.updateBBModel(dims, center)

	@staticmethod
	def loadNumpyMatrix(numpyMatrixFile):
		return np.load(numpyMatrixFile).astype(np.float32)

	@staticmethod
	def loadTrmMatrix(trmMatrixFile):
		transform = np.zeros(16, dtype=np.float32)

		with open(trmMatrixFile) as f:
			lines = f.readlines()
			translate = lines[0].split(' ')

			transform[0:3] = [float(x) for x in lines[1].split(' ')]
			transform[3] = float(translate[0])

			transform[4:7] = [float(x) for x in lines[2].split(' ')]
			transform[7] = float(translate[1])

			transform[8:11] = [float(x) for x in lines[3].split(' ')]
			transform[11] = float(translate[2])

			transform[15] = 1.0

		return transform

	@staticmethod
	def loadTxtMatrix(txtMatrixFile):
		return np.loadtxt(txtMatrixFile, dtype=np.float32, usecols=range(4))


	def _createColorTable(self):
		''' It creates a color (rgba) randomly for each bundle in the file.
		The table is then loaded to the GPU as 1D texture.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		self.colorTable = np.empty((len(self.bundlesStart), 4), dtype=np.float32)

		for i in range(len(self.bundlesStart)):
			self.colorTable[i,:] = [random.random(), random.random(), random.random(), 1.0]

		hieTable = [
			# ('AR_LEFT', [233, 18, 0]),
			# ('AR_ANT_LEFT', [65, 149, 45]),
			# ('AR_POST_LEFT', [226, 226, 0]),
			# ('AR_RIGHT', [233, 18, 0]),
			# ('AR_ANT_RIGHT', [65, 149, 45]),
			# ('AR_POST_RIGHT', [226, 226, 0]),
			# ('CST_LEFT', [228, 122, 0]),
			# ('CST_RIGHT', [228, 122, 0]),
			# ('CST_long_LEFT', [228, 122, 0]),
			# ('CST_long_RIGHT', [228, 122, 0]),
			# ('THAL_FRONT_LEFT', [186, 185, 167]),
			# ('THAL_MOT_LEFT', [45, 151, 131]),
			# ('THAL_PAR_LEFT', [237, 172, 167]),
			# ('THAL_TEMP_LEFT', [217, 156, 0]),
			# ('THAL_OCC_LEFT', [143, 201, 199]),
			# ('THAL_FRONT_RIGHT', [186, 185, 167]),
			# ('THAL_MOT_RIGHT', [45, 151, 131]),
			# ('THAL_PAR_RIGHT', [237, 172, 167]),
			# ('THAL_TEMP_RIGHT', [217, 156, 0]),
			# ('THAL_OCC_RIGHT', [143, 201, 199]),
			# ('IFO_LEFT', [226, 108, 232]),
			# ('IFO_RIGHT', [226, 108, 232]),
			# ('IL_LEFT', [103, 51, 90]),
			# ('IL_RIGHT', [103, 51, 90]),
			# ('UN_LEFT', [76, 255, 255]),
			# ('UN_RIGHT', [76, 255, 255]),
			# ('CG2_LEFT', [145, 235, 9]),
			# ('CG_LEFT', [172, 70, 32]),
			# ('CG3_LEFT', [27, 108, 183]),
			# ('CG2_RIGHT', [145, 235, 9]),
			# ('CG_RIGHT', [172, 70, 32]),
			# ('CG3_RIGHT', [27, 108, 183]),
			# ('FORNIX_LEFT', [0, 0, 0]),
			# ('FORNIX_RIGHT', [0, 0, 0]),
			# ('CC_ROSTRUM', [204, 0, 97]),
			# ('CC_SPLENIUM', [75, 39, 32]),
			# ('CC_BODY', [0, 67, 0]),
			# ('CC_GENU', [36, 0, 130]),
			# ('THAL_PAR_LEFT', [237, 162, 147])

			# fibras largas
			####################################
			# fibras cortas

			('lh_PoC-PrC_0', [255, 0, 0]),
			('rh_PoC-PrC_0', [255, 0, 0]),
			('lh_PoC-PrC_1', [0, 255, 0]),
			('rh_PoC-PrC_1', [0, 255, 0]),
			('lh_PoC-PrC_2', [0, 0, 200]),
			('rh_PoC-PrC_2', [0, 0, 200]),
			('lh_PoC-PrC_3', [255, 255, 20]),
			('rh_CAC-PoCi_0', [188, 243, 243]),
			('rh_PrC-SP_0', [190, 21, 216]),
			('lh_PoCi-RAC_0', [179, 147, 47]),
			('rh_PoCi-RAC_0', [179, 147, 47]),
			('lh_MOF-ST_0', [249, 182, 249]),
			('rh_MOF-ST_0', [249, 182, 249]),
			('rh_PrC-SM_0', [125, 100, 50]),
			('lh_PrC-SM_0', [125, 100, 50]),
			('lh_Or-Ins_0', [147, 147, 179]),
			('rh_Or-Ins_0', [147, 147, 179]),
			('lh_Op-PrC_0', [255, 0, 255]),
			('rh_Op-PrC_0', [255, 0, 255]),
			('lh_PrC-SF_0', [250, 100, 0]),
			('lh_RMF-SF_0', [100, 25, 150]),
			('rh_RMF-SF_0', [100, 25, 150]),
			('lh_RMF-SF_1', [80, 230, 180]),
			('rh_RMF-SF_1', [80, 230, 180]),
			('lh_LOF-ST_0', [240, 100, 100]),
			('rh_LOF-ST_0', [240, 100, 100]),
			('lh_Op-Ins_0', [50, 125, 100]),
			('rh_Op-Ins_0', [50, 125, 100]),
			('lh_LOF-RMF_0', [40, 40, 255]),
			('rh_LOF-RMF_0', [40, 40, 255]),
			('lh_LOF-RMF_1', [250, 160, 0]),
			('rh_LOF-RMF_1', [250, 160, 0]),
			('lh_IP-MT_0', [255, 20, 147]),
			('rh_IP-MT_0', [255, 20, 147]),
			('lh_ST-TT_0', [138, 43, 226]),
			('rh_ST-TT_0', [138, 43, 226]),
			('lh_CMF-Op_0', [210, 105, 30]),
			('lh_CAC-PrCu_0', [0, 0, 139]),
			('rh_CAC-PrCu_0', [0, 0, 139]),
			('lh_IC-PrCu_0', [0, 150, 0]),
			('rh_IC-PrCu_0', [0, 150, 0]),
			('lh_Op-SF_0', [150, 25, 150]),
			('rh_Op-SF_0', [150, 25, 150]),
			('lh_PoCi-PrCu_0', [150, 25, 150]),
			('lh_PoCi-PrCu_1', [180, 147, 180]),
			('rh_PoCi-PrCu_1', [180, 147, 180]),
			('rh_PoCi-PrCu_2', [0, 250, 0]),
			('lh_LOF-Or_0', [255, 255, 20]),
			('lh_CMF-RMF_0', [50, 100, 125]),
			('rh_CMF-RMF_0', [50, 100, 125]),
			('lh_Fu-LO_0', [188, 143, 143]),
			('rh_Fu-LO_1', [229, 229, 112]),
			('lh_PoC-Ins_0', [119, 200, 0]),
			('rh_LO-SP_0', [30, 144, 255]),
			('lh_Tr-SF_0', [255, 117, 20]),
			('rh_Tr-SF_0', [255, 117, 20]),
			('lh_SM-Ins_0', [100, 100, 200]),
			('rh_SM-Ins_0', [100, 100, 200]),
			('lh_IP-IT_0', [100, 0, 100]),
			('rh_IP-IT_0', [100, 0, 100]),
			('rh_Cu-Li_0', [184, 134, 11]),
			('lh_CMF-PoC_0', [141, 188, 143]),
			('rh_Op-Tr_0', [173, 255, 47]),
			('lh_Tr-Ins_0', [255, 160, 122]),
			('rh_Tr-Ins_0', [255, 160, 122]),
			('lh_PrC-Ins_0', [32, 178, 170]),
			('rh_PrC-Ins_0', [32, 178, 170]),
			('lh_CMF-SF_0', [224, 176, 255]),
			('rh_CMF-SF_0', [224, 176, 255]),
			('rh_CMF-SF_1', [107, 142, 35]),
			('rh_LOF-MOF_0', [15, 15, 15]),
			('lh_MT-SM_0', [139, 0, 0]),
			('rh_MT-SM_0', [139, 0, 0]),
			('lh_PoC-SM_0', [219, 112, 147]),
			('rh_PoC-SM_0', [219, 112, 147]),
			('lh_PoC-SM_1', [152, 251, 152]),
			('rh_RAC-SF_0', [238, 232, 170]),
			('lh_RAC-SF_1', [218, 112, 214]),
			('lh_PoCi-SF_0', [46, 139, 87]),
			('lh_IP-SM_0', [160, 82, 45]),
			('rh_IP-SM_0', [160, 82, 45]),
			('lh_IP-SP_0', [0, 255, 127]),
			('rh_IP-SP_0', [0, 255, 127]),
			('lh_IP-SP_1', [244, 164, 96]),
			('rh_IP-LO_0', [106, 90, 205]),
			('lh_IP-LO_1', [192, 192, 192]),
			('rh_PoC-SP_0', [255, 69, 0]),
			('rh_PoC-SP_1', [72, 209, 204]),
			('lh_IT-MT_0', [210, 180, 140]),
			('rh_IT-MT_1', [135, 206, 235]),
			('rh_IT-MT_2', [199, 21, 133]),
			('lh_ST-Ins_0', [255, 218, 185]),
			('lh_SP-SM_0', [128, 0, 0]),
			('rh_SP-SM_0', [128, 0, 0]),
			('lh_MT-ST_0', [218, 112, 214]),
			('rh_MT-ST_0', [218, 112, 214]),
			('lh_CMF-PrC_0', [205, 92, 92]),
			('rh_CMF-PrC_0', [205, 92, 92]),
			('lh_CMF-PrC_1', [205, 133, 63]),
			('rh_CMF-PrC_1', [205, 133, 63])
		]

		for i in range(len(self.bundlesName)):
			try:
				self.colorTable[i,:3] = hieTable[[i[0] for i in hieTable].index(self.bundlesName[i])][1]
				self.colorTable[i,:3] /= 255
			except:
				continue



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
		self.vao = GL.glGenVertexArrays(self.nShader)
		self.vbo = GL.glGenBuffers(3)
		self.ebo = GL.glGenBuffers(1)



		#################
		# Lines shader
		GL.glBindVertexArray(self.vao[0])

		# Enable attributes
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')
		normalAttribute =	self.shader[0].attributeLocation('vertexNor')
		colorAttribute =	self.shader[0].attributeLocation('vertexCol')

		# VBO
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[0])
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL.GL_STATIC_DRAW)	# Create empty buffer
		GL.glEnableVertexAttribArray(positionAttribute)
		GL.glVertexAttribPointer(positionAttribute,3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[1])
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL.GL_STATIC_DRAW)	# Create empty buffer
		GL.glEnableVertexAttribArray(normalAttribute)
		GL.glVertexAttribPointer(normalAttribute,	3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[2])
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.color.nbytes, self.color, GL.GL_STATIC_DRAW)	# Create empty buffer
		GL.glEnableVertexAttribArray(colorAttribute)
		GL.glVertexAttribPointer(colorAttribute,	1, GL.GL_INT, GL.GL_FALSE, 0, None)

		# EBO
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.elements.nbytes, self.elements, GL.GL_STATIC_DRAW)


		#################
		# Cylinder shader
		GL.glBindVertexArray(self.vao[1])

		# Enable attributes
		positionAttribute =	self.shader[1].attributeLocation('vertexPos')
		colorAttribute =	self.shader[1].attributeLocation('vertexCol')

		# VBO
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[0])
		GL.glEnableVertexAttribArray(positionAttribute)
		GL.glVertexAttribPointer(positionAttribute, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo[2])
		GL.glEnableVertexAttribArray(colorAttribute)
		GL.glVertexAttribPointer(colorAttribute, 1, GL.GL_INT, GL.GL_FALSE, 0, None)

		# EBO
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

		# Dereference vao
		GL.glBindVertexArray(0)


	def _loadColorTexture(self):
		''' It generates a texture (if not already). Then makes the texture0 the active one and loads the color table as a 1D texture.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''
		maxTexDim = GL.glGetIntegerv(GL.GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < len(self.bundlesStart):
			raise ValueError('To many bundles inside the file... Color texture not big enought.')
		self.validBundleColorTexDims = findIntegersMultiplierFor(len(self.bundlesStart), maxTexDim)
		# self.validBundleColorTexDims = (maxTexDim, int(math.ceil(len(self.bundlesStart)/maxTexDim)))

		if self.colorTableTexture == None:
			self.colorTableTexture = GL.glGenTextures(1)

		GL.glActiveTexture(GL.GL_TEXTURE0)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.colorTableTexture)

		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_BORDER)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_BORDER)

		bgColor = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
		GL.glTexParameterfv(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BORDER_COLOR, bgColor)

		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)

		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.validBundleColorTexDims[0], self.validBundleColorTexDims[1], 0, GL.GL_RGBA, GL.GL_FLOAT, self.colorTable.flatten())


	def loadStaticUniforms(self):
		def createCylinder(nFaces, r):
			rotationX = Quaternion.fromAngleAxis(2*np.pi/nFaces, [1, 0, 0])

			data = np.empty((nFaces+1)*2, dtype=np.float32)
			cylinderOffset = np.array([0, cylinderRadius, 0], dtype=np.float32)

			# Rotate vertex
			for i in range(nFaces+1):
				cylinderOffset = rotationX.rotateVector(cylinderOffset)
				data[ 2*i ] = cylinderOffset[1]
				data[2*i+1] = cylinderOffset[2]

			return data

		# create static data
		cylinderNFaces = 7
		cylinderRadius = 0.15
		cylinderData = createCylinder(cylinderNFaces, cylinderRadius);

		# load data
		self.shader[1].glUseProgram()
		GL.glUniform2fv(self.shader[1].glGetUniformLocation("cylinderVertex"), cylinderData.size, cylinderData);


	def loadUniforms(self):
		'''  This function is called always before drawing. It makes sure that the current bundle will be visualized with the uniforms specified for it.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 1, GL.GL_TRUE, self.model.getA())
		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation("colorTable"), 0)

		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('texture1DMax'), self.validBundleColorTexDims[0])


	@propagateToChildren
	@drawable
	@config
	def draw(self):
		'''  It has 2 decorators configuring the vao and seeing if the visualize flag is up.

		First it makes active the texture, and binds the texture from this file.
		Finally it calls the draw element with primitive restart.
		'''

		GL.glActiveTexture(GL.GL_TEXTURE0)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.colorTableTexture)

		if self.selectedShader == 0:
			GL.glDrawElements(GL.GL_LINE_STRIP, self.elements.size, GL.GL_UNSIGNED_INT, None)
		else:
			GL.glEnable(GL.GL_CULL_FACE)
			GL.glCullFace(GL.GL_FRONT);
			GL.glFrontFace(GL.GL_CCW);
			GL.glDrawElements(GL.GL_LINE_STRIP, self.elements.size, GL.GL_UNSIGNED_INT, None);
			GL.glDisable(GL.GL_CULL_FACE);

		self.boundingbox.draw()

	@staticmethod
	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''
		lineVertexGLSL = [str(_b_vs)]
		lineFragmentGLSL = [str(_sfs_fs)]
		cylinderVertexGLSL = [str(_c_vs)]
		cylinderGeometryGLSL = [str(_c_gs), str(_q_glsl)]
		cylinderFragmentGLSL = [str(_sfs_fs)]

		return [Shader(lineVertexGLSL, lineFragmentGLSL),
				Shader(cylinderVertexGLSL, cylinderFragmentGLSL, cylinderGeometryGLSL)]

	@staticmethod
	def validExtension():
		return ['bundles', 'trk', 'tck']
