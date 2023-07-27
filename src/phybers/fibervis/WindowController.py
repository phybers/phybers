'''
InPlaceSegmentationDialog.exportBundle ----> trk not implemented
'''

from .GLContext import GLWidget
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from .ui.Controllers.VisDialog import VisDialog
from .Framework.Tools.performance import timeit
from importlib_resources import files

_viewer = files('phybers.fibervis.ui').joinpath('viewer.ui')

class WindowController(QtWidgets.QMainWindow):
	''' Window controller for the app. It has function for several action.
	'''
	def __init__(self):
		super().__init__()

		glFormat = QtGui.QSurfaceFormat()
		glFormat.setVersion(4, 1)
		glFormat.setProfile(QtGui.QSurfaceFormat.CoreProfile)
		glFormat.setSamples(4)

		QtGui.QSurfaceFormat.setDefaultFormat(glFormat)

		# versionProfile = QtGui.QOpenGLVersionProfile()
		# versionProfile.setVersion(4, 1)
		# versionProfile.setProfile(QtGui.QSurfaceFormat.CoreProfile)

		# self.contextHandler = GLContext.GLWidget(versionProfile, self)
		self.contextHandler = GLWidget(self)
		self.contextHandler.setFocusPolicy(QtCore.Qt.StrongFocus)

		self.ui = uic.loadUi(_viewer, self)
		self.visObj = VisDialog(self)

		self.ui.setCentralWidget(self.contextHandler)

		self.ui.setWindowTitle('leFiber v1.0.0')

		# Connection of GUI to GLCBontext
		self.ui.actionOpenBundle.triggered.connect(self.openBundleFile)
		self.ui.actionOpenMesh.triggered.connect(self.openMeshFile)
		self.ui.actionOpenMRI.triggered.connect(self.openMRIFile)
		self.ui.actionAddROISphere.triggered.connect(self.createROI)

		# testing action
		self.ui.actionTest.triggered.connect(self.contextHandler.testingModule)

		# Visualization objects window
		# changed
		# hovered
		# toggled
		self.ui.actionVisualizationObjects.changed.connect(self.visObj.toggleVisWin(self.ui.actionVisualizationObjects.isChecked, self.pos, self.size))

		# Closed visualization win
		self.visObj.closed.connect(self.unCheckActionVisualizationObjects)

		# New visualization object
		self.contextHandler.updateViewingObjects.connect(self.visObj.updateTree)
		self.contextHandler.updateSettingWindow.connect(self.visObj.updateSettingWindow)

		# Modify visualization object
		self.visObj.changeObject.connect(self.contextHandler.modifyObject)
		self.visObj.modifySegmentation.connect(self.contextHandler.modifySegmentation)
		self.visObj.selectedObject.connect(self.contextHandler.selectedObject)

		# Notify R, T and S on objects
		self.contextHandler.objectsChanged.connect(self.visObj.objectsChanged)

		# We set the reference for the visualization objects
		self.visObj.bundleReference = self.contextHandler.bundles
		self.visObj.meshReference = self.contextHandler.meshes
		self.visObj.mriReference = self.contextHandler.mris
		self.visObj.roisReference = self.contextHandler.rois

		self.setAcceptDrops(True)

		# Hide testing tab
		self.menuTesting.menuAction().setVisible(False)

	def dragEnterEvent(self, event):
		if (event.mimeData().hasUrls()):
			event.acceptProposedAction()

	@timeit
	def dropEvent(self, event):
		for file in event.mimeData().urls():
			fileName = file.toLocalFile()

			extension = fileName.split('.')[-1]

			# Bundle
			if extension in self.contextHandler.validBundleExtension():
				self.contextHandler.addBundleFile([fileName])
			elif extension in self.contextHandler.validMeshExtension():
				self.contextHandler.addMeshFile([fileName])
			elif extension in self.contextHandler.validMRIExtension():
				self.contextHandler.addMRIFile([fileName])
			# elif extension == "bundlesdata":
			# 	self.contextHandler.addBundleFile([fileName[:-4]])
			else:
				print('File extension not sopported: ', fileName)


	def closeEvent(self, event):
		print('Cleaning...')
		self.contextHandler.cleanOpenGL()

		super().closeEvent(event)


	def keyPressEvent(self, event):
		# print('Key press: {0}'.format(event.key()))
		pass
		# self.contextHandler.setWindowState(QtCore.Qt.WindowFullScreen)
		# self.ui.showFullScreen()
		# if self.tFullScreen and event.key() == QtCore.Qt.Key_Escape:
		# 	event.accept()
		# 	self.toggleFullScreen()
		# else:
		# 	event.ignore()


	@QtCore.pyqtSlot()
	def unCheckActionVisualizationObjects(self):
		self.ui.actionVisualizationObjects.setChecked(False)


	@QtCore.pyqtSlot()
	def openBundleFile(self):
		''' Function that gets called when pressing the open bundle file action
		'''

		# Gets direction of bundle files
		formats = "" # *.bundles *.trk *.tck
		for f in self.contextHandler.validBundleExtension():
			formats += "*."+f+" "
		bundleFiles, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Bundle", "", "Bundles ("+formats+")")

		if len(bundleFiles) == 0:
			return

		self.contextHandler.addBundleFile(bundleFiles)


	@QtCore.pyqtSlot()
	def openMeshFile(self):
		''' Function that gets called when pressing the open mesh file action
		'''

		# Gets direction of bundle files
		formats = ""
		for f in self.contextHandler.validMeshExtension():
			formats += "*."+f+" "
		meshFiles, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Mesh", "", "Mesh ("+formats+")")

		if len(meshFiles) == 0:
			return

		self.contextHandler.addMeshFile(meshFiles)


	@QtCore.pyqtSlot()
	def openMRIFile(self):
		''' Function that gets called when pressing the open MRI file action
		'''

		# Gets direction of bundle files
		formats = ""
		for f in self.contextHandler.validMRIExtension():
			formats += "*."+f+" "
		mriFiles, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select MRI", "", "MRI ("+formats+")")

		if len(mriFiles) == 0:
			return

		self.contextHandler.addMRIFile(mriFiles)


	@QtCore.pyqtSlot()
	def createROI(self):
		'''
		'''

		self.contextHandler.addROI()


	def testSlot(self):
		print('testSlot!')