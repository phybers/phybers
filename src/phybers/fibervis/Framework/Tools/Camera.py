# shouldn't notify objects by itself... it should be the glcontext
import numpy as np
from .glm import Quaternion, lookAt

class Camera():
	def __init__(self, radius):
		self.radius = radius

		# reference to objects that needs to be notify
		self.notifyUpdates2Objects = []

		self.defaultValues()


	def defaultValues(self):
		self.rotation = Quaternion.identity()

		self.eye = np.array([0,0,1], dtype=np.float32)
		self.initialEye = self.eye
		self.center = np.array([0,0,0], dtype=np.float32)
		self.up = np.array([0,1,0], dtype=np.float32)

		self.view = self.calculateView()

		self.speed = 0.5
		self.zspeed = 5.0


	def orbit(self, dx, dy):
		angleMagnitud = np.sqrt(dx**2 + dy**2)
		if angleMagnitud < 1.0:
			return self.view

		axis = [-dy/angleMagnitud, -dx/angleMagnitud, 0]
		theta = angleMagnitud*np.pi/180.0*self.speed
		newRotation = Quaternion.fromAngleAxis(theta, axis)
		self.rotation = self.rotation*newRotation

		self.view = self.calculateView()

		return self.view


	def panning(self, dx, dy):
		v = np.array([-dx, dy, 0], dtype=np.float32)

		self.center += self.rotation.rotateVector(v)

		self.view = self.calculateView()

		return self.view


	def axisAndAngleFromScreen(self, dx, dy):
		angleMagnitud = np.sqrt(dx**2 + dy**2)

		axis = Quaternion.fromAngleAxis(90*np.pi/180, [0,0,1])
		axis = axis.rotateVector([dx, -dy, 0])

		axis = self.rotation.rotateVector(axis)

		return axis, angleMagnitud


	def vectorFromScreen(self, dx, dy):
		translateV = self.rotation.rotateVector([dx, -dy, 0])

		return translateV


	def zooming(self, zoom):
		if zoom > 0:
			self.radius += -self.zspeed
		elif zoom < 0:
			self.radius += self.zspeed

		if self.radius < 1.0:
			self.radius = 1.0

		self.view = self.calculateView()

		return self.view


	def changeRotationSpeed(self, speed):
		self.speed = speed


	def changeZoomSpeed(self, speed):
		self.zspeed = speed


	def frontView(self):
		self.rotation = Quaternion.identity()
		self.view = self.calculateView()

		return self.view


	def backView(self):
		self.rotation = Quaternion.fromAngleAxis(np.pi, [0,1,0])
		self.view = self.calculateView()

		return self.view


	def leftView(self):
		self.rotation = Quaternion.fromAngleAxis(np.pi/2, [0,1,0])
		self.view = self.calculateView()

		return self.view


	def rightView(self):
		self.rotation = Quaternion.fromAngleAxis(np.pi/2, [0,-1,0])
		self.view = self.calculateView()

		return self.view


	def topView(self):
		self.rotation = Quaternion.fromAngleAxis(np.pi*3/2, [1,0,0])
		self.view = self.calculateView()

		return self.view


	def bottomView(self):
		self.rotation = Quaternion.fromAngleAxis(np.pi/2, [1,0,0])
		self.view = self.calculateView()

		return self.view


	def calculateView(self):
		self.eye = self.rotation.rotateVector(self.initialEye*self.radius)+self.center
		view = lookAt(	self.eye,
						self.center,
						self.rotation.rotateVector(self.up))

		for object2Notify in self.notifyUpdates2Objects:
			object2Notify.updateCamera(self.eye)

		return view

	def setObject2Notify(self, object):
		if object not in self.notifyUpdates2Objects:
			self.notifyUpdates2Objects.append(object)

	def removeObject2Notify(self, object):
		if object in self.notifyUpdates2Objects:
			self.notifyUpdates2Objects.remove(object)