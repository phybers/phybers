from .Quaternion import Quaternion
import numpy as np

def null(w=4, h=4):
	return np.matrix([[ 0 for i in range(w)] for j in range(h)], dtype = "float32")


def identity(w=4, h=4):
	return np.matrix([[1 if i==j else 0 for i in range(w)] for j in range(h)], dtype = "float32")


def normalize(v):
	module = np.sqrt(np.multiply(v[0:3],v[0:3]).sum())

	v /= module

	return v


def translateMatrix(v):
	return np.matrix([	[1,	0,	0,	v[0]],
						[0,	1,	0,	v[1]],
						[0,	0,	1,	v[2]],
						[0,	0,	0,	1]], dtype=np.float32)


def scaleMatrix(v):
	if hasattr(v, '__iter__'):
		return np.matrix([	[v[0],	0,		0,		0],
							[0,		v[1],	0,		0],
							[0,		0,		v[2],	0],
							[0,		0,		0,		1]], dtype=np.float32)
	else:
		return np.matrix([	[v,		0,		0,		0],
							[0,		v,		0,		0],
							[0,		0,		v,		0],
							[0,		0,		0,		1]], dtype=np.float32)


def rotateMatrix(alfa, axis):
	return Quaternion.fromAngleAxis(alfa*np.pi/180, axis).rotation4Matrix()


def ortho(left, right, bottom, top, zNear, zFar):
	Result = identity()
	Result[0,0] = 2.0 / (right - left);
	Result[1,1] = 2.0 / (top - bottom);
	Result[2,2] = -2.0 / (zFar - zNear);
	Result[3,0] = -(right + left) / (right - left);
	Result[3,1] = -(top + bottom) / (top - bottom);
	Result[3,2] = -(zFar + zNear) / (zFar - zNear);

	return Result;


def frustum(left, right, bottom, top, nearVal, farVal):
	Result = null()
	Result[0,0] = (2.0 * nearVal) / (right - left)
	Result[1,1] = (2.0 * nearVal) / (top - bottom)
	Result[2,0] = (right + left) / (right - left)
	Result[2,1] = (top + bottom) / (top - bottom)
	Result[2,2] = -(farVal + nearVal) / (farVal - nearVal)
	Result[2,3] = -1.0
	Result[3,2] = -(2.0 * farVal * nearVal) / (farVal - nearVal)

	return Result


def perspective(fovy, aspect, zNear, zFar):
	rad = np.radians(fovy)

	tanHalfFovy = np.tan(rad/2.0)

	Result = null()
	Result[0,0] = 1.0/(aspect*tanHalfFovy)
	Result[1,1] = 1.0/tanHalfFovy
	Result[2,2] = -(zFar + zNear)/(zFar - zNear)
	Result[2,3] = -(2*zFar*zNear)/(zFar - zNear)
	Result[3,2] = -1.0


	return Result


def lookAt(eye, center, up):
	# f = normalize(eye-center)
	# u = normalize(up)
	# s = normalize(np.cross(u, f))
	# u = np.cross(f,s)

	# rotation = identity()

	# rotation[0,0] = s[0];
	# rotation[0,1] = s[1];
	# rotation[0,2] = s[2];

	# rotation[1,0] = u[0];
	# rotation[1,1] = u[1];
	# rotation[1,2] = u[2];

	# rotation[2,0] = f[0];
	# rotation[2,1] = f[1];
	# rotation[2,2] = f[2];

	# rotation[3,0] = -eye[0]
	# rotation[3,1] = -eye[1]
	# rotation[3,2] = -eye[2]

	f = normalize(center-eye)
	u = normalize(up)
	s = normalize(np.cross(f, u))
	u = np.cross(s, f)

	Result = identity()

	Result[0,0] = s[0];
	Result[1,0] = s[1];
	Result[2,0] = s[2];
	Result[0,1] = u[0];
	Result[1,1] = u[1];
	Result[2,1] = u[2];
	Result[0,2] = -f[0];
	Result[1,2] = -f[1];
	Result[2,2] = -f[2];
	Result[3,0] = -np.dot(s, eye)
	Result[3,1] = -np.dot(u, eye)
	Result[3,2] = np.dot(f, eye)

	return Result

	# print(rotation)

	# return rotation.T


def inverseTranspose(m):
	SubFactor00 = m[2,2] * m[3,3] - m[3,2] * m[2,3]
	SubFactor01 = m[2,1] * m[3,3] - m[3,1] * m[2,3]
	SubFactor02 = m[2,1] * m[3,2] - m[3,1] * m[2,2]
	SubFactor03 = m[2,0] * m[3,3] - m[3,0] * m[2,3]
	SubFactor04 = m[2,0] * m[3,2] - m[3,0] * m[2,2]
	SubFactor05 = m[2,0] * m[3,1] - m[3,0] * m[2,1]
	SubFactor06 = m[1,2] * m[3,3] - m[3,2] * m[1,3]
	SubFactor07 = m[1,1] * m[3,3] - m[3,1] * m[1,3]
	SubFactor08 = m[1,1] * m[3,2] - m[3,1] * m[1,2]
	SubFactor09 = m[1,0] * m[3,3] - m[3,0] * m[1,3]
	SubFactor10 = m[1,0] * m[3,2] - m[3,0] * m[1,2]
	SubFactor11 = m[1,1] * m[3,3] - m[3,1] * m[1,3]
	SubFactor12 = m[1,0] * m[3,1] - m[3,0] * m[1,1]
	SubFactor13 = m[1,2] * m[2,3] - m[2,2] * m[1,3]
	SubFactor14 = m[1,1] * m[2,3] - m[2,1] * m[1,3]
	SubFactor15 = m[1,1] * m[2,2] - m[2,1] * m[1,2]
	SubFactor16 = m[1,0] * m[2,3] - m[2,0] * m[1,3]
	SubFactor17 = m[1,0] * m[2,2] - m[2,0] * m[1,2]
	SubFactor18 = m[1,0] * m[2,1] - m[2,0] * m[1,1]

	Inverse = null()
	Inverse[0,0] = + (m[1,1] * SubFactor00 - m[1,2] * SubFactor01 + m[1,3] * SubFactor02)
	Inverse[0,1] = - (m[1,0] * SubFactor00 - m[1,2] * SubFactor03 + m[1,3] * SubFactor04)
	Inverse[0,2] = + (m[1,0] * SubFactor01 - m[1,1] * SubFactor03 + m[1,3] * SubFactor05)
	Inverse[0,3] = - (m[1,0] * SubFactor02 - m[1,1] * SubFactor04 + m[1,2] * SubFactor05)

	Inverse[1,0] = - (m[0,1] * SubFactor00 - m[0,2] * SubFactor01 + m[0,3] * SubFactor02)
	Inverse[1,1] = + (m[0,0] * SubFactor00 - m[0,2] * SubFactor03 + m[0,3] * SubFactor04)
	Inverse[1,2] = - (m[0,0] * SubFactor01 - m[0,1] * SubFactor03 + m[0,3] * SubFactor05)
	Inverse[1,3] = + (m[0,0] * SubFactor02 - m[0,1] * SubFactor04 + m[0,2] * SubFactor05)

	Inverse[2,0] = + (m[0,1] * SubFactor06 - m[0,2] * SubFactor07 + m[0,3] * SubFactor08)
	Inverse[2,1] = - (m[0,0] * SubFactor06 - m[0,2] * SubFactor09 + m[0,3] * SubFactor10)
	Inverse[2,2] = + (m[0,0] * SubFactor11 - m[0,1] * SubFactor09 + m[0,3] * SubFactor12)
	Inverse[2,3] = - (m[0,0] * SubFactor08 - m[0,1] * SubFactor10 + m[0,2] * SubFactor12)

	Inverse[3,0] = - (m[0,1] * SubFactor13 - m[0,2] * SubFactor14 + m[0,3] * SubFactor15)
	Inverse[3,1] = + (m[0,0] * SubFactor13 - m[0,2] * SubFactor16 + m[0,3] * SubFactor17)
	Inverse[3,2] = - (m[0,0] * SubFactor14 - m[0,1] * SubFactor16 + m[0,3] * SubFactor18)
	Inverse[3,3] = + (m[0,0] * SubFactor15 - m[0,1] * SubFactor17 + m[0,2] * SubFactor18)

	Determinant = m[0,0] * Inverse[0,0] + m[0,1] * Inverse[0,1] + m[0,2] * Inverse[0,2] + m[0,3] * Inverse[0,3]

	Inverse /= Determinant

	return Inverse