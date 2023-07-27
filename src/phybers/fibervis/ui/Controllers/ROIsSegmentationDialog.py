from PyQt5 import QtGui, QtWidgets, uic, QtCore
from ...Framework.Tools.visualizationEnums import *

from functools import wraps
from importlib_resources import files

_roisd_ui = files('phybers.fibervis.ui.Segmentations').joinpath(
	'ROIsSegmentationDialog.ui')


# MUST DELETE
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
	###########


def detectAlways(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		func(*args, **kwargs)

		if args[0].ui.alwaysBox.isChecked():
			args[0].segmentSubject()
	return wrapper


class ROIsSegmentationDialog(QtWidgets.QDialog):
	updateObject = QtCore.pyqtSignal(dict)


	def __init__(self, segmentation, parent):
		super().__init__(parent)
		self.ui = uic.loadUi(str(_roisd_ui), self)

		self.segmentationRef = segmentation

		self.ui.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

		self.ui.addROIButton.clicked.connect(self.addROI)
		self.ui.removeROIButton.clicked.connect(self.removeROI)

		self.ui.detectButton.clicked.connect(self.segmentSubject)

		self.ui.exportButton.clicked.connect(self.exportBundle)

		self.ui.alphaSlider.valueChanged.connect(self.alphaChanged)

		self.ui.tableWidget.cellChanged.connect(self.cellChanged)

		self.ui.logicLineEdit.returnPressed.connect(self.logicLineEditEdited)

		self.show()




	# // Actualiza dibujo al clickear checkbox de la tabla
	# this.connect(this.ui.tableWidget, SIGNAL(cellChanged(int,int)), this, SLOT(itemtoggle(int,int)));


	@detectAlways
	@QtCore.pyqtSlot()
	def addROI(self):
		treeWidgetItems = self.parentWidget().ui.treeWidget.selectedItems()
		if len(treeWidgetItems) == 0:
			return
		elif treeWidgetItems[0].identifier != VisualizationObject.ROI:
			QtWidgets.QMessageBox.question(self, "Invalid ROI", 'Must select a ROI from the visualization tool dialog.', QtWidgets.QMessageBox.Ok)
			return

		# Bad practice
		##############
		number = []
		root = identifyNumberRecursively(treeWidgetItems[0], number)

		if root.text(0) == 'Bundles':
			reference = self.parentWidget().bundleReference
		elif root.text(0) == 'Meshes':
			reference = self.parentWidget().meshReference
		elif root.text(0) == 'MRIs':
			reference = self.parentWidget().mriReference
		elif root.text(0) == 'ROIs':
			reference = self.parentWidget().roisReference
		else:
			reference = None

		refObj = retrieveItemIteratively(reference, number)
		if isinstance(refObj, list):
			QtWidgets.QMessageBox.question(self, "Too many ROIs", 'Please select one ROI.', QtWidgets.QMessageBox.Ok)
			return
		##############

		options = {	'reference' : self.segmentationRef,
					'attributes': {'addROI' : [refObj]},
					'updateViewingObjects' : True}

		self.updateObject.emit(options)


	@detectAlways
	@QtCore.pyqtSlot()
	def removeROI(self):
		index = self.ui.tableWidget.currentRow()

		# self.ui.tableWidget.removeRow(index)
		options = {	'reference' : self.segmentationRef,
					'attributes': {'removeROIFromIndex' : [index]},
					'updateViewingObjects' : True}

		self.updateObject.emit(options)


	@QtCore.pyqtSlot()
	def segmentSubject(self):
		options = {	'reference' : self.segmentationRef,
					'segmentSubject' : True}

		self.updateObject.emit(options)


	@QtCore.pyqtSlot()
	def alphaChanged(self):
		alpha = self.alphaSlider.value()/(self.alphaSlider.maximum()+1)

		options = {	'reference' : self.segmentationRef,
					'attributes': {'setAlpha' : [alpha]}}

		self.updateObject.emit(options)


	@QtCore.pyqtSlot()
	def exportBundle(self):

		# Gets direction of bundle files
		outFile, fileType = QtWidgets.QFileDialog.getSaveFileName(self, "Save Bundle file", "", "Bundle (*.bundles)")#;;Trk file (*.trk)")

		options = {	'reference' : self.segmentationRef,
					'attributes' : {'exportFile' : [outFile]}}

		self.updateObject.emit(options)


	@detectAlways
	@QtCore.pyqtSlot(int, int)
	def cellChanged(self, row, column):
		if column == 0:
			checked = self.ui.tableWidget.item(row, column).checkState() == QtCore.Qt.Checked

			options = {	'reference' : self.segmentationRef,
						'attributes' : {'setValidatorAtIndex' : [row, checked]}}

			self.updateObject.emit(options)


	@detectAlways
	@QtCore.pyqtSlot()
	def logicLineEditEdited(self):
		options = {	'reference' : self.segmentationRef,
					'attributes': {'updateLogic' : [str(self.ui.logicLineEdit.text())]}}

		self.updateObject.emit(options)


	def update(self):
		while self.ui.tableWidget.rowCount():
			self.ui.tableWidget.removeRow(0)

		for i in range(len(self.segmentationRef.children)):
			self.insertItemInTable(self.segmentationRef.children[i], self.segmentationRef.roiValidator[i])

	def objectsChanged(self, objects):
		if self.ui.alwaysBox.isChecked():
			for obj in objects:
				if obj in self.segmentationRef.children or obj is self.segmentationRef:
					self.segmentSubject()
					return


	def insertItemInTable(self, objRef, checked):
		self.ui.tableWidget.cellChanged.disconnect(self.cellChanged)

		row = self.ui.tableWidget.rowCount()
		self.ui.tableWidget.insertRow(row)

		tag = QtWidgets.QTableWidgetItem(str(row))
		tag.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
		tag.setTextAlignment(QtCore.Qt.AlignHCenter)
		tag.setFlags(tag.flags() & ~QtCore.Qt.ItemIsEditable)

		bg = QtWidgets.QTableWidgetItem()
		bg.setBackground(QtGui.QBrush(QtGui.QColor(
						int(objRef.getRGB256()[0]),
						int(objRef.getRGB256()[1]),
						int(objRef.getRGB256()[2]))))
		bg.setFlags(bg.flags() & ~QtCore.Qt.ItemIsEditable)

		roiType = QtWidgets.QTableWidgetItem(str(objRef.roiType))
		roiType.setTextAlignment(QtCore.Qt.AlignHCenter)
		roiType.setFlags(roiType.flags() & ~QtCore.Qt.ItemIsEditable)

		self.ui.tableWidget.setItem(row, 0, tag)
		self.ui.tableWidget.setItem(row, 1, bg)
		self.ui.tableWidget.setItem(row, 2, roiType)

		self.ui.tableWidget.selectRow(row)

		self.ui.tableWidget.cellChanged.connect(self.cellChanged)
