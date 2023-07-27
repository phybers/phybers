from .VisualizationBaseObject import *
from importlib_resources import files

_bbox_vs = files('phybers.fibervis.shaders').joinpath('boundingbox.vs')
_sfs_fs = files('phybers.fibervis.shaders').joinpath('standardFragmentShader.fs')

class BoundingBox(VisualizationBaseObject):
	def __init__(self, shaderDict, parent, dims, center, bbM=None):
		super().__init__(parent, shaderDict)
		if bbM is None:
			self.bbModel = glm.translateMatrix(center)*glm.scaleMatrix(dims)
		else:
			self.bbModel = bbM

		self.dims = np.array(dims, dtype=np.float32)
		self.center = np.array(center, dtype=np.float32)

		self._loadBuffers()

		# Ready to draw
		self.drawable = True


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		GL.glDeleteVertexArrays(1, [self.vao])

		GL.glDeleteBuffers(1, [self.vbo])
		GL.glDeleteBuffers(1, [self.ebo])

		self.clean = True


	def _loadBuffers(self):
		self.vao = GL.glGenVertexArrays(1)
		GL.glBindVertexArray(self.vao)

		self.vbo = GL.glGenBuffers(1)
		self.ebo = GL.glGenBuffers(1)

		boundingbox = np.array([1,	1,	0,
								1,	1,	1,
								0,	1,	1,
								0,	1,	0,
								1,	0,	0,
								1,	0,	1,
								0,	0,	0,
								0,	0,	1], dtype=np.float32)

		boundingElements = np.array([	0, 1, 1, 2, 2, 3, 3, 6, 0, 3, 0, 4,
										1, 5, 2, 7, 4, 6, 4, 5, 5, 7, 6, 7], dtype=np.uint32)

		# VBO
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, boundingbox.nbytes, boundingbox, GL.GL_STATIC_DRAW)

		# EBO
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, boundingElements.nbytes, boundingElements, GL.GL_STATIC_DRAW)

		# Enable attributes
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')

		# # Connect attributes
		GL.glEnableVertexAttribArray(positionAttribute)
		GL.glVertexAttribPointer(positionAttribute, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)


	def updateBBModel(self, dims, center):
		self.bbModel = glm.translateMatrix(center)*glm.scaleMatrix(dims)

		self.dims = np.array(dims, dtype=np.float32)
		self.center = np.array(center, dtype=np.float32)


	def loadUniforms(self):
		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("bbM"), 1, GL.GL_TRUE, self.bbModel.getA())
		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 1, GL.GL_TRUE, self.parent.model.getA())


	@drawable
	@config
	def draw(self):
		GL.glDrawElements(GL.GL_LINES, 24, GL.GL_UNSIGNED_INT, None)

	@staticmethod
	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [str(_bbox_vs)]
		fragmentGLSL = [str(_sfs_fs)]
		return [Shader(vertexGLSL, fragmentGLSL)]