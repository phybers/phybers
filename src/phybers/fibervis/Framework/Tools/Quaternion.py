import numpy as np

class Quaternion:
	''' Class for storing rotations as quaternions
	'''

	def __init__(self):
		''' Initializes a unit quaternion without rotation.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		self.w = 1
		self.x = 0
		self.y = 0
		self.z = 0

	@classmethod
	def fromAngleAxis(cls, angle, axis):
		''' Initialices a quaternion from an angle and axis.

		The quaternion is normalized.

		Parameters
		----------
		angle : float
			Angle of the rotation in radians

		axis : list, tuple, numpy.array
			A 3 element parameters with the axis of rotation. Not necessarilly normalized.

		Returns
		-------
		q : Quaternion
			Initialized quaternion

		'''

		module = np.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
		s = np.sin(angle/2) / module

		q = cls()

		q.w = np.cos(angle/2)
		q.x = float(axis[0]) * s
		q.y = float(axis[1]) * s
		q.z = float(axis[2]) * s

		return q

	@classmethod
	def fromQuaternionElements(cls, w, x, y, z):
		''' Initializes a quaternion from the given elements.

		Parameters
		----------
		w : float
			Real part of quaternion.

		x : float
			Imaginary part of quaternion, corresponding x coordinate.

		y : float
			Imaginary part of quaternion, corresponding y coordinate.

		z : float
			Imaginary part of quaternion, corresponding z coordinate.

		Returns
		-------
		q : Quaternion
			Initialized quaternion

		'''

		q = cls()

		q.w = float(w)
		q.x = float(x)
		q.y = float(y)
		q.z = float(z)

		return q

	@classmethod
	def fromQuaternion(cls, other):
		''' Initializes a quaternion from another quaternion.

		Parameters
		----------
		other : Quaternion
			Quaternion to be copied.

		Returns
		-------
		q : Quaternion
			Initialized quaternion

		'''

		q = cls()

		q.w = other.w
		q.x = other.x
		q.y = other.y
		q.z = other.z

		return q

	@classmethod
	def identity(cls):
		''' Initializes a unit quaternion without rotation.

		Parameters
		----------
		None

		Returns
		-------
		q : Quaternion
			Initialized quaternion

		'''

		q = cls()

		q.w = 1.0
		q.x = 0.0
		q.y = 0.0
		q.z = 0.0

		return q

	def normalize(self):
		''' Normalizes the quaternion.

		Parameters
		----------
		None

		Returns
		-------
		self : Quaternion

		'''

		module = np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
		self.w /= module
		self.x /= module
		self.y /= module
		self.z /= module

		return self


	def inverted(self):
		''' Invertes the quaternion, by inverting the axis.

		Parameters
		----------
		None

		Returns
		-------
		q : Quaternion
			Inverted quaternion.

		'''

		return Quaternion.fromQuaternionElements(self.w, -self.x, -self.y, -self.z)


	def rotateVector(self, vector):
		''' Rotates a vector using the quaternion.

		Parameters
		----------
		vector : list, tuple, numpy.array
			A 3 element parameters with the axis of rotation. Not necessarilly normalized.

		Returns
		-------
		array : numpy.array
			Rotated vector.

		'''

		p = Quaternion.fromQuaternionElements(0, vector[0], vector[1], vector[2])
		pp = self * p * self.inverted()

		return np.array([pp.x, pp.y, pp.z], dtype=np.float32)


	def rotation3Matrix(self):
		''' Creates a 3x3 rotation matrix from the quaternion.

		Parameters
		----------
		None

		Returns
		-------
		matrix : numpy.matrix
			Rotation matrix.

		'''

		xx = self.x**2
		yy = self.y**2
		zz = self.z**2
		xy = self.x*self.y
		wz = self.w*self.z
		xz = self.x*self.z
		wy = self.w*self.y
		yz = self.y*self.z
		wx = self.w*self.x

		return np.matrix([	[1-2*(yy+zz),	2*(xy-wz),		2*(xz+wy)],
							[2*(xy+wz),		1-2*(xx+zz),	2*(yz-wx)],
							[2*(xz-wy),		2*(yz+wx),		1-2*(xx+yy)]], dtype=np.float32)


	def rotation4Matrix(self):
		''' Creates a 4x4 rotation matrix from the quaternion.

		Parameters
		----------
		None

		Returns
		-------
		matrix : numpy.matrix
			Rotation matrix.

		'''

		xx = self.x**2
		yy = self.y**2
		zz = self.z**2
		xy = self.x*self.y
		wz = self.w*self.z
		xz = self.x*self.z
		wy = self.w*self.y
		yz = self.y*self.z
		wx = self.w*self.x

		return np.matrix([	[1-2*(yy+zz),	2*(xy-wz),		2*(xz+wy),		0],
							[2*(xy+wz),		1-2*(xx+zz),	2*(yz-wx),		0],
							[2*(xz-wy),		2*(yz+wx),		1-2*(xx+yy),	0],
							[0,				0,				0,				1]], dtype=np.float32)


	def toAngleAxis(self):
		''' Transforms the quaternion into the angle and axis of rotation in 3D coordinate system.

		Parameters
		----------
		None

		Returns
		-------
		angle : float
			Angle of rotation.

		axis : float
			axis of rotation.

		'''

		angle = np.arccos(self.w)*2
		axis = np.array([self.x, self.y, self.z], dtype=np.float32) / np.sqrt(1-self.w**2)

		return angle, axis


	def slerp(self, other, t):
		''' Spherical linear interpolation from the given quaternion to another, by the given t portion.

		Parameters
		----------
		other : Quaternion
			Final quaternion to which the interpolation goes.

		t : float
			Step from the linear interpolation between both quaternions. 0 <= t <= 1.

		Returns
		-------
		q : Quaternion
			New quaternion with the slerp rotation in t.

		'''

		return (other*self.inverted())**t * self


	def __mul__(self, other):
		''' Overload multiply, for multiplying quaternions between them.

		Parameters
		----------
		other : Quaternion
			Rotation to be apply.

		Returns
		-------
		q : Quaternion
			New quaternion with the rotation applied.

		'''

		if not isinstance(other, Quaternion):
			raise TypeError('Can not multiply with other object that is not a Quaternion')

		newW = self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
		newX = self.x*other.w + self.w*other.x - self.z*other.y + self.y*other.z
		newY = self.y*other.w + self.z*other.x + self.w*other.y - self.x*other.z
		newZ = self.z*other.w - self.y*other.x + self.x*other.y + self.w*other.z

		return Quaternion.fromQuaternionElements(newW, newX, newY, newZ)


	def __rmul__(self, other):
		''' Bypass to normal multiply.

		Parameters
		----------
		other : Quaternion
			Rotation to be apply.

		Returns
		-------
		q : Quaternion
			New quaternion with the rotation applied.

		'''

		return self*other
		# raise TypeError('Can not multiply with other object that is not a Quaternion')


	def __pow__(self, t):
		''' Scales the angle of rotation in t.

		Parameters
		----------
		t : float
			Floating point to scale the angle of rotation of the quaternion.

		Returns
		-------
		q : Quaternion
			New quaternion with the same axis, but angle scaled in t.

		'''

		angle, axis = self.toAngleAxis()

		return Quaternion.fromAngleAxis(angle*t, axis)


	def __str__(self):
		''' String representation of the quaternion.

		Parameters
		----------
		None

		Returns
		-------
		string : str
			w, x, y, z as string representation of list.

		'''

		return '[{0}, {1}, {2}, {3}]'.format(self.w, self.x, self.y, self.z)

	def __iter__(self):
		''' Iterable representation of the quaternion.

		Parameters
		----------
		None

		Returns
		-------
		iter : iterable
			yields w, x, y and z.

		'''

		yield self.w
		yield self.x
		yield self.y
		yield self.z