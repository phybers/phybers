from enum import Enum

class VisualizationObject(Enum):
	NotDefined = -1
	Bundle = 0
	Mesh = 1
	Atlas = 7
	MRI = 2
	Segmentation = 3
	MRIVolume = 4
	MRISlice = 5
	ROI = 6

class ROIType(Enum):
	Sphere = 0
	Aabb = 1
	Obb = 2
	Plane = 3

class VisualizationActions(Enum):
	Delete = 0
	ToggleDrawable = 1
	Rotate = 2
	Translate = 3
	Scale = 4
	AddSegmentation = 5
	SliceModification = 6
	VolumeModification = 7
	MeshModification = 8
	ResetTransforms = 9
	LoadAndApplyMatrix = 10
	ShaderSelection = 11

class SegmentationTypes(Enum):
	InPlace = 0
	ROIs = 1
	AtlasBased = 2
	FFClust = 3
	Test = 23

segmentations = {	'In place segmentation' : SegmentationTypes.InPlace,
					'Roi segmentation' : SegmentationTypes.ROIs,
					'Euclidean distance segmentation' : SegmentationTypes.AtlasBased,
					'FFClust' : SegmentationTypes.FFClust,
					'Test segmentation' : SegmentationTypes.Test}

mriVisualizations = {	'Volume render' : VisualizationObject.MRIVolume,
						'Slice' : VisualizationObject.MRISlice}