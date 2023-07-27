from PyQt5 import QtGui, QtWidgets, uic, QtCore
from ...Framework.Tools.visualizationEnums import *
from importlib_resources import files

_abpsd_ui = files('phybers.fibervis.ui.Segmentations').joinpath(
	'AtlasBasedParallelSegmentationDialog.ui')

class AtlasBasedParallelSegmentationDialog(QtWidgets.QDialog):
	updateObject = QtCore.pyqtSignal(dict)

	def __init__(self, segmentation, parent):
		super().__init__(parent)
		self.ui = uic.loadUi(str(_abpsd_ui), self)

		self.segmentationRef = segmentation

		self.bundleNames = None
		self.bundleSize = None
		self.states = []

		self.ui.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.ui.tableWidget.setColumnWidth(0, 150)
		self.ui.tableWidget.setColumnWidth(2, 50)
		self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

		self.ui.tableWidget.cellClicked.connect(self.toggleCheck)

		self.ui.checkSegmentAll.clicked.connect(self.checkSegmentAllBundles)

		self.ui.alphaSlider.valueChanged.connect(self.alphaChanged)

		self.ui.addBundlesButton.clicked.connect(self.addBundles)
		self.ui.removeBundlesButton.clicked.connect(self.removeBundles)
		self.ui.applyMatrixButton.clicked.connect(self.applyMatrix)

		self.ui.addThresholdFileButton.clicked.connect(self.addThresholdFile)

		self.ui.filterLineEdit.textChanged.connect(self.filter)

		self.ui.segmentButton.clicked.connect(self.segmentSubject)
		self.ui.exportBundleButton.clicked.connect(self.exportBundle)

		self.show()


	@QtCore.pyqtSlot()
	def segmentSubject(self):
		options = {	'reference' : self.segmentationRef,
					'segmentSubject' : True}

		self.updateObject.emit(options)


	def checkSegmentAllBundles(self):
		print('checkSegmentAll')


	def addThresholdFile(self):
		# Gets direction of bundle files
		thresholdFile, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select threshold file", "", "Txt (*.txt)")

		if len(thresholdFile) != 1:
			return

		options = {	'reference' : self.segmentationRef,
					'attributes': {'updateAtlas' : [None, None, thresholdFile[0]]},
					'updateViewingObjects' : True,
					'updateSettingWindow' : True}

		self.updateObject.emit(options)


	def addBundles(self):
		# Gets direction of bundle files
		bundleFiles, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Bundle", "", "Bundles (*.bundles *.trk)")

		if len(bundleFiles) == 0:
			return

		options = {	'reference' : self.segmentationRef,
					'attributes': {'updateAtlas' : [bundleFiles]},
					'updateViewingObjects' : True,
					'updateSettingWindow' : True}

		self.updateObject.emit(options)


	def removeBundles(self):
		pass


	@QtCore.pyqtSlot(int)
	def toggleCheck(self, row):
		tmpItem = self.ui.tableWidget.item(row,0)
		tmpItem.setCheckState(not tmpItem.checkState())


	# @QtCore.pyqtSlot()
	# def checkSegmentAll(self):
	# 	self.ui.tableWidget.cellChanged.disconnect(self.toggleStates)

	# 	visualize = self.ui.checkSegmentAll.isChecked()

	# 	for i in range(self.ui.tableWidget.rowCount()):
	# 		item = self.ui.tableWidget.item(i,0)
	# 		item.setCheckState(visualize)
	# 		self.states[self.bundleNames.index(item.text())] = visualize

	# 	if self.ui.checkRender.isChecked():
	# 		self.updateObject.emit(self.returnDict())

	# 	self.ui.tableWidget.cellChanged.connect(self.toggleStates)


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

				self.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(self.bundleSize[i]))
				self.ui.tableWidget.item(row,1).setTextAlignment(QtCore.Qt.AlignRight)
				row = row + 1

		checkStateN = 0

		for i in range(self.ui.tableWidget.rowCount()):
			if self.ui.tableWidget.item(i,0).checkState():
				checkStateN += 1

		if checkStateN == self.ui.tableWidget.rowCount():
			self.ui.checkSegmentAll.setChecked(True)
		elif checkStateN == 0:
			self.ui.checkSegmentAll.setChecked(False)

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
			self.ui.checkSegmentAll.setChecked(True)
		else:
			self.ui.checkSegmentAll.setChecked(False)

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


	@QtCore.pyqtSlot()
	def applyMatrix(self):
		matrixFile, fileType = QtWidgets.QFileDialog.getOpenFileNames(self, "Select matrix", "", "matrix (*.npy *.trm)")

		if len(matrixFile) != 1:
			return

		options = {	'reference' : self.segmentationRef,
					'attributes': {'updateAtlas' : [None, None, None, matrixFile[0]]},
					'updateViewingObjects' : True,
					'updateSettingWindow' : False}

		self.updateObject.emit(options)


	def updateWindow(self):

		validTableData = self.segmentationRef.atlas.getValidBundles()
		invalidTableData = self.segmentationRef.atlas.getInvalidBundles()

		self.ui.tableWidget.clearContents()
		self.ui.tableWidget.setRowCount(0)

		for i in range(len(validTableData)):
			self.ui.tableWidget.insertRow(i)
			data = validTableData[i]

			name = QtWidgets.QTableWidgetItem(data[0])
			nfiber = QtWidgets.QTableWidgetItem(str(data[1]))
			hie = QtWidgets.QTableWidgetItem()
			thr = QtWidgets.QTableWidgetItem(str(data[3]))

			hie.setBackground(QtGui.QBrush(QtGui.QColor(
													int(data[2][0]*255),
													int(data[2][1]*255),
													int(data[2][2]*255))))

			self.ui.tableWidget.setItem(i, 0, name)
			self.ui.tableWidget.setItem(i, 1, nfiber)
			self.ui.tableWidget.setItem(i, 2, hie)
			self.ui.tableWidget.setItem(i, 3, thr)

		for i in range(len(invalidTableData)):
			j = i+len(validTableData)
			self.ui.tableWidget.insertRow(j)
			data = invalidTableData[i]

			name = QtWidgets.QTableWidgetItem(data[0])
			nfiber = QtWidgets.QTableWidgetItem(str(data[1]))
			hie = QtWidgets.QTableWidgetItem()
			thr = QtWidgets.QTableWidgetItem(str(data[3]))

			name.setBackground(QtGui.QBrush(QtGui.QColor(255,0,0)))
			nfiber.setBackground(QtGui.QBrush(QtGui.QColor(255,0,0)))
			hie.setBackground(QtGui.QBrush(QtGui.QColor(0,0,0)))
			thr.setBackground(QtGui.QBrush(QtGui.QColor(255,0,0)))

			self.ui.tableWidget.setItem(j, 0, name)
			self.ui.tableWidget.setItem(j, 1, nfiber)
			self.ui.tableWidget.setItem(j, 2, hie)
			self.ui.tableWidget.setItem(j, 3, thr)


	def returnDict(self):
		return {'reference' : self.segmentationRef,
				'attributes' : {'setPercentage' : [self.ui.percentSlider.value()],
								'setStates' : [self.states]},
				'segmentSubject' : True}


	def __del__(self):
		print('Must clean befor leaving... INPLACESEGMENTATIONDIALOG', type(self))
		segmentationRef = None
		# super.__del__()
