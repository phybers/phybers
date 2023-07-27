from PyQt5 import QtGui, QtWidgets, uic, QtCore
# import PyQt5
from ...Framework.Tools.visualizationEnums import *
from importlib_resources import files

_ffcsd_ui = files('phybers.fibervis.ui.Segmentations').joinpath(
	'FFClustSegmentationDialog.ui')

class FFClustSegmentationDialog(QtWidgets.QDialog):
	updateObject = QtCore.pyqtSignal(dict)


	def __init__(self, segmentation, parent):
		super().__init__(parent)
		self.ui = uic.loadUi(str(_ffcsd_ui), self)

		self.segmentationRef = segmentation


		self.ui.alphaSlider.valueChanged.connect(self.alphaChanged)

		self.ui.segmentButton.clicked.connect(self.segmentSubject)
		self.ui.exportBundleButton.clicked.connect(self.exportBundle)
		self.ui.exportCentroidButton.clicked.connect(self.exportCentroid)

		self.show()


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


	@QtCore.pyqtSlot()
	def exportCentroid(self):
		# Gets direction of bundle files
		outFile, fileType = QtWidgets.QFileDialog.getSaveFileName(self, "Save Bundle file", "", "Bundle (*.bundles)")#;;Trk file (*.trk)")

		options = {	'reference' : self.segmentationRef,
					'attributes' : {'exportCentroidFile' : [outFile]}}

		self.updateObject.emit(options)





	def __del__(self):
		print('Must clean befor leaving... INPLACESEGMENTATIONDIALOG', type(self))
		segmentationRef = None
		# super.__del__()


	def update(self):
		pass