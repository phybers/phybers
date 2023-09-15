# shouldn't notify objects by itself... it should be the glcontext
import numpy as np
from .glm import Quaternion, lookAt


class Camera():
    ro_right = np.frombuffer(np.array([1, 0, 0], np.float32), np.float32)
    ro_up = np.frombuffer(np.array([0, 1, 0], np.float32), np.float32)
    ro_front = np.frombuffer(np.array([0, 0, 1], np.float32), np.float32)
    ro_left = np.frombuffer(np.array([-1, 0, 0], np.float32), np.float32)
    ro_down = np.frombuffer(np.array([0, -1, 0], np.float32), np.float32)
    ro_back = np.frombuffer(np.array([0, 0, -1], np.float32), np.float32)

    def __init__(self, radius):
        # reference to objects that needs to be notify
        self.notifyUpdates2Objects = []

        self.radius = radius
        self.theta = 0.0
        self.phi = 0.0
        self.up = self.ro_up
        self.forward = self.ro_back
        self.right = self.ro_right
        self.center = np.array([0, 0, 0], dtype=np.float32)
        self.eye = self.ro_front * radius
        self.p_speed = 0.5 / radius
        self.r_speed = np.pi / 360
        self.z_speed = 0.05
        self.rotation = Quaternion.identity()
        self.view = self.calculateView()

    def calculateView(self):
        rot_phi = Quaternion.fromAngleAxis(self.phi, self.up)
        rot_theta = Quaternion.fromAngleAxis(self.theta, self.right)
        self.rotation = rot_phi * rot_theta
        eye_vector = self.forward * self.radius
        self.eye = self.center - self.rotation.rotateVector(eye_vector)
        if np.round(np.abs(self.theta) - (np.pi / 2), decimals=10) == 0:
            up = rot_phi.rotateVector(self.forward * -np.sign(self.theta))
            self.view = lookAt(self.eye, self.center, up)
        else:
            self.view = lookAt(self.eye, self.center, self.up)
        for object2Notify in self.notifyUpdates2Objects:
            object2Notify.updateCamera(self.eye)
        return self.view

    def orbit(self, dx, dy):
        self.phi = (self.phi - dx * self.r_speed) % (np.pi * 2)
        self.theta = np.clip(self.theta - dy * self.r_speed, -np.pi / 2, np.pi / 2)
        return self.calculateView()

    def spin(self, theta):
        axis = self.center - self.eye
        rotation = Quaternion.fromAngleAxis(theta * self.r_speed, axis)
        self.up = rotation.rotateVector(self.up)
        self.forward = rotation.rotateVector(self.forward)
        self.right = rotation.rotateVector(self.right)
        return self.calculateView()

    def panning(self, dx, dy, dz=0):
        up = self.rotation.rotateVector(self.up)
        right = self.rotation.rotateVector(self.right)
        self.center += (right * -dx + up * dy) * self.p_speed * self.radius
        if dz:
            forward = self.rotation.rotateVector(self.forward)
            self.center += forward * dz * self.p_speed * self.radius
        return self.calculateView()

    def rotate(self, dx, dy):
        m = np.sqrt(dx**2 + dy**2)
        if m > 0:
            axis = [-dy/m, -dx/m, 0]
            theta = np.pi * self.r_speed * m / 180.0
            rotation = Quaternion.fromAngleAxis(theta, axis)
            self.center = self.eye + rotation.rotateVector(self.center - self.eye)
            self.rotation *= rotation
            self.view = self.calculateView()

    def focus(self, coords, radius=None, min_r=None):
        self.center = np.asarray(coords)
        if radius is not None:
            self.radius = radius
        elif min_r is not None:
            self.radius = max(min_r, self.radius)
        return self.calculateView()

    def tiltAxisFromScreen(self):
        return self.rotation.rotateVector(-self.forward)

    def axisAndAngleFromScreen(self, dx, dy):
        up = self.rotation.rotateVector(self.up)
        right = self.rotation.rotateVector(self.right)
        magnitude = np.sqrt(dx**2 + dy**2)
        axis = up * dx / magnitude - right * dy / magnitude
        return axis, magnitude

    def vectorFromScreen(self, dx, dy):
        up = self.rotation.rotateVector(self.up)
        right = self.rotation.rotateVector(self.right)
        translateV = (dx * right + dy * up) * self.p_speed * self.radius
        return translateV

    def zooming(self, zoom):
        self.radius = max(self.radius + self.z_speed * -zoom, 1.0)
        return self.calculateView()

    def changeRotationSpeed(self, speed):
        self.r_speed = speed

    def changeZoomSpeed(self, speed):
        self.z_speed = speed

    def frontView(self):
        self.up = self.ro_up
        self.forward = self.ro_back
        self.right = self.ro_right
        self.phi = np.pi * 0
        self.theta = 0
        return self.calculateView()

    def backView(self):
        self.up = self.ro_up
        self.forward = self.ro_back
        self.right = self.ro_right
        self.phi = np.pi * 1.0
        self.theta = 0
        return self.calculateView()

    def leftView(self):
        self.up = self.ro_up
        self.forward = self.ro_back
        self.right = self.ro_right
        self.phi = np.pi * 1.5
        self.theta = 0
        return self.calculateView()

    def rightView(self):
        self.up = self.ro_up
        self.forward = self.ro_back
        self.right = self.ro_right
        self.phi = np.pi * 0.5
        self.theta = 0
        return self.calculateView()

    def topView(self):
        self.up = self.ro_back
        self.forward = self.ro_down
        self.right = self.ro_right
        self.phi = 0
        self.theta = 0
        return self.calculateView()

    def bottomView(self):
        self.up = self.ro_back
        self.forward = self.ro_up
        self.right = self.ro_left
        self.phi = 0
        self.theta = 0
        return self.calculateView()

    def setObject2Notify(self, object):
        if object not in self.notifyUpdates2Objects:
            self.notifyUpdates2Objects.append(object)

    def removeObject2Notify(self, object):
        if object in self.notifyUpdates2Objects:
            self.notifyUpdates2Objects.remove(object)
