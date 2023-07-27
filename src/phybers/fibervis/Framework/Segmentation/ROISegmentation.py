'''
- Change tree from octree to R-tree. or study other balanced trees
- If octree pool overflows it should create a second pool
'''

from .SegmentationHandler import *
from .ROI import ROI
from ..Tools.shunting_yard import shuntingYard

from ..Tools.DataStructures import OctreePointBased


class ROISegmentation(SegmentationHandler):
	# @averageTimeit
	def __init__(self, bundle, shaderDict):
		super().__init__(bundle, shaderDict)

		self.segmentationIdentifier = SegmentationTypes.ROIs

		self.tree = None
		self.roiValidator = []
		self.rois = []
		# self.fiberSizes = bundle.fiberSizes

		for sibling in self.parent.children:
			if isinstance(sibling, ROISegmentation):
				self.tree = sibling.tree

		if self.tree == None:
			self.tree = OctreePointBased(self.points, self.fiberSizes)

		self.fileName = 'ROI Segmentation' # temporal

		self.alpha = 0.8
		self.validLogic = False

		self.configFiberValidator()

		self._loadBuffers()
		self.buildVertex2Fiber()
		self.vboAndLinkVertex2Fiber()

		self.boundingbox = BoundingBox(shaderDict, self, bundle.boundingbox.dims, bundle.boundingbox.center)


	# @timeit
	def segmentMethod(self):
		rois2beQuery = None
		roisResults = None

		if self.validLogic:
			rois2beQuery = [self.rois[i] for i in self.logicRois]
		else:
			rois2beQuery = [self.rois[i] for i in [i for i, e in enumerate(self.roiValidator) if e]]


		n = len(rois2beQuery)

		if n == 0:
			self.fiberValidator[:self.curvescount] = 1

		else:
			roisResults = np.zeros((n, self.curvescount), dtype=np.int8)

			dt = np.dtype([	('center', np.float32, 3),
							('radius', np.float32, 3),
							('roiType', np.int32, (1,))])

			dataPacked = np.empty(len(rois2beQuery), dtype=dt)

			for i in range(len(rois2beQuery)):
				dataPacked[i]['center'] = rois2beQuery[i].getCenter(self.inverseModel)
				dataPacked[i]['radius'] = rois2beQuery[i].getRadius(self.inverseModel)
				dataPacked[i]['roiType'] = rois2beQuery[i].getROIValue()


			self.tree.queryCollision(dataPacked, roisResults)


			if self.validLogic:
				infix = [roisResults[self.logicRois.index(i)] if isinstance(i, int) else i for i in self.logicInfix]
				self.fiberValidator[:self.curvescount] = shuntingYard(infix)

			else:
				self.fiberValidator[:self.curvescount] = roisResults.sum(axis=0, dtype=np.int8) #could overflow with 256 rois or more


	def addROI(self, roi):
		'''
		'''

		if isinstance(roi, ROI) and not roi in self.rois:
			self.children.append(roi)
			self.rois.append(roi)
			self.roiValidator.append(True)


	def removeROIFromIndex(self, index):
		roi = self.rois.pop(index)
		self.roiValidator.pop(index)
		self.children.remove(roi)


	def setValidatorAtIndex(self, index, validate):
		self.roiValidator[index] = validate


	def updateLogic(self, logicStr):
		self.validLogic = False

		if logicStr == '':
			raise ValueError('ROISegmentation: Empty logic string.')

		parsed = self.parseLogicString(logicStr)

		if not parsed:
			raise ValueError('ROISegmentation: Not a valid string for logic operations.')

		self.logicInfix = parsed

		self.logicRois = list(set([i for i in parsed if isinstance(i, int)]))

		if max(self.logicRois) >= len(self.rois):
			raise ValueError('ROISegmentation: Not a valid ID for ROI selection. ID: {}.'.format(max(self.logicRois)))

		self.validLogic = True


	def parseLogicString(self, logicStr):
		''' Could get a list of valid ids '''
		numberStack = ''
		infix = []

		for i in logicStr:
			if i.isdigit():
				numberStack += i

			elif i == '|' or i == '&' or i == '^' or i == '(' or i == ')' or i == '!':

				if numberStack != '':
					infix.append(int(numberStack))
					if infix[-1] >= len(self.rois):
						return False
					numberStack = ''

				infix.append(i)

			elif i == '+':
				if numberStack != '':
					infix.append(int(numberStack))
					if infix[-1] >= len(self.rois):
						return False
					numberStack = ''

				infix.append('|')

			else:
				return False

		if numberStack != '':
			infix.append(int(numberStack))

		return infix