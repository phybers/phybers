from .SegmentationHandler import *
# import Framework.CExtend.cfuncs as cfuncs
from ...FiberVis_core import inPlaceSegmentationMethod

class InPlaceSegmentation(SegmentationHandler):
	def __init__(self, bundle, shaderDict):
		super().__init__(bundle, shaderDict)

		self.segmentationIdentifier = SegmentationTypes.InPlace

		self.bundleStates = np.ones(len(self.bundlesName), dtype=np.int32) # int8 = c boolean
		self.percentage = 100
		self.fileName = 'In place segmentation' # temporal

		self.alpha = 0.8

		# Creates VBOs & an EBO, then populates them with the point, normal and color data. The elements data goes into the EBO
		self.configFiberValidator()

		self._loadBuffers()
		self.buildVertex2Fiber()
		self.vboAndLinkVertex2Fiber()

		self.boundingbox = BoundingBox(shaderDict, self, bundle.boundingbox.dims, bundle.boundingbox.center)


	def segmentMethod(self):
		self.fiberValidator[:self.curvescount] = 0

		inPlaceSegmentationMethod(
			self.bundleStates.size,
			self.percentage,
			self.bundlesStart,
			self.bundleStates,
			self.fiberValidator)

		# cfuncs.inPlaceSegmentationMethod(
		# 	self.bundleStates.size,
		# 	self.percentage,
		# 	self.bundlesStart.ctypes.data,
		# 	self.bundleStates.ctypes.data,
		# 	self.fiberValidator.ctypes.data)


	def setPercentage(self, newPercentage):
		self.percentage = newPercentage


	def setStates(self, newStates):
		self.bundleStates = np.array(newStates, dtype=np.int32)