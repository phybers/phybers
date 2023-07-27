''' Base class for every drawable object
'''

from .Shaders import *
from .Tools import glm
from .Tools.visualizationEnums import *
import random
from OpenGL import GL
import ctypes as ct
import numpy as np

from functools import wraps

fSize = np.dtype(np.float32).itemsize
iSize = np.dtype(np.int32).itemsize
uSize = np.dtype(np.uint32).itemsize


def propagateToChildren(func):
	""" Decorator for propagate the drawing function to the object's children.
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		funcsName = func.__name__

		for child in args[0].children:
			getattr(child, funcsName)(*args[:-1], **kwargs)

		return func(*args, **kwargs)

	return wrapper

def drawable(func):
	""" Decorator for checking the drawable flag state from the object
	that calls the draw function from any VisualizationBaseObject inherited class.
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		if args[0].drawable is True:
			return func(*args, **kwargs)
	return wrapper


def config(func):
	""" Decorator for draw function in any VisualizationBaseObject inherited class.
	Configures the using program and the desired vao
	and unlinks the vao when it's finished
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		obj = args[0]
		obj.shader[obj.selectedShader].glUseProgram()
		obj.loadUniforms()
		if type(obj.vao) is not np.ndarray:
			GL.glBindVertexArray(obj.vao)
		else:
			GL.glBindVertexArray(obj.vao[obj.selectedShader])
		func(*args, **kwargs)	# the draw function
		GL.glBindVertexArray(0)
	return wrapper


class VisualizationBaseObject:
	def __init__(self, parent=None, shaderDic=None):

		# Parent and children
		self.parent = parent
		self.children = []
		self.identifier = VisualizationObject.NotDefined

		# OpenGL buffer references
		self.vbo = None
		self.ebo = None
		self.vao = None

		self.texture = None

		# OpenGL shader program handler
		if isinstance(shaderDic, dict):
			self.shader = shaderDic[type(self)]
		else:
			self.shader = shaderDic
		self.nShader = 1

		# Matrixs
		self.model = glm.identity()

		self.inverseModel = glm.identity()

		self.rotationMat = glm.identity()
		self.translateMat = glm.identity()
		self.scaleMat = glm.identity()

		# Flags
		self.drawable = False
		self.clean = False
		self.selectedShader = 0

		self.boundingbox = None


	def cleanOpenGL(self):
		print('Must clean befor leaving... ', type(self))


	def __del__(self):
		if not self.clean:
			self.cleanOpenGL()


	@propagateToChildren
	def clearRef(self):
		self.parent = None
		self.children.clear()


	def draw(self):
		pass


	def setCamera(self, newCamera):
		pass


	def loadUniforms(self):

		GL.glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation(
			"M"), 1, GL.GL_TRUE, self.model.getA())


	def remove(self, item):
		self.children.remove(item)


	def rotate(self, center, angle, axis):
		rotate = glm.translateMatrix(center)*glm.rotateMatrix(angle, axis)*glm.translateMatrix(-center)

		self.rotationMat = rotate*self.rotationMat

		self.model = self.translateMat*self.rotationMat*self.scaleMat
		self.inverseModel = np.linalg.inv(self.model)


	def translate(self, vec):
		self.translateMat = glm.translateMatrix(vec)

		self.model = self.translateMat*self.rotationMat*self.scaleMat
		self.inverseModel = np.linalg.inv(self.model)


	def stackTranslate(self, vec):
		newTranslateMat = glm.translateMatrix(vec)

		self.translateMat = newTranslateMat*self.translateMat

		self.model = self.translateMat*self.rotationMat*self.scaleMat
		self.inverseModel = np.linalg.inv(self.model)


	def scale(self, vec, center):
		self.scaleMat = glm.translateMatrix(center)*glm.scaleMatrix(vec)*glm.translateMatrix(-center)

		self.model = self.translateMat*self.rotationMat*self.scaleMat
		self.inverseModel = np.linalg.inv(self.model)


	def stackScale(self, vec, center):
		newScaleMat = glm.translateMatrix(center)*glm.scaleMatrix(vec)*glm.translateMatrix(-center)

		self.scaleMat = newScaleMat*self.scaleMat

		self.model = self.translateMat*self.rotationMat*self.scaleMat
		self.inverseModel = np.linalg.inv(self.model)


	def resetModel(self):
		self.scaleMat = glm.identity()

		self.translateMat = glm.identity()

		self.rotationMat = glm.identity()

		self.model = glm.identity()
		self.inverseModel = glm.identity()


	def setSelectedShader(self, newShaderId):
		if newShaderId < self.nShader:
			self.selectedShader = newShaderId
		else:
			raise TypeError('Unsupported shaderID, maximun is ', self.nShader, ' got ', newShaderId, '.')

	def setDrawBB(self, boolean):
		if self.boundingbox is not None:
			self.boundingbox.drawable = boolean