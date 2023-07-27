from PyQt5 import QtGui, QtWidgets, uic, QtCore
# import PyQt5
from ...Framework.Tools.visualizationEnums import *
from importlib_resources import files

_aipsd_ui = files('phybers.fibervis.ui.Segmentations').joinpath(
	'InPlaceSegmentationDialog.ui')

class InPlaceSegmentationDialog(QtWidgets.QDialog):
	updateObject = QtCore.pyqtSignal(dict)


	def __init__(self, segmentation, parent):
		super().__init__(parent)
		self.ui = uic.loadUi(str(_aipsd_ui), self)

		self.segmentationRef = segmentation

		self.bundleNames = None
		self.bundleSize = None
		self.states = []
		self.setBundles(self.segmentationRef.bundlesName, self.segmentationRef.bundlesStart)

		self.ui.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.ui.tableWidget.setColumnWidth(0, 150)
		self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

		self.ui.tableWidget.cellClicked.connect(self.toggleCheck)

		self.ui.checkVisualizeAll.clicked.connect(self.visualizeAll)

		self.ui.percentSlider.valueChanged.connect(self.checkRenderState)

		self.ui.filterLineEdit.textChanged.connect(self.filter)

		self.ui.alphaSlider.valueChanged.connect(self.alphaChanged)

		self.ui.renderButton.clicked.connect(self.callUpdate)
		self.ui.exportBundleButton.clicked.connect(self.exportBundle)

		self.show()


	@QtCore.pyqtSlot(int)
	def toggleCheck(self, row):
		tmpItem = self.ui.tableWidget.item(row,0)
		tmpItem.setCheckState(not tmpItem.checkState())


	@QtCore.pyqtSlot()
	def visualizeAll(self):
		self.ui.tableWidget.cellChanged.disconnect(self.toggleStates)

		visualize = self.ui.checkVisualizeAll.isChecked()

		for i in range(self.ui.tableWidget.rowCount()):
			item = self.ui.tableWidget.item(i,0)
			item.setCheckState(visualize)
			self.states[self.bundleNames.index(item.text())] = visualize

		if self.ui.checkRender.isChecked():
			self.updateObject.emit(self.returnDict())

		self.ui.tableWidget.cellChanged.connect(self.toggleStates)


	@QtCore.pyqtSlot()
	def callUpdate(self):
		self.updateObject.emit(self.returnDict())


	@QtCore.pyqtSlot()
	def checkRenderState(self):
		if self.ui.checkRender.isChecked():
			self.updateObject.emit(self.returnDict())


	# TMP!!!!!!
	@QtCore.pyqtSlot(str)
	def filter(self, text):
		self.ui.tableWidget.cellChanged.disconnect(self.toggleStates)

		self.ui.tableWidget.clearContents()
		self.ui.tableWidget.setRowCount(0)

		row = 0
		for i in range(len(self.bundleNames)):
			if self.bundleNames[i].find(text) != -1:
				self.ui.tableWidget.insertRow(row)
				item = QtWidgets.QTableWidgetItem(self.bundleNames[i])
				item.setCheckState(self.states[i])
				self.ui.tableWidget.setItem(row, 0, item)

				self.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(self.bundleSize[i])))
				self.ui.tableWidget.item(row,1).setTextAlignment(QtCore.Qt.AlignRight)
				row = row + 1

		checkStateN = 0

		for i in range(self.ui.tableWidget.rowCount()):
			if self.ui.tableWidget.item(i,0).checkState():
				checkStateN += 1

		if checkStateN == self.ui.tableWidget.rowCount():
			self.ui.checkVisualizeAll.setChecked(True)
		elif checkStateN == 0:
			self.ui.checkVisualizeAll.setChecked(False)

		self.ui.tableWidget.cellChanged.connect(self.toggleStates)


	@QtCore.pyqtSlot(int)
	def toggleStates(self, row):
		item = self.ui.tableWidget.item(row,0)
		tmp = self.bundleNames.index(item.text())
		self.states[tmp] = bool(item.checkState())

		tmp = 0

		for i in range(self.ui.tableWidget.rowCount()):
			tmp += int(self.ui.tableWidget.item(i,0).checkState())

		if tmp == self.ui.tableWidget.rowCount():
			self.ui.checkVisualizeAll.setChecked(True)
		else:
			self.ui.checkVisualizeAll.setChecked(False)

		if self.ui.checkRender.isChecked():
			self.updateObject.emit(self.returnDict())


	@QtCore.pyqtSlot()
	def exportBundle(self):

		# Gets direction of bundle files
		outFile, fileType = QtWidgets.QFileDialog.getSaveFileName(self, "Save Bundle file", "", "Bundle (*.bundles)")#;;Trk file (*.trk)")

		options = {	'reference' : self.segmentationRef,
					'attributes' : {'exportFile' : [outFile]}}

		self.updateObject.emit(options)


	@QtCore.pyqtSlot()
	def alphaChanged(self):
		alpha = self.alphaSlider.value()/(self.alphaSlider.maximum()+1)

		options = {	'reference' : self.segmentationRef,
					'attributes': {'setAlpha' : [alpha]}}

		self.updateObject.emit(options)


	def setBundles(self, bundlenames, bundlesize):
		self.bundleNames = bundlenames
		self.bundleSize = bundlesize[1:]-bundlesize[:-1]

		# self.ui.tableWidget.cellChanged.disconnect(self.toggleStates)

		self.ui.tableWidget.clearContents()

		for i in range(len(self.bundleNames)):
			self.states.append(True)

			self.ui.tableWidget.insertRow(i)
			item = QtWidgets.QTableWidgetItem(self.bundleNames[i])
			item.setCheckState(True)
			self.ui.tableWidget.setItem(i,0,item)

			self.ui.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(str(self.bundleSize[i])))
			self.ui.tableWidget.item(i,1).setTextAlignment(QtCore.Qt.AlignRight)

		self.ui.checkVisualizeAll.setChecked(True)

		self.ui.tableWidget.cellChanged.connect(self.toggleStates)

	def returnDict(self):
		return {'reference' : self.segmentationRef,
				'attributes' : {'setPercentage' : [self.ui.percentSlider.value()],
								'setStates' : [self.states]},
				'segmentSubject' : True}


	def __del__(self):
		print('Must clean befor leaving... INPLACESEGMENTATIONDIALOG', type(self))
		segmentationRef = None
		# super.__del__()


	def update(self):
		pass