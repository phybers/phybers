'''
Dictionary is keeping a reference to the segmentations objects... not deleting
'''

from PyQt5 import QtGui, QtWidgets, uic, QtCore
import PyQt5
from ...Framework.Tools.visualizationEnums import *

# Segmentation Dialogs
from ...Framework.Segmentation.SegmentationHandler import SegmentationHandler
from .InPlaceSegmentationDialog import InPlaceSegmentationDialog
from .ROIsSegmentationDialog import ROIsSegmentationDialog
from .AtlasBasedParallelSegmentationDialog import AtlasBasedParallelSegmentationDialog
from .FFClustSegmentationDialog import FFClustSegmentationDialog
from importlib_resources import files

_vot_ui = files('phybers.fibervis.ui').joinpath(
	'visualizationObjectsTool.ui')


def identifyNumberRecursively(item, number):
	root = item

	if item.parent() != None:
		root = identifyNumberRecursively(item.parent(), number)
		number.append(item.parent().indexOfChild(item))
	else:
		return item
	return root


def retrieveItemIteratively(root, index):
	item = root

	for i in index:
		if hasattr(item, 'children'):
			item = item.children[i]
		else:
			item = item[i]

	return item


class ownQTreeWidgetItem(QtWidgets.QTreeWidgetItem):
	def setIdentifier(self, identification):
		self.identifier = identification


class VisDialog(QtWidgets.QDialog):
	''' Window controller for the app. It has function for several action.
	'''

	closed = QtCore.pyqtSignal()
	changeObject = QtCore.pyqtSignal(dict)
	modifySegmentation = QtCore.pyqtSignal(dict)
	selectedObject = QtCore.pyqtSignal(dict)


	def __init__(self, parent):
		super().__init__(parent)
		self.ui = uic.loadUi(str(_vot_ui), self)

		self.ui.setWindowTitle('Visualization Tool')

		# signal when closing
		oldCloseEvent = self.ui.closeEvent
		def newCloseEvent(*args, **kwargs):
			self.closed.emit()
			return oldCloseEvent(*args, **kwargs)
		self.ui.closeEvent = newCloseEvent

		# this 4 variables have to be treated like const
		self.bundleReference = None
		self.meshReference = None
		self.mriReference = None
		self.roisReference = None


		# Context menu
		self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.ui.treeWidget.customContextMenuRequested.connect(self.prepareMenu)

		# Setting widget
		# Signal for displaying settings
		self.ui.treeWidget.currentItemChanged.connect(self.activeItemChanged)

		self.connectAndConfigRotateGB()
		self.connectAndConfigTranslateGB()
		self.connectAndConfigScaleGB()
		self.ui.resetTransformsButton.clicked.connect(self.resetTransformsItemSelected)
		self.ui.loadMatrixFromFileButton.clicked.connect(self.loadMatrixFromFile)

		self.connectAndConfigBundleGB()
		self.connectAndConfigSliceGB()
		self.connectAndConfigVolumeGB()
		self.configMeshGB()

		# Hide rotate, translate and scale options, show when item is selected
		self.rotateGroupBox.hide()
		self.translateGroupBox.hide()
		self.scaleGroupBox.hide()

		self.bundleGroupBox.hide()
		self.sliceGroupBox.hide()
		self.meshGroupBox.hide()
		self.volumeGroupBox.hide()

		self.ui.resetTransformsButton.hide()

		# Setting windows
		self.windows = dict()

		# segmentation dialogs for identifier
		self.segmentationDialogs = {SegmentationTypes.InPlace : InPlaceSegmentationDialog,
									SegmentationTypes.ROIs : ROIsSegmentationDialog,
									SegmentationTypes.AtlasBased : AtlasBasedParallelSegmentationDialog,
									SegmentationTypes.FFClust : FFClustSegmentationDialog}


	def connectAndConfigRotateGB(self):
		self.ui.rotateAngleLineEdit.returnPressed.connect(self.rotateItemSelected)
		self.ui.rotateXLineEdit.returnPressed.connect(self.rotateItemSelected)
		self.ui.rotateYLineEdit.returnPressed.connect(self.rotateItemSelected)
		self.ui.rotateZLineEdit.returnPressed.connect(self.rotateItemSelected)
		self.ui.rotateButton.clicked.connect(self.rotateItemSelected)

		validator = QtGui.QDoubleValidator(-1000, 1000, 2, self)
		self.ui.rotateAngleLineEdit.setValidator(validator)
		self.ui.rotateXLineEdit.setValidator(validator)
		self.ui.rotateYLineEdit.setValidator(validator)
		self.ui.rotateZLineEdit.setValidator(validator)


	def connectAndConfigTranslateGB(self):
		self.ui.translateXLineEdit.returnPressed.connect(self.translateItemSelected)
		self.ui.translateYLineEdit.returnPressed.connect(self.translateItemSelected)
		self.ui.translateZLineEdit.returnPressed.connect(self.translateItemSelected)
		self.ui.translateButton.clicked.connect(self.translateItemSelected)

		validator = QtGui.QDoubleValidator(-1000, 1000, 2, self)
		self.ui.translateXLineEdit.setValidator(validator)
		self.ui.translateYLineEdit.setValidator(validator)
		self.ui.translateZLineEdit.setValidator(validator)


	def connectAndConfigScaleGB(self):
		self.ui.scaleXLineEdit.returnPressed.connect(self.scaleItemSelected)
		self.ui.scaleYLineEdit.returnPressed.connect(self.scaleItemSelected)
		self.ui.scaleZLineEdit.returnPressed.connect(self.scaleItemSelected)
		self.ui.scaleButton.clicked.connect(self.scaleItemSelected)

		validator = QtGui.QDoubleValidator(-1000, 1000, 2, self)
		self.ui.scaleXLineEdit.setValidator(validator)
		self.ui.scaleYLineEdit.setValidator(validator)
		self.ui.scaleZLineEdit.setValidator(validator)


	def connectAndConfigBundleGB(self):
		self.bundleGBSignals()


	def connectAndConfigSliceGB(self):
		self.sliceGBSignals()

		validator = QtGui.QDoubleValidator(-1000, 1000, 2, self)
		self.ui.axisCXLE.setValidator(validator)
		self.ui.axisCYLE.setValidator(validator)
		self.ui.axisCZLE.setValidator(validator)


	def connectAndConfigVolumeGB(self):
		self.volumeGBSignals()


	def configMeshGB(self, action='connect'):
		getattr(self.ui.drawLinesCheckBox.clicked, action)(self.modifyMeshObject)
		getattr(self.ui.opacitySlider.valueChanged, action)(self.modifyMeshObject)
		getattr(self.ui.setColorButton.clicked, action)(self.modifyMeshObject)
		getattr(self.ui.front2backRadioButton.clicked, action)(self.modifyMeshObject)
		getattr(self.ui.back2frontRadioButton.clicked, action)(self.modifyMeshObject)


	def toggleVisWin(self, isChecked, pos, size):
		@QtCore.pyqtSlot()
		def toggle():

			if isChecked() == True:
				moveX = pos().x()-self.size().width()-5 # 5 pixels away from the window
				moveY = pos().y()-(self.size().height()-size().height())//2

				if moveX < 0:
					moveX = 0
				if moveY < 0:
					moveY = 0
				self.move(moveX,moveY)
				self.show()
			else:
				self.hide()
		return toggle


	def addRoot(self, name, ident):
		root = ownQTreeWidgetItem(self.ui.treeWidget)
		root.setText(0, name)
		self.ui.treeWidget.addTopLevelItem(root)
		root.setExpanded(True)
		root.setIdentifier(ident)
		return root


	def addChild(self, parent, name, ident):
		item = ownQTreeWidgetItem()
		item.setText(0, name)
		parent.addChild(item)
		item.setExpanded(True)
		item.setIdentifier(ident)
		return item


	def removeItem(self, item):
		if item.parent() == None:
			idx = self.ui.treeWidget.indexOfTopLevelItem(item)
			self.ui.treeWidget.takeTopLevelItem(idx)
		else:
			item.parent().removeChild(item)
		del item


	@QtCore.pyqtSlot()
	def updateTree(self):
		self.ui.treeWidget.clear()

		def recursivelyAddChildren(parentItem, parentModel):
			for child in (parentModel.children if hasattr(parentModel, 'children') else parentModel):
				childItem = self.addChild(parentItem, child.fileName, child.identifier)
				if child.identifier == VisualizationObject.Segmentation:
					if not child in self.windows.keys():
						try:
							dialog = self.segmentationDialogs[child.segmentationIdentifier](child, self)
							self.windows[child] = dialog
							dialog.updateObject.connect(self.modifySegmentation)
						except Exception as e:
							print(e)
							raise TypeError('Segmentation type dialog not implemented: ', child.segmentationIdentifier)

					self.windows[child].update()

				recursivelyAddChildren(childItem, child)


		if len(self.bundleReference):
			bundleRoot = self.addRoot('Bundles', VisualizationObject.Bundle)

			recursivelyAddChildren(bundleRoot, self.bundleReference)

		if len(self.meshReference):
			meshRoot = self.addRoot('Meshes', VisualizationObject.Mesh)

			recursivelyAddChildren(meshRoot, self.meshReference)

		if len(self.mriReference):
			mriRoot = self.addRoot('MRIs', VisualizationObject.MRI)

			recursivelyAddChildren(mriRoot, self.mriReference)

		if len(self.roisReference):
			roisRoot = self.addRoot('ROIs', VisualizationObject.ROI)

			recursivelyAddChildren(roisRoot, self.roisReference)


	@QtCore.pyqtSlot(SegmentationHandler)
	def updateSettingWindow(self, segmentationRef):
		self.windows[segmentationRef].updateWindow()


	@QtCore.pyqtSlot(QtCore.QPoint)
	def prepareMenu(self, pos):
		item = self.ui.treeWidget.itemAt(pos)
		if item == None:
			return

		number = []
		root = identifyNumberRecursively(item,number)

		parent = item.parent()
		text = None
		if parent != None:
			text = parent.text(0)

		# Menu
		contextMenu = QtWidgets.QMenu(self.ui.treeWidget)

		# Actions
		deleteAction = contextMenu.addAction('Delete')
		addSegmentationAction = QtWidgets.QMenu('Add segmentation method')
		addMRIVisualizationAction = QtWidgets.QMenu('Add MRI visualization object')
		visibleToggleAction = QtWidgets.QAction('Visible')
		visibleToggleAction.setCheckable(True)

		windowToggleAction = QtWidgets.QAction('Setting window')
		windowToggleAction.setCheckable(True)

		segmentationAction = dict()
		mriVisAction = dict()

		# Segmentation only on bundles
		if item.identifier == VisualizationObject.Bundle and parent != None:
			contextMenu.addMenu(addSegmentationAction)

			for key in segmentations.keys():
				segmentationAction[addSegmentationAction.addAction(key)] = segmentations[key]

		# MRI slicing and volume
		if item.identifier == VisualizationObject.MRI and parent != None:
			contextMenu.addMenu(addMRIVisualizationAction)

			for key in mriVisualizations.keys():
				mriVisAction[addMRIVisualizationAction.addAction(key)] = mriVisualizations[key]


		# Visible only on Objects
		if root.text(0) == 'Bundles':
			reference = self.bundleReference
		elif root.text(0) == 'Meshes':
			reference = self.meshReference
		elif root.text(0) == 'MRIs':
			reference = self.mriReference
		elif root.text(0) == 'ROIs':
			reference = self.roisReference
		else:
			reference = None

		if parent != None:
			visibleToggleAction.setChecked(retrieveItemIteratively(reference,number).drawable)
			contextMenu.addAction(visibleToggleAction)
		if item.identifier == VisualizationObject.Segmentation:
			dialog = self.windows[retrieveItemIteratively(reference,number)]
			windowToggleAction.setChecked(dialog.isVisible())
			contextMenu.addAction(windowToggleAction)

		# test
		testAction = contextMenu.addAction('Test')

		action = contextMenu.exec_(self.ui.treeWidget.mapToGlobal(pos))

		modifyObject = None

		if action == deleteAction:
			if item.identifier == VisualizationObject.Segmentation:
				self.windows.pop(retrieveItemIteratively(reference,number), None)
			modifyObject = self.prepareDictionary(item, VisualizationActions.Delete)

		elif action == visibleToggleAction:
			modifyObject = self.prepareDictionary(item, VisualizationActions.ToggleDrawable)

		elif action == windowToggleAction:
			dialog = self.windows[retrieveItemIteratively(reference, number)]
			dialog.setVisible(not dialog.isVisible())
			return

		elif action == testAction:
			print('testAction')
			return

		elif action in segmentationAction.keys():
			modifyObject = self.prepareDictionary(item, VisualizationActions.AddSegmentation, data=segmentationAction[action])

		elif action in mriVisAction.keys():
			modifyObject = self.prepareDictionary(item, VisualizationActions.AddSegmentation, data=mriVisAction[action])

		else:
			print('Action not atended: ', action)
			return

		self.changeObject.emit(modifyObject)


	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Delete:
			item = self.ui.treeWidget.currentItem()

			if item == None:
				return

			modifyObject = self.prepareDictionary(item, VisualizationActions.Delete)

			self.changeObject.emit(modifyObject)

		else:
			event.ignore()
			return

		event.accept()


	def identifyItem(self, item):
		if item.parent() == None:
			identifier = item.identifier
			number = -1
		else:
			number = []
			root = identifyNumberRecursively(item,number)
			identifier = root.identifier

		return identifier, number


	def prepareDictionary(self, item, action, data=None):
		opts = {}
		opts['rootType'], opts['number'] = self.identifyItem(item)
		opts['action'] = action

		if data != None:
			opts['data'] = data

		return opts


	@QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
	def activeItemChanged(self, current, previous):
		if current == None:
			self.rotateGroupBox.hide()
			self.translateGroupBox.hide()
			self.scaleGroupBox.hide()
			self.ui.itemSelectedLineEdit.setText('None')

			self.bundleGroupBox.hide()
			self.sliceGroupBox.hide()
			self.meshGroupBox.hide()
			self.volumeGroupBox.hide()
			self.ui.resetTransformsButton.hide()

			activeObject = None

		else:
			self.rotateGroupBox.show()
			self.translateGroupBox.show()
			self.scaleGroupBox.show()
			self.ui.itemSelectedLineEdit.setText(current.text(0))
			self.ui.resetTransformsButton.show()

			number = []
			root = identifyNumberRecursively(current, number)

			# Visible only on Objects
			if root.text(0) == 'Bundles':
				reference = self.bundleReference
			elif root.text(0) == 'Meshes':
				reference = self.meshReference
			elif root.text(0) == 'MRIs':
				reference = self.mriReference
			elif root.text(0) == 'ROIs':
				reference = self.roisReference
			else:
				reference = None

			refObj = retrieveItemIteratively(reference, number)
			activeObject = refObj

			if current.identifier == VisualizationObject.Segmentation:
				print('SEGMENTATION')
			# --------------------BUNDLES--------------------
			if current.identifier == VisualizationObject.Bundle:
				self.bundleGroupBox.show()

				self.bundleGBSignals(action='disconnect')
				if isinstance(refObj, list):
					self.ui.shaderRadioButton_0.setChecked(refObj[0].selectedShader == 0)
					self.ui.shaderRadioButton_1.setChecked(refObj[0].selectedShader == 1)
				else:
					self.ui.shaderRadioButton_0.setChecked(refObj.selectedShader == 0)
					self.ui.shaderRadioButton_1.setChecked(refObj.selectedShader == 1)
				self.bundleGBSignals()

			else:
				self.bundleGroupBox.hide()

			# --------------------MRI SLICE--------------------
			if current.identifier == VisualizationObject.MRISlice:
				self.sliceGroupBox.show()

				self.sliceGBSignals(action='disconnect')
				self.ui.linearInterpCheckBox.setChecked(refObj.linearInterp)
				self.ui.discardPixelsCheckBox.setChecked(refObj.discardValues)
				self.ui.sliceThresholdSlider.setMaximum(int(refObj.max))
				self.ui.sliceThresholdSlider.setValue(int(refObj.threshold))
				self.ui.sliceCurrentThresholdLineEdit.setText(str(refObj.threshold))

				axis = refObj.axis == 1.0
				if axis.sum() == 1:
					if axis[0] == 1.0:
						self.ui.axisXRadioButton.setChecked(True)
					elif axis[1] == 1.0:
						self.ui.axisYRadioButton.setChecked(True)
					elif axis[2] == 1.0:
						self.ui.axisZRadioButton.setChecked(True)
				else:
					self.ui.axisCustomRadioButton.setChecked(True)

				self.axisCXLE.setText(str(refObj.axis[0]))
				self.axisCYLE.setText(str(refObj.axis[1]))
				self.axisCZLE.setText(str(refObj.axis[2]))

				self.slicePos2AxisSlider.setValue(int(refObj.pos2Axis*(self.ui.slicePos2AxisSlider.maximum()+1)))

				self.sliceBrightSlider.setValue(int(refObj.bright*self.sliceBrightSlider.maximum()))
				self.sliceContrastSlider.setValue(int(refObj.contrast*10))
				self.sliceGBSignals()

			else:
				self.sliceGroupBox.hide()

			# --------------------MRI VOLUME--------------------
			if current.identifier == VisualizationObject.MRIVolume:
				self.volumeGBSignals(action='disconnect')
				self.volumeGroupBox.show()

				self.ui.volumeAlphaSlider.setValue(int(refObj.alpha*100))

				self.ui.volumeF2BCheckBox.setChecked(refObj.f2bDrawing)

				self.ui.volumeThresholdSlider.setMaximum(int(refObj.max)*100)
				self.ui.volumeThresholdSlider.setValue(int(refObj.threshold*100))
				self.ui.volumeCurrentThresholdLineEdit.setText(str(refObj.threshold))

				self.volumeGBSignals()

			else:
				self.volumeGroupBox.hide()


			# --------------------MESH--------------------
			if current.identifier == VisualizationObject.Mesh and len(number) != 0:
				self.meshGroupBox.show()

				self.configMeshGB(action='disconnect')
				self.ui.drawLinesCheckBox.setChecked(refObj.drawableLines)
				self.ui.opacitySlider.setValue(int(self.ui.opacitySlider.maximum()*refObj.alpha))

				self.ui.colorWidget.setAutoFillBackground(True)
				self.ui.colorWidget.setPalette(QtGui.QPalette(QtGui.QColor(*(refObj.getRGB256()))))

				if refObj.back2frontSorting:
					self.ui.back2frontRadioButton.setChecked(True)
				else:
					self.ui.front2backRadioButton.setChecked(True)

				self.configMeshGB()

			else:
				self.meshGroupBox.hide()

		self.selectedObject.emit({'current' : activeObject})


	@QtCore.pyqtSlot()
	def rotateItemSelected(self):
		item = self.ui.treeWidget.currentItem()

		if item == None:
			return

		angle = self.ui.rotateAngleLineEdit.text()
		x = self.ui.rotateXLineEdit.text()
		y = self.ui.rotateYLineEdit.text()
		z = self.ui.rotateZLineEdit.text()

		angle = float(angle) if angle != '.' and len(angle) != 0 else 0.0
		x = float(x) if x != '.' and len(x) != 0 else 0.0
		y = float(y) if y != '.' and len(y) != 0 else 0.0
		z = float(z) if z != '.' and len(z) != 0 else 0.0

		axis = [x, y, z]

		if (x**2+y**2+z**2) < 0.0001:
			reply = QtWidgets.QMessageBox.question(self, "Invalid value", 'Axis for rotation was not given.', QtWidgets.QMessageBox.Ok)
			return

		modifyObject = self.prepareDictionary(item, VisualizationActions.Rotate, data=(angle, axis))

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot()
	def resetTransformsItemSelected(self):
		item = self.ui.treeWidget.currentItem()

		if item == None:
			return

		modifyObject = self.prepareDictionary(item, VisualizationActions.ResetTransforms)

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot()
	def loadMatrixFromFile(self):
		item = self.ui.treeWidget.currentItem()

		if item == None:
			return

		matrixFile, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select matrix", "", "matrix (*.npy *.trm *.txt)")

		if len(matrixFile) != 1:
			return

		modifyObject = self.prepareDictionary(item, VisualizationActions.LoadAndApplyMatrix, data=matrixFile[0])

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot()
	def translateItemSelected(self):
		item = self.ui.treeWidget.currentItem()

		if item == None:
			return

		x = self.ui.translateXLineEdit.text()
		y = self.ui.translateYLineEdit.text()
		z = self.ui.translateZLineEdit.text()

		x = float(x) if x != '.' and len(x) != 0 else 0.0
		y = float(y) if y != '.' and len(y) != 0 else 0.0
		z = float(z) if z != '.' and len(z) != 0 else 0.0

		v = [x, y, z]

		modifyObject = self.prepareDictionary(item, VisualizationActions.Translate, data=v)

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot()
	def scaleItemSelected(self):
		item = self.ui.treeWidget.currentItem()

		if item == None:
			print('SHOULDNT BE TRIGGERED')
			return

		x = self.ui.scaleXLineEdit.text()
		y = self.ui.scaleYLineEdit.text()
		z = self.ui.scaleZLineEdit.text()

		x = float(x) if x != '.' and len(x) != 0 else 1.0
		y = float(y) if y != '.' and len(y) != 0 else 1.0
		z = float(z) if z != '.' and len(z) != 0 else 1.0

		v = [x, y, z]

		modifyObject = self.prepareDictionary(item, VisualizationActions.Scale, data=v)

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot()
	def modifyBundleObject(self):
		item = self.ui.treeWidget.currentItem()
		shaderSelected = 0 if self.ui.shaderRadioButton_0.isChecked() else 1

		modifyObject = self.prepareDictionary(item, VisualizationActions.ShaderSelection, data=(shaderSelected))

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot()
	def modifySliceObject(self):
		item = self.ui.treeWidget.currentItem()

		# texture linear interpolation checkbox
		linearInterp = self.ui.linearInterpCheckBox.isChecked()

		# discard values under threshold
		discardValues = self.ui.discardPixelsCheckBox.isChecked()

		# threshold
		threshold = self.ui.sliceThresholdSlider.value()
		self.ui.sliceCurrentThresholdLineEdit.setText(str(threshold))

		# Axis
		if self.ui.axisCustomRadioButton.isChecked():
			x = self.ui.axisCXLE.text()
			y = self.ui.axisCYLE.text()
			z = self.ui.axisCZLE.text()

			x = float(x) if x != '.' and len(x) != 0 else 1.0
			y = float(y) if y != '.' and len(y) != 0 else 1.0
			z = float(z) if z != '.' and len(z) != 0 else 1.0

			if (x**2+y**2+z**2) < 0.0001:
				reply = QtWidgets.QMessageBox.question(self, "Invalid value", 'Axis for plane was not given.', QtWidgets.QMessageBox.Ok)
				return

			axis = [x, y, z]

		else:
			axis = [float(self.ui.axisXRadioButton.isChecked()),
					float(self.ui.axisYRadioButton.isChecked()),
					float(self.ui.axisZRadioButton.isChecked())]

		# pos2Axis slider
		pos2Axis = self.ui.slicePos2AxisSlider.value()/(self.ui.slicePos2AxisSlider.maximum()+1)

		# bright and contrast
		bright = self.ui.sliceBrightSlider.value()/self.ui.sliceBrightSlider.maximum()
		contrast = self.ui.sliceContrastSlider.value()/10

		modifyObject = self.prepareDictionary(item, VisualizationActions.SliceModification, data=(linearInterp, discardValues, threshold, axis, pos2Axis, bright, contrast))

		self.changeObject.emit(modifyObject)

	@QtCore.pyqtSlot()
	def modifyVolumeObject(self):
		item = self.ui.treeWidget.currentItem()

		if self.sender() == self.ui.volumeThresholdSlider or self.sender() == self.ui.volumeAlphaSlider:
			alpha = self.ui.volumeAlphaSlider.value()/100
			threshold = self.ui.volumeThresholdSlider.value()/100

			self.ui.volumeCurrentThresholdLineEdit.setText(str(threshold))

			data = [threshold, alpha]
		else:
			data = self.ui.volumeF2BCheckBox.isChecked()

		modifyObject = self.prepareDictionary(item, VisualizationActions.VolumeModification, data)

		self.changeObject.emit(modifyObject)



	@QtCore.pyqtSlot()
	def modifyMeshObject(self):
		item = self.ui.treeWidget.currentItem()

		sender = self.sender()

		if sender == self.ui.setColorButton:
			color = QtWidgets.QColorDialog.getColor()
			if color.isValid():
				self.ui.colorWidget.setPalette(QtGui.QPalette(color))
				color = (color.red()/255, color.green()/255, color.blue()/255)
			else:
				return

			data = [color]

		elif sender == self.ui.drawLinesCheckBox or sender == self.ui.opacitySlider:

			drawLines = self.ui.drawLinesCheckBox.isChecked()
			opacity = self.ui.opacitySlider.value()/self.ui.opacitySlider.maximum()

			data = (drawLines, opacity)

		elif sender == self.ui.front2backRadioButton:
			data = [False]

		elif sender == self.ui.back2frontRadioButton:
			data = [True]

		else:
			print('Unknown sender for modifyMeshObject in VisDialog:', self.sender())
			return

		modifyObject = self.prepareDictionary(item, VisualizationActions.MeshModification, data=data)

		self.changeObject.emit(modifyObject)


	@QtCore.pyqtSlot(list)
	def objectsChanged(self, objects):
		for dialogs in self.windows.keys():
			try:
				self.windows[dialogs].objectsChanged(objects)
			except:
				pass


	def bundleGBSignals(self, action='connect'):
		getattr(self.ui.shaderRadioButton_0.clicked, action) (self.modifyBundleObject)
		getattr(self.ui.shaderRadioButton_1.clicked, action) (self.modifyBundleObject)

	def sliceGBSignals(self, action='connect'):
		getattr(self.ui.linearInterpCheckBox.clicked, action) (self.modifySliceObject)
		getattr(self.ui.discardPixelsCheckBox.clicked, action) (self.modifySliceObject)
		getattr(self.ui.sliceThresholdSlider.valueChanged, action) (self.modifySliceObject)
		getattr(self.ui.axisXRadioButton.clicked, action) (self.modifySliceObject)
		getattr(self.ui.axisYRadioButton.clicked, action) (self.modifySliceObject)
		getattr(self.ui.axisZRadioButton.clicked, action) (self.modifySliceObject)
		getattr(self.ui.axisCustomRadioButton.clicked, action) (self.modifySliceObject)
		getattr(self.ui.axisCXLE.returnPressed, action) (self.modifySliceObject)
		getattr(self.ui.axisCYLE.returnPressed, action) (self.modifySliceObject)
		getattr(self.ui.axisCZLE.returnPressed, action) (self.modifySliceObject)
		getattr(self.ui.slicePos2AxisSlider.valueChanged, action) (self.modifySliceObject)
		getattr(self.ui.sliceBrightSlider.valueChanged, action) (self.modifySliceObject)
		getattr(self.ui.sliceContrastSlider.valueChanged, action) (self.modifySliceObject)

	def volumeGBSignals(self, action='connect'):
		getattr(self.ui.volumeThresholdSlider.valueChanged, action) (self.modifyVolumeObject)
		getattr(self.ui.volumeAlphaSlider.valueChanged, action) (self.modifyVolumeObject)
		getattr(self.ui.volumeF2BCheckBox.clicked, action) (self.modifyVolumeObject)
		getattr(self.ui.volumeCurrentThresholdLineEdit.returnPressed, action) (self.modifyVolumeObject)
