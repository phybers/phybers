#ifndef ROISEGMENTATIONCFUNCTIONS_H
#define ROISEGMENTATIONCFUNCTIONS_H


#include "stdio.h"
#include "math.h"
#include <stdbool.h>

#ifdef __APPLE__
#include <OpenGL/gl3.h>
#else
#include <GL/gl.h>
#endif

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


unsigned takeNodeFromPool(float *center, float * radius, struct OctreePool* nodePool);
void octreeSubdivide(struct OctreeNode* node, float *vertexPool, struct OctreePool* nodePool);
bool octreeInsertVertex(struct OctreeNode* node, unsigned idx, float *vertexPool, struct OctreePool* nodePool);
unsigned octreeRecursiveDefragment(struct OctreeNode* inNode, struct OctreePool* nodePool, unsigned *poolOffset, unsigned vertexIdxOffset, unsigned *vertexIdxPool, struct OctreeNode* swapNode, unsigned * childrenRefTMP);
void octreeDefragment();

unsigned ROIsSegmentationPopulateAndDefragmentPool(void * pyOCPool, int octreePoolSize, void *pyPoints, int pointsSize, void *pyCenter, void *pyRadius, void *pyVertexIdxPool);

#endif // ROISEGMENTATIONCFUNCTIONS_H