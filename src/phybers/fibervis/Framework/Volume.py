from .VisualizationBaseObject import *
from .BoundingBox import BoundingBox
from skimage.filters import threshold_otsu
from .Tools import glm
from importlib_resources import files

_vs_vs = files('phybers.fibervis.shaders').joinpath('volume-slice.vs')
_vs_fs = files('phybers.fibervis.shaders').joinpath('volume.fs')

class Volume(VisualizationBaseObject):
	def __init__(self, mri, shaderDict, camera):

		super().__init__(mri, shaderDict)
		self.identifier = VisualizationObject.MRIVolume

		self.fileName = 'Volume render'

		self.scaleModel = mri.affine * glm.scaleMatrix(mri.mriData.shape)

		# We select an otsu threshold for volume render and slope for grey color
		self.threshold = threshold_otsu(mri.mriData)
		self.slope = 1.0/mri.mriData.max()

		# Matrixs
		self.model = mri.translateMat*mri.rotationMat*mri.scaleMat
		self.inverseModel = np.linalg.inv(self.model)

		self.scaleMat = mri.scaleMat
		self.translateMat = mri.translateMat
		self.rotationMat = mri.rotationMat

		self.axis = None
		self.calculateAxisMat3()

		# Sampling frequency, twice the maximum frequency
		self.sliceFr = int(2*np.linalg.norm(mri.mriData.shape))

		self.loadStaticUniforms()

		# MRI data already loaded in the gpu
		self.texture = mri.texture
		self.vao = None
		self.vbo = mri.vbo

		self._loadBuffers()

		self.alpha = 0.5
		self.f2bDrawing = True

		self.np = None
		self.__camera = camera # for memory cleaning purpose only
		self.updateCamera(camera.eye)
		camera.setObject2Notify(self)

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

		self.uniDPlane = self.shader[0].glGetUniformLocation("dPlane")

		GL.glUniform1iv(self.shader[0].glGetUniformLocation("v1"), 24, v1)
		GL.glUniform1iv(self.shader[0].glGetUniformLocation("v2"), 24, v2)
		GL.glUniform1iv(self.shader[0].glGetUniformLocation("nSequence"), 64, nSequence)
		GL.glUniform3fv(self.shader[0].glGetUniformLocation("vertexPoints"), 8, self.vertexPoints)


	def _loadBuffers(self):
		self.vao = GL.glGenVertexArrays(1)
		GL.glBindVertexArray(self.vao)

		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

		# Enable attributes
		vertexIdxAttribute = self.shader[self.selectedShader].attributeLocation('vertexIdx')

		# # Connect attributes
		GL.glEnableVertexAttribArray(vertexIdxAttribute)
		GL.glVertexAttribIPointer(vertexIdxAttribute, 1, GL.GL_INT, 0, None)


	def updateCamera(self, newEye):
		self.eye = newEye
		volumeCenter = (self.model*self.scaleModel * np.array([0.5, 0.5, 0.5, 1.0], dtype=np.float32).reshape((4,1)))[:3].getA().ravel()

		self.np = self.eye - volumeCenter
		self.np /= np.linalg.norm(self.np)

		self.dPlaneBegin = np.dot((self.model*self.scaleModel * np.array([*self.vertexPoints[0], 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel(), self.np)
		self.dPlaneEnd   = self.dPlaneBegin
		self.frontIdx = 0

		for i in range(1,8):
			D = np.dot((self.model*self.scaleModel * np.array([*self.vertexPoints[i], 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel(), self.np)

			if D > self.dPlaneBegin:
				self.dPlaneBegin = D
				self.frontIdx = i
			if D < self.dPlaneEnd:
				self.dPlaneEnd = D

		if self.f2bDrawing:
			self.dPlane = self.dPlaneBegin
			self.dPlaneStep = (self.dPlaneEnd - self.dPlaneBegin)/self.sliceFr
		else:
			self.dPlane = self.dPlaneEnd
			self.dPlaneStep = (self.dPlaneBegin - self.dPlaneEnd)/self.sliceFr


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
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("dPlaneStep"), self.dPlaneStep)

		# Fragment shader
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("slope"), self.slope)
		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation("mriTexture"), 0)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("threshold"), self.threshold)
		GL.glUniform3fv(self.shader[self.selectedShader].glGetUniformLocation('eye'), 1, self.eye)
		GL.glUniformMatrix3fv(self.shader[self.selectedShader].glGetUniformLocation('axis'), 1, GL.GL_TRUE, self.axis)
		GL.glUniform1f(self.shader[self.selectedShader].glGetUniformLocation('alpha'), self.alpha)


	def calculateAxisMat3(self):
		x = np.array([1,0,0,1], dtype=np.float32)
		y = np.array([0,1,0,1], dtype=np.float32)
		z = np.array([0,0,1,1], dtype=np.float32)

		begin = (self.model*self.scaleModel * np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32).reshape((4,1)))[:3].ravel()
		x = (self.model*self.scaleModel * x.reshape((4,1)))[:3].ravel()
		y = (self.model*self.scaleModel * y.reshape((4,1)))[:3].ravel()
		z = (self.model*self.scaleModel * z.reshape((4,1)))[:3].ravel()

		x -= begin
		y -= begin
		z -= begin

		x = (x / np.linalg.norm(x)).getA().ravel()[:3]
		y = -(y / np.linalg.norm(y)).getA().ravel()[:3]
		z = (z / np.linalg.norm(z)).getA().ravel()[:3]

		self.axis = np.array([*x, *y, *z], dtype=np.float32).reshape((3,3)).T


	# @propagateToChildren
	def clearRef(self):
		super().clearRef()
		self.__camera.removeObject2Notify(self)


	def setFront2BackDrawing(self, newf2bDrawing):
		self.f2bDrawing = newf2bDrawing

		if newf2bDrawing is True:
			self.dPlane = self.dPlaneBegin
			self.dPlaneStep = (self.dPlaneEnd - self.dPlaneBegin)/self.sliceFr
		else:
			self.dPlane = self.dPlaneEnd
			self.dPlaneStep = (self.dPlaneBegin - self.dPlaneEnd)/self.sliceFr


	def setAlpha(self, newAlpha):
		self.alpha = newAlpha


	def setThreshold(self, newThreshold):
		self.threshold = newThreshold


	@drawable
	@config
	def draw(self):
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

		GL.glActiveTexture(GL.GL_TEXTURE0)
		GL.glBindTexture(GL.GL_TEXTURE_3D, self.texture)

		GL.glDrawArraysInstanced(GL.GL_TRIANGLE_FAN, 0, 6, self.sliceFr)
		GL.glDisable(GL.GL_BLEND)

		self.boundingbox.draw()

	@staticmethod
	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [str(_vs_vs)]
		fragmentGLSL = [str(_vs_fs)]
		return [Shader(vertexGLSL, fragmentGLSL)]


	def rotate(self, center, angle, axis):
		super().rotate(center, angle, axis)
		self.updateCamera(self.eye)
		self.calculateAxisMat3()


	def translate(self, vec):
		super().translate(vec)
		self.updateCamera(self.eye)
		self.calculateAxisMat3()


	def stackTranslate(self, vec):
		super().stackTranslate(vec)
		self.updateCamera(self.eye)
		self.calculateAxisMat3()


	def scale(self, vec, center):
		super().scale(vec)
		self.updateCamera(self.eye)
		self.calculateAxisMat3()


	def stackScale(self, vec, center):
		super().stackScale(vec, center)
		self.updateCamera(self.eye)
		self.calculateAxisMat3()


	def resetModel(self):
		super().resetModel()
		self.updateCamera(self.eye)
		self.calculateAxisMat3()