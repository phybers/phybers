#ifndef POINTOCTREE_H
#define POINTOCTREE_H

#include <Python.h>
#include <stdbool.h>
// ROIs segmentation.

// Octree datatype, build and defragmentation
#define OT_NODE_CAPACITY 256

struct OctreePool {
	struct OctreeNode *pool;
	unsigned **ce_pool;

	size_t pool_size;
	unsigned pool_idx;
};

struct OctreeNode {
	unsigned children[8]; 
	unsigned numberOfElements;
	unsigned contentElements;
	float radius[3];
	float center[3];
};


unsigned ROIsSegmentationPopulateAndDefragmentPool(void * pyOCPool,
	int octreePoolSize,
	void * pyPoints,
	int pointsSize,
	void * pyCenter,
	void * pyRadius,
	void * pyVertexIdxPool);


unsigned takeNodeFromPool(float *center, float * radius, struct OctreePool* nodePool);
bool octreeInsertVertex(struct OctreeNode* node, unsigned idx, float *vertexPool, struct OctreePool* nodePool);
void octreeSubdivide(struct OctreeNode* node, float *vertexPool, struct OctreePool* nodePool);
unsigned octreeRecursiveDefragment(struct OctreeNode* inNode, struct OctreePool* nodePool, unsigned *poolOffset, unsigned vertexIdxOffset, unsigned *vertexIdxPool, struct OctreeNode* swapNode, unsigned * childrenRefTMP);
void octreeDefragment();

// Octree collision query functions

struct ROI {
	float center[3];
	float radius[3];
	int roiType;
};

bool boundaryIntersectsSphere(struct ROI * sphere, struct OctreeNode * node);
bool sphereContainsVertex(struct ROI * sphere, float vertex_x, float vertex_y, float vertex_z);
bool SphereContainsBoundary(struct ROI * sphere, struct OctreeNode * node);
void querySphere(struct ROI * sphere, int nodeIdx, struct OctreeNode * nodePool, unsigned * vertex2Fiber, unsigned * vertexIdxPool, float * points, bool * result);

void queryTree(int nROI,
	void * roiDataArray,
	void * pyOCPool,
	void * pyVertexIdxPool,
	void * pyVertex2Fiber,
	void * pyPoints,
	void * pyResult,
	int curvesCount);

int createEBO(int curvesCount,
	void *pyFiberValidator,
	void *pyFiberSize,
	void *pyEbo,
	int end);


void ROISegmentationExportbundlesdata(char * filePath,
		int bundleN,
		void * pyBundlesStart,
		void * pyFiberSize,
		void * pyBundleCount,
		void * pyPoints,
		void * pyFiberValidator);


#endif