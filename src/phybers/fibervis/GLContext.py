from OpenGL import GL
from PyQt5 import QtCore, QtWidgets
from numpy import pi, sin

from .Framework.Tools import glm
from .Framework.Tools.visualizationEnums import SegmentationTypes, ROIType, VisualizationActions, VisualizationObject
from .Framework.CoordinateSystem import CoordinateSystem
from .Framework.Tools.Camera import Camera

from .Framework.BoundingBox import BoundingBox
from .Framework.Bundle import Bundle
from .Framework.Mesh import Mesh
from .Framework.MRI import MRI
from .Framework.Slice import Slice
from .Framework.Volume import Volume

from .Framework.Segmentation.SegmentationHandler import SegmentationHandler
from .Framework.Segmentation.InPlaceSegmentation import InPlaceSegmentation
from .Framework.Segmentation.ROISegmentation import ROISegmentation
from .Framework.Segmentation.ROI import ROI
from .Framework.Segmentation.AtlasBasedParallelSegmentation import AtlasBasedParallelSegmentation
from .Framework.Segmentation.FFClustSegmentation import FFClustSegmentation

# Performance test
import numpy as np
import time as time


SCALE_FACTOR = 1/12000


def defaultLighting():
    return {
    "lightPos" : [0.0, 100.0, 0.0],
    "lightAttr" : [0.5, 0.6, 1.0],
    "materialAttr" : [1.0, 1.0, 1.0], # White background for the GUI
    "shininess" : 5.0
    }


def defaultBackgroundColor():
	return [1.0, 1.0, 1.0, 1.0]


class GLWidget(QtWidgets.QOpenGLWidget):
    ''' Widget with the logic of the program.
    It uses framework classes for visualization. And it manages all the
    framework instances.
    '''

    updateViewingObjects = QtCore.pyqtSignal()
    updateSettingWindow = QtCore.pyqtSignal(SegmentationHandler)
    objectsChanged = QtCore.pyqtSignal(list)

    def __init__(self, parent = None):
        ''' Initialize the members for the OpenGL Widget
        '''

        super(GLWidget, self).__init__(parent)

        # self.version_profile = version_profile

        self.bundles = []
        self.meshes = []
        self.mris = []

        self.rois = []

        self.clearColor = defaultBackgroundColor()

        # default mouse flags
        self.orbit = False
        self.pan = False
        self.panning = False
        self.tilt = False

        self.currentObject = None
        self.draw_boundingbox = True

        # Mouse-screen attri
        self.screenX, self.screenY = 0,0

        self.segmentations = {  SegmentationTypes.InPlace : InPlaceSegmentation,
                                                        SegmentationTypes.ROIs : ROISegmentation,
                                                        SegmentationTypes.AtlasBased : AtlasBasedParallelSegmentation,
                                                        SegmentationTypes.FFClust : FFClustSegmentation }

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) # type: ignore

        self.customContextMenuRequested.connect(self.ShowContextMenu)


    def initializeGL(self):
        ''' Initialize the OpenGL context and creates all the shaders programs
        '''

        print("OpenGL version: {}".format(GL.glGetString(GL.GL_VERSION).decode("utf-8"))) # type: ignore

        # Initialize shaders
        self.shaderDict = {}
        self.shaderList = [     Bundle.createProgram(),
                                                Mesh.createProgram(),
                                                Volume.createProgram(),
                                                BoundingBox.createProgram(),
                                                SegmentationHandler.createProgram(),
                                                # ROISegmentation.createProgram(),
                                                AtlasBasedParallelSegmentation.createProgram(),
                                                Slice.createProgram(),
                                                ROI.createProgram()]

        objectsList = [ [Bundle], #inplacesegmentation muved to segmentationhandler program
                                        [Mesh],
                                        [Volume],
                                        [BoundingBox],
                                        [InPlaceSegmentation, ROISegmentation],
                                        [AtlasBasedParallelSegmentation, FFClustSegmentation],
                                        [Slice],
                                        [ROI]]

        for i in range(len(objectsList)):
            self.shaderDict.update(dict.fromkeys(objectsList[i], self.shaderList[i]))

        self.coordSystemShader = CoordinateSystem.createProgram()

        self.camera = Camera(350.0)
        self.csCamera = Camera(1/sin(22.5*pi/180))

        # Config light parameters and view
        for s in self.shaderList:
            for shader in s:
                try:
                    self._configLight(shader, defaultLighting())
                except:
                    pass
                self._configView(shader)

        self._configView(self.coordSystemShader[0], self.csCamera)

        # Initialize some variables
        self.coordSystem = CoordinateSystem(self.coordSystemShader)
        self.proj = glm.perspective(45.0, 1, 0.01, 100000.0)
        self._configPerspective(self.coordSystemShader[0])


        self.testing = False
        self.FrameTime = GL.glGenQueries(1)

        ##########
        print(GL.GL_MAX_UNIFORM_BLOCK_SIZE, GL.glGetIntegerv(GL.GL_MAX_UNIFORM_BLOCK_SIZE))
        print(GL.GL_MAX_VERTEX_UNIFORM_COMPONENTS, GL.glGetIntegerv(GL.GL_MAX_VERTEX_UNIFORM_COMPONENTS))
        print(GL.GL_MAX_TEXTURE_SIZE, ' {} max dim.'.format(GL.glGetIntegerv(GL.GL_MAX_TEXTURE_SIZE)))
        print(GL.GL_MAX_3D_TEXTURE_SIZE, ' {} max dim.'.format(GL.glGetIntegerv(GL.GL_MAX_3D_TEXTURE_SIZE)))



        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_PRIMITIVE_RESTART)
        GL.glPrimitiveRestartIndex(0xFFFFFFFF)


    def paintGL(self):
        ''' Paint function. Its called by the widget.
        '''

        GL.glViewport(0, 0, self.width(), self.height())

        GL.glClearColor(*self.clearColor)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # FRAME TIME
        if self.testing:
            GL.glBeginQuery(GL.GL_TIME_ELAPSED, self.FrameTime)

        for bundle in self.bundles:
            bundle.draw()

        for mri in self.mris:
            mri.draw()

        for roi in self.rois:
            roi.draw()

        for mesh in self.meshes:
            mesh.draw(self.camera.eye)

        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        GL.glViewport(0, 0, 150, 150)
        self.coordSystem.draw()

        # FRAME TIME
        if self.testing:
            GL.glEndQuery(GL.GL_TIME_ELAPSED)  # Termina consulta.
            ready = False
            while not ready:
                ready = GL.glGetQueryObjectuiv(self.FrameTime, GL.GL_QUERY_RESULT_AVAILABLE)

            self.testArray[self.testing_i] = (GL.glGetQueryObjectuiv(
                    self.FrameTime, GL.GL_QUERY_RESULT)/1000000000.0)
            self.testing_i += 1


    def resizeGL(self, width, height):
        ''' Recalculate the projection matrix, and upload the new one to all shaders
        '''

        self.proj = glm.perspective(45.0, width/height, 0.01, 100000.0)
        for s in self.shaderList:
            for shader in s:
                self._configPerspective(shader)


    def validBundleExtension(self):
        return Bundle.validExtension()


    def validMeshExtension(self):
        return Mesh.validExtension()


    def validMRIExtension(self):
        return MRI.validExtension()


    def addBundleFile(self, bundleFiles):
        # Makes the context the current one
        self.makeCurrent()

        new_bundles = [Bundle(bundlePath, self.shaderDict, self.bundles) for bundlePath in bundleFiles]
        if new_bundles:
            self.bundles.extend(new_bundles)

            if hasattr(self, 'camera'):
                bboxs = np.array([bundle.calculateBoundingBoxDimCenter() for bundle in new_bundles])
                center = (bboxs[:, 0].max(axis=0) + bboxs[:, 0].min(axis=0)) / 2

                self.camera.center = center
                self.camera.view = self.camera.calculateView()

                for s in self.shaderList:
                    for shader in s:
                        self._configView(shader)

            self._configView(self.coordSystemShader[0], self.csCamera)

        self.updateViewingObjects.emit()
        self.update()


    def addMeshFile(self, meshFiles):
        # Makes the context the current one
        self.makeCurrent()

        for meshPath in meshFiles:
            self.meshes.append(Mesh(meshPath, self.shaderDict, self.meshes))
            # self.meshes.append(Mesh(meshPath, self.meshShader, self.meshes))

        self.updateViewingObjects.emit()
        self.update()


    def addMRIFile(self, mriFiles):
        # Makes the context the current one
        self.makeCurrent()

        for mriPath in mriFiles:
            self.mris.append(MRI(mriPath, self.shaderDict, self.mris))

        self.updateViewingObjects.emit()
        self.update()


    def addROI(self):
        self.makeCurrent()

        self.rois.append(ROI(ROIType.Sphere, self.camera.center, 30.0, self.shaderDict, self.rois))

        self.updateViewingObjects.emit()
        self.update()


    @QtCore.pyqtSlot(dict)
    def modifyObject(self, options):
        # Makes the context the current one
        self.makeCurrent()

        def retrieveItemIteratively(root, index):
            item = root

            for i in index:
                if hasattr(item, 'children'):
                    item = item.children[i]
                else:
                    item = item[i]

            return item

        objectRoot = None
        itemObject = None

        rootType = options['rootType']
        index = options['number']
        action = options['action']

        if rootType == VisualizationObject.Bundle:
            objectRoot = self.bundles
        elif rootType == VisualizationObject.Mesh:
            objectRoot = self.meshes
        elif rootType == VisualizationObject.MRI:
            objectRoot = self.mris
        elif rootType == VisualizationObject.ROI:
            objectRoot = self.rois
        else:
            raise TypeError('Unrecognise visualization objects type: ', rootType)

        if index != -1:
            itemObject = retrieveItemIteratively(objectRoot, index)


        # Delete
        #########################
        if action == VisualizationActions.Delete:
            if index != -1:
                itemObject.cleanOpenGL()
                itemObject.parent.remove(itemObject)
                itemObject.clearRef()
            else:
                while(len(objectRoot) != 0):
                    item = objectRoot[0]
                    item.cleanOpenGL()
                    objectRoot.remove(item)
                    item.clearRef()
            self.updateViewingObjects.emit()

        # Toggle drawable
        #########################
        elif action == VisualizationActions.ToggleDrawable:
            itemObject.drawable = not itemObject.drawable

        # Rotate
        #########################
        elif action == VisualizationActions.Rotate:
            angle, axis = options['data']

            if index == -1:
                for i in objectRoot:
                    i.rotate(self.camera.center, angle, axis)
                self.objectsChanged.emit(objectRoot)

            else:
                itemObject.rotate(self.camera.center, angle, axis)
                self.objectsChanged.emit([itemObject])

        # Translate
        #########################
        elif action == VisualizationActions.Translate:
            v = options['data']

            if index == -1:
                for i in objectRoot:
                    i.translate(v)
                self.objectsChanged.emit(objectRoot)
            else:
                itemObject.translate(v)
                self.objectsChanged.emit([itemObject])

        # Scale
        #########################
        elif action == VisualizationActions.Scale:
            v = options['data']

            if index == -1:
                for i in objectRoot:
                    i.scale(v, self.camera.center)
                self.objectsChanged.emit(objectRoot)

            else:
                itemObject.scale(v, self.camera.center)

                self.objectsChanged.emit([itemObject])

        # ResetTransforms
        ##########################}
        elif action == VisualizationActions.ResetTransforms:
            if index == -1:
                for i in objectRoot:
                    i.resetModel()
                self.objectsChanged.emit(objectRoot)

            else:
                itemObject.resetModel()

                self.objectsChanged.emit([itemObject])

        # Load and Apply Matrix
        elif action == VisualizationActions.LoadAndApplyMatrix:
            matrixFile = options['data']

            itemObject.loadAndApplyMatrix(matrixFile)

        # Add Segmentation
        # ########################
        elif action == VisualizationActions.AddSegmentation:
            segmentationType = options['data']

            if segmentationType == SegmentationTypes.InPlace:
                segmentationObject = InPlaceSegmentation(itemObject, self.shaderDict)

            elif segmentationType == SegmentationTypes.ROIs:
                segmentationObject = ROISegmentation(itemObject, self.shaderDict)

            elif segmentationType == SegmentationTypes.AtlasBased:
                segmentationObject = AtlasBasedParallelSegmentation(itemObject, self.shaderDict)

            elif segmentationType == SegmentationTypes.FFClust:
                segmentationObject = FFClustSegmentation(itemObject, self.shaderDict)

            # Volume visualizations
            # #####################
            elif segmentationType == VisualizationObject.MRISlice:
                segmentationObject = Slice(itemObject, self.shaderDict)

            elif segmentationType == VisualizationObject.MRIVolume:
                segmentationObject = Volume(itemObject, self.shaderDict, self.camera)


            else:
                raise TypeError('Segmentation type not implemented yet: ', segmentationType)

            itemObject.children.append(segmentationObject)
            self.updateViewingObjects.emit()

        # Slice Modification
        elif action == VisualizationActions.SliceModification:
            linearInterp, discardValues, threshold, axis, pos2Axis, bright, contrast = options['data']

            itemObject.setLinearInterpolation(linearInterp)
            itemObject.setDiscardValuesWithThreshold(discardValues, threshold)
            itemObject.calculatePlaneNormal(axis, pos2Axis)
            itemObject.setBright(bright)
            itemObject.setContrast(contrast)

        # Mesh Modification
        elif action == VisualizationActions.MeshModification:
            if len(options['data']) == 1:
                if isinstance(options['data'][0], bool):
                    itemObject.setFront2BackSorting(options['data'][0])
                else:
                    itemObject.setColor(options['data'][0])

            else:
                drawLines, alpha = options['data']

                if index == -1:
                    for i in objectRoot:
                        i.setDrawLines(drawLines)
                        i.setAlpha(alpha)
                else:
                    itemObject.setDrawLines(drawLines)
                    itemObject.setAlpha(alpha)

        # Volume Modification
        elif action == VisualizationActions.VolumeModification:
            data = options['data']
            if isinstance(data, bool):
                itemObject.setFront2BackDrawing(data)
            elif len(data) == 2:
                itemObject.setThreshold(data[0])
                itemObject.setAlpha(data[1])
            else:
                raise TypeError('Unrecognise data')

        # Shader selection
        elif action == VisualizationActions.ShaderSelection:
            selected_shader = options['data'][0]

            if index == -1:
                for i in objectRoot:
                    i.setSelectedShader(selected_shader)
            else:
                itemObject.setSelectedShader(selected_shader)
        # Focus camera on object
        elif action == VisualizationActions.FocusObject:
            size = None
            center = itemObject.get_center()
            try:
                size = np.max(itemObject.get_size()) * 2
            except NotImplementedError:
                print(f"Object {itemObject} does not implement get_size.")
            finally:
                self.camera.focus(center, min_r=size)
                for shaders in self.shaderList:
                    for shader in shaders:
                        self._configView(shader)
        elif action == VisualizationActions.ColorSelection:
            data = options['data']

            if index == -1:
                for i in objectRoot:
                    i.set_color(data)
            else:
                itemObject.set_color(data)
        else:
            raise TypeError('Unrecognise visualization objects action')

        self.update()


    @QtCore.pyqtSlot(dict)
    def selectedObject(self, options):
        self.currentObject = options.get('current')

    @QtCore.pyqtSlot(dict)
    def modifySegmentation(self, options):
        # Makes the context the current one
        self.makeCurrent()

        segmentation = options.get('reference')
        attributes = options.get('attributes')
        segmentSubject = options.get('segmentSubject')
        updateViewingObjects = options.get('updateViewingObjects')
        updateSettingWindow = options.get('updateSettingWindow')

        if not isinstance(segmentation, SegmentationHandler):
            raise TypeError('modfySegmentation got an unxpected object reference: ', type(segmentation))

        if attributes:
            for attr in attributes.keys():
                try:
                    getattr(segmentation, attr)(*attributes[attr])
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", str(e), QtWidgets.QMessageBox.Ok)

        if segmentSubject:
            segmentation.segmentSubject()

        if updateViewingObjects:
            self.updateViewingObjects.emit()

        if updateSettingWindow:
            self.updateSettingWindow.emit(segmentation)

        self.update()


    def _configLight(self, shader, attributes):
        lightPos = attributes['lightPos']
        light = attributes['lightAttr']
        lightLa = light[0]
        lightLd = light[1]
        lightLs = light[2]
        material = attributes['materialAttr']
        materialKa = material[0]
        materialKd = material[1]
        materialKs = material[2]
        shininess = attributes['shininess']

        shader.glUseProgram()

        # Light
        GL.glUniform4f(shader.glGetUniformLocation("Light.pos"), *lightPos, 1.0)
        GL.glUniform3f(shader.glGetUniformLocation("Light.La"), lightLa, lightLa, lightLa)
        GL.glUniform3f(shader.glGetUniformLocation("Light.Ld"), lightLd, lightLd, lightLd)
        GL.glUniform3f(shader.glGetUniformLocation("Light.Ls"), lightLs, lightLs, lightLs)

        # Material
        GL.glUniform3f(shader.glGetUniformLocation("Material.Ka"), materialKa, materialKa, materialKa)
        GL.glUniform3f(shader.glGetUniformLocation("Material.Kd"), materialKd, materialKd, materialKd)
        GL.glUniform3f(shader.glGetUniformLocation("Material.Ks"), materialKs, materialKs, materialKs)
        GL.glUniform1f(shader.glGetUniformLocation("Material.shininess"), shininess)


    def _configPerspective(self, shader):
        shader.glUseProgram()
        GL.glUniformMatrix4fv(shader.glGetUniformLocation("P"),
                              1, GL.GL_TRUE, self.proj.getA())

    def _configView(self, shader, camera=None):
        if camera == None:
            camera = self.camera
        shader.glUseProgram()
        GL.glUniformMatrix4fv(shader.glGetUniformLocation("V"),
                              1, GL.GL_FALSE, camera.view.getA())



    def mousePressEvent(self, event):
        """ Captura el evento del boton del mouse clickeado y selecciona la funcion correspondiente
                a este. """
        self.screenX, self.screenY = event.pos().x(), event.pos().y()

        if event.button() == QtCore.Qt.LeftButton:
            self.orbit = True
            self.pan = False
            self.tilt = False
            event.accept()

        elif event.button() == QtCore.Qt.RightButton: # Permite desplazar el modelo.
            self.orbit = False
            self.pan = True
            self.panning = False
            self.tilt = False
            event.accept()

        elif event.button() == QtCore.Qt.MiddleButton:
            self.orbit = False
            self.pan = False
            self.tilt = True
            event.accept()

        else:
            self.orbit = False
            self.pan = False
            self.tilt = False
            event.ignore()


    def mouseMoveEvent(self, event):
        """ Ejecuta la funcion correspondiente al boton del mouse clickeado. """
        newScreenX, newScreenY = event.pos().x(), event.pos().y()
        dx, dy = newScreenX - self.screenX, newScreenY - self.screenY

        self.screenX, self.screenY = newScreenX, newScreenY

        if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier:
            if not self.currentObject:
                return

            if self.orbit:
                axis, angle = self.camera.axisAndAngleFromScreen(dx, dy)

                if isinstance(self.currentObject, list):
                    for cObject_i in self.currentObject:
                        cObject_i.rotate(cObject_i.get_center(), angle, axis)
                else:
                    self.currentObject.rotate(self.currentObject.get_center(), angle, axis)

            elif self.pan:
                self.panning = True
                translateV = self.camera.vectorFromScreen(dx, -dy)

                if isinstance(self.currentObject, list):
                    for cObject_i in self.currentObject:
                        cObject_i.stackTranslate(translateV)
                else:
                    self.currentObject.stackTranslate(translateV)
            elif self.tilt:
                axis = self.camera.tiltAxisFromScreen()
                if isinstance(self.currentObject, list):
                    for cObject_i in self.currentObject:
                        cObject_i.spin(dx * np.pi / 10, axis)
                else:
                    self.currentObject.spin(dx *np.pi / 10, axis)
            self.objectsChanged.emit([self.currentObject])
        else:
            if self.orbit:
                if True:
                    self.camera.orbit(dx, dy)
                    self.csCamera.orbit(dx, dy)
                self._configView(self.coordSystemShader[0], self.csCamera)
            elif self.pan:
                self.panning = True
                self.camera.panning(dx, dy)
            elif self.tilt:
                self.camera.spin(np.pi * dx / 10)
                self.csCamera.spin(np.pi * dx / 10)
                self._configView(self.coordSystemShader[0], self.csCamera)
            else:
                return

            for s in self.shaderList:
                for shader in s:
                    self._configView(shader)

        event.accept()
        self.update()


    def wheelEvent(self, event):
        if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier:
            if not self.currentObject:
                return

            delta = event.angleDelta().y()

            if isinstance(self.currentObject, list):
                for cObject_i in self.currentObject:
                    cObject_i.stackScale(delta*SCALE_FACTOR+1.0, self.camera.center)
            else:
                self.currentObject.stackScale(delta*SCALE_FACTOR+1.0, self.camera.center)

            self.objectsChanged.emit([self.currentObject])

        else:
            self.camera.zooming(event.angleDelta().y())

            for s in self.shaderList:
                for shader in s:
                    self._configView(shader)

        event.accept()
        self.update()

    def set_draw_bbox(self, value=None):
        if value is None:
            self.draw_boundingbox = not self.draw_boundingbox
        else:
            self.draw_boundingbox = value
        for bundle in self.bundles:
            bundle.setDrawBB(self.draw_boundingbox)
        for mri in self.mris:
            mri.setDrawBB(self.draw_boundingbox)
        for mesh in self.meshes:
            mesh.setDrawBB(self.draw_boundingbox)


    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_1:
            self.camera.frontView()
            self.csCamera.frontView()
        elif key == QtCore.Qt.Key_2:
            self.camera.backView()
            self.csCamera.backView()
        elif key == QtCore.Qt.Key_3:
            self.camera.leftView()
            self.csCamera.leftView()
        elif key == QtCore.Qt.Key_4:
            self.camera.rightView()
            self.csCamera.rightView()
        elif key == QtCore.Qt.Key_5:
            self.camera.topView()
            self.csCamera.topView()
        elif key == QtCore.Qt.Key_6:
            self.camera.bottomView()
            self.csCamera.bottomView()
        elif key == QtCore.Qt.Key_B:
            self.set_draw_bbox()
        elif key == QtCore.Qt.Key_W:
            self.camera.panning(0, 0, -10)
        elif key == QtCore.Qt.Key_A:
            self.camera.panning(10, 0)
        elif key == QtCore.Qt.Key_S:
            self.camera.panning(0, 0, 10)
        elif key == QtCore.Qt.Key_D:
            self.camera.panning(-10, 0)
        elif key == QtCore.Qt.Key_R:
            self.camera.panning(0, 10)
        elif key == QtCore.Qt.Key_F:
            self.camera.panning(0, -10)
        elif key == QtCore.Qt.Key_Q:
            self.camera.spin(np.pi * 1)
            self.csCamera.spin(np.pi * 1)
        elif key == QtCore.Qt.Key_E:
            self.camera.spin(np.pi * -1)
            self.csCamera.spin(np.pi * -1)
        elif key == QtCore.Qt.Key_Up:
            self.camera.orbit(0, 1)
            self.csCamera.orbit(0, 1)
        elif key == QtCore.Qt.Key_Down:
            self.camera.orbit(0, -1)
            self.csCamera.orbit(0, -1)
        elif key == QtCore.Qt.Key_Left:
            self.camera.orbit(1, 0)
            self.csCamera.orbit(1, 0)
        elif key == QtCore.Qt.Key_Right:
            self.camera.orbit(-1, 0)
            self.csCamera.orbit(-1, 0)
        elif key == QtCore.Qt.Key_F4:
            self.debug_breakpoint()
        else:
            event.ignore()
            return

        for s in self.shaderList:
            for shader in s:
                self._configView(shader)

        self._configView(self.coordSystemShader[0], self.csCamera)


        event.accept()
        self.update()


    @QtCore.pyqtSlot(QtCore.QPoint)
    def ShowContextMenu(self, pos):
        if self.panning:
            return

        self.makeCurrent()

        contextMenu = QtWidgets.QMenu()

        resetCameraAction = contextMenu.addAction("Reset camera")

        action = contextMenu.exec(self.mapToGlobal(pos))

        if action == resetCameraAction:
            self.camera.defaultValues()
            self.csCamera.defaultValues()

            for s in self.shaderList:
                for shader in s:
                    self._configView(shader)

            self._configView(self.coordSystemShader[0], self.csCamera)

        self.update()



    def testingModule(self):
        print('testingModule')
        self.segmentationTest()


    def cleanOpenGL(self):
        self.makeCurrent()

        for bundle in self.bundles:
            bundle.cleanOpenGL()

        for mesh in self.meshes:
            mesh.cleanOpenGL()

        for mri in self.mris:
            mri.cleanOpenGL()

        for roi in self.rois:
            roi.cleanOpenGL()

        self.coordSystem.cleanOpenGL()


    def performanceTestFPS(self):
        self.makeCurrent()
        testingN = 1000
        n = 100
        self.testing_i = 0
        self.testing = True
        self.testArray = np.empty(testingN*n, dtype=np.float32)
        for i in range(testingN):
            self.camera.orbit(10, 0)
            self.csCamera.orbit(10, 0)

            self._configView(self.coordSystemShader[0], self.csCamera)

            for s in self.shaderList:
                for shader in s:
                    self._configView(shader)

            for j in range(n):
                self.paintGL()

        self.testing = False

        print("Test ended. Number of samples taken: ", self.testing_i, "\nAverage frame time:", np.mean(self.testArray), "\nAverage fps: ", 1/np.mean(self.testArray))


    def segmentationTest(self):
        self.makeCurrent()
        try:
            testingN = 1000
            n = 10
            self.testing_i = 0
            self.testArray = np.empty(testingN*n, dtype=np.float32)

            for i in range(testingN):
                for j in range(n):
                    tb = time.time()
                    self.bundles[0].children[0].segmentSubject()
                    te = time.time()

                    self.testArray[self.testing_i] = te-tb
                    self.testing_i += 1

            print("Test ended. Number of samples taken: ", self.testing_i, "\nAverage time:", np.mean(self.testArray))
        except Exception as e:
            print(e)

    def debug_breakpoint(self):
        if not self.currentObject:
            return
        self.objectsChanged.emit([self.currentObject])

        for s in self.shaderList:
            for shader in s:
                self._configView(shader)
