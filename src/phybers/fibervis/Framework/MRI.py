from OpenGL import GL
from .VisualizationBaseObject import *
from .BoundingBox import BoundingBox
import nibabel as nib

class MRI(VisualizationBaseObject):
	def __init__(self, sPath, shaderDict, parent):
		''' Initialize a MRI object.
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
		super().__init__(parent, None)
		self.identifier = VisualizationObject.MRI

		self.path = sPath
		self.fileName = sPath.split('/')[-1]

		self.mri = None
		self.readMRI()

		# Boundingbox edge color
		# self.color = np.array([1,1,1,1], dtype=np.float32)

		# Initialize of texture id and loading of self.colorTable into the GPU
		self.texture = None
		self._loadTexture()

		# Creates VBO then populates them with the vertexIdx data.
		self.vbo = None
		self._loadBuffers()

		# Ready to draw
		self.drawable = True

		# We set the boundingbox parameters
		dims = self.mriData.shape
		center = np.array([0, 0, 0], dtype=np.float32)

		self.boundingbox = BoundingBox(shaderDict, self, dims, center)

		print("Loading ready:\n\tDimensions of MRI: ", self.mriData.shape)


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		GL.glDeleteBuffers(1, [self.vbo])

		GL.glDeleteTextures([self.texture])

		self.clean = True


	def readMRI(self):
		'''

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		extension = self.path.split('.')[-1]

		# NIfTI file
		if extension == 'gz' or extension == 'nii':
			self._openNIfTI()

		# DICOM file
		# elif extension == 'dicom':
		# 	self.openDICOM()

		# Unsopported file
		else:
			raise TypeError('Unsupported file.')

		self.resetModel()


	def _openNIfTI(self):
		'''

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		print('Opening MRI file {}'.format(self.path))

		self.mri = nib.load(self.path)
		self.mriData = np.array(self.mri.get_fdata(), dtype=np.float32).reshape(self.mri.get_fdata().shape)
		self.affine = np.asmatrix(self.mri.affine.reshape((4,4))).astype(np.float32)

		# print(self.mri.get_qform(coded=True))

		# # TESTING
		# self.mriData = np.swapaxes(self.mriData,0,1)
		# self.mriData = np.swapaxes(self.mriData,0,2)
		# # self.mriData = np.swapaxes(self.mriData,1,2)

		# self.mriData = self.mriData[::-1,:,:]
		# # self.mriData = self.mriData[:,::-1,:]
		# self.mriData = self.mriData[:,:,::-1]
		# self.affine = np.eye(4,dtype=np.float32)
		# self.affine[0][0] = 1.1
		# # self.affine = self.affine.T
		# img = nib.Nifti1Image(self.mriData, self.affine)
		# nib.save(img, self.fileName)

		print(self.affine)
		self.affine[0,3]=0
		self.affine[1,3]=0
		self.affine[2,3]=0
		# print(self.mri.affine)

		self.activeTransform = self.affine
		self.model = self.model*self.activeTransform


	def _loadTexture(self):
		if self.texture == None:
			self.texture = GL.glGenTextures(1)

		GL.glActiveTexture(GL.GL_TEXTURE0)
		GL.glBindTexture(GL.GL_TEXTURE_3D, self.texture)

		GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_BORDER)
		GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_BORDER)
		GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_BORDER)

		bgColor = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
		GL.glTexParameterfv(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_BORDER_COLOR, bgColor)

		# Filtered
		GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
		GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

		# Not filtered
		# GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
		# GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)

		# Must swap axes 0 and 2, cuz data is not alined
		GL.glTexImage3D(GL.GL_TEXTURE_3D, 0, GL.GL_R32F, *self.mriData.shape[:3], 0, GL.GL_RED, GL.GL_FLOAT, np.swapaxes(self.mriData, 0, 2))


	def _loadBuffers(self):
		# Buffer with the texture data. Slice and Volume visualization objects
		self.vbo = GL.glGenBuffers(1)

		vertexIdx = np.arange(6, dtype=np.int32)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, vertexIdx.nbytes, vertexIdx, GL.GL_STATIC_DRAW)


	def rotate(self, center, angle, axis):
		rotate = glm.translateMatrix(center)*glm.rotateMatrix(angle, axis)*glm.translateMatrix(-center)

		self.rotationMat = rotate*self.rotationMat

		self.model = self.translateMat*self.rotationMat*self.scaleMat*self.activeTransform
		self.inverseModel = np.linalg.inv(self.model)


	def translate(self, vec):
		self.translateMat = glm.translateMatrix(vec)

		self.model = self.translateMat*self.rotationMat*self.scaleMat*self.activeTransform
		self.inverseModel = np.linalg.inv(self.model)


	def stackTranslate(self, vec):
		newTranslateMat = glm.translateMatrix(vec)

		self.translateMat = newTranslateMat*self.translateMat

		self.model = self.translateMat*self.rotationMat*self.scaleMat*self.activeTransform
		self.inverseModel = np.linalg.inv(self.model)


	def scale(self, vec, center):
		self.scaleMat = glm.translateMatrix(center)*glm.scaleMatrix(vec)*glm.translateMatrix(-center)

		self.model = self.translateMat*self.rotationMat*self.scaleMat*self.activeTransform
		self.inverseModel = np.linalg.inv(self.model)


	def stackScale(self, vec, center):
		newScaleMat = glm.translateMatrix(center)*glm.scaleMatrix(vec)*glm.translateMatrix(-center)

		self.scaleMat = newScaleMat*self.scaleMat

		self.model = self.translateMat*self.rotationMat*self.scaleMat*self.activeTransform
		self.inverseModel = np.linalg.inv(self.model)


	def resetModel(self):
		self.scaleMat = glm.identity()

		self.translateMat = glm.identity()

		self.rotationMat = glm.identity()

		self.model = glm.identity()*self.activeTransform
		self.inverseModel = glm.identity()


	@propagateToChildren
	@drawable
	def draw(self):
		self.boundingbox.draw()

	@staticmethod
	def validExtension():
		return ['gz', 'nii']