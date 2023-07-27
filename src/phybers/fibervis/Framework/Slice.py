from .VisualizationBaseObject import *
from .BoundingBox import BoundingBox
import nibabel as nib
from importlib_resources import files

_vs_vs = files('phybers.fibervis.shaders').joinpath('volume-slice.vs')
_s_fs = files('phybers.fibervis.shaders').joinpath('slice.fs')

def configTexture(func):
	''' Decorator for set the texture filter
	'''

	def wrapper(*args, **kwargs):
		GL.glActiveTexture(GL.GL_TEXTURE0)
		GL.glBindTexture(GL.GL_TEXTURE_3D, args[0].texture)

		if not args[0].linearInterp:
			GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
			GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)

			func(*args, **kwargs)

			GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
			GL.glTexParameteri(GL.GL_TEXTURE_3D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

		else:
			func(*args, **kwargs)

	return wrapper


class Slice(VisualizationBaseObject):
	def __init__(self, mri, shaderDict):

		super().__init__(mri, shaderDict)
		self.identifier = VisualizationObject.MRISlice

		self.fileName = 'Slice render'

		self.scaleModel = np.matmul(mri.affine, glm.scaleMatrix(mri.mriData.shape))

		self.dims = np.array(mri.mriData.shape, dtype=np.float32)

		# Matrixs
		self.model = mri.translateMat*mri.rotationMat*mri.scaleMat

		self.inverseModel = mri.inverseModel
		self.scaleMat = mri.scaleMat
		self.translateMat = mri.translateMat
		self.rotationMat = mri.rotationMat

		# visualization parameters
		self.linearInterp = True

		self.discardValues = False
		self.threshold = 0.0

		self.slope = 1.0/mri.mriData.max()
		self.bright = 0.0
		self.contrast = 1.0

		self.pos2Axis = None
		self.axis = [0.0, 0.0, 0.0]
		self.calculatePlaneNormal([1.0, 0.0, 0.0], 0.5)

		self.frontIdx = 0

		self.loadStaticUniforms()

		# MRI data already loaded in the gpu
		self.texture = mri.texture
		self.vao = None
		self.vbo = mri.vbo

		self._loadBuffers()

		# Ready to draw
		self.drawable = True

		self.boundingbox = BoundingBox(shaderDict, self, mri.boundingbox.dims, mri.boundingbox.center, self.scaleModel)

		self.max = mri.mriData.max()


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		GL.glDeleteVertexArrays(1, [self.vao])

		self.clean = True


	def loadStaticUniforms(self):
		self.shader[0].glUseProgram()

		v1 = np.array([0,1,3,-1, 1,0,1,3, 0,4,5,-1, 4,0,4,5, 0,2,6,-1, 2,0,2,6], dtype=np.int32)
		v2 = np.array([1,3,7,-1, 5,1,3,7, 4,5,7,-1, 6,4,5,7, 2,6,7,-1, 3,2,6,7], dtype=np.int32)

		nSequence = np.array([	0,1,2,3,4,5,6,7, 1,3,0,2,5,7,4,6, 2,0,3,1,6,4,7,5, 3,2,1,0,7,6,5,4,
								4,0,6,2,5,1,7,3, 5,1,4,0,7,3,6,2, 6,2,7,3,4,0,5,1, 7,6,3,2,5,4,1,0], dtype=np.int32)

		self.vertexPoints = np.array([	1,1,0,	1,1,1,	0,1,0,	0,1,1,
										1,0,0,	1,0,1,	0,0,0,	0,0,1], dtype=np.float32).reshape((8,3))

		GL.glUniform1iv(self.shader[0].glGetUniformLocation("v1"), v1.size, v1)
		GL.glUniform1iv(self.shader[0].glGetUniformLocation("v2"), v2.size, v2)
		GL.glUniform1iv(self.shader[0].glGetUniformLocation("nSequence"), nSequence.size, nSequence)
		GL.glUniform3fv(self.shader[0].glGetUniformLocation("vertexPoints"), self.vertexPoints.size, self.vertexPoints)


	def _loadBuffers(self):
		self.vao = GL.glGenVertexArrays(1)
		GL.glBindVertexArray(self.vao)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

		# Enable attributes
		vertexIdxAttribute = self.shader[self.selectedShader].attributeLocation('vertexIdx')

		# # Connect attributes
		GL.glEnableVertexAttribArray(vertexIdxAttribute)
		GL.glVertexAttribIPointer(vertexIdxAttribute, 1, GL.GL_INT, 0, None)


	def loadUniforms(self):
		'''  This function is called always before drawing. It makes sure that the current bundle will be visualized with the uniforms specified for it.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''


		# Vertex shader
		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 1, GL.GL_TRUE, self.model.getA())
		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("S"), 1, GL.GL_TRUE, self.scaleModel.getA())

		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation("frontIdx"), self.frontIdx)
		GL.glUniform4f(self.shader[self.selectedShader].glGetUniformLocation("np"), *self.np, 0.0)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("dPlane"), self.dPlane)

		# Fragment shader
		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation("mriTexture"), 0)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("slope"), self.slope)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation('bright'), self.bright)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation('contrast'), self.contrast)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation('threshold'), self.threshold if self.discardValues else 0)


	def calculatePlaneNormal(self, axis, pos2Axis_new, newModel=False):
		self.pos2Axis = pos2Axis_new

		newAxis = np.array(axis[:3], dtype=np.float32)
		newAxis /= np.linalg.norm(newAxis)

		if not np.array_equal(newAxis, self.axis) or newModel:
			self.axis = newAxis

			begin = (self.model*self.scaleModel * np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel()
			end = (self.model*self.scaleModel * np.array([*self.axis, 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel()

			axisLengthV = end - begin

			self.np = (axisLengthV / np.linalg.norm(axisLengthV)).getA().ravel()[:3]

			if (self.axis==0.0).sum() == 2:
				# plane eq: dot(vertex, normal) + D = 0
				self.dPlaneBegin = np.dot(begin, self.np)
				self.dPlaneEnd = np.dot(end, self.np)

			else:
				self.dPlaneBegin = np.dot((self.model*self.scaleModel * np.array([*self.vertexPoints[0], 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel(), self.np)
				self.dPlaneEnd = np.dot((self.model*self.scaleModel * np.array([*self.vertexPoints[0], 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel(), self.np)

				for i in range(1,8):
					D = np.dot((self.model*self.scaleModel * np.array([*self.vertexPoints[i], 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel(), self.np)
					if D > self.dPlaneEnd:
						self.dPlaneEnd = D
					if D < self.dPlaneBegin:
						self.dPlaneBegin = D
						self.frontIdx = i

		self.dPlane = (self.dPlaneEnd - self.dPlaneBegin)*self.pos2Axis + self.dPlaneBegin


	def setLinearInterpolation(self, linearInterp):
		self.linearInterp = linearInterp


	def setDiscardValuesWithThreshold(self, discardValues, threshold):
		self.discardValues = discardValues
		self.threshold = threshold


	def setBright(self, bright):
		self.bright = bright


	def setContrast(self, contrast):
		self.contrast = contrast


	@drawable
	@config
	@configTexture
	def draw(self):
		GL.glDrawArraysInstanced(GL.GL_TRIANGLE_FAN, 0, 6, 1) # so we dont have to create another vertex shader

		self.boundingbox.draw()

	@staticmethod
	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [str(_vs_vs)]
		fragmentGLSL = [str(_s_fs)]
		return [Shader(vertexGLSL, fragmentGLSL)]


	def rotate(self, center, angle, axis):
		super().rotate(center, angle, axis)
		self.calculatePlaneNormal(self.axis, self.pos2Axis, True)


	def translate(self, vec):
		super().translate(vec)
		self.calculatePlaneNormal(self.axis, self.pos2Axis, True)


	def stackTranslate(self, vec):
		super().stackTranslate(vec)
		self.calculatePlaneNormal(self.axis, self.pos2Axis, True)


	def scale(self, vec, center):
		super().scale(vec, center)
		self.calculatePlaneNormal(self.axis, self.pos2Axis, True)


	def stackScale(self, vec, center):
		super().stackScale(vec, center)
		self.calculatePlaneNormal(self.axis, self.pos2Axis, True)


	def resetModel(self):
		super().resetModel()
		self.calculatePlaneNormal(self.axis, self.pos2Axis, True)