'''
'''

from ..VisualizationBaseObject import *
from ..Tools.visualizationEnums import *
from ..Tools.Quaternion import Quaternion
from importlib_resources import files

_b_vs = files('phybers.fibervis.shaders').joinpath('bundle.vs')
_sfs_vs = files('phybers.fibervis.shaders').joinpath('standardFragmentShader.fs')

class ROI(VisualizationBaseObject):
	'''
	'''

	def __init__(self, roitype, center, radius, shaderDict, parent):
		'''
		'''

		if not roitype in ROIType:
			raise TypeError('Unsupported ROI type.')

		super().__init__(parent, shaderDict)
		self.identifier = VisualizationObject.ROI

		self.fileName = str(roitype).split('.')[-1]

		self.roiType = roitype

		self.center = np.array(center, dtype=np.float32)

		self.radius = np.array(radius, dtype=np.float32)

		self.squaredRadius  = self.radius**2

		self.points = None
		self.normals = None
		self.color = None
		self.createROI()

		# Initialize the values on colorTable
		self.colorTable = np.array([random.random(), random.random(), random.random(), 1.0], dtype=np.float32)

		# Initialize of texture id and loading of self.colorTable into the GPU
		self.colorTableTexture = None
		self._loadColorTexture()

		# Creates VBOs & an EBO, then populates them with the point, normal and color data. The elements data goes into the EBO
		self._loadBuffers()

		# Random translation
		self.translate([random.random()*100 for x in range(3)])

		# Ready to draw
		self.drawable = True#parent.drawable


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		GL.glDeleteVertexArrays(1, [self.vao])

		GL.glDeleteBuffers(1, [self.vbo])

		GL.glDeleteTextures([self.colorTableTexture])

		self.clean = True


	def createROI(self):
		if self.roiType == ROIType.Sphere:
			self.createSphere()

			self.translation = glm.translateMatrix(self.center)
			self.scalation = glm.scaleMatrix((self.radius, self.radius, self.radius))


		elif self.roiType == ROIType.Aabb:
			raise TypeError('ROI type not implemented: ', self.roiType)

		elif self.roiType == ROIType.Obb:
			raise TypeError('ROI type not implemented: ', self.roiType)

		elif self.roiType == ROIType.Plane:
			raise TypeError('ROI type not implemented: ', self.roiType)


	def _loadColorTexture(self):
		''' It generates a texture (if not already). Then makes the texture0 the active one and loads the color table as a 1D texture.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		self.validBundleColorTexDims = (np.int32(1), np.int32(1))

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

		# GL.glTexImage1D(GL.GL_TEXTURE_1D, 0, GL.GL_RGBA, 1, 0, GL.GL_RGBA, GL.GL_FLOAT, self.colorTable.flatten())
		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, *self.validBundleColorTexDims, 0, GL.GL_RGBA, GL.GL_FLOAT, self.colorTable.flatten())


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
		self.vao = GL.glGenVertexArrays(1)
		GL.glBindVertexArray(self.vao)

		self.vbo = GL.glGenBuffers(1)

		# VBO
		bufferSize = self.points.nbytes + self.normals.nbytes + self.color.nbytes
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, bufferSize, None, GL.GL_STATIC_DRAW)	# Create empty buffer

		# Populate buffer with points
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
			0,
			self.points.nbytes,
			self.points.flatten())

		# Normals
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
			self.points.nbytes,
			self.normals.nbytes,
			self.normals.flatten())

		# Color-bundle id
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
			(2*self.points.nbytes),
			self.color.nbytes,
			self.color.flatten())

		# Enable attributes
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')
		normalAttribute =	self.shader[0].attributeLocation('vertexNor')
		colorAttribute =	self.shader[0].attributeLocation('vertexCol')

		# # Connect attributes
		GL.glEnableVertexAttribArray(positionAttribute)
		GL.glVertexAttribPointer(positionAttribute,3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

		GL.glEnableVertexAttribArray(normalAttribute)
		GL.glVertexAttribPointer(normalAttribute,	3, GL.GL_FLOAT, GL.GL_FALSE, 0, ct.c_void_p(self.points.nbytes))

		GL.glEnableVertexAttribArray(colorAttribute)
		GL.glVertexAttribPointer(colorAttribute,	1, GL.GL_INT, GL.GL_FALSE, 0, ct.c_void_p(2*self.points.nbytes))

	def createSphere(self):
		def subdivideTriangles(triangles):
			result = []

			for triangle in triangles:
				# first triangle
				result.append([	triangle[0],
								(triangle[1]-triangle[0])*0.5 + triangle[0],
								(triangle[2]-triangle[0])*0.5 + triangle[0]])

				# second triangle
				result.append([	triangle[1],
								(triangle[0]-triangle[1])*0.5 + triangle[1],
								(triangle[2]-triangle[1])*0.5 + triangle[1]])

				# third triangle
				result.append([	triangle[2],
								(triangle[0]-triangle[2])*0.5 + triangle[2],
								(triangle[1]-triangle[2])*0.5 + triangle[2]])

				# fourth triangle
				result.append([	(triangle[1]-triangle[0])*0.5 + triangle[0],
								(triangle[2]-triangle[0])*0.5 + triangle[0],
								(triangle[2]-triangle[1])*0.5 + triangle[1]])

			return np.array(result, dtype=np.float32)

		triangles = np.array([[[1.0, 0.0, 0.0],
							   [0.0, 1.0, 0.0],
							   [0.0, 0.0, 1.0]]], dtype=np.float32)

		# We subdivide the triangle in 4 triangles
		for i in range(3):
			triangles = subdivideTriangles(triangles)

		# We normalize the sphere vertex, so we have also the normals
		for triangle in triangles:
			for vertex in triangle:
				vertex /= np.sqrt((vertex**2).sum())

		# We create the half sphere, by rotating the current 1/8
		rotated = np.copy(triangles)
		rotation = Quaternion.fromAngleAxis(np.pi/2, [0.0,1.0,0.0])
		for i in range(3):
			for triangle in rotated:
				for vertex in triangle:
					vertex[:] = rotation.rotateVector(vertex)
			triangles = np.concatenate((triangles,rotated))

		# We create the whole sphere
		rotated = np.copy(triangles)
		rotated[:,:,1] *= -1
		triangles = np.concatenate((triangles,rotated))

		self.points = np.ravel(triangles)
		self.normals = self.points
		self.color = np.zeros(self.points.size//3, dtype=np.int32)


	def setContainsMethods(self):
		if self.roiType == ROIType.Sphere:
			self.containsVertex = self.containsVertexSphere
			self.containsBoundary = self.containsBoundarySphere
			self.intersectsBoundary = self.intersectsBoundarySphere

		elif self.roiType == ROIType.Aabb:
			raise TypeError('Contains method for ROI type not implemented: ', self.roiType)

		elif self.roiType == ROIType.Obb:
			raise TypeError('Contains method for ROI type not implemented: ', self.roiType)

		elif self.roiType == ROIType.Plane:
			raise TypeError('Contains method for ROI type not implemented: ', self.roiType)

	def containsBoundary(self, center, radius):
		print('method not being called')
		pass


	def containsVertex(self, vertex):
		print('method not being called')
		pass


	def intersectsBoundary(self, center, radius):
		print('method not being called')
		pass


	def containsBoundarySphere(self, center, radius):
		points = center + np.array([[ radius[0],  radius[1],  radius[2]],
									[-radius[0],  radius[1],  radius[2]],
									[ radius[0], -radius[1],  radius[2]],
									[-radius[0], -radius[1],  radius[2]],
									[ radius[0],  radius[1], -radius[2]],
									[-radius[0],  radius[1], -radius[2]],
									[ radius[0], -radius[1], -radius[2]],
									[-radius[0], -radius[1], -radius[2]]],dtype=np.float32)

		dist = points - self.center

		return ((dist**2).sum() <= self.squaredRadius).sum()


	def containsVertexSphere(self, vertex):
		dist = vertex - self.center

		return (dist**2).sum() <= self.squaredRadius


	def intersectsBoundarySphere(self, center, radius):
		squaredDist = 0.0

		if self.center[0] < center[0]-radius[0]:
			squaredDist += (self.center[0]-(center[0]-radius[0]))**2
		elif self.center[0] > center[0]+radius[0]:
			squaredDist += (self.center[0]-(center[0]+radius[0]))**2

		if self.center[1] < center[1]-radius[1]:
			squaredDist += (self.center[1]-(center[1]-radius[1]))**2
		elif self.center[1] > center[1]+radius[1]:
			squaredDist += (self.center[1]-(center[1]+radius[1]))**2

		if self.center[2] < center[2]-radius[2]:
			squaredDist += (self.center[2]-(center[2]-radius[2]))**2
		elif self.center[2] > center[2]+radius[2]:
			squaredDist += (self.center[2]-(center[2]+radius[2]))**2

		return squaredDist <= self.squaredRadius


	def loadUniforms(self):
		'''  This function is called always before drawing. It makes sure that the current bundle will be visualized with the uniforms specified for it.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		finalModel = self.model*self.translation*self.scalation
		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 1, GL.GL_TRUE, finalModel.getA())
		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation("colorTable"), 0)

		GL.glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('texture1DMax'), self.validBundleColorTexDims[0])


	def getRGB256(self):
		return self.colorTable*255


	def getCenter(self, inverseModel = glm.identity()):
		finalModel = self.model*self.translation*self.scalation
		return (inverseModel * finalModel * np.array([0, 0, 0, 1], dtype=np.float32).reshape((4,1)))[:3].ravel()


	def getRadius(self, inverseModel = glm.identity()):
		finalModel = inverseModel * self.model*self.translation*self.scalation

		r = (finalModel * np.array([1, 0, 0, 1], dtype=np.float32).reshape((4,1)))[:3].ravel()
		r = r - self.getCenter(inverseModel)
		r = np.linalg.norm(r)

		return np.array([r, r, r], dtype=np.float32)


	def changeFileName(self, newFilename):
		self.fileName = newFilename


	def getROIValue(self):
		return self.roiType.value


	@drawable
	@config
	def draw(self):
		GL.glActiveTexture(GL.GL_TEXTURE0)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.colorTableTexture)

		GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.color.size);

	@staticmethod
	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [str(_b_vs)]
		fragmentGLSL = [str(_sfs_vs)]
		return [Shader(vertexGLSL, fragmentGLSL)]