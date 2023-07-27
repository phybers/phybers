from .VisualizationBaseObject import *
from importlib_resources import files

_cs_vs = files('phybers.fibervis.shaders').joinpath('coordinateSystem.vs')
_sfs_fs = files('phybers.fibervis.shaders').joinpath(
	'standardFragmentShader.fs')

class CoordinateSystem(VisualizationBaseObject):
	def __init__(self, shaderProgram):

		super().__init__()

		self.shader = shaderProgram

		radiusCilinder = 0.015
		lengthCilinder = 0.8

		radiusCone = 0.05
		lengthCone = 0.2

		self.points, self.elements = CoordinateSystem.createArrow(radiusCilinder, lengthCilinder, radiusCone, lengthCone, detail=10)

		model0 = glm.Quaternion.identity().rotation4Matrix()
		model1 = glm.Quaternion.fromAngleAxis(np.pi/2, (0,0,1)).rotation4Matrix()
		model2 = glm.Quaternion.fromAngleAxis(-np.pi/2, (0,1,0)).rotation4Matrix()

		self.model = np.concatenate(( model0.getA(), model1.getA(), model2.getA() ))

		self.color = np.array([1,0,0,1, 0,1,0,1, 0,0,1,1], dtype=np.float32)

		self._loadBuffers()


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		GL.glDeleteVertexArrays(1, [self.vao])

		GL.glDeleteBuffers(1, [self.vbo])
		GL.glDeleteBuffers(1, [self.ebo])

		self.clean = True

	@staticmethod
	def createArrow(rCilinder, lCilinder, rCone, lCone, detail=3):
		# Creates an arrow on the x-axis, with the specified measure.
		# detail is the number of faces, 3 = pyramid
		#
		# Parameters
		# ----------
		# rCilinder : float
		# 	radius for the cilinder.
		# lCilinder : float
		# 	lengh for the arrow before the head.
		# rCone : float
		#	radius for the arrow head.
		# lCone : float
		#	length of the arrow head.
		# detail : int
		#	number of faces to build the arrow.
		#
		# Returns
		# -------
		# arrowPoints : numpy.array
		# 	An array with the points.
		# elements : numpy.array
		#	Array with the order of the drawing.

		if not isinstance(detail, int):
			raise TypeError('Variable detail must be a integer major than 2.')

		n = (detail+1)*3 *3
		arrowPoints = np.zeros(n, dtype=np.float32)

		arrowPoints[3] = lCilinder
		arrowPoints[6] = lCilinder+lCone

		angle = 2.0*np.pi/detail
		line = [0.0,		rCilinder,	0.0,
				lCilinder,	rCilinder,	0.0]

		for i in range(detail):
			rotation = glm.Quaternion.fromAngleAxis(angle*i, [1,0,0])
			arrowPoints[9+i*6 : 12+i*6] = rotation.rotateVector(line[:3])
			arrowPoints[12+i*6 : 15+i*6] = rotation.rotateVector(line[3:])

		k = 9 + detail*6
		line = [lCilinder, rCone, 0]
		for i in range(detail):
			rotation = glm.Quaternion.fromAngleAxis(angle*i, [1,0,0])
			arrowPoints[k+i*3 : k+i*3+3] = rotation.rotateVector(line)

		elements = []

		for i in range(detail):
			elements.append(0)
			elements.append(i*2+3)
			elements.append(i*2+2+3)
		elements[-1] = 3

		for i in range(detail):
			elements.append(3+i*2)
			elements.append(3+i*2+1)
			elements.append(3+i*2+2)

			elements.append(3+i*2+1)
			elements.append(3+i*2+2)
			elements.append(3+i*2+3)
		elements[-1] = 4
		elements[-2] = 3
		elements[-4] = 3

		for i in range(detail):
			elements.append(1)
			elements.append(i + 3+2*detail)
			elements.append(i+1+3+2*detail)
		elements[-1] = 3+2*detail

		for i in range(detail):
			elements.append(2)
			elements.append(i + 3+2*detail)
			elements.append(i+1+3+2*detail)
		elements[-1] = 3+2*detail

		elements = np.array(elements, np.int32)

		return arrowPoints, elements


	def _loadBuffers(self):
		''' It generates a VAO, VBO and EBO.
		It populates them with the vertex (the VBO), also the elements (the EBO).

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
		self.ebo = GL.glGenBuffers(1)

		# VBO
		# bufferSize = self.points.nbytes
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.points.nbytes, self.points.flatten(), GL.GL_STATIC_DRAW)	# Create empty buffer

		# Populate buffer with points
		# GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
		# 	0,
		# 	self.points.nbytes,
		# 	self.points.flatten())

		# EBO
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.elements.nbytes, self.elements.flatten(), GL.GL_STATIC_DRAW)

		# Enable attributes
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')

		# # Connect attributes
		GL.glEnableVertexAttribArray(positionAttribute)
		GL.glVertexAttribPointer(positionAttribute, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)


	def loadUniforms(self):

		GL.glUniform4fv(self.shader[self.selectedShader].glGetUniformLocation('colorArray'), 3, self.color)
		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 3, GL.GL_TRUE, self.model)



	@config
	def draw(self):
		GL.glDrawElementsInstanced(GL.GL_TRIANGLES, len(self.elements), GL.GL_UNSIGNED_INT, None, 3)

	@staticmethod
	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [str(_cs_vs)]
		fragmentGLSL = [str(_sfs_fs)]
		return [Shader(vertexGLSL, fragmentGLSL)]